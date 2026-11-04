"""Offline tests for the read-only G02 run analysis (TASK-P02-003, DEC-071)."""

import hashlib
import io
import json
import os
import sys
import tempfile
import unittest
from contextlib import redirect_stdout
from datetime import datetime, timezone
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from gladiator_capture import live_analysis as A  # noqa: E402
from gladiator_capture.rawstore import RawStore  # noqa: E402

S = 10**9
T0 = 1_800_000_000 * S  # 2027-01-15T08:00:00Z
SYMS = ["BTC/USD", "ETH/USD"]


def ts(ns):
    return datetime.fromtimestamp(ns / 1e9, timezone.utc).strftime("%Y-%m-%dT%H:%M:%S.%fZ")


def snap(sym):
    return json.dumps({"channel": "book", "type": "snapshot", "data": [{"symbol": sym, "bids": [], "asks": [], "checksum": 1}]})


def upd(sym, at_ns):
    return json.dumps({"channel": "book", "type": "update",
                       "data": [{"symbol": sym, "bids": [], "asks": [], "checksum": 1, "timestamp": ts(at_ns)}]})


HB = json.dumps({"channel": "heartbeat"})


class Run:
    """A synthetic live-capture directory: frames (one segment per list), events, summary, store."""

    def __init__(self, root: Path, segments: list, events: list, duration_s=None, summary=True, ingest=True):
        self.root = root
        root.mkdir(parents=True, exist_ok=True)
        store = RawStore(root / "store", clock=lambda: T0)
        for seg in segments:
            name = root / f"frames-{seg[0][0]}.jsonl"
            name.write_text("".join(json.dumps({"recv_ns": r, "frame": f}) + "\n" for r, f in seg))
            if ingest:
                store.ingest_file(name, source_id="SR-02", source_approval_id="SA-03",
                                  request=f"wss://ws.kraken.com/v2#segment:{name.name}", retrieved_at_ns=T0)
        store.close()
        (root / "events.jsonl").write_text("".join(json.dumps({"at_ns": t, "kind": k, **kw}) + "\n" for t, k, kw in events))
        if summary:
            (root / "live-summary.jsonl").write_text(json.dumps({
                "duration_s": duration_s, "ran_at_utc": datetime.fromtimestamp(T0 / 1e9, timezone.utc).isoformat(),
                "R4": {s: {"valid_share": 1.0} for s in SYMS}}) + "\n")


def steady(start_s, end_s, step_s=1, extra=None):
    """A heartbeat every step_s seconds over [start, end), with optional frames merged in."""
    out = [(T0 + t * S, HB) for t in range(start_s, end_s, step_s)]
    out += extra or []
    return sorted(out)


def valid_both(t_s):
    return [(T0 + t_s * S, "book_valid", {"symbol": s}) for s in SYMS]


class AnalysisTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.dir = Path(self.tmp.name)

    def tearDown(self):
        self.tmp.cleanup()

    def basic(self, frames, events, duration_s=1000, **kw):
        run = Run(self.dir / "run", [frames], events, duration_s=duration_s, **kw)
        return A.analyse_live(run.root, SYMS, compress=True)

    def test_silence_counts_as_invalid_under_dec071(self):
        # books valid at 2 s; frames stop at 100 s and resume at 400 s; no event says the book was invalid
        frames = steady(0, 100, extra=[(T0 + 1 * S, snap(s)) for s in SYMS]) + steady(400, 1000)
        r = self.basic(frames, [(T0 + 1, "ntp", {"offset_ms": 5.0})] + valid_both(2))
        p = r["pairs"]["BTC/USD"]
        self.assertAlmostEqual(p["invalid_s_capture_events_only"], 2.0, places=3)
        self.assertAlmostEqual(p["invalid_s_dec071"], 2.0 + 301, places=3)  # 99 s -> 400 s is the gap
        self.assertEqual(r["silences"]["count"], 1)
        self.assertFalse(p["R4_pass"])
        self.assertEqual(p["longest_valid_stretch"]["hours"], (1000 - 400) / 3600)
        self.assertEqual(p["capture_summary_valid_share_not_for_R4"], 1.0)

    def test_fifteen_second_silence_is_not_a_gap(self):
        frames = [(T0, snap("BTC/USD")), (T0, snap("ETH/USD")), (T0 + 15 * S, HB), (T0 + 31 * S, HB)]
        r = self.basic(frames, valid_both(0), duration_s=31)
        self.assertEqual(r["silences"]["count"], 1)  # only the 16 s one
        self.assertAlmostEqual(r["pairs"]["ETH/USD"]["invalid_s_dec071"], 16.0)

    def test_tail_silence_counts_when_run_finished(self):
        frames = steady(0, 50, extra=[(T0, snap(s)) for s in SYMS])
        r = self.basic(frames, valid_both(0), duration_s=200)
        self.assertAlmostEqual(r["pairs"]["BTC/USD"]["invalid_s_dec071"], 200 - 49)

    def test_maintenance_excluded(self):
        frames = steady(0, 1000, extra=[(T0, snap(s)) for s in SYMS] + [(T0 + 520 * S, snap(s)) for s in SYMS])
        ev = valid_both(0) + [(T0 + 500 * S, "venue_status", {"data": [{"system": "maintenance"}]}),
                              (T0 + 501 * S, "disconnect", {}),
                              (T0 + 600 * S, "venue_status", {"data": [{"system": "online"}]})] + valid_both(520)
        r = self.basic(frames, ev)
        self.assertEqual(r["window"]["maintenance_s"], 100)
        self.assertAlmostEqual(r["pairs"]["BTC/USD"]["invalid_s_dec071"], 0)
        self.assertEqual(r["pairs"]["BTC/USD"]["valid_share_dec071"], 1.0)

    def test_q5_requires_fresh_snapshot(self):
        frames = steady(0, 100, extra=[(T0, snap(s)) for s in SYMS] + [(T0 + 60 * S, snap("BTC/USD"))])
        ev = valid_both(0) + [(T0 + 50 * S, "disconnect", {})] + valid_both(61)
        r = self.basic(frames, ev, duration_s=100)
        self.assertFalse(r["Q5"]["pass"])
        self.assertEqual([v["symbol"] for v in r["Q5"]["book_valid_without_fresh_snapshot"]], ["ETH/USD"])

    def test_parse_error_opens_invalid_interval(self):  # the PR #30 defect on the running capture
        frames = steady(0, 100, extra=[(T0, snap(s)) for s in SYMS] + [(T0 + 40 * S, snap(s)) for s in SYMS])
        ev = valid_both(0) + [(T0 + 30 * S, "parse_error", {"error": "KeyError"})] + valid_both(40)
        r = self.basic(frames, ev, duration_s=100)
        self.assertEqual(r["parse_errors"], 1)
        self.assertAlmostEqual(r["pairs"]["BTC/USD"]["invalid_s_capture_events_only"], 10)
        self.assertTrue(r["Q5"]["pass"])

    def test_r3_from_disconnect_to_valid(self):
        frames = steady(0, 300, extra=[(T0, snap(s)) for s in SYMS] + [(T0 + 103 * S, snap(s)) for s in SYMS]
                        + [(T0 + 270 * S, snap(s)) for s in SYMS])
        ev = (valid_both(0) + [(T0 + 100 * S, "disconnect", {})] + valid_both(103)
              + [(T0 + 200 * S, "disconnect", {})] + valid_both(270))
        r = self.basic(frames, ev, duration_s=300)
        r3 = r["pairs"]["BTC/USD"]["R3_recovery_s"]
        self.assertEqual((r3["n"], r3["max"]), (2, 70.0))
        self.assertEqual(r["pairs"]["BTC/USD"]["R3_breaches_over_60s"], 1)

    def test_provisional_skips_open_segment(self):
        segs = [steady(0, 10, extra=[(T0, snap(s)) for s in SYMS]), steady(10, 20)]
        run = Run(self.dir / "run", segs, valid_both(0), summary=False)
        r = A.analyse_live(run.root, SYMS, compress=False)
        self.assertTrue(r["provisional"])
        self.assertEqual(r["skipped_open_segment"], f"frames-{T0 + 10 * S}.jsonl")
        self.assertEqual(r["frames"]["segments"], 1)
        self.assertEqual(r["window"]["analysed_end"], ts(T0 + 9 * S))

    def test_t3_latency_raw_and_offset_corrected(self):
        frames = [(T0, snap("BTC/USD")), (T0 + 10 * S, upd("BTC/USD", T0 + 10 * S - 40 * 10**6))]
        r = self.basic(frames, [(T0 - 1, "ntp", {"offset_ms": 7.0})] + valid_both(0), duration_s=10)
        day = ts(T0)[:10]
        d = r["T3_latency"]["book:BTC/USD"][day]
        self.assertEqual((d["raw_ms"]["p50"], d["offset_corrected_ms"]["p50"]), (40, 47))

    def test_t5_t6_time_flags(self):
        frames = steady(0, 400, extra=[(T0, snap(s)) for s in SYMS])
        ev = valid_both(0) + [(T0 + 10 * S, "ntp", {"offset_ms": 50.0}), (T0 + 40 * S, "ntp", {"offset_ms": 1500.0}),
                              (T0 + 70 * S, "ntp", {"offset_ms": None}), (T0 + 100 * S, "ntp", {"offset_ms": 20.0})]
        r = self.basic(frames, ev, duration_s=400)
        c = r["clock_T5_T6"]
        self.assertEqual((c["samples"], c["failed"], c["over_100ms"]), (4, 1, 1))
        self.assertEqual([x["offset_ms"] for x in c["over_1s"]], [1500.0])
        # unknown before 10 s, >1 s from 40 to 100 s, stale after 160 s (no sample after 100 s)
        self.assertAlmostEqual(c["T6_intraday_abstain_s"], 10 + 60 + 240)
        self.assertAlmostEqual(c["T5_uncertainty_flag_s"], 10 + 60)

    def test_r5_gzip_size(self):
        frames = steady(0, 1000, extra=[(T0, snap(s)) for s in SYMS])
        r = self.basic(frames, valid_both(0))
        self.assertGreater(r["R5_storage"]["gzip_bytes"], 0)
        self.assertLess(r["R5_storage"]["gzip_bytes"], r["R5_storage"]["uncompressed_bytes"])
        self.assertTrue(r["R5_storage"]["pass"])

    def test_segment_hash_checked_against_index(self):
        run = Run(self.dir / "run", [steady(0, 10, extra=[(T0, snap(s)) for s in SYMS])], valid_both(0), duration_s=10)
        r = A.analyse_live(run.root, SYMS, compress=False)
        self.assertEqual((r["segment_hash_vs_index"]["mismatch"], r["store"]["ok"]), ([], True))
        seg = next(run.root.glob("frames-*.jsonl"))
        with open(seg, "a") as fh:
            fh.write(json.dumps({"recv_ns": T0 + 11 * S, "frame": HB}) + "\n")
        r = A.analyse_live(run.root, SYMS, compress=False)
        self.assertEqual(r["segment_hash_vs_index"]["mismatch"], [seg.name])

    def test_malformed_lines_reported_not_raised(self):
        run = Run(self.dir / "run", [steady(0, 10, extra=[(T0, snap(s)) for s in SYMS])], valid_both(0), duration_s=10)
        seg = next(run.root.glob("frames-*.jsonl"))
        with open(seg, "a") as fh:
            fh.write("{not json\n")
        idx = run.root / "store" / "index.jsonl"
        idx.write_bytes(b"{bad\n" + idx.read_bytes() + b'{"cut')
        r = A.analyse_live(run.root, SYMS, compress=False)
        self.assertEqual(r["frames"]["malformed_count"], 1)
        self.assertEqual(r["store"]["index"]["malformed_interior"], [1])
        self.assertTrue(r["store"]["index"]["incomplete_tail"])
        self.assertFalse(r["store"]["opens_read_only"])  # an interior bad line makes the store refuse to open

    def test_store_object_tamper_detected(self):
        run = Run(self.dir / "run", [steady(0, 10)], valid_both(0), duration_s=10)
        obj = next(p for p in (run.root / "store" / "objects").rglob("*") if p.is_file())
        data = bytearray(obj.read_bytes())
        data[0] ^= 1
        obj.write_bytes(bytes(data))
        res = A.check_store(run.root / "store")
        self.assertEqual((res["ok"], res["objects"]["hash_mismatch"]), (False, [obj.name]))

    def test_analysis_changes_nothing(self):
        frames = steady(0, 100, extra=[(T0, snap(s)) for s in SYMS])
        run = Run(self.dir / "run", [frames], valid_both(0), duration_s=100)

        def tree():
            out = {}
            for p in sorted(run.root.rglob("*")):
                st = p.stat()
                out[str(p)] = (st.st_size, st.st_mtime_ns,
                               hashlib.sha256(p.read_bytes()).hexdigest() if p.is_file() else None)
            return out

        before = tree()
        A.analyse_live(run.root, SYMS, compress=True)
        A.check_store(run.root / "store")
        self.assertEqual(tree(), before)

    def test_cli_guards_and_report(self):
        run = Run(self.dir / "run", [steady(0, 10, extra=[(T0, snap(s)) for s in SYMS])], valid_both(0), duration_s=10)
        with self.assertRaises(SystemExit):
            A.main(["live", "--run", str(run.root), "--out", str(run.root / "r.json")])
        repo = Path(__file__).resolve().parents[1]
        with self.assertRaises(SystemExit):
            A.main(["live", "--run", str(run.root), "--out", str(repo / "r.json")])
        out = self.dir / "reports" / "r.json"
        with redirect_stdout(io.StringIO()):
            self.assertEqual(A.main(["live", "--no-compress", "--run", str(run.root), "--out", str(out)]), 0)
        rep = json.loads(out.read_text())
        self.assertEqual((rep["provisional"], rep["frames"]["frames"]), (False, 12))

    def test_rest_summary(self):
        root = self.dir / "rest"
        (root / "store").mkdir(parents=True)
        RawStore(root / "store").close()
        (root / "started_utc.txt").write_text("2026-10-29")
        ok = {"raw_id": "x", "gap": None, "attempts": 1, "api_error": None}
        rows = [{"day": "2026-10-29", "results": {"XBTUSD": ok, "ETHUSD": ok, "AssetPairs": ok}, "ran_at_utc": "a"},
                {"day": "2026-10-30", "results": {"XBTUSD": ok, "ETHUSD": {**ok, "raw_id": None, "gap": "timeout"},
                                                  "AssetPairs": ok}, "ran_at_utc": "b"}]
        (root / "daily-summary.jsonl").write_text("".join(json.dumps(r) + "\n" for r in rows))
        r = A.analyse_rest(root)
        self.assertEqual((r["distinct_days"], r["all_calls_stored"]), (2, False))
        self.assertEqual(r["days"][1]["gaps"], {"ETHUSD": "timeout"})
        self.assertTrue(r["store"]["ok"])


class IntervalTests(unittest.TestCase):
    def test_merge_subtract_complement(self):
        self.assertEqual(A.merge([(5, 7), (1, 3), (2, 4), (9, 9)]), [(1, 4), (5, 7)])
        self.assertEqual(A.subtract([(0, 10)], [(2, 3), (5, 12)]), [(0, 2), (3, 5)])
        self.assertEqual(A.complement([(2, 3)], 0, 5), [(0, 2), (3, 5)])
        self.assertEqual(A.quantiles(__import__("collections").Counter({1: 50, 2: 45, 9: 5})),
                         {"n": 100, "p50": 1, "p95": 2, "p99": 9, "max": 9})


if __name__ == "__main__":
    unittest.main()
