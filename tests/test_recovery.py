"""RC-05 to RC-08 (offline; DEC-065)."""

import errno
import json
import os
import sys
import tempfile
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from gladiator_capture import fetch as Fe  # noqa: E402
from gladiator_capture import live_records as LR  # noqa: E402
from gladiator_capture import rawstore as R  # noqa: E402
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


class StoreFailureTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.root = Path(self.tmp.name)
        self.f = self.root / "a.bin"
        self.f.write_bytes(b"y" * 100)

    def tearDown(self):
        RawStore._copy = staticmethod(__import__("shutil").copyfile)
        self.tmp.cleanup()

    def test_second_writer_refused(self):
        s = RawStore(self.root / "s")
        with self.assertRaises(RuntimeError):
            RawStore(self.root / "s")
        s.close()
        RawStore(self.root / "s").close()

    def test_truncated_tail_repaired_and_store_stays_usable(self):
        s = RawStore(self.root / "s")
        s.ingest_file(self.f, source_id="S", source_approval_id="A", request="u")
        s.close()
        with open(self.root / "s" / "journal.jsonl", "ab") as fh:
            fh.write(b'{"at_ns": 1, "outco')  # fragment from a failed write
        s2 = RawStore(self.root / "s")
        self.assertEqual(s2.repaired[0]["file"], "journal.jsonl")
        g = self.root / "b.bin"
        g.write_bytes(b"z")
        s2.ingest_file(g, source_id="S", source_approval_id="A", request="v")
        s2.close()
        s3 = RawStore(self.root / "s")  # would raise JSONDecodeError without the repair
        self.assertEqual([e.outcome for e in s3.journal_entries()][-2:], ["started", "stored"])
        s3.close()

    def test_read_only_changes_nothing(self):
        s = RawStore(self.root / "s")
        s.ingest_file(self.f, source_id="S", source_approval_id="A", request="u")
        s.close()
        part = self.root / "s" / "objects" / "zz" / "x.part"
        part.parent.mkdir(parents=True, exist_ok=True)
        part.write_bytes(b"in progress")
        before = sorted((p.name, p.stat().st_size) for p in (self.root / "s").rglob("*") if p.is_file())
        ro = RawStore(self.root / "s", read_only=True)
        self.assertEqual(len(ro.objects), 1)
        with self.assertRaises(PermissionError):
            ro.ingest_file(self.f, source_id="S", source_approval_id="A", request="w")
        after = sorted((p.name, p.stat().st_size) for p in (self.root / "s").rglob("*") if p.is_file())
        self.assertEqual(before, after)
        self.assertTrue(part.exists())
        with self.assertRaises(PermissionError):
            ro.recover()
        self.assertTrue(part.exists())

    def test_recovered_complete_after_index(self):
        s = RawStore(self.root / "s")
        s.ingest_file(self.f, source_id="S", source_approval_id="A", request="u")
        lines = (self.root / "s" / "journal.jsonl").read_text().splitlines()
        (self.root / "s" / "journal.jsonl").write_text(lines[0] + "\n")  # crash before `stored` was journalled
        s.close()
        s2 = RawStore(self.root / "s")
        self.assertEqual(len(s2.last_recovery["completed_before_crash"]), 1)
        self.assertEqual(s2.journal_entries()[-1].outcome, "recovered_complete")
        s2.close()

    def test_copy_hash_mismatch_labelled_with_raw_id(self):
        def bad_copy(a, b):
            Path(b).write_bytes(b"not the same")

        s = RawStore(self.root / "s")
        RawStore._copy = staticmethod(bad_copy)
        res = Fe.fetch("u", type("T", (), {"get": lambda self, u: Fe.Response(200, b"abc", {"Content-Length": "3"})})(),
                       s, source_id="S", source_approval_id="A", sleep=lambda x: None)
        e = s.journal_entries()[-2]
        self.assertEqual((e.outcome, e.detail, e.raw_id is not None), ("failed", "copy_hash_mismatch", True))
        self.assertEqual(res.gap.evidence, "copy_hash_mismatch")
        self.assertEqual(list((self.root / "s").glob("objects/*/*.part")), [])
        self.assertEqual(s.recover()["incomplete"], [])
        s.close()

    def test_rename_failure_cleans_up(self):
        s = RawStore(self.root / "s")
        orig = Path.rename

        def boom(self_, target):
            raise OSError(errno.EIO, "I/O error")

        Path.rename = boom
        try:
            with self.assertRaises(OSError):
                s.ingest_file(self.f, source_id="S", source_approval_id="A", request="u")
        finally:
            Path.rename = orig
        self.assertEqual(list((self.root / "s").glob("objects/*/*.part")), [])
        self.assertEqual(s.journal_entries()[-1].outcome, "failed")
        s.close()

    def test_fetch_temp_file_failure(self):
        import tempfile as tf
        orig = tf.NamedTemporaryFile

        def no_inodes(*a, **k):
            raise OSError(errno.ENOSPC, "No space left on device")

        s = RawStore(self.root / "s")
        Fe.tempfile.NamedTemporaryFile = no_inodes
        try:
            res = Fe.fetch("u", type("T", (), {"get": lambda self, u: Fe.Response(200, b"abc", {"Content-Length": "3"})})(),
                           s, source_id="S", source_approval_id="A", sleep=lambda x: None)
        finally:
            Fe.tempfile.NamedTemporaryFile = orig
        self.assertEqual((res.raw, res.gap.availability_state), (None, "SOURCE_UNAVAILABLE"))
        self.assertTrue(res.gap.evidence.startswith("write_failed"))
        s.close()


class ShortAppendTests(unittest.TestCase):
    """RC-06: a short journal/index append is rolled back, so later appends and a reopen still work
    (Codex review of PR #31)."""

    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.root = Path(self.tmp.name)
        self.real_write, self.real_ftruncate = os.write, os.ftruncate

    def tearDown(self):
        R.os.write, R.os.ftruncate = self.real_write, self.real_ftruncate
        self.tmp.cleanup()

    def short_first_index_write(self):
        real, done = self.real_write, []

        def w(fd, data):
            if not done and b'"member_path"' in data:  # the first RawObject index line
                done.append(1)
                return real(fd, data[: len(data) // 2])
            return real(fd, data)
        R.os.write = w

    @staticmethod
    def transport(body):
        return type("T", (), {"get": lambda self, u: Fe.Response(200, body, {"Content-Length": str(len(body))})})()

    def test_short_index_write_then_more_fetches_then_reopen(self):
        store = RawStore(self.root / "s")
        self.short_first_index_write()
        res = Fe.fetch("u1", self.transport(b"one"), store, source_id="S", source_approval_id="A", sleep=lambda s: None)
        self.assertIsNone(res.raw)
        self.assertTrue(res.gap.evidence.startswith("write_failed"))
        R.os.write = self.real_write
        for u, body in (("u2", b"two"), ("u3", b"three")):
            self.assertIsNotNone(Fe.fetch(u, self.transport(body), store, source_id="S", source_approval_id="A",
                                          sleep=lambda s: None).raw)
        rolled_back = [r["file"] for r in store.repaired]
        store.close()
        reopened = RawStore(self.root / "s")  # previously raised JSONDecodeError on the merged line
        self.assertEqual(rolled_back, ["index.jsonl"])
        self.assertEqual(sorted(reopened.object_for_request), ["u2", "u3"])
        self.assertEqual(reopened.repaired, [])
        self.assertTrue((self.root / "s" / "index.jsonl").read_bytes().endswith(b"\n"))

    def test_journal_write_raising_is_rolled_back(self):
        store = RawStore(self.root / "s")
        real, done = self.real_write, []

        def w(fd, data):
            if not done and b'"started"' in data:
                done.append(1)
                real(fd, data[:7])
                raise OSError(errno.ENOSPC, "No space left on device")
            return real(fd, data)
        R.os.write = w
        f = self.root / "a.bin"
        f.write_bytes(b"x")
        with self.assertRaises(OSError):
            store.ingest_file(f, source_id="S", source_approval_id="A", request="u")
        self.assertEqual([r["file"] for r in store.repaired], ["journal.jsonl"])
        R.os.write = self.real_write
        store.ingest_file(f, source_id="S", source_approval_id="A", request="u")
        store.close()
        self.assertEqual([e.outcome for e in RawStore(self.root / "s").journal_entries()], ["started", "stored"])

    def test_member_index_retried_after_rollback(self):
        import zipfile
        z = self.root / "c.zip"
        with zipfile.ZipFile(z, "w") as zf:
            zf.writestr("m.csv", "1,2\n")
        store = RawStore(self.root / "s")
        container = store.ingest_file(z, source_id="S", source_approval_id="A", request="u")
        real, done = self.real_write, []

        def w(fd, data):
            if not done and b'"member_path": "m.csv"' in data:
                done.append(1)
                return real(fd, data[:5])
            return real(fd, data)
        R.os.write = w
        with self.assertRaises(OSError):
            store.member(container, "m.csv")
        R.os.write = self.real_write
        obj = store.member(container, "m.csv")
        store.close()
        self.assertIn(obj.raw_id, RawStore(self.root / "s").objects)  # indexed on the retry

    def test_failed_rollback_makes_store_unusable_until_reopen(self):
        store = RawStore(self.root / "s")
        self.short_first_index_write()

        def no_truncate(fd, size):
            raise OSError(errno.EIO, "I/O error")
        R.os.ftruncate = no_truncate
        f = self.root / "a.bin"
        f.write_bytes(b"x")
        with self.assertRaises(OSError):
            store.ingest_file(f, source_id="S", source_approval_id="A", request="u")
        self.assertEqual(store.unusable, "rollback_failed:index.jsonl")
        R.os.write, R.os.ftruncate = self.real_write, self.real_ftruncate
        with self.assertRaises(OSError):
            store.ingest_file(f, source_id="S", source_approval_id="A", request="u")  # refused, not merged
        store.close()
        reopened = RawStore(self.root / "s")
        self.assertEqual(reopened.repaired[0]["file"], "index.jsonl")  # the fragment is cut and kept
        self.assertIsNotNone(reopened.ingest_file(f, source_id="S", source_approval_id="A", request="u"))


if __name__ == "__main__":
    unittest.main()
