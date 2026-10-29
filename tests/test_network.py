"""Offline tests for the network side (no network access)."""

import json
import sys
import tempfile
import unittest
import zlib
from decimal import Decimal
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from gladiator_capture import live as L  # noqa: E402
from gladiator_capture import ws as W  # noqa: E402
from gladiator_capture.fetch import Response  # noqa: E402
from gladiator_capture.rawstore import RawStore  # noqa: E402
from gladiator_capture import cli as C  # noqa: E402
from gladiator_capture import transport as T  # noqa: E402
from gladiator_capture.transport import Robots  # noqa: E402


class FrameTests(unittest.TestCase):
    def test_roundtrip_sizes(self):
        for n in (0, 5, 125, 126, 70000):
            payload = bytes(range(256)) * (n // 256) + bytes(n % 256)
            frame = W.encode_frame(payload, mask=True)
            buf = [frame]
            r = W.FrameReader(lambda k: buf.pop(0) if buf else b"", allow_masked=True)
            fin, op, data = r.frame()
            self.assertEqual((fin, op, data), (True, 1, payload))

    def test_fragmented(self):
        f1 = bytes([0x01, 3]) + b"abc"  # text, not final, unmasked
        f2 = bytes([0x80, 3]) + b"def"  # continuation, final
        ws = W.WebSocket.__new__(W.WebSocket)
        buf = [f1 + f2]
        ws.reader = W.FrameReader(lambda k: buf.pop(0) if buf else b"")
        ws.sock = None
        self.assertEqual(ws.recv_text(), "abcdef")


class ChecksumTests(unittest.TestCase):
    def test_format_and_order(self):
        asks = {Decimal("50000.1"): Decimal("0.5"), Decimal("50000.2"): Decimal("1")}
        bids = {Decimal("49999.9"): Decimal("2"), Decimal("49999.8"): Decimal("0.00000001")}
        s = "500001" + "50000000" + "500002" + "100000000" + "499999" + "200000000" + "499998" + "1"
        self.assertEqual(L.book_checksum(asks, bids, 1, 8), zlib.crc32(s.encode()) & 0xFFFFFFFF)


class FakeWS:
    def __init__(self, frames):
        self.frames = list(frames)
        self.sent = []

    def send_text(self, t):
        self.sent.append(json.loads(t))

    def recv_text(self):
        if not self.frames:
            raise W.WebSocketClosed("end")
        return self.frames.pop(0)

    def settimeout(self, t):
        pass

    def close(self):
        pass


class CaptureTests(unittest.TestCase):
    def frames(self, bad_update=False):
        bids = {Decimal("100.0"): Decimal("1")}
        asks = {Decimal("101.0"): Decimal("2")}
        snap_ck = L.book_checksum(asks, bids, 1, 8)
        snap = {"channel": "book", "type": "snapshot", "data": [{"symbol": "BTC/USD", "bids": [{"price": 100.0, "qty": 1}],
                                                                "asks": [{"price": 101.0, "qty": 2}], "checksum": snap_ck}]}
        asks2 = {Decimal("101.0"): Decimal("3")}
        upd_ck = L.book_checksum(asks2, bids, 1, 8) ^ (1 if bad_update else 0)
        upd = {"channel": "book", "type": "update", "data": [{"symbol": "BTC/USD", "bids": [], "asks": [{"price": 101.0, "qty": 3}],
                                                              "checksum": upd_ck, "timestamp": "2026-10-28T00:00:00.000000Z"}]}
        trade = {"channel": "trade", "type": "update", "data": [{"symbol": "BTC/USD", "side": "buy", "price": 101.0, "qty": 0.1,
                                                                 "ord_type": "market", "trade_id": 1,
                                                                 "timestamp": "2026-10-28T00:00:00.000000Z"}]}
        return [json.dumps(x) for x in (snap, upd, trade)]

    def run_capture(self, frames):
        t = [1_793_145_600_000_000_000]  # 2026-10-28T00:00:00Z

        def clock():
            t[0] += 10_000_000  # 10 ms per call
            return t[0]

        fake = FakeWS(frames)
        with tempfile.TemporaryDirectory() as d:
            cap = L.Capture(Path(d), ["BTC/USD"], {"BTC/USD": (1, 8)}, duration_s=5, connect=lambda url: fake,
                            clock=clock, sleep=lambda s: None, ntp=lambda: 1.5, monotonic=clock)
            summary = cap.run()
            lines = [l for f in sorted(Path(d).glob("frames-*.jsonl")) for l in f.read_text().splitlines()]
            self.cap = cap
        return summary, fake, lines

    def test_good_book(self):
        summary, fake, lines = self.run_capture(self.frames())
        self.assertEqual((summary["checksum_ok"], summary["checksum_fail"], summary["trades"]), (2, 0, 1))
        self.assertEqual(len(lines), 3)  # every frame journalled before parsing
        self.assertEqual({m["params"]["channel"] for m in fake.sent}, {"book", "trade"})
        self.assertEqual(len(self.cap.segments), 1)  # the segment was ingested as a raw object

    def test_checksum_failure_resubscribes(self):  # S-15, Q-5
        summary, fake, _ = self.run_capture(self.frames(bad_update=True))
        self.assertEqual((summary["checksum_fail"], summary["resyncs"]), (1, 1))
        self.assertIn("unsubscribe", [m["method"] for m in fake.sent])


class RobotsTests(unittest.TestCase):
    def test_404_allows_and_disallow_respected(self):
        class T:
            def __init__(self, m):
                pass

            def get(self, url):
                if "a.example" in url:
                    return Response(404)
                return Response(200, b"User-agent: *\nDisallow: /private/\n")

        with tempfile.TemporaryDirectory() as d:
            r = Robots(RawStore(Path(d) / "s"), transport_factory=T)
            self.assertEqual(r.allowed("https://a.example/x")[0], True)
            self.assertEqual(r.allowed("https://b.example/private/x")[0], False)
            self.assertEqual(r.allowed("https://b.example/public/x")[0], True)


class MoreWsTests(unittest.TestCase):
    def ws_with(self, data):
        ws = W.WebSocket.__new__(W.WebSocket)
        buf = [data]
        ws.reader = W.FrameReader(lambda k: buf.pop(0) if buf else b"")
        sent = []

        class Sock:
            def sendall(self, b):
                sent.append(b)
        ws.sock = Sock()
        return ws, sent

    def test_ping_answered_then_text(self):
        ws, sent = self.ws_with(bytes([0x89, 2]) + b"hi" + bytes([0x81, 2]) + b"ok")
        self.assertEqual(ws.recv_text(), "ok")
        self.assertEqual(sent[0][0] & 0x0F, 0xA)  # pong

    def test_close_answered(self):
        ws, sent = self.ws_with(bytes([0x88, 2]) + b"\x03\xe8")
        with self.assertRaises(W.WebSocketClosed):
            ws.recv_text()
        self.assertEqual(sent[0][0] & 0x0F, 0x8)

    def test_masked_server_frame_and_rsv_rejected(self):
        for data in (W.encode_frame(b"x", mask=True), bytes([0xC1, 1]) + b"x"):
            ws, _ = self.ws_with(data)
            with self.assertRaises(W.WebSocketClosed):
                ws.recv_text()


class MoreCaptureTests(CaptureTests):
    def test_unknown_symbol_and_parse_error_continue(self):
        frames = self.frames()
        frames.insert(1, json.dumps({"channel": "book", "type": "update", "data": [{"symbol": "XRP/USD", "checksum": 1}]}))
        frames.insert(2, "not json")
        summary, _, lines = self.run_capture(frames)
        self.assertEqual((summary["parse_errors"], summary["checksum_ok"]), (1, 2))
        self.assertEqual(len(lines), 5)

    def test_malformed_update_invalidates_and_resyncs(self):  # Q-5 / S-15 (Codex review of PR #30)
        frames = self.frames()
        bad = {"channel": "book", "type": "update", "data": [{"symbol": "BTC/USD", "bids": [{"price": 100.0, "qty": 9}],
                                                              "asks": []}]}  # quantity changed, no checksum
        frames.insert(1, json.dumps(bad))
        summary, fake, _ = self.run_capture(frames)
        self.assertEqual((summary["parse_errors"], summary["resyncs"]), (1, 1))
        self.assertIn("unsubscribe", [m["method"] for m in fake.sent])
        # the following good update is not accepted on the unverified book
        self.assertEqual((summary["checksum_ok"], summary["checksum_fail"]), (1, 0))

    def test_malformed_snapshot_and_resync_cap(self):  # parse errors share the S-15 resync cap
        frames = self.frames()
        bad_snap = json.dumps({"channel": "book", "type": "snapshot", "data": [{"symbol": "BTC/USD", "bids": [], "asks": []}]})
        summary, fake, _ = self.run_capture([frames[0]] + [bad_snap] * (L.RESYNC_MAX_PER_MIN + 2) + frames)  # synced first
        self.assertEqual(summary["parse_errors"], L.RESYNC_MAX_PER_MIN + 2)
        self.assertEqual((summary["resyncs"], summary["resync_capped"]), (L.RESYNC_MAX_PER_MIN, 2))
        self.assertEqual(summary["recovery_parse_error_s"]["n"], 1)  # recovered on the good snapshot

    def test_updates_skipped_until_snapshot(self):
        frames = self.frames()
        summary, _, _ = self.run_capture([frames[1]] + frames)  # update before any snapshot
        self.assertEqual((summary["checksum_ok"], summary["checksum_fail"]), (2, 0))

    def test_resync_cap(self):
        snap, bad = self.frames(bad_update=True)[:2]
        frames = [snap] + [x for _ in range(L.RESYNC_MAX_PER_MIN + 2) for x in (bad, snap)]
        summary, _, _ = self.run_capture(frames)
        self.assertEqual(summary["resyncs"], L.RESYNC_MAX_PER_MIN)
        self.assertGreater(summary["resync_capped"], 0)

    def test_maintenance_tracked(self):
        st = lambda s: json.dumps({"channel": "status", "type": "update", "data": [{"system": s}]})
        frames = self.frames()
        summary, _, _ = self.run_capture([frames[0], st("maintenance"), st("maintenance"), st("online")] + frames[1:])
        self.assertGreater(summary["maintenance_s"], 0)

    def test_maintenance_invalid_time_excluded(self):  # R-4 / RC-11
        st = lambda s: json.dumps({"channel": "status", "type": "update", "data": [{"system": s}]})
        frames = self.frames()
        summary, _, _ = self.run_capture([st("maintenance")] + frames[:1] + [st("online")] + frames[1:])
        self.assertGreater(summary["invalid_in_maintenance_s"]["BTC/USD"], 0)
        self.assertGreater(summary["maintenance_s"], 0)

    def test_redirect_terminal_in_fetch(self):
        from gladiator_capture import fetch as Fe
        with tempfile.TemporaryDirectory() as d:
            store = RawStore(Path(d) / "s")
            calls = []

            class Tr:
                def get(self, u):
                    calls.append(u)
                    return Response(302, b"", {"Location": "http://x"})
            r = Fe.fetch("u", Tr(), store, source_id="S", source_approval_id="A", sleep=lambda s: None)
            self.assertEqual((len(calls), r.gap.evidence), (1, "http_302"))

    def test_backoff_resets_only_after_valid_book(self):
        sleeps = []
        conns = [0]

        def connect(url):
            conns[0] += 1
            raise ConnectionError("refused")

        t = [0]

        def clock():
            t[0] += 1_000_000_000
            return t[0]

        with tempfile.TemporaryDirectory() as d:
            cap = L.Capture(Path(d), ["BTC/USD"], {"BTC/USD": (1, 8)}, duration_s=60, connect=connect, clock=clock,
                            sleep=sleeps.append, ntp=lambda: None, monotonic=clock)
            cap.run()
        bases = [L.RECONNECT_DELAYS_S[min(i, len(L.RECONNECT_DELAYS_S) - 1)] for i in range(len(sleeps))]
        self.assertGreater(len(sleeps), 2)
        self.assertTrue(all(b <= s <= b * 1.25 for s, b in zip(sleeps, bases)))  # backoff never reset without a valid book


class TransportTests(unittest.TestCase):
    def test_redirects_not_followed(self):
        self.assertIsNone(T._NoRedirect().redirect_request(None, None, 302, "Found", {}, "http://evil.example/"))

    def test_incomplete_read_becomes_connection_error(self):
        import http.client

        class R:
            status = 200
            headers = {}

            def __enter__(self):
                return self

            def __exit__(self, *a):
                return False

            def read(self):
                raise http.client.IncompleteRead(b"ab", 10)

        orig = T._OPENER
        T._OPENER = type("O", (), {"open": lambda self, req, timeout: R()})()
        try:
            with self.assertRaises(ConnectionError):
                T.HttpsTransport().get("https://example.invalid/x")
        finally:
            T._OPENER = orig

    def test_https_only(self):
        with self.assertRaises(ValueError):
            T.HttpsTransport().get("http://example.invalid/")

    def test_robots_unreachable_blocks(self):
        class Bad:
            def __init__(self, m):
                pass

            def get(self, url):
                raise ConnectionError("down")

        with tempfile.TemporaryDirectory() as d:
            r = Robots(RawStore(Path(d) / "s"), transport_factory=Bad)
            self.assertEqual(r.allowed("https://x.example/a"), (False, "robots_unreachable"))


class CliTests(unittest.TestCase):
    def test_daily_self_stop(self):
        with tempfile.TemporaryDirectory() as d:
            out = Path(d)
            (out / "started_utc.txt").write_text("2000-01-01")
            self.assertIn("stopped", C.cmd_daily(out))

    def test_out_guard(self):
        repo = Path(C.__file__).resolve().parents[2]
        with self.assertRaises(SystemExit):
            C.main(["daily", "--out", str(repo / "tmp-out")])


if __name__ == "__main__":
    unittest.main()
