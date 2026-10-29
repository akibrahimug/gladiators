"""Command-line entry points for the DEC-057 retrievals (DEC-062). Run through capture.py with -I.

  head   --out DIR                 18 Binance HEAD requests for the W-A files
  live   --out DIR --seconds N     Kraken WebSocket v2 capture (W-J): BTC/USD and ETH/USD, book depth 10 + trade
  daily  --out DIR                 one day of the 30-day Kraken REST pull (DEC-061); stops itself after 30 days
"""

from __future__ import annotations

import argparse
import json
import sys
import time
from datetime import datetime, timezone
from pathlib import Path

from . import fetch as F
from . import live as L
from .rawstore import RawStore
from .transport import HttpsTransport, Robots, head_capture, polite_pause

BINANCE = "https://data.binance.vision/data/spot/monthly/klines/{s}/1d/{s}-1d-{m}.zip"
SYMBOLS = ["BTCUSDT", "ETHUSDT", "BNBUSDT", "SOLUSDT", "XRPUSDT", "ADAUSDT", "DOGEUSDT", "LTCUSDT", "LINKUSDT", "DOTUSDT"]
REST_OHLC = "https://api.kraken.com/0/public/OHLC?pair={p}&interval=1440"
REST_PAIRS = "https://api.kraken.com/0/public/AssetPairs"
DAILY_DAYS = 30
# Checksum precisions (price decimals, qty decimals) from the held AssetPairs snapshot, 2026-10-27
PRECISIONS = {"BTC/USD": (1, 8), "ETH/USD": (2, 8)}


def cmd_head(out: Path) -> dict:
    store = RawStore(out / "store")
    robots = Robots(store)
    results = []
    for s in SYMBOLS:
        for m in ("2024-12", "2025-01"):
            if s == "BTCUSDT":
                continue  # Last-Modified for both BTCUSDT files is already held
            url = BINANCE.format(s=s, m=m)
            ok, note = robots.allowed(url)
            if not ok:
                results.append({"url": url, "skipped": note})
                continue
            try:
                results.append(head_capture(url, store, source_id="SR-04", source_approval_id="SA-01"))
            except (TimeoutError, ConnectionError) as e:
                results.append({"url": url, "error": f"{type(e).__name__}: {e}"[:200]})
            polite_pause()
    return {"robots": {h: n for h, (_, n) in robots.cache.items()}, "heads": results}


def cmd_live(out: Path, seconds: float) -> dict:
    return L.Capture(out, list(PRECISIONS), PRECISIONS, seconds).run()


def cmd_daily(out: Path) -> dict:
    out.mkdir(parents=True, exist_ok=True)
    started_file = out / "started_utc.txt"
    today = datetime.now(timezone.utc).date()
    if not started_file.exists():
        started_file.write_text(today.isoformat())
    started = datetime.fromisoformat(started_file.read_text().strip()).date()
    if (today - started).days >= DAILY_DAYS:
        return {"stopped": f"{DAILY_DAYS}-day window ended (started {started})"}
    store = RawStore(out / "store")
    robots = Robots(store)
    t = HttpsTransport("GET")
    res = {}
    for name, url in (("XBTUSD", REST_OHLC.format(p="XBTUSD")), ("ETHUSD", REST_OHLC.format(p="ETHUSD")),
                      ("AssetPairs", REST_PAIRS)):
        ok, note = robots.allowed(url)
        if not ok:
            res[name] = {"skipped": note}
            continue
        r = F.fetch(url, t, store, source_id="SR-05", source_approval_id="SA-02")
        api_error = None
        if r.raw is not None:
            try:
                api_error = json.loads(store.read(r.raw.raw_id)).get("error") or None
            except ValueError:
                api_error = ["non_json_body"]
        res[name] = {"raw_id": r.raw.raw_id if r.raw else None, "gap": r.gap.evidence if r.gap else None,
                     "attempts": r.attempts, "api_error": api_error}
        polite_pause(1.0)
    return {"day": today.isoformat(), "started": started.isoformat(), "results": res}


def main(argv=None):
    ap = argparse.ArgumentParser()
    ap.add_argument("command", choices=["head", "live", "daily"])
    ap.add_argument("--out", required=True, type=Path)
    ap.add_argument("--seconds", type=float, default=3600)
    a = ap.parse_args(argv)
    repo = Path(__file__).resolve().parents[2]
    if repo in a.out.resolve().parents or a.out.resolve() == repo:
        sys.exit("--out must be outside the repository (DEC-030)")
    a.out.mkdir(parents=True, exist_ok=True)
    t0 = time.time()
    result = {"head": lambda: cmd_head(a.out), "live": lambda: cmd_live(a.out, a.seconds),
              "daily": lambda: cmd_daily(a.out)}[a.command]()
    result["ran_at_utc"] = datetime.fromtimestamp(t0, timezone.utc).isoformat()
    with open(a.out / f"{a.command}-summary.jsonl", "a") as fh:
        fh.write(json.dumps(result, default=str) + "\n")
    print(json.dumps(result, indent=1, default=str))


if __name__ == "__main__":
    main()
