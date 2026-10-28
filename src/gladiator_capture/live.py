"""Kraken WebSocket v2 live capture: `book` depth 10 and `trade` (W-J, DEC-057, DEC-062).

- Every received frame is written, before parsing, to an hourly journal segment with its receive
  time. Each closed segment is ingested into the RawStore as a raw object with SR-02 and SA-03
  (event contract §2).
- The book is rebuilt from snapshot plus updates and checked against the venue CRC32 checksum.
  On a mismatch the book is invalidated and resubscribed (S-15, Q-5), at most RESYNC_MAX_PER_MIN
  times a minute per pair.
- On a disconnect the client reconnects with jittered backoff. The backoff resets only after a
  valid book (RC-09, R-2).
- Venue `status` other than "online" is tracked as maintenance and excluded from R-4 (RC-11).
"""

from __future__ import annotations

import json
import random
import socket
import struct
import time
import zlib
from dataclasses import dataclass, field
from datetime import datetime
from decimal import Decimal
from pathlib import Path
from typing import Optional

from .rawstore import RawStore
from .ws import WebSocket, WebSocketClosed

URL = "wss://ws.kraken.com/v2"
DEPTH = 10
RECONNECT_DELAYS_S = (1, 2, 5, 10, 30, 60)
RESYNC_MAX_PER_MIN = 6
SEGMENT_NS = 3600 * 1_000_000_000


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
    invalid_reason: str = "initial"
    synced_once: bool = False
    resync_times: list = field(default_factory=list)

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


_RFC3339 = __import__("re").compile(r"^(\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2})(?:\.(\d+))?(Z|[+-]\d{2}:\d{2})$")


def rfc3339_to_ns(text: str) -> int:
    """RFC 3339 to integer ns, for any fraction length (Python 3.9's fromisoformat accepts only 3 or 6)."""
    m = _RFC3339.match(text)
    if not m:
        raise ValueError(f"not RFC 3339: {text!r}")
    base = datetime.fromisoformat(m.group(1) + ("+00:00" if m.group(3) == "Z" else m.group(3)))
    frac = (m.group(2) or "").ljust(9, "0")[:9]
    return int(base.timestamp()) * 1_000_000_000 + int(frac)


def ntp_offset_ms(server: str = "time.apple.com", timeout: float = 2.0) -> Optional[float]:
    """One SNTP query (T-5): local clock offset from the server, in ms. None on any failure or a
    malformed reply."""
    packet = b"\x1b" + 47 * b"\0"
    try:
        with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as s:
            s.settimeout(timeout)
            t0 = time.time()
            s.sendto(packet, (server, 123))
            data, _ = s.recvfrom(512)
            t3 = time.time()
    except OSError:
        return None
    if len(data) < 48 or (data[0] & 0x07) != 4 or data[1] == 0:  # mode 4 (server), stratum > 0
        return None

    def ts(off):
        sec, frac = struct.unpack("!II", data[off:off + 8])
        return sec - 2208988800 + frac / 2 ** 32

    t1, t2 = ts(32), ts(40)
    return ((t1 - t0) + (t2 - t3)) / 2 * 1000


class Capture:
    def __init__(self, out: Path, symbols: list, precisions: dict, duration_s: float, connect=WebSocket,
                 clock=time.time_ns, sleep=time.sleep, ntp=ntp_offset_ms, monotonic=time.monotonic_ns,
                 store: Optional[RawStore] = None):
        self.out = Path(out)
        self.out.mkdir(parents=True, exist_ok=True)
        self.store = store or RawStore(self.out / "store")
        self.events = open(self.out / "events.jsonl", "a", buffering=1)
        self.symbols = symbols
        self.books = {s: Book(s, *precisions[s]) for s in symbols}
        self.duration_ns = int(duration_s * 1e9)
        self.connect, self.clock, self.sleep, self.ntp, self.mono = connect, clock, sleep, ntp, monotonic
        self.segment = None
        self.segment_start = None
        self.segments = []
        self.offset_ms: Optional[float] = None
        self.maint_since: Optional[int] = None
        self.st = {"frames": 0, "trades": 0, "book_updates": 0, "checksum_ok": 0, "checksum_fail": 0, "resyncs": 0,
                   "resync_capped": 0, "disconnects": 0, "parse_errors": 0, "subscribe_errors": 0,
                   "latency_raw_ms": {}, "ntp_offsets_ms": [], "recovery_disconnect_s": [],
                   "recovery_checksum_s": [], "initial_sync_s": {}, "maintenance_ns": 0,
                   "invalid_book_ns": {s: 0 for s in symbols}, "invalid_in_maintenance_ns": {s: 0 for s in symbols},
                   "status": []}

    # -- journal ---------------------------------------------------------------
    def event(self, kind: str, **kw) -> None:
        self.events.write(json.dumps({"at_ns": self.clock(), "kind": kind, **kw}, default=str) + "\n")

    def _close_segment(self) -> None:
        if self.segment is None:
            return
        seg, self.segment = self.segment, None
        seg.close()
        path = Path(seg.name)
        try:
            obj = self.store.ingest_file(path, source_id="SR-02", source_approval_id="SA-03",
                                         request=f"wss://ws.kraken.com/v2#segment:{path.name}",
                                         retrieved_at_ns=self.clock())
            self.segments.append({"file": path.name, "raw_id": obj.raw_id, "bytes": obj.byte_length})
        except OSError as e:  # the segment stays on disk; record and continue
            self.segments.append({"file": path.name, "raw_id": None, "bytes": path.stat().st_size,
                                  "ingest_error": f"{type(e).__name__}: {e}"[:200]})
            self.event("segment_ingest_error", file=path.name, error=str(e)[:200])

    def journal(self, recv_ns: int, text: str) -> None:
        if self.segment is None or recv_ns - self.segment_start >= SEGMENT_NS:
            self._close_segment()
            self.segment_start = recv_ns
            self.segment = open(self.out / f"frames-{recv_ns}.jsonl", "a", buffering=1)
        self.segment.write(json.dumps({"recv_ns": recv_ns, "frame": text}) + "\n")

    # -- protocol --------------------------------------------------------------
    def subscribe(self, ws, channel: str, extra: Optional[dict] = None, symbols: Optional[list] = None) -> None:
        params = {"channel": channel, "symbol": symbols or self.symbols, **(extra or {})}
        ws.send_text(json.dumps({"method": "subscribe", "params": params}))

    def invalidate(self, sym: str, reason: str, now: int) -> None:
        b = self.books[sym]
        if b.valid or b.invalid_since_ns is None:
            b.valid = False
            b.invalid_since_ns = now
            b.invalid_reason = reason
        self.event("book_invalid", symbol=sym, reason=reason)

    def _latency(self, key: str, recv_ns: int, ts: str) -> None:
        self.st["latency_raw_ms"].setdefault(key, []).append((recv_ns - rfc3339_to_ns(ts)) / 1e6)

    def handle(self, ws, text: str, recv_ns: int) -> None:
        msg = json.loads(text, parse_float=Decimal)
        if msg.get("method") == "subscribe" and msg.get("success") is False:
            self.st["subscribe_errors"] += 1
            self.event("subscribe_error", detail=msg.get("error"))
            return
        ch = msg.get("channel")
        if ch == "trade" and msg.get("type") in ("update", "snapshot"):
            for t in msg.get("data", []):
                self.st["trades"] += 1
                if msg["type"] == "update":
                    self._latency(f"trade:{t.get('symbol')}", recv_ns, t["timestamp"])
        elif ch == "book":
            for d in msg.get("data", []):
                sym = d.get("symbol")
                if sym not in self.books:
                    self.event("unknown_symbol", symbol=sym)
                    continue
                self._book(ws, msg["type"], d, recv_ns)
        elif ch == "status":
            data = msg.get("data") or [{}]
            system = data[0].get("system")
            self.st["status"].append(system)
            self.event("venue_status", data=data)
            if system == "maintenance" and self.maint_since is None:  # cancel_only/post_only are not maintenance
                self.maint_since = recv_ns
            elif system != "maintenance" and self.maint_since is not None:
                self._end_maintenance(recv_ns)

    def _end_maintenance(self, now: int) -> None:
        """Close a maintenance interval; invalid-book time inside it is excluded from R-4 (RC-11)."""
        self.st["maintenance_ns"] += now - self.maint_since
        for s, b in self.books.items():
            if not b.valid and b.invalid_since_ns is not None:
                self.st["invalid_in_maintenance_ns"][s] += now - max(b.invalid_since_ns, self.maint_since)
        self.st.setdefault("maintenance_intervals", []).append((self.maint_since, now))
        self.maint_since = None

    def _book(self, ws, kind: str, d: dict, recv_ns: int) -> None:
        sym = d["symbol"]
        b = self.books[sym]
        if kind == "snapshot":
            b.bids, b.asks = {}, {}
            b.apply(d.get("bids", []), b.bids)
            b.apply(d.get("asks", []), b.asks)
        else:
            if not b.valid:
                return  # wait for the fresh snapshot (Q-5)
            b.apply(d.get("bids", []), b.bids)
            b.apply(d.get("asks", []), b.asks)
            b.truncate()
            self.st["book_updates"] += 1
            if "timestamp" in d:
                self._latency(f"book:{sym}", recv_ns, d["timestamp"])
        if b.checksum() == int(d["checksum"]):
            self.st["checksum_ok"] += 1
            if not b.valid:
                if b.invalid_since_ns is not None:
                    dur = recv_ns - b.invalid_since_ns
                    self.st["invalid_book_ns"][sym] += dur
                    if self.maint_since is not None:
                        self.st["invalid_in_maintenance_ns"][sym] += recv_ns - max(b.invalid_since_ns, self.maint_since)
                    if not b.synced_once:
                        self.st["initial_sync_s"][sym] = dur / 1e9
                    elif b.invalid_reason == "disconnect":
                        self.st["recovery_disconnect_s"].append(dur / 1e9)
                    else:
                        self.st["recovery_checksum_s"].append(dur / 1e9)
                b.valid, b.invalid_since_ns, b.synced_once = True, None, True
                self.event("book_valid", symbol=sym)
        else:
            self.st["checksum_fail"] += 1
            self.invalidate(sym, "checksum_mismatch", recv_ns)
            b.resync_times = [t for t in b.resync_times if recv_ns - t < 60 * 1_000_000_000]
            if len(b.resync_times) >= RESYNC_MAX_PER_MIN:
                self.st["resync_capped"] += 1
                return
            b.resync_times.append(recv_ns)
            self.st["resyncs"] += 1
            ws.send_text(json.dumps({"method": "unsubscribe", "params": {"channel": "book", "symbol": [sym], "depth": DEPTH}}))
            self.subscribe(ws, "book", {"depth": DEPTH, "snapshot": True}, symbols=[sym])

    # -- loop ------------------------------------------------------------------
    def run(self) -> dict:
        start, mono0 = self.clock(), self.mono()
        deadline = mono0 + self.duration_ns
        for s in self.symbols:
            self.books[s].invalid_since_ns = start
        attempt = 0
        next_ntp = mono0
        connected_at = None
        while self.mono() < deadline:
            ws = None
            try:
                ws = self.connect(URL)
                connected_at = self.mono()
                self.event("connected")
                self.subscribe(ws, "book", {"depth": DEPTH, "snapshot": True})
                self.subscribe(ws, "trade", {"snapshot": False})
                ws.settimeout(15)
                while self.mono() < deadline:
                    if self.mono() >= next_ntp:
                        off = self.ntp()
                        self.offset_ms = off
                        self.st["ntp_offsets_ms"].append(off)
                        self.event("ntp", offset_ms=off)
                        next_ntp = self.mono() + 60 * 1_000_000_000
                    text = ws.recv_text()
                    recv_ns = self.clock()
                    self.journal(recv_ns, text)
                    self.st["frames"] += 1
                    try:
                        self.handle(ws, text, recv_ns)
                    except (WebSocketClosed, OSError):
                        raise  # a broken socket during a resync is a disconnect, not a parse error
                    except Exception as e:  # the frame is journalled; record and continue
                        self.st["parse_errors"] += 1
                        self.event("parse_error", error=type(e).__name__, detail=str(e)[:200])
                    if attempt and all(b.valid for b in self.books.values()):
                        attempt = 0  # reset backoff only after a valid book
            except (WebSocketClosed, ConnectionError, OSError, socket.timeout, UnicodeDecodeError) as e:
                self.st["disconnects"] += 1
                now = self.clock()
                for s in self.symbols:
                    self.invalidate(s, "disconnect", now)
                self.event("disconnect", error=type(e).__name__, detail=str(e)[:200])
                delay = RECONNECT_DELAYS_S[min(attempt, len(RECONNECT_DELAYS_S) - 1)]
                self.sleep(delay * (1 + random.random() * 0.25))
                attempt += 1
            finally:
                if ws is not None:
                    try:
                        ws.close()
                    except OSError:
                        pass
        end = self.clock()
        for s, b in self.books.items():
            if not b.valid and b.invalid_since_ns is not None:
                self.st["invalid_book_ns"][s] += end - b.invalid_since_ns
                if self.maint_since is not None:
                    self.st["invalid_in_maintenance_ns"][s] += end - max(b.invalid_since_ns, self.maint_since)
                b.invalid_since_ns = None  # counted
        if self.maint_since is not None:
            self._end_maintenance(end)
        self._close_segment()
        self.events.close()
        return self.summary(start, end)

    def summary(self, start: int, end: int) -> dict:
        st = self.st

        def pct(xs, q):
            xs = sorted(xs)
            return xs[min(len(xs) - 1, int(q * len(xs)))] if xs else None

        def dist(xs):
            return {"n": len(xs), "p50": pct(xs, .5), "p95": pct(xs, .95), "p99": pct(xs, .99),
                    "max": max(xs) if xs else None}

        offs = [o for o in st["ntp_offsets_ms"] if o is not None]
        mean_off = sum(offs) / len(offs) if offs else None
        wall = end - start
        maint = st["maintenance_ns"]
        lat = {k: {"raw": dist(v), "offset_corrected": dist([x + mean_off for x in v]) if mean_off is not None else None}
               for k, v in st["latency_raw_ms"].items()}
        r4 = {}
        for s in self.symbols:
            init = st["initial_sync_s"].get(s, 0) * 1e9
            r4[s] = {"valid_share": 1 - st["invalid_book_ns"][s] / wall,
                     "valid_share_excl_initial_sync_and_maintenance":
                         1 - max(0, st["invalid_book_ns"][s] - init - st["invalid_in_maintenance_ns"][s])
                         / max(1, wall - init - maint)}
        size = sum(x["bytes"] for x in self.segments)
        return {
            "duration_s": wall / 1e9, "frames": st["frames"], "trades": st["trades"], "book_updates": st["book_updates"],
            "checksum_ok": st["checksum_ok"], "checksum_fail": st["checksum_fail"], "resyncs": st["resyncs"],
            "resync_capped": st["resync_capped"], "disconnects": st["disconnects"], "parse_errors": st["parse_errors"],
            "subscribe_errors": st["subscribe_errors"],
            "latency_ms_T3": lat, "latency_note": "raw = local receive - venue timestamp; offset_corrected adds the "
                                                  "mean SNTP offset. ingest - receive is not measured: frames are "
                                                  "journalled before parsing, and normalization runs offline",
            "initial_sync_s": st["initial_sync_s"], "recovery_disconnect_s_R3": dist(st["recovery_disconnect_s"]),
            "recovery_checksum_s": dist(st["recovery_checksum_s"]), "maintenance_s": maint / 1e9,
            "invalid_in_maintenance_s": {s: v / 1e9 for s, v in st["invalid_in_maintenance_ns"].items()}, "R4": r4,
            "ntp_offset_ms_T5": {"samples": len(offs), "failed": len(st["ntp_offsets_ms"]) - len(offs),
                                 "mean": mean_off, "max_abs": max((abs(o) for o in offs), default=None),
                                 "over_100ms": any(abs(o) > 100 for o in offs)},
            "storage_R5": {"uncompressed_bytes": size,
                           "uncompressed_bytes_per_pair_per_day": size / len(self.symbols) / (wall / 86400e9),
                           "note": "uncompressed journal; R-5 caps compressed size"},
            "segments": self.segments, "venue_status_seen": sorted(set(x for x in st["status"] if x)),
        }
