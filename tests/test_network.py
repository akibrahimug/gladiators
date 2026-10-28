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
from gladiator_capture.transport import Robots  # noqa: E402


class FrameTests(unittest.TestCase):
    def test_roundtrip_sizes(self):
        for n in (0, 5, 125, 126, 70000):
            payload = bytes(range(256)) * (n // 256) + bytes(n % 256)
            frame = W.encode_frame(payload, mask=True)
            buf = [frame]
            r = W.FrameReader(lambda k: buf.pop(0) if buf else b"")
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
            cap = L.Capture(Path(d), ["BTC/USD"], {"BTC/USD": (1, 8)}, duration_s=0.5, connect=lambda url: fake,
                            clock=clock, sleep=lambda s: None, ntp=lambda: 1.5)
            summary = cap.run()
            lines = (Path(d) / "frames.jsonl").read_text().splitlines()
        return summary, fake, lines

    def test_good_book(self):
        summary, fake, lines = self.run_capture(self.frames())
        self.assertEqual((summary["checksum_ok"], summary["checksum_fail"], summary["trades"]), (2, 0, 1))
        self.assertEqual(len(lines), 3)  # every frame journalled before parsing
        self.assertEqual({m["params"]["channel"] for m in fake.sent}, {"status", "book", "trade"})

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


if __name__ == "__main__":
    unittest.main()
