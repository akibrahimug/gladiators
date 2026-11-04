"""Offline, read-only analysis of captured runs for G02 (TASK-P02-003, CV-12).

Reads a live-capture directory (`events.jsonl`, `frames-*.jsonl`, `live-summary.jsonl`, `store/`)
or a REST-pull directory (`daily-summary.jsonl`, `store/`) and reports:

- R-1/R-4: book-invalid time per pair, as the union of
  (a) the capture's own invalid intervals (`book_invalid`/`disconnect` to `book_valid`), with a
      `parse_error` also opening an interval for each pair (the PR #30 defect, review fixes), and
  (b) DEC-071 frame silences: when the next frame arrives more than 15 s after the previous one,
      the gap runs from the last frame received to the next one.
  Venue maintenance is excluded (RC-11). The capture's built-in `invalid_book_ns` is reported
  beside it and is not used for R-4.
- R-3: time from each `disconnect` to the next `book_valid` per pair.
- Q-5: every `book_valid` must follow a book snapshot frame for that pair received since the pair
  was last invalidated.
- T-3: local receive minus venue timestamp, per channel, pair and UTC day, raw and corrected by the
  latest SNTP sample. Quantiles use 1 ms bins.
- T-5/T-6: SNTP sample counts, offsets and time under each flag.
- R-5: gzip-compressed bytes per pair per day.
- Integrity: every frame line parses; each closed segment's SHA-256 equals its store index entry;
  the store's index and journal lines all parse; every indexed object exists with its length and hash.

Nothing in the run directory is written, renamed or locked: files are opened for reading only and
the store is opened with `read_only=True`. A run without `live-summary.jsonl` is still being
written (or did not finish), so its newest segment is skipped and the report is marked provisional.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import sys
import zlib
from collections import Counter
from datetime import datetime, timezone
from pathlib import Path
from typing import Optional

from .rawstore import RawStore

SILENCE_NS = 15 * 10**9  # DEC-071: the capture's receive timeout; Kraken heartbeats every 1 s
T5_FLAG_MS = 100
T6_INTRADAY_MS = 1_000
T6_DAILY_MS = 60_000
T6_STALE_NS = 60 * 10**9
T5_STALE_NS = 3600 * 10**9
DAY_NS = 86400 * 10**9
STALE_FRAME_MS = 15_000  # a book/trade item older than this on receipt is reported (buffered after a wake)


# -- interval arithmetic ---------------------------------------------------------
def merge(intervals: list) -> list:
    out = []
    for a, b in sorted(i for i in intervals if i[1] > i[0]):
        if out and a <= out[-1][1]:
            out[-1][1] = max(out[-1][1], b)
        else:
            out.append([a, b])
    return [tuple(x) for x in out]


def clip(intervals: list, lo: int, hi: int) -> list:
    return [(max(a, lo), min(b, hi)) for a, b in intervals if min(b, hi) > max(a, lo)]


def total(intervals: list) -> int:
    return sum(b - a for a, b in intervals)


def subtract(intervals: list, remove: list) -> list:
    """intervals minus remove; both merged."""
    out = []
    remove = merge(remove)
    for a, b in merge(intervals):
        cur = a
        for c, d in remove:
            if d <= cur or c >= b:
                continue
            if c > cur:
                out.append((cur, c))
            cur = max(cur, d)
        if cur < b:
            out.append((cur, b))
    return out


def complement(intervals: list, lo: int, hi: int) -> list:
    return subtract([(lo, hi)], intervals)


def quantiles(hist: Counter) -> dict:
    n = sum(hist.values())
    if not n:
        return {"n": 0, "p50": None, "p95": None, "p99": None, "max": None}
    keys = sorted(hist)
    res = {"n": n}
    for name, q in (("p50", .5), ("p95", .95), ("p99", .99)):
        target, acc = q * n, 0
        for k in keys:
            acc += hist[k]
            if acc >= target:
                res[name] = k
                break
    res["max"] = keys[-1]
    return res


def dist(xs: list) -> dict:
    xs = sorted(xs)
    if not xs:
        return {"n": 0, "p50": None, "p95": None, "max": None}
    pick = lambda q: xs[min(len(xs) - 1, int(q * len(xs)))]
    return {"n": len(xs), "p50": pick(.5), "p95": pick(.95), "max": xs[-1]}


def iso(ns: Optional[int]) -> Optional[str]:
    if ns is None:
        return None
    return datetime.fromtimestamp(ns / 1e9, timezone.utc).strftime("%Y-%m-%dT%H:%M:%S.%fZ")


def rfc3339_ns(text: str) -> int:
    from .live import rfc3339_to_ns
    return rfc3339_to_ns(text)


# -- store integrity -------------------------------------------------------------
def scan_jsonl(path: Path) -> dict:
    """Line-by-line check that never raises: interior malformed lines and an incomplete tail."""
    res = {"file": path.name, "exists": path.exists(), "lines": 0, "malformed_interior": [], "incomplete_tail": False}
    if not path.exists():
        return res
    data = path.read_bytes()
    lines = data.split(b"\n")
    last = len(lines) - 1  # data ending in "\n" leaves an empty final element
    for i, line in enumerate(lines):
        if not line.strip():
            continue
        res["lines"] += 1
        try:
            json.loads(line)
        except ValueError:
            if i == last:
                res["incomplete_tail"] = True
            else:
                res["malformed_interior"].append(i + 1)
    if data and not data.endswith(b"\n"):
        res["incomplete_tail"] = True
    return res


def sha256_and_gzip(path: Path, compress: bool) -> tuple:
    h = hashlib.sha256()
    z = zlib.compressobj(6, zlib.DEFLATED, 31) if compress else None
    gz = 0
    with open(path, "rb") as fh:
        for chunk in iter(lambda: fh.read(1 << 22), b""):
            h.update(chunk)
            if z:
                gz += len(z.compress(chunk))
    if z:
        gz += len(z.flush())
    return h.hexdigest(), (gz if compress else None)


def check_store(root: Path) -> dict:
    res = {"root": str(root), "index": scan_jsonl(root / "index.jsonl"), "journal": scan_jsonl(root / "journal.jsonl")}
    try:
        st = RawStore(root, read_only=True)
        res["opens_read_only"] = True
        res["truncated_lines"] = st.truncated_lines
    except Exception as e:  # reported, not raised
        res["opens_read_only"] = False
        res["open_error"] = f"{type(e).__name__}: {e}"[:300]
        return res
    missing, bad_len, bad_hash = [], [], []
    for raw_id, obj in sorted(st.objects.items()):
        p = st.object_path(raw_id)
        if not p.exists():
            missing.append(raw_id)
            continue
        if p.stat().st_size != obj.byte_length:
            bad_len.append(raw_id)
        elif sha256_and_gzip(p, False)[0] != raw_id:
            bad_hash.append(raw_id)
    res["objects"] = {"indexed": len(st.objects), "missing": missing, "length_mismatch": bad_len,
                      "hash_mismatch": bad_hash}
    res["journal_outcomes"] = dict(sorted(Counter(e.get("outcome") for e in st._read_lines(root / "journal.jsonl")).items()))
    res["ok"] = (not res["index"]["malformed_interior"] and not res["journal"]["malformed_interior"]
                 and not missing and not bad_len and not bad_hash)
    return res


# -- live run --------------------------------------------------------------------
def _segments(run: Path) -> list:
    return sorted(run.glob("frames-*.jsonl"), key=lambda p: int(p.stem.split("-")[1]))


def _read_events(run: Path) -> tuple:
    events, malformed = [], 0
    with open(run / "events.jsonl", "rb") as fh:
        for line in fh:
            try:
                events.append(json.loads(line))
            except ValueError:
                malformed += 1
    return events, malformed


def _summary(run: Path) -> Optional[dict]:
    p = run / "live-summary.jsonl"
    if not p.exists() or not p.stat().st_size:
        return None
    lines = [l for l in p.read_text().splitlines() if l.strip()]
    return json.loads(lines[-1]) if lines else None


def analyse_live(run: Path, symbols: list, compress: bool = True) -> dict:
    run = Path(run)
    summary = _summary(run)
    provisional = summary is None
    events, events_malformed = _read_events(run)
    segs = _segments(run)
    skipped_open_segment = None
    if provisional and segs:
        skipped_open_segment = segs[-1].name
        segs = segs[:-1]

    # SNTP samples (successful and failed), in time order
    ntp = sorted((e["at_ns"], e.get("offset_ms")) for e in events if e.get("kind") == "ntp")
    good_ntp = [(t, float(o)) for t, o in ntp if o is not None]

    # frames: silences, snapshots, latency, malformed lines, per-segment hash and gzip size
    silences, snapshots = [], {s: [] for s in symbols}
    lat = {}
    stale_items = Counter()
    malformed_frames, frames, first_recv, last_recv = [], 0, None, None
    seg_rows = []
    oi, cur_off = 0, None
    prev = None
    for seg in segs:
        digest, gz = sha256_and_gzip(seg, compress)
        n_seg = 0
        with open(seg, "rb") as fh:
            for ln, line in enumerate(fh, 1):
                try:
                    rec = json.loads(line)
                    recv, text = int(rec["recv_ns"]), rec["frame"]
                except (ValueError, KeyError, TypeError):
                    malformed_frames.append(f"{seg.name}:{ln}")
                    continue
                frames += 1
                n_seg += 1
                if first_recv is None:
                    first_recv = recv
                last_recv = recv
                if prev is not None and recv - prev > SILENCE_NS:
                    silences.append((prev, recv))
                prev = recv
                if '"book"' not in text and '"trade"' not in text:
                    continue
                try:
                    msg = json.loads(text)
                except ValueError:
                    malformed_frames.append(f"{seg.name}:{ln}:frame")
                    continue
                ch, typ = msg.get("channel"), msg.get("type")
                if ch not in ("book", "trade") or typ not in ("snapshot", "update"):
                    continue
                while oi < len(good_ntp) and good_ntp[oi][0] <= recv:
                    cur_off = good_ntp[oi][1]
                    oi += 1
                day = iso(recv)[:10]
                for d in msg.get("data") or []:
                    sym = d.get("symbol")
                    if ch == "book" and typ == "snapshot":
                        if sym in snapshots:
                            snapshots[sym].append(recv)
                        continue
                    ts = d.get("timestamp")
                    if typ != "update" or not ts:
                        continue
                    raw = (recv - rfc3339_ns(ts)) / 1e6
                    key = (ch, sym, day)
                    h = lat.setdefault(key, (Counter(), Counter()))
                    h[0][int(raw // 1)] += 1
                    if cur_off is not None:
                        h[1][int((raw + cur_off) // 1)] += 1
                    if raw > STALE_FRAME_MS:
                        stale_items[f"{ch}:{sym}"] += 1
        seg_rows.append({"file": seg.name, "frames": n_seg, "bytes": seg.stat().st_size, "gzip_bytes": gz,
                         "sha256": digest})

    # run window
    if summary is not None:
        start = int(datetime.fromisoformat(summary["ran_at_utc"]).timestamp() * 1e9)
        end = start + int(summary["duration_s"] * 1e9)
    else:
        cands = [x for x in (first_recv, events[0]["at_ns"] if events else None) if x is not None]
        start = min(cands) if cands else 0
        end = last_recv or start
    wall = end - start

    # capture-reported invalid intervals per pair, plus parse_error as invalidation (review fixes)
    inv = {s: [] for s in symbols}
    since = {s: start for s in symbols}  # books start invalid
    last_invalidation = {s: start for s in symbols}
    q5_violations = []
    disconnects, parse_errors, maint, maint_since, counts = [], [], [], None, Counter()
    recov = {s: [] for s in symbols}
    pending_disc = {s: None for s in symbols}
    snap_i = {s: 0 for s in symbols}
    for e in sorted(events, key=lambda e: e["at_ns"]):
        k, t = e.get("kind"), e["at_ns"]
        counts[k] += 1
        if k in ("book_invalid", "parse_error", "disconnect"):
            targets = [e["symbol"]] if k == "book_invalid" else symbols
            for s in targets:
                if s not in since:
                    continue
                if since[s] is None:
                    since[s] = t
                last_invalidation[s] = t
            if k == "disconnect":
                disconnects.append(t)
                for s in symbols:
                    pending_disc[s] = t if pending_disc[s] is None else pending_disc[s]
            if k == "parse_error":
                parse_errors.append(t)
        elif k == "book_valid":
            s = e.get("symbol")
            if s not in since:
                continue
            if since[s] is not None:
                inv[s].append((since[s], t))
                since[s] = None
            # Q-5: a snapshot for s received in [last_invalidation, t]
            snaps = snapshots[s]
            while snap_i[s] < len(snaps) and snaps[snap_i[s]] < last_invalidation[s]:
                snap_i[s] += 1
            ok = snap_i[s] < len(snaps) and snaps[snap_i[s]] <= t
            in_scope = first_recv is not None and last_recv is not None and first_recv <= t <= last_recv
            if in_scope and not ok:
                q5_violations.append({"symbol": s, "book_valid_at": iso(t), "invalidated_at": iso(last_invalidation[s])})
            if pending_disc[s] is not None:
                recov[s].append((t - pending_disc[s]) / 1e9)
                pending_disc[s] = None
        elif k == "venue_status":
            system = ((e.get("data") or [{}])[0] or {}).get("system")
            if system == "maintenance" and maint_since is None:
                maint_since = t
            elif system != "maintenance" and maint_since is not None:
                maint.append((maint_since, t))
                maint_since = None
    for s in symbols:
        if since[s] is not None:
            inv[s].append((since[s], end))
    if maint_since is not None:
        maint.append((maint_since, end))
    maint = merge(clip(maint, start, end))

    silence_iv = list(silences)
    if last_recv is not None and not provisional and end - last_recv > SILENCE_NS:
        silence_iv.append((last_recv, end))
    analysed_end = end if not provisional else (last_recv or end)

    pairs = {}
    for s in symbols:
        own = merge(clip(inv[s], start, analysed_end))
        both = merge(clip(own + silence_iv, start, analysed_end))
        initial = [iv for iv in own if iv[0] == start][:1]
        denom = (analysed_end - start) - total(maint)
        invalid = total(subtract(both, maint))
        invalid_excl_init = total(subtract(subtract(both, maint), initial))
        valid = complement(both, start, analysed_end)
        longest = max(valid, key=lambda iv: iv[1] - iv[0], default=None)
        pairs[s] = {
            "invalid_s_dec071": invalid / 1e9,
            "invalid_s_capture_events_only": total(subtract(own, maint)) / 1e9,
            "valid_share_dec071": 1 - invalid / denom if denom > 0 else None,
            "valid_share_dec071_excl_initial_sync": (1 - invalid_excl_init / (denom - total(initial)))
            if denom - total(initial) > 0 else None,
            "R4_pass": (1 - invalid / denom) >= 0.99 if denom > 0 else None,
            "longest_valid_stretch": None if longest is None else
            {"from": iso(longest[0]), "to": iso(longest[1]), "hours": (longest[1] - longest[0]) / 3.6e12},
            "R3_recovery_s": dist(recov[s]),
            "R3_breaches_over_60s": sum(1 for x in recov[s] if x > 60),
        }
        if summary is not None:
            pairs[s]["capture_summary_valid_share_not_for_R4"] = ((summary.get("R4") or {}).get(s) or {}).get("valid_share")

    # T-5 / T-6 time coverage from the latest successful sample
    def flag_time(pred_off, stale_ns):
        flagged = []
        pts = [(t, o) for t, o in good_ntp if start <= t <= analysed_end]
        lead = [(start, pts[0][0] if pts else analysed_end)]  # before the first sample: unknown (DEC-067)
        flagged += lead
        for i, (t, o) in enumerate(pts):
            nxt = pts[i + 1][0] if i + 1 < len(pts) else analysed_end
            if pred_off(abs(o)):
                flagged.append((t, nxt))
            elif stale_ns is not None and nxt - t > stale_ns:
                flagged.append((t + stale_ns, nxt))
        return total(merge(flagged)) / 1e9

    in_window = [o for t, o in good_ntp if start <= t <= analysed_end]
    gaps = [b - a for (a, _), (b, _) in zip(good_ntp, good_ntp[1:])]
    clock = {
        "samples": len([1 for t, _ in ntp if start <= t <= analysed_end]),
        "failed": len([1 for t, o in ntp if o is None and start <= t <= analysed_end]),
        "max_abs_ms": max((abs(o) for o in in_window), default=None),
        "over_100ms": sum(1 for o in in_window if abs(o) > T5_FLAG_MS),
        "over_1s": [{"at": iso(t), "offset_ms": o} for t, o in good_ntp if abs(o) > T6_INTRADAY_MS and start <= t <= analysed_end],
        "over_60s": sum(1 for o in in_window if abs(o) > T6_DAILY_MS),
        "max_interval_between_samples_s": max(gaps, default=0) / 1e9 if gaps else None,
        "intervals_over_1h": sum(1 for g in gaps if g > T5_STALE_NS),
        "T5_uncertainty_flag_s": flag_time(lambda a: a > T5_FLAG_MS, None),
        "T6_intraday_abstain_s": flag_time(lambda a: a > T6_INTRADAY_MS, T6_STALE_NS),
        "T6_daily_abstain_s": flag_time(lambda a: a > T6_DAILY_MS, None),
    }

    latency = {}
    for (ch, sym, day), (raw, cor) in sorted(lat.items()):
        latency.setdefault(f"{ch}:{sym}", {})[day] = {"raw_ms": quantiles(raw), "offset_corrected_ms": quantiles(cor)}

    gz_total = sum(r["gzip_bytes"] or 0 for r in seg_rows)
    covered_days = (last_recv - first_recv) / DAY_NS if first_recv is not None and last_recv else None

    # segment hashes against the store index
    store_root = run / "store"
    store = check_store(store_root) if store_root.exists() else {"exists": False}
    seg_index = {}
    if store.get("opens_read_only"):
        st = RawStore(store_root, read_only=True)
        for obj in st.objects.values():
            if "#segment:" in obj.request:
                seg_index[obj.request.split("#segment:")[1]] = obj.raw_id
    seg_mismatch = [r["file"] for r in seg_rows if seg_index.get(r["file"]) not in (None, r["sha256"])]
    seg_unindexed = [r["file"] for r in seg_rows if r["file"] not in seg_index]

    return {
        "run": str(run), "provisional": provisional, "skipped_open_segment": skipped_open_segment,
        "window": {"start": iso(start), "end": iso(end), "analysed_end": iso(analysed_end), "wall_h": wall / 3.6e12,
                   "maintenance_s": total(maint) / 1e9, "maintenance_intervals": [[iso(a), iso(b)] for a, b in maint]},
        "frames": {"segments": len(seg_rows), "frames": frames, "first": iso(first_recv), "last": iso(last_recv),
                   "malformed": malformed_frames[:50], "malformed_count": len(malformed_frames),
                   "events_malformed_lines": events_malformed},
        "gap_rule": "DEC-071: a gap runs from the last frame received to the next when they are more than 15 s apart",
        "silences": {"count": len(silences), "total_s": total(silences) / 1e9,
                     "over_60s": [[iso(a), iso(b), (b - a) / 1e9] for a, b in silences if b - a > 60 * 10**9]},
        "events": dict(sorted(counts.items())), "disconnects": len(disconnects), "parse_errors": len(parse_errors),
        "pairs": pairs,
        "Q5": {"book_valid_without_fresh_snapshot": q5_violations, "pass": not q5_violations},
        "T3_latency": latency,
        "T3_ingest_note": "ingest - receive is not measured: frames are journalled before parsing and normalised offline",
        "T3_items_older_than_15s_on_receipt": dict(sorted(stale_items.items())),
        "clock_T5_T6": clock,
        "R5_storage": {"uncompressed_bytes": sum(r["bytes"] for r in seg_rows), "gzip_bytes": gz_total if compress else None,
                       "gzip_bytes_per_pair_per_day": (gz_total / len(symbols) / covered_days)
                       if compress and covered_days else None,
                       "pass": (gz_total / len(symbols) / covered_days) <= 2 * 10**9 if compress and covered_days else None},
        "segments": seg_rows,
        "store": store,
        "segment_hash_vs_index": {"checked": len(seg_rows), "mismatch": seg_mismatch, "not_indexed": seg_unindexed},
        "capture_summary": None if summary is None else {k: summary.get(k) for k in
                                                         ("duration_s", "frames", "disconnects", "parse_errors",
                                                          "checksum_fail", "resyncs", "resync_capped", "R4",
                                                          "venue_status_seen", "ran_at_utc")},
    }


# -- REST pull -------------------------------------------------------------------
def analyse_rest(run: Path) -> dict:
    run = Path(run)
    days = []
    p = run / "daily-summary.jsonl"
    rows = [json.loads(l) for l in p.read_text().splitlines() if l.strip()] if p.exists() else []
    for r in rows:
        res = r.get("results") or {}
        days.append({"day": r.get("day"), "ran_at_utc": r.get("ran_at_utc"), "stopped": r.get("stopped"),
                     "calls": len(res),
                     "stored": sum(1 for v in res.values() if v.get("raw_id")),
                     "first_attempt": sum(1 for v in res.values() if v.get("attempts") == 1),
                     "gaps": {k: v.get("gap") for k, v in res.items() if v.get("gap")},
                     "api_errors": {k: v.get("api_error") for k, v in res.items() if v.get("api_error")}})
    seen = [d["day"] for d in days if d["day"]]
    return {"run": str(run), "started": (run / "started_utc.txt").read_text().strip() if (run / "started_utc.txt").exists() else None,
            "days": days, "distinct_days": len(set(seen)), "duplicate_days": sorted(d for d, c in Counter(seen).items() if c > 1),
            "all_calls_stored": all(d["stored"] == d["calls"] == 3 for d in days if not d["stopped"]),
            "store": check_store(run / "store")}


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description="Read-only G02 analysis of a captured run (TASK-P02-003)")
    ap.add_argument("kind", choices=["live", "rest"])
    ap.add_argument("--run", required=True, type=Path)
    ap.add_argument("--out", required=True, type=Path, help="report file (.json), outside the run and the repository")
    ap.add_argument("--no-compress", action="store_true", help="skip the gzip size measurement (R-5)")
    ap.add_argument("--symbols", default="BTC/USD,ETH/USD")
    a = ap.parse_args(argv)
    run, out = a.run.resolve(), a.out.resolve()
    repo = Path(__file__).resolve().parents[2]
    for guard, why in ((run, "the run directory"), (repo, "the repository (DEC-030)")):
        if guard == out.parent or guard in out.parents:
            sys.exit(f"--out must be outside {why}")
    report = analyse_live(run, a.symbols.split(","), compress=not a.no_compress) if a.kind == "live" else analyse_rest(run)
    report["analysed_at_utc"] = datetime.now(timezone.utc).isoformat()
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(report, indent=1, sort_keys=True, default=str) + "\n")
    print(json.dumps({k: report[k] for k in report if k not in ("segments", "T3_latency", "days")}, indent=1,
                     sort_keys=True, default=str))
    return 0
