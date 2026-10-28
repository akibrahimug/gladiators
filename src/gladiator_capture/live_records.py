"""Normalize journalled Kraken v2 frames into records, with clock-offset handling (RC-07, RC-08).

- Values are kept exactly as received: JSON numbers are read as their original text (event
  contract §4.1, C15), so the book checksum can be recomputed from stored strings.
- Book snapshots and updates, and trade updates, become `NativeMarketEvent` records
  (event contract §4.4): `message_type` is `snapshot` or `update`, and `native_sequence` is
  null for the book. Order is the receive order. `native_seq` (the key) is recv_ns * 100 + index
  within the frame, which is stable however the frames are segmented.
- T-5: while the latest SNTP offset exceeds 100 ms, a record carries `timestamp_uncertainty_ms`.
  A latest sample older than 60 min is `clock_offset_stale`.
- T-6: an offset over 1 s marks `clock_abstain_intraday`; over 60 s also `clock_abstain_daily`.
  A latest sample older than 1 min also marks `clock_abstain_intraday`, because T-6 requires
  logging at least every minute for intraday-dependent decisions.
- A record before the first sample is `clock_offset_unknown` and `clock_abstain_intraday`.
  This is Proposed: conservative, but not yet confirmed by the user.
- `available_at` = `received_at` (`live_receive`).
"""

from __future__ import annotations

import json
from pathlib import Path
from typing import Iterable, Optional

from .live import rfc3339_to_ns
from .records import Record

T5_FLAG_MS = 100  # T-5 (DEC-042)
T5_STALE_NS = 3600 * 10**9  # T-5: offset logged at least hourly
T6_INTRADAY_MS = 1_000  # T-6 (DEC-042)
T6_DAILY_MS = 60_000
T6_STALE_NS = 60 * 10**9  # T-6: <= 1 min logging when intraday-dependent decisions exist
QUOTE = {"BTC/USD": "USD", "ETH/USD": "USD"}
API_VERSION = "v2"


def offsets_from_events(events_path: Path) -> list:
    """(at_ns, offset_ms) for each successful SNTP sample, in time order."""
    out = []
    for line in Path(events_path).read_text().splitlines():
        e = json.loads(line)
        if e.get("kind") == "ntp" and e.get("offset_ms") is not None:
            out.append((e["at_ns"], float(e["offset_ms"])))
    return sorted(out)


def clock_flags(offset_ms: Optional[float], age_ns: Optional[int] = 0) -> tuple:
    if offset_ms is None:
        return None, ["clock_offset_unknown", "clock_abstain_intraday"]
    flags, unc = [], None
    a = abs(offset_ms)
    if a > T5_FLAG_MS:
        unc = a
    if a > T6_INTRADAY_MS or (age_ns or 0) > T6_STALE_NS:
        flags.append("clock_abstain_intraday")
    if a > T6_DAILY_MS:
        flags.append("clock_abstain_daily")
    if (age_ns or 0) > T5_STALE_NS:
        flags.append("clock_offset_stale")
    return unc, flags


def normalize(frames: Iterable[tuple], offsets: list, *, raw_id: str, ingested_at: int) -> list:
    """frames: (line_no, recv_ns, text). Returns book snapshot/update and trade update records."""
    out = []
    oi, current, current_at = 0, None, None
    for line_no, recv_ns, text in frames:
        while oi < len(offsets) and offsets[oi][0] <= recv_ns:
            current_at, current = offsets[oi]
            oi += 1
        try:
            msg = json.loads(text, parse_float=lambda s: s, parse_int=lambda s: s)
        except ValueError:
            continue
        ch, typ = msg.get("channel"), msg.get("type")
        if not ((ch == "book" and typ in ("snapshot", "update")) or (ch == "trade" and typ == "update")):
            continue
        unc, flags = clock_flags(current, None if current_at is None else recv_ns - current_at)
        for i, d in enumerate(msg.get("data", [])):
            sym = d.get("symbol")
            fields = {"message_type": typ, "timestamp_uncertainty_ms": unc, "size_unit": "base",
                      "quote_currency": QUOTE.get(sym), "source_version": API_VERSION}
            if ch == "trade":
                fields.update(price=d["price"], qty=d["qty"], side=d.get("side"), ord_type=d.get("ord_type"),
                              side_semantics="taker_side", native_sequence=d["trade_id"])
                ts = rfc3339_to_ns(d["timestamp"])
            else:
                fields.update(bids=[[x["price"], x["qty"]] for x in d.get("bids", [])],
                              asks=[[x["price"], x["qty"]] for x in d.get("asks", [])],
                              checksum=d["checksum"], native_sequence=None)
                ts = rfc3339_to_ns(d["timestamp"]) if "timestamp" in d else recv_ns  # snapshots carry no timestamp
            out.append(Record(
                record_type="NativeMarketEvent", source_id="SR-02", feed_id=f"kraken:ws2:{ch}", venue="kraken",
                native_symbol=sym, source_event_time=ts // 1000, source_time_unit="us", received_at=recv_ns,
                ingested_at=ingested_at, available_at=recv_ns, available_at_basis="live_receive", raw_id=raw_id,
                raw_locator=f"line:{line_no}#data[{i}]", rights_id="SA-03", native_seq=recv_ns * 100 + i,
                quality_flags=list(flags) + (["source_time_is_receive_time"] if ch == "book" and "timestamp" not in d else []),
                fields=fields))
    return out


def read_segment(path: Path) -> Iterable[tuple]:
    with open(path) as fh:
        for n, line in enumerate(fh):
            r = json.loads(line)
            yield n, r["recv_ns"], r["frame"]
