"""Offline tests for book validity, venue status and maintenance records (TASK-P02-014, DEC-075)."""

import json
import sys
import tempfile
import unittest
from datetime import datetime, timezone
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from gladiator_capture import live_validity as V  # noqa: E402

S = 10**9
T0 = 1_800_000_000 * S  # 2027-01-15T08:00:00Z
SYMS = ["BTC/USD", "ETH/USD"]


def ts(ns):
    return datetime.fromtimestamp(ns / 1e9, timezone.utc).strftime("%Y-%m-%dT%H:%M:%S.%fZ")


def status(cid=111, system="online", maint=None, **extra):
    d = {"version": "2.0.10", "system": system, "api_version": "v2", "connection_id": cid,
         "upcoming_maintenance": [] if maint is None else maint, "emergency": []}
    d.update(extra)
    return json.dumps({"channel": "status", "type": "update", "data": [d]})


def snap(*syms):
    return json.dumps({"channel": "book", "type": "snapshot",
                       "data": [{"symbol": s, "bids": [], "asks": [], "checksum": 1} for s in syms]})


def upd(sym):
    return json.dumps({"channel": "book", "type": "update",
                       "data": [{"symbol": sym, "bids": [], "asks": [], "checksum": 1, "timestamp": ts(T0)}]})


HB = json.dumps({"channel": "heartbeat"})
TRADE = json.dumps({"channel": "trade", "type": "update", "data": [{"symbol": "BTC/USD", "price": 1.5}]})


def item(eid, a, b, services=("spot_ws",), title="WS maintenance"):
    d = {"event_id": eid, "title": title, "expected_start_utc": ts(a), "expected_end_utc": ts(b)}
    if services is not None:
        d["affected_services"] = list(services)
    return d


def frames(seq):
    """(t_offset_ns, text) -> derive input with synthetic raw ids."""
    return [(T0 + t, text, "raw-a", f"line:{i}") for i, (t, text) in enumerate(seq)]


def derive(seq, symbols=SYMS):
    return V.derive_live_validity(frames(seq), symbols)


def ivs(res, sym="BTC/USD"):
    return [(g.interval_start - T0, g.interval_end - T0, g.evidence, g.available_at - T0) for g in res.gaps[sym]]


def healthy(t=0, cid=111):
    """A connection's opening: status, both snapshots."""
    return [(t, status(cid)), (t + 1, snap("BTC/USD")), (t + 2, snap("ETH/USD"))]


class TestStart(unittest.TestCase):
    def test_a_initial_sync_until_each_pairs_first_snapshot(self):
        res = derive([(0, status()), (5, HB), (10, snap("BTC/USD")), (20, snap("ETH/USD")), (30, upd("BTC/USD"))])
        self.assertEqual(ivs(res), [(0, 10, "start", 10)])
        self.assertEqual(ivs(res, "ETH/USD"), [(0, 20, "start", 20)])

    def test_a_snapshot_for_other_symbols_does_not_close(self):
        res = derive([(0, status()), (10, snap("XRP/USD")), (20, snap("BTC/USD", "ETH/USD"))])
        self.assertEqual(ivs(res), [(0, 20, "start", 20)])
        self.assertEqual(ivs(res, "ETH/USD"), [(0, 20, "start", 20)])
        self.assertEqual(res.gaps["BTC/USD"][0].instrument_id, "kraken:BTC/USD:1")
        g = res.gaps["BTC/USD"][0]
        self.assertEqual((g.source_id, g.feed_id, g.gap_class, g.availability_state),
                         ("SR-02", "kraken:ws2:book", "data_gap", "SOURCE_UNAVAILABLE"))

    def test_update_does_not_close_start(self):
        res = derive([(0, status()), (10, upd("BTC/USD")), (20, snap("BTC/USD")), (30, snap("ETH/USD"))])
        self.assertEqual(ivs(res), [(0, 20, "start", 20)])


class TestSilence(unittest.TestCase):
    def test_b_silence_over_15s_any_channel(self):
        seq = healthy() + [(10 * S, TRADE), (10 * S + 15 * S + 1, HB), (40 * S, HB)]
        res = derive(seq)
        self.assertEqual(ivs(res)[1:], [(10 * S, 25 * S + 1, "silence>15s", 25 * S + 1)])
        self.assertEqual(ivs(res, "ETH/USD")[1:], [(10 * S, 25 * S + 1, "silence>15s", 25 * S + 1)])

    def test_b_silence_of_exactly_15s_is_not_a_gap(self):
        seq = healthy() + [(10 * S, HB), (25 * S, HB)]
        self.assertEqual(ivs(derive(seq)), [(0, 1, "start", 1)])

    def test_b_silence_through_unparseable_frames_counts_them(self):
        seq = healthy() + [(10 * S, "not json"), (20 * S, "{bad"), (30 * S, HB)]
        self.assertEqual(ivs(derive(seq)), [(0, 1, "start", 1)])


class TestReconnect(unittest.TestCase):
    def test_c_reconnect_without_silence(self):
        seq = healthy() + [(5 * S, upd("BTC/USD")), (6 * S, HB), (7 * S, status(222)), (8 * S, snap("BTC/USD")),
                           (9 * S, snap("ETH/USD"))]
        res = derive(seq)
        self.assertEqual(ivs(res)[1:], [(6 * S, 8 * S, "reconnect", 8 * S)])
        self.assertEqual(ivs(res, "ETH/USD")[1:], [(6 * S, 9 * S, "reconnect", 9 * S)])

    def test_c_same_connection_id_is_not_a_reconnect(self):
        seq = healthy() + [(5 * S, status(111, system="online")), (6 * S, HB)]
        self.assertEqual(ivs(derive(seq)), [(0, 1, "start", 1)])

    def test_c_first_status_is_not_a_reconnect(self):
        res = derive([(0, HB), (1, status(5)), (2, snap("BTC/USD", "ETH/USD"))])
        self.assertEqual(ivs(res), [(0, 2, "start", 2)])

    def test_c_reconnect_after_silence_merges(self):
        seq = healthy() + [(10 * S, HB), (40 * S, status(222)), (41 * S, snap("BTC/USD")), (42 * S, snap("ETH/USD"))]
        res = derive(seq)
        self.assertEqual(ivs(res)[1:], [(10 * S, 41 * S, "silence>15s+reconnect", 41 * S)])

    def test_c_reconnect_does_not_need_updates_to_end(self):
        seq = healthy() + [(5 * S, status(222)), (6 * S, upd("BTC/USD")), (7 * S, upd("BTC/USD")), (8 * S, snap("BTC/USD"))]
        res = derive(seq)
        self.assertEqual(ivs(res)[1:], [(2, 8 * S, "reconnect", 8 * S)])


class TestResync(unittest.TestCase):
    def test_d_resync_without_reconnect(self):
        seq = healthy() + [(5 * S, upd("BTC/USD")), (6 * S, upd("ETH/USD")), (7 * S, HB), (8 * S, snap("BTC/USD")),
                           (9 * S, upd("BTC/USD"))]
        res = derive(seq)
        self.assertEqual(ivs(res)[1:], [(5 * S, 8 * S, "resync", 8 * S)])
        self.assertEqual(ivs(res, "ETH/USD"), [(0, 2, "start", 2)])

    def test_d_first_snapshot_after_reconnect_is_not_a_resync(self):
        seq = healthy() + [(5 * S, upd("BTC/USD")), (6 * S, status(222)), (8 * S, snap("BTC/USD"))]
        self.assertEqual(ivs(derive(seq))[1:], [(5 * S, 8 * S, "reconnect", 8 * S)])

    def test_d_second_resync_starts_at_last_book_frame(self):
        seq = healthy() + [(5 * S, snap("BTC/USD")), (6 * S, upd("BTC/USD")), (9 * S, snap("BTC/USD"))]
        # the first resync starts at the opening snapshot, so it joins the start interval
        self.assertEqual(ivs(derive(seq)), [(0, 5 * S, "start+resync", 5 * S), (6 * S, 9 * S, "resync", 9 * S)])


class TestOpenEnd(unittest.TestCase):
    def test_e_open_at_end_after_reconnect(self):
        seq = healthy() + [(5 * S, HB), (6 * S, status(222)), (8 * S, snap("ETH/USD")), (10 * S, HB)]
        res = derive(seq)
        self.assertEqual(ivs(res)[1:], [(5 * S, 10 * S, "reconnect+open_at_end", 10 * S)])
        self.assertEqual(ivs(res, "ETH/USD")[1:], [(5 * S, 8 * S, "reconnect", 8 * S)])

    def test_e_never_synced(self):
        res = derive([(0, status()), (3 * S, HB)])
        self.assertEqual(ivs(res), [(0, 3 * S, "start+open_at_end", 3 * S)])


class TestMerging(unittest.TestCase):
    def test_merge_merges_adjacent_and_keeps_separate(self):
        raw = [(10, 20, {"resync"}, 20), (20, 30, {"silence>15s"}, 30), (31, 40, {"resync"}, 40),
               (35, 38, {"reconnect"}, 38), (5, 5, {"start"}, 5)]
        self.assertEqual(V.merge_intervals(raw), [[10, 30, {"resync", "silence>15s"}, 30],
                                                  [31, 40, {"resync", "reconnect"}, 40]])

    def test_adjacent_resync_and_silence_merge(self):
        # a resync closes at the snapshot; the frame after it then ends a silence that starts there
        seq = healthy() + [(5 * S, upd("BTC/USD")), (8 * S, snap("BTC/USD")), (30 * S, HB)]
        res = derive(seq)
        self.assertEqual(ivs(res)[1:], [(5 * S, 30 * S, "silence>15s+resync", 30 * S)])

    def test_overlapping_reconnect_and_silence(self):
        seq = healthy() + [(4 * S, HB), (20 * S, HB), (21 * S, status(9)), (22 * S, snap("BTC/USD", "ETH/USD"))]
        res = derive(seq)
        self.assertEqual(ivs(res)[1:], [(4 * S, 22 * S, "silence>15s+reconnect", 22 * S)])

    def test_start_and_silence_merge(self):
        res = derive([(0, status()), (20 * S, HB), (21 * S, snap("BTC/USD", "ETH/USD"))])
        self.assertEqual(ivs(res), [(0, 21 * S, "start+silence>15s", 21 * S)])


class TestVenueStatus(unittest.TestCase):
    def test_one_record_per_status_frame_with_exact_numbers(self):
        cid = 3088306452635049563
        m = [item(61, T0 + 100 * S, T0 + 200 * S)]
        res = derive([(0, status(cid, maint=m)), (1, HB), (2, status(cid, system="maintenance"))])
        self.assertEqual(len(res.venue_status), 2)
        r = res.venue_status[0]
        self.assertEqual((r.record_type, r.feed_id, r.source_id, r.rights_id, r.venue), ("VenueStatus", "kraken:ws2:status",
                                                                                         "SR-02", "SA-03", "kraken"))
        self.assertEqual((r.available_at, r.received_at, r.available_at_basis), (T0, T0, "live_receive"))
        self.assertEqual((r.native_seq, r.raw_id, r.raw_locator), (T0 * 100, "raw-a", "line:0#data[0]"))
        self.assertEqual(r.fields, {"system": "online", "api_version": "v2", "connection_id": str(cid),
                                    "version": "2.0.10", "upcoming_maintenance": [dict(m[0], event_id="61")]})
        self.assertEqual(r.source_event_time, T0 // 1000)
        self.assertIn("source_time_is_receive_time", r.quality_flags)
        self.assertEqual(res.venue_status[1].fields["system"], "maintenance")
        self.assertEqual(res.venue_status[1].raw_locator, "line:2#data[0]")

    def test_multi_item_status_frame_gives_distinct_keys(self):
        text = json.dumps({"channel": "status", "type": "update",
                           "data": [{"system": "online", "connection_id": 1}, {"system": "online", "connection_id": 1}]})
        res = derive([(0, text)])
        self.assertEqual([r.native_seq for r in res.venue_status], [T0 * 100, T0 * 100 + 1])
        self.assertEqual([r.raw_locator for r in res.venue_status], ["line:0#data[0]", "line:0#data[1]"])
        self.assertEqual(len({r.record_id for r in res.venue_status}), 2)

    def test_status_without_connection_id_is_not_a_reconnect(self):
        no_id = json.dumps({"channel": "status", "type": "update", "data": [{"system": "online"}]})
        seq = healthy() + [(10 * S, no_id), (20 * S, status(111)), (30 * S, upd("BTC/USD")),
                           (40 * S, status(222)), (41 * S, snap("BTC/USD"))]
        self.assertEqual(ivs(res := derive(seq)), [(0, 1, "start", 1), (30 * S, 41 * S, "reconnect", 41 * S)])
        self.assertEqual(len(res.venue_status), 4)

    def test_non_dict_status_items_skipped(self):
        text = json.dumps({"channel": "status", "type": "update", "data": ["x", {"system": "online", "connection_id": 1}]})
        res = derive([(0, text)])
        self.assertEqual([r.raw_locator for r in res.venue_status], ["line:0#data[1]"])

    def test_two_reconnects_before_a_snapshot_keep_the_earliest_start(self):
        seq = healthy() + [(10 * S, upd("BTC/USD")), (20 * S, status(222)), (21 * S, upd("ETH/USD")),
                           (30 * S, status(333)), (31 * S, snap("BTC/USD"))]
        self.assertEqual(ivs(derive(seq))[-1], (10 * S, 31 * S, "reconnect", 31 * S))

    def test_reconnect_during_start_interval_keeps_start(self):
        seq = [(0, status(111)), (5 * S, status(222)), (6 * S, snap("BTC/USD"))]
        self.assertEqual(ivs(derive(seq)), [(0, 6 * S, "start+reconnect", 6 * S)])

    def test_non_status_frames_give_no_status_records(self):
        res = derive(healthy()[1:] + [(5, HB), (6, json.dumps({"method": "subscribe", "result": {"channel": "status"}}))])
        self.assertEqual(res.venue_status, [])

    def test_upcoming_maintenance_numbers_kept_as_text(self):
        text = ('{"channel":"status","type":"update","data":[{"system":"online","connection_id":1,'
                '"upcoming_maintenance":[{"event_id":7,"title":"x","expected_start_utc":"%s",'
                '"expected_end_utc":"%s","weight":1.50}]}]}' % (ts(T0 + S), ts(T0 + 2 * S)))
        res = derive([(0, text)])
        r = res.venue_status[0]
        self.assertEqual(res.maintenance[0].event_id, 7)  # windows use the parsed id, as the analysis does
        self.assertEqual(r.fields["upcoming_maintenance"][0]["event_id"], "7")
        self.assertEqual(r.fields["upcoming_maintenance"][0]["weight"], "1.50")


class TestMaintenance(unittest.TestCase):
    def test_status_maintenance_period(self):
        seq = healthy() + [(10 * S, status(111, system="maintenance")), (20 * S, status(111, system="cancel_only")),
                           (30 * S, status(111, system="online"))]
        res = derive(seq)
        w = [m for m in res.maintenance if m.source == "status"]
        self.assertEqual(len(w), 1)
        self.assertEqual((w[0].excluded_start - T0, w[0].excluded_end - T0, w[0].available_at - T0, w[0].withdrawn,
                          w[0].open_at_end), (10 * S, 20 * S, 20 * S, False, False))

    def test_status_maintenance_open_at_end(self):
        res = derive(healthy() + [(10 * S, status(111, system="maintenance")), (12 * S, HB)])
        w = [m for m in res.maintenance if m.source == "status"]
        self.assertEqual((w[0].excluded_start - T0, w[0].excluded_end - T0, w[0].open_at_end), (10 * S, 12 * S, True))

    def test_maintenance_is_not_book_invalidity(self):
        res = derive(healthy() + [(10 * S, status(111, system="maintenance")), (12 * S, upd("BTC/USD")),
                                  (14 * S, status(111))])
        self.assertEqual(ivs(res), [(0, 1, "start", 1)])

    def test_announced_spot_ws_counted_in_full(self):
        a, b = T0 + 100 * S, T0 + 200 * S
        seq = [(0, status(maint=[item(55, a, b)])), (150 * S, status(maint=[]))]  # unlisted after its start
        res = derive(seq)
        w = [m for m in res.maintenance if m.source == "announced"]
        self.assertEqual(len(w), 1)
        m = w[0]
        self.assertEqual((m.event_id, m.announced_start, m.announced_end, m.excluded_start, m.excluded_end),
                         (55, a, b, a, b))
        self.assertEqual((m.first_listed, m.unlisted_at, m.withdrawn, m.available_at, m.open_at_end),
                         (T0, T0 + 150 * S, False, T0 + 150 * S, False))
        self.assertEqual(m.title, "WS maintenance")

    def test_announced_item_unlisted_before_start_is_withdrawn(self):
        a, b = T0 + 100 * S, T0 + 200 * S
        res = derive([(0, status(maint=[item(61, a, b)])), (50 * S, status(maint=[]))])
        m = [m for m in res.maintenance if m.source == "announced"][0]
        self.assertTrue(m.withdrawn)
        self.assertIsNone(m.excluded_start)
        self.assertIsNone(m.excluded_end)
        self.assertEqual((m.announced_start, m.unlisted_at), (a, T0 + 50 * S))
        self.assertEqual(m.available_at, T0 + 50 * S)  # the withdrawal is not visible before it happens

    def test_announced_item_still_listed_at_end_is_available_there(self):
        a, b = T0 + 100 * S, T0 + 200 * S
        res = derive([(0, status(maint=[item(70, a, b)])), (30 * S, HB)])
        m = [m for m in res.maintenance if m.source == "announced"][0]
        self.assertEqual((m.unlisted_at, m.available_at - T0, m.open_at_end), (None, 30 * S, True))

    def test_announced_non_spot_ws_ignored_and_no_services_kept(self):
        a, b = T0 + 100 * S, T0 + 200 * S
        res = derive([(0, status(maint=[item(1, a, b, services=("rest_api",)), item(2, a, b, services=None)]))])
        self.assertEqual([m.event_id for m in res.maintenance], [2])

    def test_windows_sorted_by_start(self):
        res = derive([(0, status(maint=[item(2, T0 + 300 * S, T0 + 400 * S), item(1, T0 + 100 * S, T0 + 200 * S)])),
                      (10 * S, status(system="maintenance")), (20 * S, status())])
        self.assertEqual([(m.source, m.event_id) for m in res.maintenance],
                         [("status", None), ("announced", 1), ("announced", 2)])


class TestRunDirectory(unittest.TestCase):
    def test_segments_read_in_numeric_order_and_raw_ids(self):
        with tempfile.TemporaryDirectory() as d:
            run = Path(d)
            early, late = 9990, 100000  # "frames-100000" sorts before "frames-999" as text
            self.assertLess(f"frames-{late}.jsonl", f"frames-{early // 10}.jsonl")
            # names chosen so lexical order differs from numeric order
            (run / f"frames-{late}.jsonl").write_text(
                "".join(json.dumps({"recv_ns": T0 + t, "frame": f}) + "\n" for t, f in
                        [(30 * S, status(222)), (31 * S, snap("BTC/USD", "ETH/USD"))]) + '{"recv_ns": 1')
            (run / f"frames-{early // 10}.jsonl").write_text(
                "".join(json.dumps({"recv_ns": T0 + t, "frame": f}) + "\n" for t, f in
                        [(0, status(111)), (1, snap("BTC/USD", "ETH/USD")), (10 * S, HB), (20 * S, HB)]))
            (run / "store").mkdir()
            (run / "store" / "index.jsonl").write_text(json.dumps(
                {"raw_id": "abc", "request": f"wss://ws.kraken.com/v2#segment:frames-{early // 10}.jsonl",
                 "member_path": None}) + "\n")
            bad = []
            fr = list(V.run_frames(run, bad))
            self.assertEqual([f[0] - T0 for f in fr], [0, 1, 10 * S, 20 * S, 30 * S, 31 * S])
            self.assertEqual(fr[0][2:], ("abc", "line:0"))
            self.assertEqual(fr[4][2:], (f"unindexed:frames-{late}.jsonl", "line:0"))
            self.assertEqual(bad, [f"frames-{late}.jsonl:2"])
            res = V.derive_live_validity(fr, SYMS)
            self.assertEqual(ivs(res), [(0, 1, "start", 1), (20 * S, 31 * S, "reconnect", 31 * S)])
            self.assertEqual(res.venue_status[1].raw_id, f"unindexed:frames-{late}.jsonl")
            self.assertEqual((res.frames, res.first_recv, res.last_recv), (6, T0, T0 + 31 * S))


class TestDeterminism(unittest.TestCase):
    def seq(self):
        m = [item(55, T0 + 100 * S, T0 + 200 * S), item(61, T0 + 300 * S, T0 + 400 * S)]
        return healthy() + [(5 * S, status(111, maint=m)), (6 * S, upd("BTC/USD")), (8 * S, snap("BTC/USD")),
                            (30 * S, HB), (31 * S, status(222, maint=m[:1])), (32 * S, snap("ETH/USD")),
                            (150 * S, status(222, system="maintenance")), (160 * S, status(222))]

    def dump(self, res):
        return json.dumps({"vs": [r.to_json(include_clock=False) for r in res.venue_status],
                           "gaps": {s: [g.__dict__ for g in gs] for s, gs in res.gaps.items()},
                           "maint": [m.__dict__ for m in res.maintenance]}, sort_keys=True)

    def test_same_frames_same_output(self):
        a = V.derive_live_validity(frames(self.seq()), SYMS, ingested_at=1)
        b = V.derive_live_validity(iter(frames(self.seq())), SYMS, ingested_at=2)
        self.assertEqual(self.dump(a), self.dump(b))
        self.assertEqual([r.record_id for r in a.venue_status], [r.record_id for r in b.venue_status])
        self.assertEqual(ivs(a), [(0, 1, "start", 1),
                                  (6 * S, 160 * S, "silence>15s+reconnect+resync+open_at_end", 160 * S)])
        self.assertEqual(ivs(a, "ETH/USD"), [(0, 2, "start", 2), (8 * S, 150 * S, "silence>15s+reconnect", 150 * S)])
        self.assertEqual(len({r.native_seq for r in a.venue_status}), len(a.venue_status))


if __name__ == "__main__":
    unittest.main()
