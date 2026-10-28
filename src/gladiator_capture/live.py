"""Kraken WebSocket v2 live capture: `book` depth 10, `trade` and `status` (W-J, DEC-057, DEC-062).

Every received frame is written, before parsing, to an append-only journal with its receive
time (raw preservation, event contract §2). The book is rebuilt from snapshot plus updates and
checked against the venue CRC32 checksum. On a mismatch the book is invalidated and
resubscribed (S-15, Q-5). On a disconnect the client reconnects with backoff (RC-09, R-2).
"""

from __future__ import annotations

import json
import socket
import struct
import time
import zlib
from dataclasses import dataclass, field
from datetime import datetime
from decimal import Decimal
from pathlib import Path
from typing import Optional

from .ws import WebSocket, WebSocketClosed

URL = "wss://ws.kraken.com/v2"
DEPTH = 10
RECONNECT_DELAYS_S = (1, 2, 5, 10, 30, 60)


def _fmt(value: Decimal, decimals: int) -> str:
    """Kraken checksum formatting: fixed precision, decimal point removed, leading zeros removed."""
    s = format(value, f".{decimals}f").replace(".", "").lstrip("0")
    return s or "0"


def book_checksum(asks: dict, bids: dict, price_dec: int, qty_dec: int) -> int:
    """CRC32 over the top 10 asks (ascending price) then the top 10 bids (descending price)."""
    s = "".join(_fmt(p, price_dec) + _fmt(asks[p], qty_dec) for p in sorted(asks)[:DEPTH])
    s += "".join(_fmt(p, price_dec) + _fmt(bids[p], qty_dec) for p in sorted(bids, reverse=True)[:DEPTH])
    return zlib.crc32(s.encode()) & 0xFFFFFFFF


@dataclass
class Book:
    symbol: str
    price_dec: int
    qty_dec: int
    bids: dict = field(default_factory=dict)
    asks: dict = field(default_factory=dict)
    valid: bool = False
    invalid_since_ns: Optional[int] = None
    synced_once: bool = False

    def apply(self, levels: list, side: dict) -> None:
        for lv in levels:
            p, q = Decimal(str(lv["price"])), Decimal(str(lv["qty"]))
            if q == 0:
                side.pop(p, None)
            else:
                side[p] = q

    def truncate(self) -> None:
        for p in sorted(self.asks)[DEPTH:]:
            del self.asks[p]
        for p in sorted(self.bids, reverse=True)[DEPTH:]:
            del self.bids[p]

    def checksum(self) -> int:
        return book_checksum(self.asks, self.bids, self.price_dec, self.qty_dec)


def rfc3339_to_ns(text: str) -> int:
    dt = datetime.fromisoformat(text.replace("Z", "+00:00"))
    return int(dt.timestamp()) * 1_000_000_000 + dt.microsecond * 1000


def ntp_offset_ms(server: str = "time.apple.com", timeout: float = 5.0) -> Optional[float]:
    """One SNTP query (T-5): local clock offset from the server, in ms. None on failure."""
    packet = b"\x1b" + 47 * b"\0"
    try:
        with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as s:
            s.settimeout(timeout)
            t0 = time.time()
            s.sendto(packet, (server, 123))
            data, _ = s.recvfrom(48)
            t3 = time.time()
    except OSError:
        return None
    def ts(off):
        sec, frac = struct.unpack("!II", data[off:off + 8])
        return sec - 2208988800 + frac / 2 ** 32
    t1, t2 = ts(32), ts(40)
    return ((t1 - t0) + (t2 - t3)) / 2 * 1000


class Capture:
    def __init__(self, out: Path, symbols: list, precisions: dict, duration_s: float, connect=WebSocket,
                 clock=time.time_ns, sleep=time.sleep, ntp=ntp_offset_ms):
        self.out = Path(out)
        self.out.mkdir(parents=True, exist_ok=True)
        self.journal = open(self.out / "frames.jsonl", "a")
        self.events = open(self.out / "events.jsonl", "a")
        self.symbols = symbols
        self.books = {s: Book(s, *precisions[s]) for s in symbols}
        self.duration_ns = int(duration_s * 1e9)
        self.connect, self.clock, self.sleep, self.ntp = connect, clock, sleep, ntp
        self.stats = {"frames": 0, "trades": 0, "book_updates": 0, "checksum_ok": 0, "checksum_fail": 0,
                      "resyncs": 0, "disconnects": 0, "latency_ms": [], "ntp_offsets_ms": [], "recovery_s": [], "initial_sync_s": [],
                      "status": [], "invalid_book_ns": {s: 0 for s in symbols}}

    def event(self, kind: str, **kw) -> None:
        self.events.write(json.dumps({"at_ns": self.clock(), "kind": kind, **kw}, default=str) + "\n")

    def subscribe(self, ws, channel: str, extra: Optional[dict] = None) -> None:
        params = {"channel": channel, "symbol": self.symbols, **(extra or {})}
        if channel == "status":
            params = {"channel": "status"}
        ws.send_text(json.dumps({"method": "subscribe", "params": params}))

    def invalidate(self, sym: str, reason: str) -> None:
        b = self.books[sym]
        if b.valid:
            b.valid = False
            b.invalid_since_ns = self.clock()
        self.event("book_invalid", symbol=sym, reason=reason)

    def handle(self, ws, text: str, recv_ns: int) -> None:
        msg = json.loads(text, parse_float=Decimal)
        ch = msg.get("channel")
        if ch == "trade" and msg.get("type") in ("update", "snapshot"):
            for t in msg.get("data", []):
                self.stats["trades"] += 1
                if msg["type"] == "update":
                    self.stats["latency_ms"].append((recv_ns - rfc3339_to_ns(t["timestamp"])) / 1e6)
        elif ch == "book":
            for d in msg.get("data", []):
                sym = d["symbol"]
                b = self.books[sym]
                if msg["type"] == "snapshot":
                    b.bids, b.asks = {}, {}
                    b.apply(d.get("bids", []), b.bids)
                    b.apply(d.get("asks", []), b.asks)
                else:
                    if b.invalid_since_ns is not None and not b.valid:
                        continue  # wait for the fresh snapshot (Q-5)
                    b.apply(d.get("bids", []), b.bids)
                    b.apply(d.get("asks", []), b.asks)
                    b.truncate()
                    self.stats["book_updates"] += 1
                    if "timestamp" in d:
                        self.stats["latency_ms"].append((recv_ns - rfc3339_to_ns(d["timestamp"])) / 1e6)
                if b.checksum() == int(d["checksum"]):
                    self.stats["checksum_ok"] += 1
                    if not b.valid:
                        if b.invalid_since_ns is not None:
                            self.stats["invalid_book_ns"][sym] += recv_ns - b.invalid_since_ns
                            key = "recovery_s" if b.synced_once else "initial_sync_s"
                            self.stats[key].append((recv_ns - b.invalid_since_ns) / 1e9)
                        b.valid, b.invalid_since_ns, b.synced_once = True, None, True
                        self.event("book_valid", symbol=sym)
                else:
                    self.stats["checksum_fail"] += 1
                    self.invalidate(sym, "checksum_mismatch")
                    self.stats["resyncs"] += 1
                    ws.send_text(json.dumps({"method": "unsubscribe", "params": {"channel": "book", "symbol": [sym], "depth": DEPTH}}))
                    ws.send_text(json.dumps({"method": "subscribe", "params": {"channel": "book", "symbol": [sym], "depth": DEPTH, "snapshot": True}}))
        elif ch == "status":
            self.stats["status"].append(msg.get("data"))
            self.event("venue_status", data=msg.get("data"))

    def run(self) -> dict:
        start = self.clock()
        deadline = start + self.duration_ns
        for s in self.symbols:
            self.books[s].invalid_since_ns = start
        attempt = 0
        next_ntp = 0
        while self.clock() < deadline:
            try:
                ws = self.connect(URL)
                attempt = 0
                self.event("connected")
                self.subscribe(ws, "status")
                self.subscribe(ws, "book", {"depth": DEPTH, "snapshot": True})
                self.subscribe(ws, "trade", {"snapshot": False})
                ws.settimeout(15)
                while self.clock() < deadline:
                    if self.clock() >= next_ntp:
                        off = self.ntp()
                        self.stats["ntp_offsets_ms"].append(off)
                        self.event("ntp", offset_ms=off)
                        next_ntp = self.clock() + 60 * 1_000_000_000
                    text = ws.recv_text()
                    recv_ns = self.clock()
                    self.journal.write(json.dumps({"recv_ns": recv_ns, "frame": text}) + "\n")
                    self.stats["frames"] += 1
                    self.handle(ws, text, recv_ns)
                ws.close()
            except (WebSocketClosed, ConnectionError, OSError, socket.timeout) as e:
                self.stats["disconnects"] += 1
                for s in self.symbols:
                    self.invalidate(s, "disconnect")
                self.event("disconnect", error=type(e).__name__, detail=str(e)[:200])
                self.sleep(RECONNECT_DELAYS_S[min(attempt, len(RECONNECT_DELAYS_S) - 1)])
                attempt += 1
        end = self.clock()
        for s, b in self.books.items():
            if not b.valid and b.invalid_since_ns is not None:
                self.stats["invalid_book_ns"][s] += end - b.invalid_since_ns
        self.journal.close()
        self.events.close()
        return self.summary(start, end)

    def summary(self, start: int, end: int) -> dict:
        st = self.stats
        def pct(xs, q):
            xs = sorted(xs)
            return xs[min(len(xs) - 1, int(q * len(xs)))] if xs else None
        lat = st["latency_ms"]
        offs = [o for o in st["ntp_offsets_ms"] if o is not None]
        wall = end - start
        size = sum(p.stat().st_size for p in self.out.glob("*.jsonl"))
        return {
            "duration_s": wall / 1e9, "frames": st["frames"], "trades": st["trades"], "book_updates": st["book_updates"],
            "checksum_ok": st["checksum_ok"], "checksum_fail": st["checksum_fail"], "resyncs": st["resyncs"],
            "disconnects": st["disconnects"],
            "latency_ms": {"p50": pct(lat, .5), "p95": pct(lat, .95), "p99": pct(lat, .99), "max": max(lat) if lat else None},
            "recovery_s": {"p50": pct(st["recovery_s"], .5), "p95": pct(st["recovery_s"], .95),
                           "max": max(st["recovery_s"]) if st["recovery_s"] else None, "count": len(st["recovery_s"])},
            "initial_sync_s": st["initial_sync_s"],
            "valid_book_share": {s: 1 - st["invalid_book_ns"][s] / wall for s in self.symbols},
            "valid_book_share_after_initial_sync": {
                s: 1 - (st["invalid_book_ns"][s] - (st["initial_sync_s"][i] * 1e9 if i < len(st["initial_sync_s"]) else 0))
                / (wall - (st["initial_sync_s"][i] * 1e9 if i < len(st["initial_sync_s"]) else 0))
                for i, s in enumerate(self.symbols)},
            "timestamp_uncertainty_flag_t5": any(o is not None and abs(o) > 100 for o in st["ntp_offsets_ms"]),
            "ntp_offset_ms": {"samples": len(offs), "max_abs": max((abs(o) for o in offs), default=None),
                              "failed": len(st["ntp_offsets_ms"]) - len(offs)},
            "storage_bytes": size, "venue_status": st["status"][:5],
        }
