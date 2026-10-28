"""Derived records, coverage and replay (event contract §4.5, §6; validation plan CV-05 to CV-10)."""

from __future__ import annotations

import hashlib
import json
from dataclasses import asdict, dataclass, field
from decimal import Decimal
from typing import Iterable, Optional

from .records import NS, Record

EPOCH_GAP_DAYS = 7  # TH-1 (DEC-056)
EPOCH_PRICE_FACTOR = Decimal(10)  # TH-2 (DEC-056)


@dataclass
class GapInterval:
    source_id: str
    feed_id: str
    instrument_id: str
    interval_start: int  # ns
    interval_end: int  # ns, exclusive
    gap_class: str  # no_trade | data_gap | status_unknown
    evidence: str
    available_at: int

    @property
    def availability_state(self) -> str:
        return "NO_EVENT" if self.gap_class == "no_trade" else "SOURCE_UNAVAILABLE"


@dataclass
class InstrumentEpoch:
    venue: str
    native_symbol: str
    epoch: int
    start_ns: int
    trigger: str
    evidence: dict
    review_status: str = "proposed"


def valid(records: Iterable[Record]) -> list:
    return [r for r in records if r.quality_state == "valid"]


def bar_gaps(records: list, step_ns: int) -> list:
    """S-04: each missing interval in a sparse bar series is a GapInterval. From an archive
    alone the cause is unknown, so the class is status_unknown (Q-2 amended, DEC-040).
    Zero-volume bars also give a status_unknown interval."""
    rs = sorted(valid(records), key=lambda r: r.event_time_ns())
    gaps = []
    for a, b in zip(rs, rs[1:]):
        t = a.event_time_ns() + step_ns
        while t < b.event_time_ns():
            gaps.append(GapInterval(a.source_id, a.feed_id, a.instrument_id, t, t + step_ns, "status_unknown",
                                    "missing_bar", max(a.available_at, b.available_at)))
            t += step_ns
    for r in rs:
        if "zero_volume" in r.quality_flags:
            gaps.append(GapInterval(r.source_id, r.feed_id, r.instrument_id, r.event_time_ns(),
                                    r.event_time_ns() + step_ns, "status_unknown", "zero_volume", r.available_at))
    return gaps


def trade_gaps(records: list) -> list:
    """S-05: a break in native trade IDs is a data_gap."""
    rs = sorted(valid(records), key=lambda r: r.fields["native_trade_id"])
    gaps = []
    for a, b in zip(rs, rs[1:]):
        if b.fields["native_trade_id"] != a.fields["native_trade_id"] + 1:
            gaps.append(GapInterval(a.source_id, a.feed_id, a.instrument_id, a.event_time_ns(), b.event_time_ns(),
                                    "data_gap", f"trade_id {a.fields['native_trade_id']}->{b.fields['native_trade_id']}",
                                    b.available_at))
    return gaps


def propose_epochs(records: list, gap_days: int = EPOCH_GAP_DAYS, factor: Decimal = EPOCH_PRICE_FACTOR) -> list:
    """S-10, §3.2: a gap over G days AND a close-to-open factor over K proposes a new epoch."""
    rs = sorted(valid(records), key=lambda r: r.event_time_ns())
    out = []
    epoch = 1
    for a, b in zip(rs, rs[1:]):
        gap = (b.event_time_ns() - a.event_time_ns()) // (86_400 * NS["s"]) - 1
        if gap > gap_days:
            prev, nxt = Decimal(a.fields["close"]), Decimal(b.fields["open"])
            ratio = max(prev, nxt) / min(prev, nxt) if min(prev, nxt) > 0 else Decimal("Infinity")
            if ratio > factor:
                epoch += 1
                out.append(InstrumentEpoch(b.venue, b.native_symbol, epoch, b.event_time_ns(), "gap_and_price",
                                           {"gap_days": int(gap), "factor": str(ratio.quantize(Decimal("0.01"))),
                                            "last_close": a.fields["close"], "first_open": b.fields["open"]}))
    return out


def coverage(records: list, gaps: list, start_ns: int, end_ns: int, step_ns: int) -> Decimal:
    """Q-4: share of intervals in [start, end) that are present (valid) or classified no_trade."""
    total = (end_ns - start_ns) // step_ns
    present = {r.event_time_ns() for r in valid(records) if start_ns <= r.event_time_ns() < end_ns}
    no_trade = {g.interval_start for g in gaps if g.gap_class == "no_trade" and start_ns <= g.interval_start < end_ns}
    return Decimal(len(present | no_trade)) / Decimal(total) if total else Decimal(0)


def qualifies(records: list, gaps: list, start_ns: int, end_ns: int, step_ns: int,
              threshold: Decimal = Decimal("0.95")) -> bool:
    return coverage(records, gaps, start_ns, end_ns, step_ns) >= threshold


def coverage_report(name: str, records: list, gaps: list, raw_count: int) -> dict:
    """Q-3 / CV-06: counts per snapshot."""
    q = [r for r in records if r.quality_state == "quarantined"]
    dup = [r for r in q if (r.reason or "").startswith("duplicate")]
    classes: dict = {}
    for g in gaps:
        classes[g.gap_class] = classes.get(g.gap_class, 0) + 1
    return {"window": name, "raw": raw_count, "accepted": len(records) - len(q), "quarantined": len(q),
            "duplicates": len(dup), "gaps_by_class": classes}


def replay_order(records: list) -> list:
    """DEC-054: available_at, source_id, instrument_id, source_event_time, native seq, version."""
    return sorted(valid(records), key=lambda r: (r.available_at, r.source_id, r.instrument_id,
                                                 r.event_time_ns(), r.native_seq, r.version))


def as_of(records: list, t_ns: int) -> list:
    """§6: records with available_at <= t; per record_key only the highest such version."""
    best: dict = {}
    for r in valid(records):
        if r.available_at <= t_ns:
            k = r.record_key
            if k not in best or r.version > best[k].version:
                best[k] = r
    return replay_order(list(best.values()))


def output_hash(records: list) -> str:
    h = hashlib.sha256()
    for r in replay_order(records):
        h.update(json.dumps(r.to_json(), sort_keys=True, default=str).encode())
        h.update(b"\n")
    return h.hexdigest()


def apply_revision(old: list, new: list) -> list:
    """S-09 / DEC-053: records from a revised object become version old+1; old versions are kept."""
    by_key = {r.record_key: r for r in old}
    for r in new:
        if r.record_key in by_key:
            r.version = by_key[r.record_key].version + 1
    return old + new
