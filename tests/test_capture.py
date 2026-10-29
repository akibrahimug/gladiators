"""Unit tests on synthetic data (no vendor data is committed, DEC-030)."""

import json
import sys
import tempfile
import unittest
from decimal import Decimal
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from gladiator_capture import analysis as A  # noqa: E402
from gladiator_capture import fetch as Fe  # noqa: E402
from gladiator_capture import records as R  # noqa: E402
from gladiator_capture.rawstore import RawStore, sha256_file  # noqa: E402

DAY_S = 86_400


def kline(t_ms, o="10", h="11", l="9", c="10.5", v="100"):
    return f"{t_ms},{o},{h},{l},{c},{v},{t_ms + DAY_S * 1000 - 1},1000,5,50,500,0"


def month_klines(start_s, days, unit="ms"):
    mul = 1000 if unit == "ms" else 1_000_000
    rows = []
    for i in range(days):
        t = (start_s + i * DAY_S) * mul
        rows.append(f"{t},10,11,9,10.5,100,{t + DAY_S * mul - 1},1000,5,50,500,0")
    return "\n".join(rows) + "\n"


class FakeRaw:
    def __init__(self, raw_id="r1", retrieved_at_ns=2_000_000_000 * R.NS["s"], last_modified=None, supersedes=None):
        self.raw_id = raw_id
        self.retrieved_at_ns = retrieved_at_ns
        self.server_last_modified = last_modified
        self.supersedes_raw_id = supersedes
        self.member_path = None


DEC_2024 = 1733011200  # 2024-12-01T00:00:00Z
JAN_2025 = 1735689600  # 2025-01-01T00:00:00Z


class RawStoreTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.root = Path(self.tmp.name)
        self.store = RawStore(self.root / "store", clock=lambda: 123)
        self.f = self.root / "a.csv"
        self.f.write_text("x\n")

    def tearDown(self):
        self.tmp.cleanup()

    def test_idempotent_reingest(self):  # S-02a
        a = self.store.ingest_file(self.f, source_id="SR-04", source_approval_id="SA-01", request="u")
        b = self.store.ingest_file(self.f, source_id="SR-04", source_approval_id="SA-01", request="u")
        self.assertEqual(a.raw_id, b.raw_id)
        self.assertEqual(len(self.store.objects), 1)

    def test_revision_chain(self):  # S-09
        a = self.store.ingest_file(self.f, source_id="SR-04", source_approval_id="SA-01", request="u")
        self.f.write_text("y\n")
        b = self.store.ingest_file(self.f, source_id="SR-04", source_approval_id="SA-01", request="u")
        self.assertEqual(b.supersedes_raw_id, a.raw_id)
        self.assertTrue(self.store.object_path(a.raw_id).exists())  # every version kept (DEC-048)

    def test_checksum_mismatch_quarantines(self):  # S-01
        o = self.store.ingest_file(self.f, source_id="SR-04", source_approval_id="SA-01", request="u",
                                   published_checksum="00" * 32)
        self.assertEqual(o.checksum_status, "mismatch")
        self.assertTrue(o.quarantined)
        ok = self.store.ingest_file(self.f, source_id="SR-04", source_approval_id="SA-01", request="v",
                                    published_checksum=sha256_file(self.f))
        self.assertEqual(ok.checksum_status, "verified")

    def test_same_bytes_two_requests(self):  # each request keeps its own retrieval record
        a = self.store.ingest_file(self.f, source_id="SR-04", source_approval_id="SA-01", request="u", retrieved_at_ns=1)
        self.store.ingest_file(self.f, source_id="SR-04", source_approval_id="SA-01", request="w", retrieved_at_ns=2)
        again = self.store.ingest_file(self.f, source_id="SR-04", source_approval_id="SA-01", request="u")
        self.assertEqual((again.request, again.retrieved_at_ns), ("u", 1))

    def test_index_reload(self):
        a = self.store.ingest_file(self.f, source_id="SR-04", source_approval_id="SA-01", request="u")
        again = RawStore(self.root / "store")
        self.assertIn(a.raw_id, again.objects)


class BinanceParseTests(unittest.TestCase):
    def parse(self, text, name="BTCUSDT-1d-2024-12.csv", lm=None):
        return R.parse_binance_klines(text.encode(), name=name, symbol="BTCUSDT", interval="1d",
                                      raw=FakeRaw(last_modified=lm), ingested_at=1)

    def test_valid_month_and_available_at(self):
        res = self.parse(month_klines(DEC_2024, 31), lm="Wed, 08 Jan 2025 00:50:27 GMT")
        self.assertEqual(len(res.records), 31)
        r = res.records[0]
        self.assertEqual((r.source_time_unit, r.available_at_basis), ("ms", "archive_published"))
        self.assertEqual(r.available_at, 1736297427 * R.NS["s"])
        self.assertNotIn("late", r.quality_flags)  # monthly files are exempt from TH-6

    def test_fallback_to_retrieved(self):
        r = self.parse(month_klines(DEC_2024, 2)).records[0]
        self.assertEqual(r.available_at_basis, "retrieved")

    def test_unit_contradicts_era(self):  # S-07
        res = self.parse(month_klines(JAN_2025, 3, unit="ms"), name="BTCUSDT-1d-2025-01.csv")
        self.assertTrue(res.file_quarantined)
        self.assertEqual(res.reason, "unit_contradicts_era")
        ok = self.parse(month_klines(JAN_2025, 3, unit="us"), name="BTCUSDT-1d-2025-01.csv")
        self.assertFalse(ok.file_quarantined)
        self.assertEqual(ok.records[0].source_time_unit, "us")

    def test_duplicates_quarantine_both(self):  # S-02b, S-03
        lines = month_klines(DEC_2024, 3).splitlines()
        same = "\n".join(lines + [lines[1]]) + "\n"
        res = self.parse(same)
        self.assertEqual(sum(r.quality_state == "quarantined" for r in res.records), 2)
        self.assertEqual({r.reason for r in res.records if r.reason}, {"duplicate_timestamp"})
        diff = lines[1].replace(",10.5,", ",10.6,", 1)
        res2 = self.parse("\n".join(lines + [diff]) + "\n")
        self.assertEqual({r.reason for r in res2.records if r.reason}, {"duplicate_conflicting"})

    def test_invalid_rows(self):  # S-06
        lines = month_klines(DEC_2024, 3).splitlines()
        t0 = lines[0].split(",")[0]
        lines[0] = kline(int(t0), h="8")  # high < low
        t1 = lines[1].split(",")[0]
        lines[1] = kline(int(t1), c="NaN")
        res = self.parse("\n".join(lines) + "\n")
        self.assertEqual([r.reason for r in res.records], ["invalid_ohlc", "nonfinite_or_invalid_number", None])

    def test_column_count(self):  # S-13
        res = self.parse("1733011200000,1,2,0.5,1.5,1\n")
        self.assertTrue(res.file_quarantined)

    def test_naive_time(self):  # F-06b
        self.assertEqual(R.check_naive_time("2026-10-14T08:30:00"), "timezone_naive")
        self.assertIsNone(R.check_naive_time("2026-10-14T08:30:00-04:00"))

    def test_daily_file_late_flag(self):  # TH-6
        day = DEC_2024
        text = month_klines(day, 1)
        on_time = R.parse_binance_klines(text.encode(), name="BTCUSDT-1d-2024-12-01.csv", symbol="BTCUSDT",
                                         interval="1d", raw=FakeRaw(last_modified="Mon, 02 Dec 2024 03:00:00 GMT"),
                                         ingested_at=1).records[0]
        late = R.parse_binance_klines(text.encode(), name="BTCUSDT-1d-2024-12-01.csv", symbol="BTCUSDT",
                                      interval="1d", raw=FakeRaw(last_modified="Thu, 05 Dec 2024 03:00:00 GMT"),
                                      ingested_at=1).records[0]
        self.assertNotIn("late", on_time.quality_flags)
        self.assertIn("late", late.quality_flags)


class TradeTests(unittest.TestCase):
    def test_trade_gap(self):  # S-05
        t = JAN_2025 * 1_000_000
        rows = [f"{i},1,1,1,{t + i},True,True" for i in (1, 2, 4)]
        res = R.parse_binance_trades(("\n".join(rows) + "\n").encode(), name="ETHUSDT-trades-2025-01-15.csv",
                                     symbol="ETHUSDT", raw=FakeRaw(), ingested_at=1)
        gaps = A.trade_gaps(res.records)
        self.assertEqual([g.gap_class for g in gaps], ["data_gap"])


class KrakenTests(unittest.TestCase):
    def test_csv_gaps_status_unknown(self):  # S-04
        rows = [f"{1600000000 - 1600000000 % DAY_S + d * DAY_S},1,2,0.5,1.5,3,4" for d in (0, 1, 4)]
        res = R.parse_kraken_csv(("\n".join(rows) + "\n").encode(), pair="XBTUSD", interval_min=1440,
                                 raw=FakeRaw(), generated_ns=5 * R.NS["s"], ingested_at=1)
        gaps = A.bar_gaps(res.records, DAY_S * R.NS["s"])
        self.assertEqual(len(gaps), 2)
        self.assertTrue(all(g.gap_class == "status_unknown" and g.availability_state == "SOURCE_UNAVAILABLE"
                            for g in gaps))
        self.assertEqual(res.records[0].available_at_basis, "archive_published")

    def test_rest_incomplete_dropped_and_late(self):  # S-12, TH-6
        base = 1790000000 - 1790000000 % DAY_S
        rows = [[base + d * DAY_S, "1", "2", "0.5", "1.5", "1.2", "3", 4] for d in range(4)]
        doc = {"error": [], "result": {"XXBTZUSD": rows, "last": base + 2 * DAY_S}}
        received = (base + 3 * DAY_S + 3600) * R.NS["s"]  # during the 4th bar
        res = R.parse_kraken_rest_ohlc(json.dumps(doc).encode(), request_pair="XBTUSD", interval_min=1440,
                                       raw=FakeRaw(retrieved_at_ns=received), ingested_at=1)
        self.assertEqual(len(res.records), 3)
        self.assertEqual(res.records[0].fields["native_response_key"], "XXBTZUSD")
        self.assertEqual(res.records[0].native_symbol, "XBTUSD")
        self.assertEqual(["late" in r.quality_flags for r in res.records], [True, False, False])


class AnalysisTests(unittest.TestCase):
    def bars(self, days, closes=None):
        text = "\n".join(
            kline((DEC_2024 + d * DAY_S) * 1000, o=(closes or {}).get(d, "10"), h="2000", l="0.00001",
                  c=(closes or {}).get(d, "10")) for d in days) + "\n"
        return R.parse_binance_klines(text.encode(), name="X-1d-2024-12.csv", symbol="X", interval="1d",
                                      raw=FakeRaw(), ingested_at=1).records

    def test_epoch_break(self):  # S-10
        recs = self.bars([0, 1, 20], closes={0: "0.00005", 1: "0.00005", 20: "1"})
        eps = A.propose_epochs(recs)
        self.assertEqual(len(eps), 1)
        self.assertEqual(eps[0].review_status, "proposed")
        self.assertEqual(A.propose_epochs(self.bars([0, 1, 20])), [])  # gap without price jump

    def test_coverage_threshold(self):  # Q-4, F-18
        step = DAY_S * R.NS["s"]
        start = DEC_2024 * R.NS["s"]
        days = [d for d in range(365) if d >= 19]
        recs = self.bars(days)
        self.assertFalse(A.qualifies(recs, [], start, start + 365 * step, step))  # 346/365
        recs2 = self.bars([d for d in range(365) if d >= 18])
        self.assertTrue(A.qualifies(recs2, [], start, start + 365 * step, step))  # 347/365

    def test_as_of_and_revision(self):  # S-09, S-16
        old = self.bars([0, 1])
        new = self.bars([0, 1])
        for r in new:
            r.available_at = old[0].available_at + 10
            r.fields["close"] = "11"
        merged = A.apply_revision(old, new)
        before = A.as_of(merged, old[0].available_at)
        after = A.as_of(merged, old[0].available_at + 10)
        self.assertEqual({r.version for r in before}, {1})
        self.assertEqual({r.version for r in after}, {2})
        self.assertEqual(A.as_of(merged, old[0].available_at - 1), [])

    def test_determinism(self):  # CV-09: same raw input, same output
        self.assertEqual(A.output_hash(self.bars([0, 1, 2])), A.output_hash(self.bars([0, 1, 2])))

    def test_out_of_order_rows(self):  # S-08: reordered rows replay in event order
        order = [r.source_event_time for r in A.replay_order(self.bars([2, 0, 1]))]
        self.assertEqual(order, sorted(order))


class ReviewFixTests(unittest.TestCase):
    def test_revision_with_last_modified_takes_retrieval_time(self):  # H1, DEC-053
        lm = "Wed, 08 Jan 2025 00:50:27 GMT"
        text = month_klines(DEC_2024, 2).encode()
        v1 = R.parse_binance_klines(text, name="X-1d-2024-12.csv", symbol="X", interval="1d",
                                    raw=FakeRaw(last_modified=lm), ingested_at=1).records
        later = 2_100_000_000 * R.NS["s"]
        v2 = R.parse_binance_klines(text.replace(b",10.5,", b",10.6,"), name="X-1d-2024-12.csv", symbol="X",
                                    interval="1d", raw=FakeRaw("r2", later, lm, supersedes="r1"), ingested_at=1).records
        self.assertEqual((v2[0].available_at, v2[0].available_at_basis), (later, "retrieved"))
        self.assertIn("last_modified_after_period", v2[0].quality_flags)
        merged = A.apply_revision(v1, v2)
        self.assertEqual({r.version for r in A.as_of(merged, R.http_date_to_ns(lm))}, {1})
        self.assertEqual(v2[0].supersedes_record_id, v1[0].record_id)

    def test_bar_key_stable_when_rows_shift(self):  # M2
        old = R.parse_binance_klines(month_klines(DEC_2024 + DAY_S, 3).encode(), name="X-1d-2024-12.csv", symbol="X",
                                     interval="1d", raw=FakeRaw(), ingested_at=1).records
        new = R.parse_binance_klines(month_klines(DEC_2024, 4).encode(), name="X-1d-2024-12.csv", symbol="X",
                                     interval="1d", raw=FakeRaw("r2", supersedes="r1"), ingested_at=1).records
        merged = A.apply_revision(old, new)
        self.assertEqual(len(A.as_of(merged, 10**30)), 4)

    def test_zero_volume_decimal(self):  # L2
        self.assertTrue(R.is_zero("0E-8") and R.is_zero("0.000"))
        text = (kline(DEC_2024 * 1000, v="0.00") + "\n").encode()
        r = R.parse_binance_klines(text, name="X-1d-2024-12.csv", symbol="X", interval="1d", raw=FakeRaw(),
                                   ingested_at=1).records[0]
        self.assertIn("zero_volume", r.quality_flags)

    def test_trades_q1_and_duplicates(self):  # M5
        t = JAN_2025 * 1_000_000
        rows = [f"1,NaN,1,1,{t},True,True", f"2,1,1,1,{t + 1},True,True", f"2,1,1,1,{t + 2},True,True",
                f"x,1,1,1,{t + 3},True,True"]
        res = R.parse_binance_trades(("\n".join(rows) + "\n").encode(), name="E-trades-2025-01-15.csv", symbol="E",
                                     raw=FakeRaw(), ingested_at=1)
        self.assertEqual([r.reason for r in res.records],
                         ["nonfinite_or_invalid_number", "duplicate_conflicting", "duplicate_conflicting", "invalid_trade_id"])

    def test_checksum_checked_on_repeat(self):  # L3
        with tempfile.TemporaryDirectory() as d:
            store = RawStore(Path(d) / "s")
            f = Path(d) / "a"
            f.write_text("x")
            store.ingest_file(f, source_id="S", source_approval_id="A", request="u")
            again = store.ingest_file(f, source_id="S", source_approval_id="A", request="u", published_checksum="00" * 32)
            self.assertTrue(again.quarantined)

    def test_stale_and_entry_blocked(self):  # S-17, CV-06
        self.assertTrue(A.is_stale("cftc:cot", 0, 15 * 86_400 * R.NS["s"]))
        self.assertFalse(A.is_stale("cftc:cot", 0, 7 * 86_400 * R.NS["s"]))
        step = DAY_S * R.NS["s"]
        recs = AnalysisTests().bars(list(range(30)))
        start = DEC_2024 * R.NS["s"]
        gaps = [A.GapInterval("s", "f", "i", start + 29 * step, start + 30 * step, "status_unknown", "x", 0)]
        self.assertEqual(A.entry_blocked(recs, gaps, start + 29 * step, 20), "status_unknown_on_decision_day")
        self.assertEqual(A.entry_blocked(recs, [], start + 29 * step, 40), "coverage_below_q4")
        self.assertIsNone(A.entry_blocked(recs, [], start + 29 * step, 20))

    def test_qualifies_listing_partway(self):  # Q-4 listing clause
        step = DAY_S * R.NS["s"]
        start = DEC_2024 * R.NS["s"]
        recs = AnalysisTests().bars(list(range(10, 30)))
        self.assertFalse(A.qualifies(recs, [], start, start + 30 * step, step))
        self.assertTrue(A.qualifies(recs, [], start, start + 30 * step, step, listed_ns=start + 10 * step))
        self.assertFalse(A.qualifies(recs, [], start, start + 30 * step, step, listed_ns=start + 10 * step,
                                     min_training_intervals=25))


class FetchTests(unittest.TestCase):
    class T:
        def __init__(self, script):
            self.script, self.calls = list(script), 0

        def get(self, request):
            self.calls += 1
            x = self.script.pop(0)
            if isinstance(x, Exception):
                raise x
            return x

    def run_fetch(self, script, checksum=None):
        with tempfile.TemporaryDirectory() as d:
            store = RawStore(Path(d) / "s")
            tr = self.T(script)
            slept = []
            res = Fe.fetch("u", tr, store, source_id="S", source_approval_id="A", published_checksum=checksum,
                           sleep=slept.append)
            return res, tr.calls, slept

    def test_403_no_retry(self):  # RC-02, DEC-050
        res, calls, slept = self.run_fetch([Fe.Response(403)])
        self.assertEqual((res.raw, calls, res.gap.evidence, res.gap.availability_state),
                         (None, 1, "http_403", "SOURCE_UNAVAILABLE"))

    def test_retries_then_gives_up(self):  # RC-01
        res, calls, slept = self.run_fetch([Fe.Response(500)] * 4)
        self.assertEqual((calls, slept), (4, [30, 120, 600]))
        self.assertIsNone(res.raw)

    def test_429_retry_does_not_consume_retries(self):  # L-d
        res, calls, slept = self.run_fetch([Fe.Response(429, b"", {"Retry-After": "5"})] + [Fe.Response(500)] * 4)
        self.assertEqual((calls, slept), (5, [5, 30, 120, 600]))

    def test_default_sleep_is_real(self):  # N1
        import inspect
        self.assertIs(inspect.signature(Fe.fetch).parameters["sleep"].default, __import__("time").sleep)

    def test_429_and_truncation(self):  # RC-02 429, RC-03
        body = b"abc"
        ok = Fe.Response(200, body, {"Content-Length": "3"})
        res, calls, slept = self.run_fetch([Fe.Response(429, b"", {"Retry-After": "5"}), ok])
        self.assertEqual((res.raw is not None, slept), (True, [5]))
        res, calls, _ = self.run_fetch([Fe.Response(429, b"", {"Retry-After": "9999"})])
        self.assertEqual((res.raw, calls), (None, 1))
        res, calls, _ = self.run_fetch([Fe.Response(200, b"a", {"Content-Length": "3"}), ok])
        self.assertEqual((res.raw is not None, calls), (True, 2))


if __name__ == "__main__":
    unittest.main()
