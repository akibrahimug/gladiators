"""RC-05 to RC-08 (offline; DEC-065)."""

import errno
import json
import sys
import tempfile
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from gladiator_capture import fetch as Fe  # noqa: E402
from gladiator_capture import live_records as LR  # noqa: E402
from gladiator_capture.rawstore import RawStore  # noqa: E402


class Crash(BaseException):
    """Stands in for the process dying mid-copy."""


class RecoveryTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.root = Path(self.tmp.name)
        self.f = self.root / "a.bin"
        self.f.write_bytes(b"x" * 1000)

    def tearDown(self):
        self.tmp.cleanup()
        RawStore._copy = staticmethod(__import__("shutil").copyfile)

    def test_rc05_crash_marker_and_recovery(self):
        def half_then_crash(src, dst):
            Path(dst).write_bytes(Path(src).read_bytes()[:500])
            raise Crash()

        store = RawStore(self.root / "s")
        RawStore._copy = staticmethod(half_then_crash)
        with self.assertRaises(Crash):
            store.ingest_file(self.f, source_id="S", source_approval_id="A", request="u")
        RawStore._copy = staticmethod(__import__("shutil").copyfile)
        store.close()  # the crashed process's lock is released
        restarted = RawStore(self.root / "s")  # a new process; recover() runs on opening
        rec = restarted.last_recovery
        self.assertEqual(len(rec["incomplete"]), 1)
        self.assertEqual(len(rec["partials_removed"]), 1)
        obj = restarted.ingest_file(self.f, source_id="S", source_approval_id="A", request="u")
        self.assertTrue(restarted.object_path(obj.raw_id).exists())
        self.assertEqual(restarted.recover()["incomplete"], [])  # nothing left open
        outcomes = [e.outcome for e in restarted.journal_entries()]
        self.assertEqual(outcomes, ["started", "recovered_incomplete", "started", "stored"])

    def test_rc06_disk_full(self):
        def enospc(src, dst):
            Path(dst).write_bytes(b"partial")
            raise OSError(errno.ENOSPC, "No space left on device")

        store = RawStore(self.root / "s")
        RawStore._copy = staticmethod(enospc)
        with self.assertRaises(OSError):
            store.ingest_file(self.f, source_id="S", source_approval_id="A", request="u")
        self.assertEqual(list(self.root.glob("s/objects/*/*.part")), [])
        self.assertEqual(store.journal_entries()[-1].outcome, "failed")

        class T:
            calls = 0

            def get(self, u):
                T.calls += 1
                return Fe.Response(200, b"abc", {"Content-Length": "3"})

        res = Fe.fetch("u2", T(), store, source_id="S", source_approval_id="A", sleep=lambda s: None)
        self.assertEqual((res.raw, T.calls), (None, 1))  # no retry into a full disk
        self.assertTrue(res.gap.evidence.startswith("write_failed"))
        self.assertEqual(res.gap.availability_state, "SOURCE_UNAVAILABLE")


class ClockTests(unittest.TestCase):
    def frames(self, recv_ns):
        trade = {"channel": "trade", "type": "update", "data": [{"symbol": "BTC/USD", "side": "buy", "price": 1.5,
                                                                 "qty": 0.1, "ord_type": "market", "trade_id": 7,
                                                                 "timestamp": "2026-10-28T10:00:00.000001Z"}]}
        return [(0, recv_ns, json.dumps(trade))]

    def test_rc07_rc08_flags(self):
        t = 1_793_181_600_000_000_000
        cases = [(None, None, ["clock_offset_unknown", "clock_abstain_intraday"]), (50.0, None, []), (150.0, 150.0, []),
                 (1500.0, 1500.0, ["clock_abstain_intraday"]),
                 (-70000.0, 70000.0, ["clock_abstain_intraday", "clock_abstain_daily"])]
        for off, unc, flags in cases:
            offsets = [] if off is None else [(t - 1, off)]
            r = LR.normalize(self.frames(t), offsets, raw_id="r", ingested_at=0)[0]
            self.assertEqual((r.fields["timestamp_uncertainty_ms"], r.quality_flags), (unc, flags), off)
        self.assertEqual((r.available_at_basis, r.source_time_unit, r.source_event_time % 1_000_000), ("live_receive", "us", 1))

    def test_offset_applies_from_its_sample_time(self):
        t = 1_793_181_600_000_000_000
        r = LR.normalize(self.frames(t), [(t + 1, 500.0)], raw_id="r", ingested_at=0)[0]
        self.assertIn("clock_offset_unknown", r.quality_flags)  # the sample came after the frame


if __name__ == "__main__":
    unittest.main()
