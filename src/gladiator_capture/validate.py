"""Run the capture validation plan (windows W-A to W-I, fixtures F-01 to F-18) on held files.

Usage: python3 -I -m gladiator_capture.validate --sample-root <dir> --out <dir outside the repo>

No network access (DEC-058). Held files are treated as untrusted data: they are read,
hashed and parsed, and nothing inside them is executed.
"""

from __future__ import annotations

import argparse
import json
import re
import shutil
import zipfile
from datetime import datetime, timezone
from decimal import Decimal
from pathlib import Path

from . import analysis as A
from . import records as R
from .rawstore import RawStore

DAY_NS = 86_400 * R.NS["s"]
KRAKEN_GENERATED_NS = int(datetime(2026, 10, 1, tzinfo=timezone.utc).timestamp()) * R.NS["s"]
VOLUME_REL_TOL = Decimal("1e-9")  # F-4h comparison (P01 sample tolerance)
SYMBOLS = ["BTCUSDT", "ETHUSDT", "BNBUSDT", "SOLUSDT", "XRPUSDT", "ADAUSDT", "DOGEUSDT", "LTCUSDT", "LINKUSDT", "DOTUSDT"]


def mtime_ns(p: Path) -> int:
    return p.stat().st_mtime_ns


def published_checksum(zip_path: Path):
    c = zip_path.with_name(zip_path.name + ".CHECKSUM")
    return c.read_text().split()[0] if c.exists() else None


def header_last_modified(evidence: Path, name: str):
    for h in evidence.glob(f"hdr_*{name}.txt"):
        m = re.search(r"^last-modified:\s*(.+?)\s*$", h.read_text(), re.I | re.M)
        if m:
            return m.group(1)
    return None


def zip_single_member(store: RawStore, obj):
    members = store.members(obj)
    assert len(members) == 1, obj.request
    return members[0]


class Run:
    def __init__(self, sample: Path, out: Path):
        self.sample = sample
        self.out = out
        if out.exists():
            shutil.rmtree(out)
        out.mkdir(parents=True)
        self.store = RawStore(out / "store")
        self.ingested_at = 0  # fixed for determinism of the normalized output
        self.report = {"windows": {}, "fixtures": {}}

    # -- helpers ---------------------------------------------------------------
    def ingest_binance_zip(self, path: Path, request: str, kind="klines", symbol=None, interval="1d", lm=None):
        lm = lm if lm is not None else header_last_modified(self.sample / "dl-sample-binance" / "evidence", path.name)
        obj = self.store.ingest_file(path, source_id="SR-04", source_approval_id="SA-01", request=request,
                                     published_checksum=published_checksum(path), server_last_modified=lm,
                                     retrieved_at_ns=mtime_ns(path))
        if obj.quarantined:
            return obj, R.ParseResult([], True, obj.reason)
        member = zip_single_member(self.store, obj)
        data = self.store.read(member.raw_id)
        name = member.member_path
        if kind == "klines":
            res = R.parse_binance_klines(data, name=name, symbol=symbol, interval=interval, raw=obj,
                                         ingested_at=self.ingested_at)
        else:
            res = R.parse_binance_trades(data, name=name, symbol=symbol, raw=obj, ingested_at=self.ingested_at)
        return obj, res

    def kraken_member(self, zip_obj, member_name):
        with zipfile.ZipFile(self.store.object_path(zip_obj.raw_id)) as zf:
            return zf.read(member_name)

    # -- windows ---------------------------------------------------------------
    def w_a(self):
        b = self.sample / "dl-sample-binance"
        recs, quarantined_files, verified, lm_held = [], 0, 0, 0
        units = {}
        for s in SYMBOLS:
            for m in ("2024-12", "2025-01"):
                p = b / f"{s}-1d-{m}.zip"
                obj, res = self.ingest_binance_zip(p, f"binance:spot/monthly/klines/{s}/1d/{p.name}", symbol=s)
                verified += obj.checksum_status == "verified"
                lm_held += obj.server_last_modified is not None
                quarantined_files += res.file_quarantined
                recs += res.records
                units.setdefault(m, set()).update(r.source_time_unit for r in res.records)
        gaps = []
        for s in SYMBOLS:
            gaps += A.bar_gaps([r for r in recs if r.native_symbol == s], DAY_NS)
        rep = A.coverage_report("W-A", recs, gaps, raw_count=20)
        rep.update(checksums_verified=verified, last_modified_held=lm_held, files_quarantined=quarantined_files,
                   units={k: sorted(v) for k, v in units.items()},
                   basis={b_: sum(r.available_at_basis == b_ for r in recs) for b_ in ("archive_published", "retrieved")},
                   late_flags=sum("late" in r.quality_flags for r in recs),
                   records_missing_four_times=sum(not all([r.source_event_time, r.received_at is not None,
                                                           r.ingested_at is not None, r.available_at])
                                                  for r in recs),
                   records_missing_venue_feed=sum(not (r.venue and r.source_id and r.feed_id) for r in recs),
                   hash_run1=A.output_hash(recs))
        self.wa_records = recs
        self.report["windows"]["W-A"] = rep

    def w_b(self):
        rev = self.sample / "dl-sample-binance" / "readme" / "rev"
        changelog = (self.sample / "dl-sample-binance" / "readme" / "u" / "2022-08-08_kline_updates.csv").read_text()
        out = {}
        for name, kind in (("1INCHUSDT-1d-2022-03-08.zip", "daily"), ("1INCHUSDT-1d-2022-03.zip", "monthly")):
            obj, res = self.ingest_binance_zip(rev / name, f"binance:spot/{kind}/klines/1INCHUSDT/1d/{name}",
                                               symbol="1INCHUSDT")
            in_changelog = f"/1INCHUSDT/1d/{name}," in changelog
            out[kind] = {"records": len(res.records), "checksum": obj.checksum_status,
                         "last_modified": obj.server_last_modified, "rewrite_flag": in_changelog}
            if kind == "daily":
                daily = res.records
            else:
                row = [r for r in res.records if r.source_event_time == daily[0].source_event_time][0]
                out["monthly_row_equals_daily"] = row.fields == daily[0].fields
        self.report["windows"]["W-B"] = out

    def w_c(self):
        luna = self.sample / "dl-sample-binance" / "luna"
        recs = []
        for m in ("2022-04", "2022-05", "2022-06", "2022-09"):
            p = luna / f"LUNAUSDT-1d-{m}.zip"
            recs += self.ingest_binance_zip(p, f"binance:spot/monthly/klines/LUNAUSDT/1d/{p.name}", symbol="LUNAUSDT")[1].records
        epochs = A.propose_epochs(recs)
        self.report["windows"]["W-C"] = {
            "records": len(recs),
            "epochs": [{"start": datetime.fromtimestamp(e.start_ns / 1e9, timezone.utc).date().isoformat(),
                        **e.evidence, "review_status": e.review_status} for e in epochs]}

    def w_d(self):
        p = self.sample / "dl-sample-binance" / "ETHUSDT-trades-2025-01-15.zip"
        obj, res = self.ingest_binance_zip(p, f"binance:spot/daily/trades/ETHUSDT/{p.name}", kind="trades", symbol="ETHUSDT")
        self.wd_obj = obj
        self.report["windows"]["W-D"] = {"records": len(res.records), "checksum": obj.checksum_status,
                                         "data_gaps": len(A.trade_gaps(res.records)),
                                         "unit": res.records[0].source_time_unit if res.records else None}

    def kraken_full(self):
        p = self.sample / "dl-sample-kraken" / "Kraken_OHLCVT_Full.zip"
        self.full = self.store.ingest_file(p, source_id="SR-05", source_approval_id="SA-02",
                                           request="kraken:ohlcvt/Kraken_OHLCVT_Full.zip", retrieved_at_ns=mtime_ns(p))
        return self.full

    def kraken_pair(self, pair):
        data = self.kraken_member(self.full, f"{pair}_1440.csv")
        return R.parse_kraken_csv(data, pair=pair, interval_min=1440, raw=self.full,
                                  generated_ns=KRAKEN_GENERATED_NS, ingested_at=self.ingested_at).records

    def w_e(self):
        self.kraken_full()
        out = {}
        self.we = {}
        for pair in ("XBTUSD", "ETHUSD"):
            recs = self.kraken_pair(pair)
            gaps = A.bar_gaps(recs, DAY_NS)
            self.we[pair] = (recs, gaps)
            out[pair] = A.coverage_report(pair, recs, gaps, raw_count=1)
            out[pair]["first"] = datetime.fromtimestamp(recs[0].event_time_ns() / 1e9, timezone.utc).date().isoformat()
            out[pair]["last"] = datetime.fromtimestamp(recs[-1].event_time_ns() / 1e9, timezone.utc).date().isoformat()
            out[pair]["available_at"] = datetime.fromtimestamp(recs[0].available_at / 1e9, timezone.utc).isoformat()
        with zipfile.ZipFile(self.store.object_path(self.full.raw_id)) as zf:
            names = zf.namelist()
            manifest = json.loads(zf.read("MANIFEST.json"))
        csvs = [n for n in names if re.fullmatch(r"[^/]+_\d+\.csv", n)]
        out["manifest"] = {"manifest_pairs": manifest["pairs"], "manifest_files": manifest["files"],
                           "zip_pairs": len({n.rsplit("_", 1)[0] for n in csvs}), "zip_pair_interval_csvs": len(csvs),
                           "mismatch_logged": manifest["files"] != len(csvs)}
        # CV-07: 365-day look-backs after 2015-12-31
        step = DAY_NS
        worst = {}
        for pair, (recs, gaps) in self.we.items():
            starts = range(int(datetime(2016, 1, 1, tzinfo=timezone.utc).timestamp()) * R.NS["s"],
                           int(datetime(2025, 10, 1, tzinfo=timezone.utc).timestamp()) * R.NS["s"], 30 * step)
            worst[pair] = str(min(A.coverage(recs, gaps, s, s + 365 * step, step) for s in starts).quantize(Decimal("0.0001")))
        out["cv07_min_coverage_365d_after_2016"] = worst
        self.report["windows"]["W-E"] = out

    def w_f(self):
        out = {}
        for pair in ("ANTETH", "AGLDUSD", "AIRUSD", "ANKRGBP"):
            recs = self.kraken_pair(pair)
            out[pair] = {"records": len(recs),
                         "last_bar": datetime.fromtimestamp(recs[-1].event_time_ns() / 1e9, timezone.utc).date().isoformat(),
                         "delisting_upper_bound": True}
        self.report["windows"]["W-F"] = out

    def w_g(self):
        p = self.sample / "dl-sample-kraken" / "Kraken_OHLCVT_2026Q3.zip"
        obj = self.store.ingest_file(p, source_id="SR-05", source_approval_id="SA-02",
                                     request="kraken:ohlcvt/Kraken_OHLCVT_2026Q3.zip", retrieved_at_ns=mtime_ns(p))
        with zipfile.ZipFile(self.store.object_path(obj.raw_id)) as zf:
            csvs = [n for n in zf.namelist() if re.fullmatch(r"[^/]+_\d+\.csv", n)]
            manifest = json.loads(zf.read("MANIFEST.json"))
        self.report["windows"]["W-G"] = {"checksum_status": obj.checksum_status, "pairs": len({n.rsplit('_', 1)[0] for n in csvs}),
                                         "csvs": len(csvs), "manifest_pairs": manifest["pairs"], "manifest_files": manifest["files"]}

    def w_h(self):
        out = {}
        for pair in ("XBTUSD", "ETHUSD"):
            p = self.sample / "dl-sample-kraken" / "rest" / f"ohlc_{pair}_1440.json"
            obj = self.store.ingest_file(p, source_id="SR-05", source_approval_id="SA-02",
                                         request=f"kraken:rest/OHLC?pair={pair}&interval=1440", retrieved_at_ns=mtime_ns(p))
            res = R.parse_kraken_rest_ohlc(self.store.read(obj.raw_id), request_pair=pair, interval_min=1440, raw=obj,
                                           ingested_at=self.ingested_at)
            arch = {r.source_event_time: r for r in self.we[pair][0]}
            compared = mism = 0
            diffs = []
            for r in res.records:
                a = arch.get(r.source_event_time)
                if a is None:
                    continue
                compared += 1
                ok = all(Decimal(a.fields[k]) == Decimal(r.fields[k]) for k in ("open", "high", "low", "close", "trade_count"))
                va, vr = Decimal(a.fields["volume"]), Decimal(r.fields["volume"])
                ok = ok and abs(va - vr) <= VOLUME_REL_TOL * max(abs(va), abs(vr))
                if not ok:
                    mism += 1
                    diffs.append({"date": datetime.fromtimestamp(r.source_event_time, timezone.utc).date().isoformat(),
                                  **{k: [a.fields[k], str(r.fields[k])] for k in ("trade_count", "volume")}})
            out[pair] = {"completed_bars": len(res.records), "note": res.reason,
                         "late_flags": sum("late" in r.quality_flags for r in res.records),
                         "response_key": res.records[0].fields["native_response_key"],
                         "compared_with_archive": compared, "mismatches": mism, "mismatch_detail": diffs}
        self.report["windows"]["W-H"] = out

    def w_i(self):
        ctx = self.sample / "dl-sample-context"
        out = {}
        for name in ("monetary20260916a.htm", "fomcminutes20260729.htm", "cftc_deacmesf.htm"):
            text = (ctx / name).read_text(errors="replace")
            hdr = (ctx / (name + ".hdr")).read_text()
            m = re.search(r"for release at\s*([0-9:]+\s*[ap]\.m\.(?:\s*E[DS]T)?)", text, re.I)
            lm = re.search(r"^last-modified:\s*(.+?)\s*$", hdr, re.I | re.M)
            out[name] = {"stated_release": m.group(1).strip() if m else None,
                         "last_modified": lm.group(1) if lm else None,
                         "basis": "stated_release" if m and name.startswith("monetary") else "first_published"}
        self.report["windows"]["W-I"] = out

    # -- fixtures --------------------------------------------------------------
    def fixtures(self):
        fx = self.report["fixtures"]
        b = self.sample / "dl-sample-binance"
        work = self.out / "fixtures"
        work.mkdir()
        base_zip = b / "BTCUSDT-1d-2024-12.zip"
        base_csv = zipfile.ZipFile(base_zip).read("BTCUSDT-1d-2024-12.csv").decode().rstrip("\n")
        rows = base_csv.splitlines()
        lm = header_last_modified(b / "evidence", base_zip.name)
        raw = type("Raw", (), {"raw_id": "fixture", "retrieved_at_ns": mtime_ns(base_zip), "server_last_modified": lm})()

        def parse(text, name="BTCUSDT-1d-2024-12.csv"):
            return R.parse_binance_klines(text.encode(), name=name, symbol="BTCUSDT", interval="1d", raw=raw,
                                          ingested_at=self.ingested_at)

        def counts(res):
            q = sum(r.quality_state == "quarantined" for r in res.records)
            return {"file_quarantined": res.file_quarantined, "quarantined": q, "valid": len(res.records) - q}

        # F-01: flip one byte
        f01 = work / base_zip.name
        data = bytearray(base_zip.read_bytes())
        data[100] ^= 0xFF
        f01.write_bytes(bytes(data))
        o = self.store.ingest_file(f01, source_id="SR-04", source_approval_id="SA-01", request="fixture:F-01",
                                   published_checksum=published_checksum(base_zip))
        fx["F-01"] = {"checksum_status": o.checksum_status, "quarantined": o.quarantined, "expected": "mismatch, quarantined"}
        # F-02a: ingest the same object twice
        a = self.store.ingest_file(base_zip, source_id="SR-04", source_approval_id="SA-01", request="fixture:F-02a")
        a2 = self.store.ingest_file(base_zip, source_id="SR-04", source_approval_id="SA-01", request="fixture:F-02a")
        fx["F-02a"] = {"same_raw_id": a.raw_id == a2.raw_id, "records": len(parse(base_csv + "\n").records), "expected": 31}
        fx["F-02b"] = {**counts(parse("\n".join(rows + [rows[4]]) + "\n")), "expected": "2 quarantined, 30 valid"}
        alt = rows[4].split(",")
        alt[4] = str(Decimal(alt[4]) + 1)
        fx["F-03"] = {**counts(parse("\n".join(rows + [",".join(alt)]) + "\n")), "expected": "2 quarantined, 30 valid"}
        recs, gaps = self.we["XBTUSD"]
        fx["F-04"] = {"gaps": len(gaps), "classes": sorted({g.gap_class for g in gaps}),
                      "first": datetime.fromtimestamp(gaps[0].interval_start / 1e9, timezone.utc).date().isoformat(),
                      "last": datetime.fromtimestamp(gaps[-1].interval_start / 1e9, timezone.utc).date().isoformat(),
                      "expected": "12 status_unknown, 2013-10-11 to 2014-12-25"}
        tz = zipfile.ZipFile(b / "ETHUSDT-trades-2025-01-15.zip")
        tdata = tz.read(tz.namelist()[0]).decode().splitlines()
        del tdata[999]
        tres = R.parse_binance_trades(("\n".join(tdata) + "\n").encode(), name="ETHUSDT-trades-2025-01-15.csv",
                                      symbol="ETHUSDT", raw=raw, ingested_at=self.ingested_at)
        fx["F-05"] = {"data_gaps": len(A.trade_gaps(tres.records)), "valid": len(tres.records), "expected": "1 data_gap, 2,689,487 valid"}
        e = list(rows)
        f0 = e[0].split(",")
        f0[2] = str(Decimal(f0[3]) - 1)
        e[0] = ",".join(f0)
        f1 = e[1].split(",")
        f1[4] = "NaN"
        e[1] = ",".join(f1)
        fx["F-06"] = {**counts(parse("\n".join(e) + "\n")), "expected": "2 quarantined, 29 valid"}
        fx["F-06b"] = {"reason": R.check_naive_time("2026-10-14T08:30:00"), "expected": "timezone_naive"}
        jan = zipfile.ZipFile(b / "BTCUSDT-1d-2025-01.zip").read("BTCUSDT-1d-2025-01.csv").decode().splitlines()
        j0 = jan[0].split(",")
        j0[0] = str(int(j0[0]) // 1000)
        jan[0] = ",".join(j0)
        fx["F-07"] = {**counts(parse("\n".join(jan) + "\n", name="BTCUSDT-1d-2025-01.csv")), "expected": "file quarantined"}
        sw = list(rows)
        sw[2], sw[3] = sw[3], sw[2]
        swapped = parse("\n".join(sw) + "\n").records
        orig = parse(base_csv + "\n").records
        fx["F-08"] = {"valid": len(swapped),
                      "replay_order_same": [r.source_event_time for r in A.replay_order(swapped)] ==
                                           [r.source_event_time for r in A.replay_order(orig)],
                      "expected": "31 valid, order unchanged"}
        # F-09: constructed old version, then the real new one
        rev = b / "readme" / "rev" / "1INCHUSDT-1d-2022-03-08.zip"
        new_csv = zipfile.ZipFile(rev).read("1INCHUSDT-1d-2022-03-08.csv").decode()
        old_fields = new_csv.split(",")
        old_fields[4] = str(Decimal(old_fields[4]) + Decimal("0.001"))
        old_path = work / "1INCHUSDT-1d-2022-03-08.old.csv"
        old_path.write_text(",".join(old_fields))
        new_path = work / "1INCHUSDT-1d-2022-03-08.new.csv"
        new_path.write_text(new_csv)
        t_old = mtime_ns(rev) - 10 * DAY_NS
        o1 = self.store.ingest_file(old_path, source_id="SR-04", source_approval_id="SA-01", request="fixture:F-09",
                                    retrieved_at_ns=t_old)
        o2 = self.store.ingest_file(new_path, source_id="SR-04", source_approval_id="SA-01", request="fixture:F-09",
                                    retrieved_at_ns=mtime_ns(rev))
        mk = lambda o, text: R.parse_binance_klines(text.encode(), name="1INCHUSDT-1d-2022-03-08.csv", symbol="1INCHUSDT",
                                                    interval="1d", raw=o, ingested_at=self.ingested_at).records
        v1, v2 = mk(o1, old_path.read_text()), mk(o2, new_csv)
        merged = A.apply_revision(v1, v2)
        fx["F-09"] = {"versions": sorted({r.version for r in merged}), "supersedes_set": o2.supersedes_raw_id == o1.raw_id,
                      "seen_before_revision": [r.version for r in A.as_of(merged, o2.retrieved_at_ns - 1)],
                      "seen_after_revision": [r.version for r in A.as_of(merged, o2.retrieved_at_ns)],
                      "expected": "2 versions; version 1 before, version 2 after"}
        fx["F-10"] = {"epochs": self.report["windows"]["W-C"]["epochs"], "expected": "1 proposed break on 2022-05-31"}
        fx["F-11"] = {"last_bar": self.report["windows"]["W-F"]["ANKRGBP"]["last_bar"], "expected": "2022-12-31, upper bound"}
        fx["F-12"] = {"XBTUSD_completed": self.report["windows"]["W-H"]["XBTUSD"]["completed_bars"],
                      "note": self.report["windows"]["W-H"]["XBTUSD"]["note"], "expected": "57 kept, 1 dropped"}
        fx["F-13"] = {**counts(parse("\n".join(",".join(r.split(",")[:11]) for r in rows) + "\n")), "expected": "file quarantined"}
        gi = A.GapInterval("SR-99", "bls:cpi", "official:CPI:1", 0, 0, "data_gap", "http_status=403", 0)
        hdr = (self.sample / "dl-sample-context" / "bls_cpi.nr0.htm.hdr").read_text().splitlines()[0]
        fx["F-14"] = {"recorded_status": hdr.strip(), "gap_state": gi.availability_state, "retried_other_route": False,
                      "expected": "SOURCE_UNAVAILABLE, no retry"}
        decision = int(datetime(2025, 1, 7, tzinfo=timezone.utc).timestamp()) * R.NS["s"]
        fx["F-16"] = {"visible_at_2025-01-07": len(A.as_of(orig, decision)),
                      "visible_after_last_modified": len(A.as_of(orig, orig[0].available_at)), "expected": "0, then 31"}
        cot_lm = R.http_date_to_ns("Fri, 23 Oct 2026 19:27:36 GMT")
        fx["F-17"] = {"stale_at_plus_15d": (cot_lm + 15 * DAY_NS) - cot_lm > 14 * DAY_NS,
                      "stale_at_plus_7d": (cot_lm + 7 * DAY_NS) - cot_lm > 14 * DAY_NS, "expected": "True, False"}
        xrecs, xgaps = self.we["XBTUSD"]
        end = int(datetime(2026, 10, 1, tzinfo=timezone.utc).timestamp()) * R.NS["s"]
        start = end - 365 * DAY_NS
        drop = {start + i * DAY_NS for i in range(19)}
        thinned = [r for r in xrecs if r.event_time_ns() not in drop]
        restored = [r for r in xrecs if r.event_time_ns() not in drop or r.event_time_ns() == start]
        fx["F-18"] = {"qualifies_346": A.qualifies(thinned, [], start, end, DAY_NS),
                      "qualifies_347": A.qualifies(restored, [], start, end, DAY_NS), "expected": "False, True"}

    def determinism(self):
        recs2 = []
        b = self.sample / "dl-sample-binance"
        for s in SYMBOLS:
            for m in ("2024-12", "2025-01"):
                p = b / f"{s}-1d-{m}.zip"
                recs2 += self.ingest_binance_zip(p, f"binance:spot/monthly/klines/{s}/1d/{p.name}", symbol=s)[1].records
        self.report["windows"]["W-A"]["hash_run2"] = A.output_hash(recs2)
        self.report["windows"]["W-A"]["deterministic"] = (self.report["windows"]["W-A"]["hash_run1"] ==
                                                          self.report["windows"]["W-A"]["hash_run2"])

    def run(self):
        for step in (self.w_a, self.w_b, self.w_c, self.w_d, self.w_e, self.w_f, self.w_g, self.w_h, self.w_i,
                     self.fixtures, self.determinism):
            step()
        return self.report


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--sample-root", required=True, type=Path)
    ap.add_argument("--out", required=True, type=Path)
    args = ap.parse_args()
    report = Run(args.sample_root, args.out).run()
    text = json.dumps(report, indent=1, sort_keys=True, default=str)
    (args.out / "report.json").write_text(text)
    print(text)


if __name__ == "__main__":
    main()
