"""Normalized records, parsers and Q-1 validation (event contract §3–§5)."""

from __future__ import annotations

import csv
import hashlib
import io
import json
import math
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
        return (self.source_id, self.feed_id, self.native_symbol, self.source_event_time, self.native_seq)

    @property
    def record_id(self) -> str:
        blob = json.dumps([list(self.record_key), self.version], separators=(",", ":"))
        return hashlib.sha256(blob.encode()).hexdigest()

    def event_time_ns(self) -> int:
        return self.source_event_time * NS[self.source_time_unit]

    def to_json(self) -> dict:
        d = {k: v for k, v in self.__dict__.items()}
        d["instrument_id"] = self.instrument_id
        d["record_id"] = self.record_id
        return d


def http_date_to_ns(value: Optional[str]) -> Optional[int]:
    if not value:
        return None
    return int(parsedate_to_datetime(value).timestamp()) * NS["s"]


def _decimal(text: str) -> Decimal:
    d = Decimal(text)
    if not d.is_finite():
        raise InvalidOperation("non-finite")
    return d


def check_ohlc(o: str, h: str, l: str, c: str, v: str) -> Optional[str]:
    """Q-1 row check; returns a reason or None. Values stay strings on the record."""
    try:
        do, dh, dl, dc, dv = (_decimal(x) for x in (o, h, l, c, v))
    except (InvalidOperation, ValueError):
        return "nonfinite_or_invalid_number"
    if not (dl <= min(do, dc) and dh >= max(do, dc) and dl > 0 and dv >= 0):
        return "invalid_ohlc"
    return None


def _int_time(text: str) -> Optional[int]:
    return int(text) if re.fullmatch(r"\d+", text.strip()) else None


def binance_era_unit(period_start: datetime) -> str:
    """Declared era table (event contract §3.1): never digit count alone."""
    return "us" if period_start >= BINANCE_US_FROM else "ms"


def _digits_ok(value: int, unit: str) -> bool:
    expected = {"s": 10, "ms": 13, "us": 16}[unit]
    return len(str(value)) == expected


def _period_from_name(name: str) -> tuple[datetime, Optional[datetime], str]:
    """Return (start, end, kind) from a Binance file name (YYYY-MM or YYYY-MM-DD)."""
    m = re.search(r"-(\d{4})-(\d{2})(?:-(\d{2}))?\.(?:csv|zip)$", name)
    if not m:
        raise ValueError(f"no period in {name}")
    y, mo, d = int(m.group(1)), int(m.group(2)), m.group(3)
    if d:
        start = datetime(y, mo, int(d), tzinfo=timezone.utc)
        end = datetime.fromtimestamp(start.timestamp() + 86400, timezone.utc)
        return start, end, "daily"
    start = datetime(y, mo, 1, tzinfo=timezone.utc)
    end = datetime(y + (mo == 12), mo % 12 + 1, 1, tzinfo=timezone.utc)
    return start, end, "monthly"


@dataclass
class ParseResult:
    records: list
    file_quarantined: bool = False
    reason: Optional[str] = None


def _mark_duplicates(records: list) -> None:
    """S-02b/S-03: duplicate timestamps inside one file quarantine every copy (Q-1)."""
    seen: dict = {}
    for r in records:
        seen.setdefault((r.native_symbol, r.source_event_time, r.fields.get("interval")), []).append(r)
    for group in seen.values():
        if len(group) > 1:
            conflict = len({json.dumps(g.fields, sort_keys=True, default=str) for g in group}) > 1
            for g in group:
                g.quality_state = "quarantined"
                g.reason = "duplicate_conflicting" if conflict else "duplicate_timestamp"


def _late_flag(rec: Record, period_end_ns: Optional[int], kind: str) -> None:
    """TH-6: daily files, REST and live only; monthly files and Kraken archives exempt."""
    if kind in ("daily", "rest", "live") and period_end_ns is not None:
        if rec.available_at - period_end_ns > LATE_LIMIT_NS:
            rec.quality_flags.append("late")


def parse_binance_klines(data: bytes, *, name: str, symbol: str, interval: str, raw, ingested_at: int,
                         rights_id: str = "SA-01") -> ParseResult:
    start, end, kind = _period_from_name(name)
    unit = binance_era_unit(start)
    lm = http_date_to_ns(raw.server_last_modified)
    available_at, basis = (lm, "archive_published") if lm else (raw.retrieved_at_ns, "retrieved")
    rows = list(csv.reader(io.StringIO(data.decode())))
    out = []
    for i, row in enumerate(rows):
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
            available_at_basis=basis, raw_id=raw.raw_id, raw_locator=f"row:{i}", rights_id=rights_id, native_seq=i,
            fields={"interval": interval, "open": row[1], "high": row[2], "low": row[3], "close": row[4],
                    "volume": row[5], "native_close_time": row[6], "quote_volume": row[7], "trade_count": row[8],
                    "taker_buy_base_volume": row[9], "taker_buy_quote_volume": row[10], "quote_currency": "USDT"},
        )
        bad = check_ohlc(row[1], row[2], row[3], row[4], row[5])
        if bad:
            rec.quality_state, rec.reason = "quarantined", bad
        if row[5].strip() in ("0", "0.0", "0.00000000"):
            rec.quality_flags.append("zero_volume")
        out.append(rec)
    _mark_duplicates(out)
    for rec in out:
        bar_end = rec.event_time_ns() + DAY_NS if interval == "1d" else None
        _late_flag(rec, bar_end, kind)
    return ParseResult(out)


def parse_binance_trades(data: bytes, *, name: str, symbol: str, raw, ingested_at: int,
                         rights_id: str = "SA-01") -> ParseResult:
    start, end, kind = _period_from_name(name)
    unit = binance_era_unit(start)
    lm = http_date_to_ns(raw.server_last_modified)
    available_at, basis = (lm, "archive_published") if lm else (raw.retrieved_at_ns, "retrieved")
    out = []
    for i, row in enumerate(csv.reader(io.StringIO(data.decode()))):
        if len(row) != 7:
            return ParseResult([], True, "schema_column_count")
        t = _int_time(row[4])
        if t is None or not _digits_ok(t, unit):
            return ParseResult([], True, "unit_contradicts_era" if t is not None else "schema_time_type")
        out.append(Record(
            record_type="TradeEvent", source_id="SR-04", feed_id="binance:spot:trades:daily", venue="binance",
            native_symbol=symbol, source_event_time=t, source_time_unit=unit, received_at=raw.retrieved_at_ns,
            ingested_at=ingested_at, available_at=available_at, available_at_basis=basis, raw_id=raw.raw_id,
            raw_locator=f"row:{i}", rights_id=rights_id, native_seq=int(row[0]),
            fields={"native_trade_id": int(row[0]), "price": row[1], "qty": row[2], "quote_qty": row[3],
                    "is_buyer_maker": row[5], "side_semantics": "buyer_is_maker", "is_best_match": row[6],
                    "quote_currency": "USDT"},
        ))
    return ParseResult(out)


def parse_kraken_csv(data: bytes, *, pair: str, interval_min: int, raw, generated_ns: Optional[int],
                     ingested_at: int, rights_id: str = "SA-02") -> ParseResult:
    available_at, basis = (generated_ns, "archive_published") if generated_ns else (raw.retrieved_at_ns, "retrieved")
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
            available_at_basis=basis, raw_id=raw.raw_id, raw_locator=f"row:{i}", rights_id=rights_id, native_seq=i,
            fields={"interval": interval_min, "open": row[1], "high": row[2], "low": row[3], "close": row[4],
                    "volume": row[5], "trade_count": row[6], "quote_currency": "USD"},
        )
        bad = check_ohlc(row[1], row[2], row[3], row[4], row[5])
        if bad:
            rec.quality_state, rec.reason = "quarantined", bad
        out.append(rec)
    _mark_duplicates(out)
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
            raw_id=raw.raw_id, raw_locator=f"result.{response_key}[{i}]", rights_id=rights_id, native_seq=i,
            fields={"interval": interval_min, "open": row[1], "high": row[2], "low": row[3], "close": row[4],
                    "vwap": row[5], "volume": row[6], "trade_count": row[7], "native_response_key": response_key,
                    "quote_currency": "USD"},
        )
        bad = check_ohlc(row[1], row[2], row[3], row[4], row[6])
        if bad:
            rec.quality_state, rec.reason = "quarantined", bad
        _late_flag(rec, (t + step) * NS["s"], "rest")
        out.append(rec)
    _mark_duplicates(out)
    res = ParseResult(out)
    res.reason = f"dropped_incomplete={dropped}"
    return res


def check_naive_time(text: str) -> Optional[str]:
    """F-06b: an ISO time without a zone is quarantined (Q-1)."""
    try:
        dt = datetime.fromisoformat(text)
    except ValueError:
        return "invalid_time"
    return "timezone_naive" if dt.tzinfo is None else None
