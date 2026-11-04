"""Normalized records, parsers and Q-1 validation (event contract §3–§5)."""

from __future__ import annotations

import csv
import hashlib
import io
import json
import re
from dataclasses import dataclass, field
from datetime import datetime, timezone
from decimal import Decimal, InvalidOperation
from email.utils import parsedate_to_datetime
from typing import Optional

from . import SCHEMA_VERSION

NS = {"s": 1_000_000_000, "ms": 1_000_000, "us": 1_000, "ns": 1}
DAY_NS = 86_400 * NS["s"]
LATE_LIMIT_NS = 48 * 3600 * NS["s"]  # TH-6 (DEC-056)

BINANCE_US_FROM = datetime(2025, 1, 1, tzinfo=timezone.utc)

# Fields that come from our own clocks; excluded from the content hash (event contract §6).
CLOCK_FIELDS = ("ingested_at",)


@dataclass
class Record:
    record_type: str
    source_id: str
    feed_id: str
    venue: str
    native_symbol: str
    source_event_time: int
    source_time_unit: str
    received_at: int
    ingested_at: int
    available_at: int
    available_at_basis: str
    raw_id: str
    raw_locator: str
    rights_id: str
    native_seq: int
    version: int = 1
    supersedes_record_id: Optional[str] = None
    epoch: int = 1
    quality_state: str = "valid"
    quality_flags: list = field(default_factory=list)
    reason: Optional[str] = None
    fields: dict = field(default_factory=dict)
    schema_version: str = SCHEMA_VERSION
    market: str = "CRYPTO_SPOT"
    producer: str = "gladiator_capture/" + SCHEMA_VERSION

    @property
    def instrument_id(self) -> str:
        return f"{self.venue}:{self.native_symbol}:{self.epoch}"

    @property
    def record_key(self) -> tuple:
        """Natural key without epoch or version (event contract §3). For bars, native_seq is the
        bar start, so the key is stable across revisions and sliding REST windows."""
        return (self.source_id, self.feed_id, self.native_symbol, self.source_event_time, self.native_seq)

    @property
    def record_id(self) -> str:
        blob = json.dumps([list(self.record_key), self.version], separators=(",", ":"))
        return hashlib.sha256(blob.encode()).hexdigest()

    def event_time_ns(self) -> int:
        return self.source_event_time * NS[self.source_time_unit]

    def to_json(self, include_clock: bool = True) -> dict:
        d = dict(self.__dict__)
        if not include_clock:
            for k in CLOCK_FIELDS:
                d.pop(k, None)
        d["instrument_id"] = self.instrument_id
        d["record_id"] = self.record_id
        return d


@dataclass
class ParseResult:
    records: list
    file_quarantined: bool = False
    reason: Optional[str] = None
    dropped_incomplete: int = 0


def http_date_to_ns(value: Optional[str]) -> Optional[int]:
    if not value:
        return None
    return int(parsedate_to_datetime(value).timestamp()) * NS["s"]


def _decimal(text: str) -> Decimal:
    d = Decimal(text)
    if not d.is_finite():
        raise InvalidOperation("non-finite")
    return d


def is_zero(text: str) -> bool:
    try:
        return Decimal(text) == 0
    except InvalidOperation:
        return False


def check_ohlc(o: str, h: str, l: str, c: str, v: str) -> Optional[str]:
    """Q-1 row check; returns a reason or None. Values stay strings on the record."""
    try:
        do, dh, dl, dc, dv = (_decimal(x) for x in (o, h, l, c, v))
    except (InvalidOperation, ValueError):
        return "nonfinite_or_invalid_number"
    if not (dl <= min(do, dc) and dh >= max(do, dc) and dl > 0 and dv >= 0):
        return "invalid_ohlc"
    return None


def check_trade(price: str, qty: str, quote_qty: str) -> Optional[str]:
    try:
        p, q, qq = (_decimal(x) for x in (price, qty, quote_qty))
    except (InvalidOperation, ValueError):
        return "nonfinite_or_invalid_number"
    return None if p > 0 and q > 0 and qq >= 0 else "invalid_trade_values"


def check_naive_time(text: str) -> Optional[str]:
    """F-06b: an ISO time without a zone is quarantined (Q-1)."""
    try:
        dt = datetime.fromisoformat(text)
    except ValueError:
        return "invalid_time"
    return "timezone_naive" if dt.tzinfo is None else None


def _int_time(text: str) -> Optional[int]:
    return int(text) if re.fullmatch(r"\d+", text.strip()) else None


def binance_era_unit(period_start: datetime) -> str:
    """Declared era table (event contract §3.1): never digit count alone."""
    return "us" if period_start >= BINANCE_US_FROM else "ms"


def _digits_ok(value: int, unit: str) -> bool:
    return len(str(value)) == {"s": 10, "ms": 13, "us": 16}[unit]


def _period_from_name(name: str) -> tuple:
    """(start, end, kind) from a Binance file name (YYYY-MM or YYYY-MM-DD)."""
    m = re.search(r"-(\d{4})-(\d{2})(?:-(\d{2}))?\.(?:csv|zip)$", name)
    if not m:
        raise ValueError(f"no period in {name}")
    y, mo, d = int(m.group(1)), int(m.group(2)), m.group(3)
    if d:
        start = datetime(y, mo, int(d), tzinfo=timezone.utc)
        return start, datetime.fromtimestamp(start.timestamp() + 86400, timezone.utc), "daily"
    start = datetime(y, mo, 1, tzinfo=timezone.utc)
    return start, datetime(y + (mo == 12), mo % 12 + 1, 1, tzinfo=timezone.utc), "monthly"


# DEC-069: a Binance file's Last-Modified is only the earliest time it could have been public, so
# its records take Last-Modified plus this margin and are flagged as estimated.
BINANCE_PUBLICATION_MARGIN_NS = 6 * 3600 * NS["s"]


def availability(raw, archive_published_ns: Optional[int], margin_ns: int = 0) -> tuple:
    """§3.1 and DEC-053. A superseding object always takes our retrieval time; otherwise the
    archive's publication time plus margin_ns (DEC-069) if known; otherwise our retrieval time."""
    if getattr(raw, "supersedes_raw_id", None):
        return raw.retrieved_at_ns, "retrieved"
    if archive_published_ns:
        return archive_published_ns + margin_ns, "archive_published"
    return raw.retrieved_at_ns, "retrieved"


def _binance_availability(raw) -> tuple:
    """DEC-069: (available_at, basis, flags) for a Binance file."""
    available_at, basis = availability(raw, http_date_to_ns(raw.server_last_modified), BINANCE_PUBLICATION_MARGIN_NS)
    return available_at, basis, (["available_at_estimated"] if basis == "archive_published" else [])


def _locator(raw, i: int) -> str:
    member = getattr(raw, "member_path", None)
    return f"{member}#row:{i}" if member else f"row:{i}"


def _rewrite_flags(raw, rewrite_listed: bool) -> list:
    """TH-4: evidence only: a changelog listing, or new bytes on re-retrieval."""
    return ["last_modified_after_period"] if rewrite_listed or getattr(raw, "supersedes_raw_id", None) else []


def _mark_duplicates(records: list, key) -> None:
    """S-02b/S-03: duplicate keys inside one file quarantine every copy (Q-1)."""
    groups: dict = {}
    for r in records:
        groups.setdefault(key(r), []).append(r)
    for group in groups.values():
        if len(group) > 1:
            conflict = len({json.dumps([g.source_event_time, g.fields], sort_keys=True, default=str) for g in group}) > 1
            for g in group:
                g.quality_state = "quarantined"
                g.reason = "duplicate_conflicting" if conflict else "duplicate_timestamp"


def _late_flag(rec: Record, period_end_ns: Optional[int], kind: str) -> None:
    """TH-6: daily files, REST and live only; monthly files and Kraken archives exempt."""
    if kind in ("daily", "rest", "live") and period_end_ns is not None and rec.available_at - period_end_ns > LATE_LIMIT_NS:
        rec.quality_flags.append("late")


def parse_binance_klines(data: bytes, *, name: str, symbol: str, interval: str, raw, ingested_at: int,
                         rights_id: str = "SA-01", rewrite_listed: bool = False) -> ParseResult:
    start, end, kind = _period_from_name(name)
    unit = binance_era_unit(start)
    available_at, basis, est = _binance_availability(raw)
    out = []
    for i, row in enumerate(csv.reader(io.StringIO(data.decode()))):
        if len(row) != 12:
            return ParseResult([], True, "schema_column_count")
        t = _int_time(row[0])
        if t is None:
            return ParseResult([], True, "schema_time_type")
        if not _digits_ok(t, unit):
            return ParseResult([], True, "unit_contradicts_era")
        rec = Record(
            record_type="BarEvent", source_id="SR-04", feed_id=f"binance:spot:klines:{interval}:{kind}",
            venue="binance", native_symbol=symbol, source_event_time=t, source_time_unit=unit,
            received_at=raw.retrieved_at_ns, ingested_at=ingested_at, available_at=available_at,
            available_at_basis=basis, raw_id=raw.raw_id, raw_locator=_locator(raw, i), rights_id=rights_id,
            native_seq=t, quality_flags=est + _rewrite_flags(raw, rewrite_listed),
            fields={"interval": interval, "open": row[1], "high": row[2], "low": row[3], "close": row[4],
                    "volume": row[5], "native_close_time": row[6], "quote_volume": row[7], "trade_count": row[8],
                    "taker_buy_base_volume": row[9], "taker_buy_quote_volume": row[10], "quote_currency": "USDT"},
        )
        bad = check_ohlc(row[1], row[2], row[3], row[4], row[5])
        if bad:
            rec.quality_state, rec.reason = "quarantined", bad
        elif is_zero(row[5]):
            rec.quality_flags.append("zero_volume")
        out.append(rec)
    _mark_duplicates(out, lambda r: r.source_event_time)
    if interval == "1d":  # TH-6 is defined on daily bars; other intervals are not in the baseline
        for rec in out:
            _late_flag(rec, rec.event_time_ns() + DAY_NS, kind)
    return ParseResult(out)


def parse_binance_trades(data: bytes, *, name: str, symbol: str, raw, ingested_at: int,
                         rights_id: str = "SA-01") -> ParseResult:
    start, end, kind = _period_from_name(name)
    unit = binance_era_unit(start)
    available_at, basis, est = _binance_availability(raw)
    period_end_ns = int(end.timestamp()) * NS["s"]
    out = []
    for i, row in enumerate(csv.reader(io.StringIO(data.decode()))):
        if len(row) != 7:
            return ParseResult([], True, "schema_column_count")
        t = _int_time(row[4])
        if t is None or not _digits_ok(t, unit):
            return ParseResult([], True, "unit_contradicts_era" if t is not None else "schema_time_type")
        tid = _int_time(row[0])
        rec = Record(
            record_type="TradeEvent", source_id="SR-04", feed_id="binance:spot:trades:daily", venue="binance",
            native_symbol=symbol, source_event_time=t, source_time_unit=unit, received_at=raw.retrieved_at_ns,
            ingested_at=ingested_at, available_at=available_at, available_at_basis=basis, raw_id=raw.raw_id,
            raw_locator=_locator(raw, i), rights_id=rights_id, native_seq=tid if tid is not None else -1,
            quality_flags=list(est), fields={"native_trade_id": tid, "price": row[1], "qty": row[2], "quote_qty": row[3],
                    "is_buyer_maker": row[5], "side_semantics": "buyer_is_maker", "is_best_match": row[6],
                    "quote_currency": "USDT"},
        )
        bad = "invalid_trade_id" if tid is None else check_trade(row[1], row[2], row[3])
        if bad:
            rec.quality_state, rec.reason = "quarantined", bad
        _late_flag(rec, period_end_ns, kind)
        out.append(rec)
    _mark_duplicates([r for r in out if r.fields["native_trade_id"] is not None], lambda r: r.fields["native_trade_id"])
    return ParseResult(out)


def parse_kraken_csv(data: bytes, *, pair: str, interval_min: int, raw, generated_ns: Optional[int],
                     ingested_at: int, rights_id: str = "SA-02") -> ParseResult:
    available_at, basis = availability(raw, generated_ns)
    out = []
    for i, row in enumerate(csv.reader(io.StringIO(data.decode()))):
        if len(row) != 7:
            return ParseResult([], True, "schema_column_count")
        t = _int_time(row[0])
        if t is None or not _digits_ok(t, "s"):
            return ParseResult([], True, "unit_contradicts_era" if t is not None else "schema_time_type")
        rec = Record(
            record_type="BarEvent", source_id="SR-05", feed_id=f"kraken:ohlcvt:{interval_min}:archive",
            venue="kraken", native_symbol=pair, source_event_time=t, source_time_unit="s",
            received_at=raw.retrieved_at_ns, ingested_at=ingested_at, available_at=available_at,
            available_at_basis=basis, raw_id=raw.raw_id, raw_locator=_locator(raw, i), rights_id=rights_id,
            native_seq=t, quality_flags=_rewrite_flags(raw, False),
            fields={"interval": interval_min, "open": row[1], "high": row[2], "low": row[3], "close": row[4],
                    "volume": row[5], "trade_count": row[6], "quote_currency": "USD"},
        )
        bad = check_ohlc(row[1], row[2], row[3], row[4], row[5])
        if bad:
            rec.quality_state, rec.reason = "quarantined", bad
        elif is_zero(row[5]):
            rec.quality_flags.append("zero_volume")
        out.append(rec)
    _mark_duplicates(out, lambda r: r.source_event_time)
    return ParseResult(out)


def parse_kraken_rest_ohlc(data: bytes, *, request_pair: str, interval_min: int, raw, ingested_at: int,
                           rights_id: str = "SA-02") -> ParseResult:
    doc = json.loads(data)
    if doc.get("error"):
        return ParseResult([], True, "api_error:" + ";".join(doc["error"]))
    keys = [k for k in doc["result"] if k != "last"]
    if len(keys) != 1:
        return ParseResult([], True, "schema_result_keys")
    response_key = keys[0]
    step = interval_min * 60
    out = []
    dropped = 0
    for i, row in enumerate(doc["result"][response_key]):
        if len(row) != 8:
            return ParseResult([], True, "schema_field_count")
        t = int(row[0])
        if (t + step) * NS["s"] > raw.retrieved_at_ns:  # S-12: incomplete current bar
            dropped += 1
            continue
        rec = Record(
            record_type="BarEvent", source_id="SR-05", feed_id=f"kraken:rest:ohlc:{interval_min}", venue="kraken",
            native_symbol=request_pair, source_event_time=t, source_time_unit="s", received_at=raw.retrieved_at_ns,
            ingested_at=ingested_at, available_at=raw.retrieved_at_ns, available_at_basis="live_receive",
            raw_id=raw.raw_id, raw_locator=f"result.{response_key}[{i}]", rights_id=rights_id, native_seq=t,
            fields={"interval": interval_min, "open": row[1], "high": row[2], "low": row[3], "close": row[4],
                    "vwap": row[5], "volume": row[6], "trade_count": str(row[7]), "native_response_key": response_key,
                    "quote_currency": "USD"},
        )
        bad = check_ohlc(row[1], row[2], row[3], row[4], row[6])
        if bad:
            rec.quality_state, rec.reason = "quarantined", bad
        elif is_zero(row[6]):
            rec.quality_flags.append("zero_volume")
        _late_flag(rec, (t + step) * NS["s"], "rest")
        out.append(rec)
    _mark_duplicates(out, lambda r: r.source_event_time)
    return ParseResult(out, dropped_incomplete=dropped)
