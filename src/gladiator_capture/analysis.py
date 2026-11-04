"""Derived records, coverage, staleness and replay (event contract §4.5, §5, §6; plan CV-05 to CV-10)."""

from __future__ import annotations

import hashlib
import json
from dataclasses import dataclass
from decimal import Decimal
from typing import Iterable, Optional

from .records import NS, Record

DAY_NS = 86_400 * NS["s"]
EPOCH_GAP_DAYS = 7  # TH-1 (DEC-056)
EPOCH_PRICE_FACTOR = Decimal(10)  # TH-2 (DEC-056)
Q4_THRESHOLD = Decimal("0.95")  # Q-4 (DEC-042)

# TH-5 (DEC-056): stale at 2x the documented update interval.
UPDATE_INTERVAL_NS = {
    "cftc:cot": 7 * DAY_NS,
    "coinmetrics:community": DAY_NS,
    "gdelt": 15 * 60 * NS["s"],
}


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


def bar_gaps(records: list, step_ns: int, start_ns: Optional[int] = None, end_ns: Optional[int] = None) -> list:
    """S-04: each interval with no valid bar is a GapInterval, over [start, end) if given, else
    between the first and last bars. From an archive alone the cause is unknown, so the class is
    status_unknown (Q-2 amended, DEC-040). A quarantined bar's interval is a data_gap. A
    zero-volume bar also gives a status_unknown interval."""
    if not records:
        return []
    sample = records[0]
    present = {r.event_time_ns() for r in valid(records)}
    quarantined = {r.event_time_ns() for r in records if r.quality_state == "quarantined"}
    times = sorted(present | quarantined)
    lo = start_ns if start_ns is not None else times[0]
    hi = end_ns if end_ns is not None else times[-1] + step_ns
    avail = max(r.available_at for r in records)
    gaps = []
    t = lo
    while t < hi:
        if t not in present:
            cls, ev = ("data_gap", "quarantined_bar") if t in quarantined else ("status_unknown", "missing_bar")
            gaps.append(GapInterval(sample.source_id, sample.feed_id, sample.instrument_id, t, t + step_ns, cls, ev, avail))
        t += step_ns
    for r in valid(records):
        if "zero_volume" in r.quality_flags and lo <= r.event_time_ns() < hi:
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


def propose_epochs(records: list, step_ns: int = DAY_NS, gap_days: int = EPOCH_GAP_DAYS,
                   factor: Decimal = EPOCH_PRICE_FACTOR) -> list:
    """S-10, §3.2: a gap over G days AND a close-to-open factor over K proposes a new epoch.
    The gap counts the missing intervals between consecutive valid bars."""
    rs = sorted(valid(records), key=lambda r: r.event_time_ns())
    out = []
    epoch = 1
    for a, b in zip(rs, rs[1:]):
        missing = (b.event_time_ns() - a.event_time_ns()) // step_ns - 1
        gap_days_observed = missing * step_ns / DAY_NS
        if gap_days_observed > gap_days:
            prev, nxt = Decimal(a.fields["close"]), Decimal(b.fields["open"])
            ratio = max(prev, nxt) / min(prev, nxt) if min(prev, nxt) > 0 else Decimal("Infinity")
            if ratio > factor:
                epoch += 1
                out.append(InstrumentEpoch(b.venue, b.native_symbol, epoch, b.event_time_ns(), "gap_and_price",
                                           {"gap_days": gap_days_observed, "factor": str(ratio.quantize(Decimal("0.01"))),
                                            "last_close": a.fields["close"], "first_open": b.fields["open"]}))
    return out


def coverage(records: list, gaps: list, start_ns: int, end_ns: int, step_ns: int) -> Decimal:
    """Q-4: share of intervals in [start, end) that are present (valid) or classified no_trade."""
    total = (end_ns - start_ns) // step_ns
    present = {r.event_time_ns() for r in valid(records) if start_ns <= r.event_time_ns() < end_ns}
    no_trade = {g.interval_start for g in gaps if g.gap_class == "no_trade" and start_ns <= g.interval_start < end_ns}
    return Decimal(len(present | no_trade)) / Decimal(total) if total else Decimal(0)


def qualifies(records: list, gaps: list, start_ns: int, end_ns: int, step_ns: int,
              threshold: Decimal = Q4_THRESHOLD, listed_ns: Optional[int] = None,
              min_training_intervals: int = 0) -> bool:
    """Q-4 pre-fold rule. A pair listed partway through the look-back counts only intervals since
    listing, and must still have at least the minimum training length."""
    if listed_ns is not None and listed_ns > start_ns:
        start_ns = listed_ns  # listing times are interval starts (bar-start stamps)
    if (end_ns - start_ns) // step_ns < min_training_intervals:
        return False
    return coverage(records, gaps, start_ns, end_ns, step_ns) >= threshold


def entry_blocked(records: list, gaps: list, decision_day_ns: int, lookback_days: int, step_ns: int = DAY_NS) -> Optional[str]:
    """CV-06 fail-closed trigger: new entries on a pair are blocked when its look-back coverage is
    below Q-4, or when the last completed interval before the decision, [D - step, D), overlaps a
    data_gap or status_unknown (DEC-040; 10-DATA:18 completed bars only, :40 missing critical price
    coverage stops new entries). no_trade does not block. Only gaps known by D (available_at <= D)
    count, so a replay cannot block on a gap found later (10-DATA:18). A bar missing at D is
    itself a gap known at D, so this does not fail open. Callers build gaps from what is visible
    at D; for a feed that publishes late (DEC-069), its last completed bar may not be visible yet
    and then blocks entries until it is. Returns the reason or None."""
    if not qualifies(records, gaps, decision_day_ns - lookback_days * step_ns, decision_day_ns, step_ns):
        return "coverage_below_q4"
    last_start = decision_day_ns - step_ns
    for cls in ("data_gap", "status_unknown"):
        if any(g.gap_class == cls and g.available_at <= decision_day_ns and g.interval_start < decision_day_ns
               and g.interval_end > last_start for g in gaps):
            return f"{cls}_in_last_completed_interval"
    return None


def is_stale(feed: str, available_at_ns: int, decision_ns: int) -> bool:
    """S-17 / TH-5: an observation is stale when it is older than 2x its update interval."""
    return decision_ns - available_at_ns > 2 * UPDATE_INTERVAL_NS[feed]


def coverage_report(name: str, records: list, gaps: list, raw_files: int) -> dict:
    """Q-3 / CV-06: counts per snapshot."""
    q = [r for r in records if r.quality_state == "quarantined"]
    dup = [r for r in q if (r.reason or "").startswith("duplicate")]
    classes: dict = {}
    for g in gaps:
        classes[g.gap_class] = classes.get(g.gap_class, 0) + 1
    return {"window": name, "raw_files": raw_files, "raw_rows": len(records), "accepted": len(records) - len(q),
            "quarantined": len(q), "duplicates": len(dup), "missing_by_class": classes}


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
    """Hash of the normalized content in replay order, excluding our own processing clock."""
    h = hashlib.sha256()
    for r in replay_order(records):
        h.update(json.dumps(r.to_json(include_clock=False), sort_keys=True, default=str).encode())
        h.update(b"\n")
    return h.hexdigest()


def apply_revision(old: list, new: list) -> list:
    """S-09 / DEC-053: records from a revised object become version old+1 and point at the record
    they supersede. Old versions are kept. The new records' available_at comes from the
    superseding raw object (retrieved_at), set by the parser."""
    by_key = {r.record_key: r for r in old}
    for r in new:
        prev = by_key.get(r.record_key)
        if prev is not None:
            r.version = prev.version + 1
            r.supersedes_record_id = prev.record_id
    return old + new
