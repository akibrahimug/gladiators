"""Book validity, venue status and maintenance as P02 records, from raw frames alone (DEC-075).

`derive_live_validity(frames, symbols)` reads a run's journalled Kraken v2 frames in receive order
across all of its segments and returns three kinds of record (event contract §4.4, §4.5):

- `VenueStatus`: one `records.Record` per item of each `status` channel frame, with `system`,
  `api_version`, `connection_id`, `version` and the received `upcoming_maintenance` list unchanged.
  JSON numbers are kept as their original text, as in `live_records`. The frame carries no venue
  time, so `source_event_time` is the receive time, flagged `source_time_is_receive_time`.
- Book-invalid `analysis.GapInterval`s per pair, `gap_class` `data_gap`. A book is invalid over:
  (a) `start`: from the run's first frame to the pair's first book snapshot;
  (b) `silence>15s` (DEC-071): from the last frame on any channel to the next, when they are more
      than 15 s apart (strictly, as in `live_analysis`);
  (c) `reconnect`: a `status` frame whose `connection_id` differs from the previous one starts a
      new connection; the book is invalid from the last frame before that status frame until the
      pair's first book snapshot after it;
  (d) `resync`: a book snapshot for a pair with no new connection since its previous snapshot
      (the capture resubscribed after a checksum mismatch); invalid from the pair's last book
      frame before it until the snapshot;
  (e) `open_at_end`: an interval still open at the run's last frame ends there.
  Overlapping or adjacent intervals are merged; `evidence` lists the rules, joined by "+", in the
  order above. `available_at` is the receive time of the frame that ends the interval.
- `MaintenanceWindow`s for the R-4 exclusion (DEC-074), not book invalidity: each period while
  `status` reports `maintenance`, and each announced `spot_ws` window from
  `live_analysis.announced_maintenance`, including withdrawn ones (`withdrawn`, nothing excluded).

The derivation is pure: it reads nothing but the frames given, so the same frames give the same
output. `run_frames(run)` builds the frame sequence from a run directory, reading only.
"""

from __future__ import annotations

import json
from dataclasses import dataclass, field
from pathlib import Path
from typing import Iterable, Optional

from .analysis import GapInterval
from .live_analysis import SILENCE_NS, announced_maintenance
from .records import Record

SOURCE_ID = "SR-02"
RIGHTS_ID = "SA-03"
VENUE = "kraken"
STATUS_FEED = "kraken:ws2:status"
BOOK_FEED = "kraken:ws2:book"
RULES = ("start", "silence>15s", "reconnect", "resync", "open_at_end")  # evidence order


@dataclass
class MaintenanceWindow:
    """A venue maintenance period excluded from R-4 (DEC-074). `source` is `status` (the `status`
    channel reported `maintenance`) or `announced` (an `upcoming_maintenance` item for `spot_ws`).
    `excluded_start`/`excluded_end` are None when the item was withdrawn (unlisted before start)."""
    source: str
    event_id: object
    title: Optional[str]
    announced_start: Optional[int]
    announced_end: Optional[int]
    excluded_start: Optional[int]
    excluded_end: Optional[int]
    first_listed: Optional[int]
    unlisted_at: Optional[int]
    withdrawn: bool
    available_at: int
    open_at_end: bool = False
    source_id: str = SOURCE_ID
    feed_id: str = STATUS_FEED
    venue: str = VENUE


@dataclass
class LiveValidity:
    venue_status: list = field(default_factory=list)
    gaps: dict = field(default_factory=dict)  # symbol -> [GapInterval]
    maintenance: list = field(default_factory=list)
    frames: int = 0
    first_recv: Optional[int] = None
    last_recv: Optional[int] = None
    announced_items_skipped: int = 0


def instrument_id(symbol: str, epoch: int = 1) -> str:
    return f"{VENUE}:{symbol}:{epoch}"


def merge_intervals(raw: list) -> list:
    """(start, end, rules, available_at) tuples -> merged, overlapping or adjacent ones joined."""
    out = []
    for a, b, rules, avail in sorted((x for x in raw if x[1] > x[0]), key=lambda x: (x[0], x[1])):
        if out and a <= out[-1][1]:
            last = out[-1]
            last[1] = max(last[1], b)
            last[2] = last[2] | rules
            last[3] = max(last[3], avail)
        else:
            out.append([a, b, set(rules), avail])
    return out


def _evidence(rules: set) -> str:
    return "+".join(r for r in RULES if r in rules)


def _status_record(recv_ns: int, i: int, d: dict, raw_id: str, raw_locator: str, ingested_at: int) -> Record:
    return Record(
        record_type="VenueStatus", source_id=SOURCE_ID, feed_id=STATUS_FEED, venue=VENUE, native_symbol=None,
        source_event_time=recv_ns // 1000, source_time_unit="us", received_at=recv_ns, ingested_at=ingested_at,
        available_at=recv_ns, available_at_basis="live_receive", raw_id=raw_id,
        raw_locator=f"{raw_locator}#data[{i}]", rights_id=RIGHTS_ID, native_seq=recv_ns * 100 + i,
        quality_flags=["source_time_is_receive_time"],
        fields={"system": d.get("system"), "api_version": d.get("api_version"),
                "connection_id": d.get("connection_id"), "version": d.get("version"),
                "upcoming_maintenance": d.get("upcoming_maintenance")})


def derive_live_validity(frames: Iterable[tuple], symbols: list, *, ingested_at: int = 0) -> LiveValidity:
    """frames: (recv_ns, text, raw_id, raw_locator) in receive order across all of a run's segments."""
    res = LiveValidity()
    raw = {s: [] for s in symbols}
    open_iv = {s: None for s in symbols}  # pair -> [start, rules] while invalid
    last_book = {s: None for s in symbols}  # recv of the pair's last book frame
    snap_conn = {s: None for s in symbols}  # connection count at the pair's last snapshot
    conn_id, conns = None, 0
    prev = None
    statuses = []  # (recv, data[0]) for announced_maintenance, numbers parsed as JSON numbers
    maint_since = None

    def invalidate(s, start, rule):
        if open_iv[s] is None:
            open_iv[s] = [start, {rule}]
        else:
            open_iv[s][0] = min(open_iv[s][0], start)
            open_iv[s][1].add(rule)

    for recv, text, raw_id, raw_locator in frames:
        res.frames += 1
        if res.first_recv is None:
            res.first_recv = recv
            for s in symbols:
                invalidate(s, recv, "start")  # (a)
        if prev is not None and recv - prev > SILENCE_NS:  # (b)
            for s in symbols:
                raw[s].append((prev, recv, {"silence>15s"}, recv))
        last_frame = prev
        prev = recv
        res.last_recv = recv
        if '"status"' not in text and '"book"' not in text:
            continue
        try:
            msg = json.loads(text)
        except ValueError:
            continue
        if not isinstance(msg, dict):
            continue
        ch, typ, data = msg.get("channel"), msg.get("type"), msg.get("data")
        if ch == "status":
            try:
                exact = json.loads(text, parse_float=lambda x: x, parse_int=lambda x: x)["data"]
            except (ValueError, KeyError, TypeError):
                exact = None
            items = exact if isinstance(exact, list) else []
            for i, d in enumerate(items):
                if isinstance(d, dict):
                    res.venue_status.append(_status_record(recv, i, d, raw_id, raw_locator, ingested_at))
            first = (data or [{}])[0] if isinstance(data, list) else {}
            first = first if isinstance(first, dict) else {}
            statuses.append((recv, first))
            cid = first.get("connection_id")
            if cid is not None:
                if conn_id is not None and cid != conn_id:  # (c)
                    conns += 1
                    for s in symbols:
                        invalidate(s, last_frame if last_frame is not None else recv, "reconnect")
                conn_id = cid
            system = first.get("system")
            if system == "maintenance" and maint_since is None:
                maint_since = recv
            elif system != "maintenance" and maint_since is not None:
                res.maintenance.append(_status_window(maint_since, recv, False))
                maint_since = None
        elif ch == "book" and typ in ("snapshot", "update") and isinstance(data, list):
            for d in data:
                s = d.get("symbol") if isinstance(d, dict) else None
                if s not in raw:
                    continue
                if typ == "snapshot":
                    if snap_conn[s] == conns and last_book[s] is not None:  # (d)
                        raw[s].append((last_book[s], recv, {"resync"}, recv))
                    if open_iv[s] is not None:
                        raw[s].append((open_iv[s][0], recv, open_iv[s][1], recv))
                        open_iv[s] = None
                    snap_conn[s] = conns
                last_book[s] = recv

    end = res.last_recv
    for s in symbols:
        if open_iv[s] is not None:  # (e)
            raw[s].append((open_iv[s][0], end, open_iv[s][1] | {"open_at_end"}, end))
    if maint_since is not None:
        res.maintenance.append(_status_window(maint_since, end, True))
    for s in symbols:
        res.gaps[s] = [GapInterval(SOURCE_ID, BOOK_FEED, instrument_id(s), a, b, "data_gap", _evidence(rules), avail)
                       for a, b, rules, avail in merge_intervals(raw[s])]
    announced, res.announced_items_skipped = announced_maintenance(statuses)
    for w in announced:
        withdrawn = w["excluded"] is None
        res.maintenance.append(MaintenanceWindow(
            source="announced", event_id=w["event_id"], title=w["title"], announced_start=w["start"],
            announced_end=w["end"], excluded_start=None if withdrawn else w["excluded"][0],
            excluded_end=None if withdrawn else w["excluded"][1], first_listed=w["first_listed"],
            unlisted_at=w["unlisted_at"], withdrawn=withdrawn, available_at=w["first_listed"]))
    res.maintenance.sort(key=lambda m: (m.announced_start if m.announced_start is not None else m.excluded_start,
                                        m.source, str(m.event_id)))
    return res


def _status_window(a: int, b: int, open_at_end: bool) -> MaintenanceWindow:
    return MaintenanceWindow(source="status", event_id=None, title=None, announced_start=None, announced_end=None,
                             excluded_start=a, excluded_end=b, first_listed=None, unlisted_at=None, withdrawn=False,
                             available_at=b, open_at_end=open_at_end)


def segments(run: Path) -> list:
    """A run's frame segments in time order (by the receive time in the name, not lexically)."""
    return sorted(Path(run).glob("frames-*.jsonl"), key=lambda p: int(p.stem.split("-")[1]))


def segment_raw_ids(run: Path) -> dict:
    """Segment file name -> raw_id from the run's store index, read only. Missing store: empty."""
    out = {}
    index = Path(run) / "store" / "index.jsonl"
    if not index.exists():
        return out
    with open(index, "rb") as fh:
        for line in fh:
            try:
                d = json.loads(line)
            except ValueError:
                continue
            req = d.get("request") or ""
            if "#segment:" in req and d.get("member_path") is None:
                out.setdefault(req.split("#segment:")[1], d.get("raw_id"))
    return out


def run_frames(run: Path, malformed: Optional[list] = None) -> Iterable[tuple]:
    """(recv_ns, text, raw_id, raw_locator) for every readable frame line of a run, in segment
    order. Files are only opened for reading. A segment not in the store index (still being
    written) gets raw_id `unindexed:<file>`. Unreadable lines are skipped and, if `malformed` is a
    list, appended to it as `<file>:<line>`. `raw_locator` is `line:<n>` (0-based, as in
    `live_records.read_segment`)."""
    ids = segment_raw_ids(run)
    for seg in segments(run):
        raw_id = ids.get(seg.name) or f"unindexed:{seg.name}"
        with open(seg, "rb") as fh:
            for n, line in enumerate(fh):
                try:
                    r = json.loads(line)
                    recv, text = int(r["recv_ns"]), r["frame"]
                except (ValueError, KeyError, TypeError):
                    if malformed is not None:
                        malformed.append(f"{seg.name}:{n}")
                    continue
                yield recv, text, raw_id, f"line:{n}"
