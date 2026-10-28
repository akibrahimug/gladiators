"""Normalize journalled Kraken v2 frames into records, with clock-offset handling (RC-07, RC-08).

- T-5: while the latest logged SNTP offset exceeds 100 ms, each record carries
  `timestamp_uncertainty_ms` = that offset.
- T-6: an offset over 1 s marks the record `clock_abstain_intraday`; over 60 s also `clock_abstain_daily`.
  Dependent decisions must ABSTAIN on such records.
- `available_at` = `received_at` (`live_receive`).
"""

from __future__ import annotations

import json
from decimal import Decimal
from pathlib import Path
from typing import Iterable, Optional

from .live import rfc3339_to_ns
from .records import Record

T5_FLAG_MS = 100  # T-5 (DEC-042)
T6_INTRADAY_MS = 1_000  # T-6 (DEC-042)
T6_DAILY_MS = 60_000


def offsets_from_events(events_path: Path) -> list:
    """(at_ns, offset_ms) for each successful SNTP sample, in time order."""
    out = []
    for line in Path(events_path).read_text().splitlines():
        e = json.loads(line)
        if e.get("kind") == "ntp" and e.get("offset_ms") is not None:
            out.append((e["at_ns"], float(e["offset_ms"])))
    return sorted(out)


def clock_flags(offset_ms: Optional[float]) -> tuple:
    if offset_ms is None:
        return None, ["clock_offset_unknown"]
    flags, unc = [], None
    if abs(offset_ms) > T5_FLAG_MS:
        unc = abs(offset_ms)
    if abs(offset_ms) > T6_INTRADAY_MS:
        flags.append("clock_abstain_intraday")
    if abs(offset_ms) > T6_DAILY_MS:
        flags.append("clock_abstain_daily")
    return unc, flags


def normalize(frames: Iterable[tuple], offsets: list, *, raw_id: str, ingested_at: int) -> list:
    """frames: (line_no, recv_ns, text). Returns trade and book-update records."""
    out = []
    oi, current = 0, None
    for line_no, recv_ns, text in frames:
        while oi < len(offsets) and offsets[oi][0] <= recv_ns:
            current = offsets[oi][1]
            oi += 1
        try:
            msg = json.loads(text, parse_float=Decimal)
        except ValueError:
            continue
        ch, typ = msg.get("channel"), msg.get("type")
        if ch not in ("trade", "book") or typ != "update":
            continue
        unc, flags = clock_flags(current)
        for i, d in enumerate(msg.get("data", [])):
            if "timestamp" not in d:
                continue
            ts = rfc3339_to_ns(d["timestamp"])
            fields = {"message_type": f"{ch}_update", "timestamp_uncertainty_ms": unc, "size_unit": "base"}
            if ch == "trade":
                fields.update(price=str(d["price"]), qty=str(d["qty"]), side=d.get("side"), ord_type=d.get("ord_type"),
                              side_semantics="taker_side")
                seq = int(d["trade_id"])
            else:
                fields.update(bids=[[str(x["price"]), str(x["qty"])] for x in d.get("bids", [])],
                              asks=[[str(x["price"]), str(x["qty"])] for x in d.get("asks", [])],
                              checksum=int(d["checksum"]))
                seq = line_no * 1000 + i
            out.append(Record(
                record_type="NativeMarketEvent", source_id="SR-02", feed_id=f"kraken:ws2:{ch}", venue="kraken",
                native_symbol=d["symbol"], source_event_time=ts // 1000, source_time_unit="us", received_at=recv_ns,
                ingested_at=ingested_at, available_at=recv_ns, available_at_basis="live_receive", raw_id=raw_id,
                raw_locator=f"line:{line_no}#data[{i}]", rights_id="SA-03", native_seq=seq,
                quality_flags=list(flags), fields=fields))
    return out


def read_segment(path: Path) -> Iterable[tuple]:
    with open(path) as fh:
        for n, line in enumerate(fh):
            r = json.loads(line)
            yield n, r["recv_ns"], r["frame"]
