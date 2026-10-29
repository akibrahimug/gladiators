"""Run the capture validation plan (windows W-A to W-I, fixtures F-01 to F-18) on held files.

Usage: python3 -I run_validation.py --sample-root <dir> --out <new dir outside the repo and sample root>

No network access (DEC-058). Held files are untrusted data: they are read, hashed and
parsed, and nothing inside them is executed or imported.
"""

from __future__ import annotations

import argparse
import json
import re
import zipfile
from datetime import datetime, timezone
from decimal import Decimal
from pathlib import Path

from . import analysis as A
from . import fetch as F
from . import records as R
from .rawstore import RawStore, sha256_bytes, sha256_file

DAY_NS = 86_400 * R.NS["s"]
VOLUME_REL_TOL = Decimal("1e-9")  # F-4h comparison, DEC-059 (supersedes the 8-decimal rule)
SYMBOLS = ["BTCUSDT", "ETHUSDT", "BNBUSDT", "SOLUSDT", "XRPUSDT", "ADAUSDT", "DOGEUSDT", "LTCUSDT", "LINKUSDT", "DOTUSDT"]
MARKER = ".gladiator_validation_output"
REPO_ROOT = Path(__file__).resolve().parents[2]


def mtime_ns(p: Path) -> int:
    return p.stat().st_mtime_ns


def ts_date(ns: int) -> str:
    return datetime.fromtimestamp(ns / 1e9, timezone.utc).date().isoformat()


def published_checksum(zip_path: Path):
    c = zip_path.with_name(zip_path.name + ".CHECKSUM")
    return c.read_text().split()[0] if c.exists() else None


def header_last_modified(evidence: Path, name: str):
    for h in evidence.glob(f"hdr_*{name}.txt"):
        m = re.search(r"^last-modified:\s*(.+?)\s*$", h.read_text(), re.I | re.M)
        if m:
            return m.group(1)
    return None


def prepare_out(out: Path, sample: Path) -> None:
    """Never delete anything the runner did not create."""
    out = out.resolve()
    sample = sample.resolve()
    held = [d for d in sample.glob("dl-sample-*") if d.is_dir()]
    for forbidden in held + [REPO_ROOT]:
        if out == forbidden or forbidden in out.parents or out in forbidden.parents:
            raise SystemExit(f"--out must not overlap {forbidden}")
    if out == sample or out in sample.parents:
        raise SystemExit("--out must not contain the sample root")
    if out.exists() and any(out.iterdir()):
        if not (out / MARKER).exists():
            raise SystemExit(f"--out {out} is not empty and was not created by this runner")
        for p in sorted(out.rglob("*"), reverse=True):
            p.unlink() if p.is_file() or p.is_symlink() else p.rmdir()
    out.mkdir(parents=True, exist_ok=True)
    (out / MARKER).write_text("created by gladiator_capture.validate\n")


class FakeTransport:
    """Scripted responses for the recovery fixtures; there is no network transport (DEC-058)."""

    def __init__(self, script):
        self.script = list(script)
        self.calls = 0

    def get(self, request):
        self.calls += 1
        item = self.script.pop(0)
        if isinstance(item, Exception):
            raise item
        return item


class Run:
    def __init__(self, sample: Path, out: Path):
        self.sample = sample
        self.out = out
        prepare_out(out, sample)
        self.store = RawStore(out / "store")
        self.all_records = []
        self.report = {"windows": {}, "fixtures": {}, "criteria": {}}
        self.changelog = (sample / "dl-sample-binance" / "readme" / "u" / "2022-08-08_kline_updates.csv").read_text()

    def now(self) -> int:
        return self.store.clock()

    def keep(self, recs):
        self.all_records += recs
        return recs

    # -- ingestion helpers -----------------------------------------------------
    def ingest_binance_zip(self, path: Path, request: str, kind="klines", symbol=None, interval="1d"):
        lm = header_last_modified(self.sample / "dl-sample-binance" / "evidence", path.name)
        obj = self.store.ingest_file(path, source_id="SR-04", source_approval_id="SA-01", request=request,
                                     published_checksum=published_checksum(path), server_last_modified=lm,
                                     retrieved_at_ns=mtime_ns(path))
        if obj.quarantined:
            return obj, R.ParseResult([], True, obj.reason)
        with zipfile.ZipFile(self.store.object_path(obj.raw_id)) as zf:
            names = [n for n in zf.namelist() if not n.startswith("__MACOSX/")]
        member = self.store.member(obj, names[0])
        data = self.store.read(member.raw_id)
        if kind == "klines":
            listed = f"/{symbol}/{interval}/{path.name}," in self.changelog
            res = R.parse_binance_klines(data, name=member.member_path, symbol=symbol, interval=interval, raw=member,
                                         ingested_at=self.now(), rewrite_listed=listed)
        else:
            res = R.parse_binance_trades(data, name=member.member_path, symbol=symbol, raw=member, ingested_at=self.now())
        self.keep(res.records)
        return obj, res

    def kraken_container(self, name):
        p = self.sample / "dl-sample-kraken" / name
        obj = self.store.ingest_file(p, source_id="SR-05", source_approval_id="SA-02",
                                     request=f"kraken:ohlcvt/{name}", retrieved_at_ns=mtime_ns(p))
        with zipfile.ZipFile(self.store.object_path(obj.raw_id)) as zf:
            names = zf.namelist()
            manifest = json.loads(zf.read("MANIFEST.json"))
        generated = datetime.fromisoformat(manifest["generated"]).replace(tzinfo=timezone.utc)
        return obj, names, manifest, int(generated.timestamp()) * R.NS["s"]

    def kraken_pair(self, pair, interval=1440, keep=True):
        member = self.store.member(self.full, f"{pair}_{interval}.csv")
        res = R.parse_kraken_csv(self.store.read(member.raw_id), pair=pair, interval_min=interval, raw=member,
                                 generated_ns=self.full_generated, ingested_at=self.now())
        return self.keep(res.records) if keep else res.records

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
        rep = A.coverage_report("W-A", recs, gaps, raw_files=20)
        rep.update(checksums_verified=verified, last_modified_held=lm_held, files_quarantined=quarantined_files,
                   units={k: sorted(v) for k, v in units.items()},
                   basis={x: sum(r.available_at_basis == x for r in recs) for x in ("archive_published", "retrieved")},
                   late_flags=sum("late" in r.quality_flags for r in recs), content_hash=A.output_hash(recs))
        self.report["windows"]["W-A"] = rep

    def w_b(self):
        rev = self.sample / "dl-sample-binance" / "readme" / "rev"
        out = {}
        for name, kind in (("1INCHUSDT-1d-2022-03-08.zip", "daily"), ("1INCHUSDT-1d-2022-03.zip", "monthly")):
            obj, res = self.ingest_binance_zip(rev / name, f"binance:spot/{kind}/klines/1INCHUSDT/1d/{name}",
                                               symbol="1INCHUSDT")
            out[kind] = {"records": len(res.records), "checksum": obj.checksum_status,
                         "last_modified": obj.server_last_modified,
                         "records_with_rewrite_flag": sum("last_modified_after_period" in r.quality_flags for r in res.records)}
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
        p = luna / "LUNCUSDT-1d-2022-09.zip"
        lunc = self.ingest_binance_zip(p, f"binance:spot/monthly/klines/LUNCUSDT/1d/{p.name}", symbol="LUNCUSDT")[1].records
        epochs = A.propose_epochs(recs)
        self.report["windows"]["W-C"] = {
            "luna_records": len(recs), "lunc_records": len(lunc), "lunc_first": ts_date(lunc[0].event_time_ns()),
            "epochs": [{"start": ts_date(e.start_ns), **e.evidence, "review_status": e.review_status} for e in epochs]}

    def w_d(self):
        p = self.sample / "dl-sample-binance" / "ETHUSDT-trades-2025-01-15.zip"
        obj, res = self.ingest_binance_zip(p, f"binance:spot/daily/trades/ETHUSDT/{p.name}", kind="trades", symbol="ETHUSDT")
        self.report["windows"]["W-D"] = {
            "records": len(res.records), "checksum": obj.checksum_status, "data_gaps": len(A.trade_gaps(res.records)),
            "quarantined": sum(r.quality_state == "quarantined" for r in res.records),
            "late_flags": sum("late" in r.quality_flags for r in res.records),
            "basis": sorted({r.available_at_basis for r in res.records}),
            "unit": res.records[0].source_time_unit if res.records else None}

    def w_e(self):
        self.full, names, manifest, self.full_generated = self.kraken_container("Kraken_OHLCVT_Full.zip")
        out, self.we = {}, {}
        decision = int(datetime(2026, 9, 30, tzinfo=timezone.utc).timestamp()) * R.NS["s"]
        for pair in ("XBTUSD", "ETHUSD"):
            recs = self.kraken_pair(pair)
            gaps = A.bar_gaps(recs, DAY_NS)
            self.we[pair] = (recs, gaps)
            rep = A.coverage_report(pair, recs, gaps, raw_files=1)
            rep.update(first=ts_date(recs[0].event_time_ns()), last=ts_date(recs[-1].event_time_ns()),
                       available_at=datetime.fromtimestamp(recs[0].available_at / 1e9, timezone.utc).isoformat(),
                       entry_blocked_on_2026_09_30_365d=A.entry_blocked(recs, gaps, decision, 365))
            out[pair] = rep
        csvs = [n for n in names if re.fullmatch(r"[^/]+_\d+\.csv", n)]
        out["manifest"] = {"manifest_generated": manifest["generated"], "manifest_pairs": manifest["pairs"],
                           "manifest_files": manifest["files"], "zip_pairs": len({n.rsplit("_", 1)[0] for n in csvs}),
                           "zip_pair_interval_csvs": len(csvs), "mismatch_logged": manifest["files"] != len(csvs)}
        # CV-07: every 365-day look-back (daily step) from 2016-01-01 to the archive end
        worst = {}
        first = int(datetime(2016, 1, 1, tzinfo=timezone.utc).timestamp()) * R.NS["s"]
        last = int(datetime(2025, 10, 1, tzinfo=timezone.utc).timestamp()) * R.NS["s"]
        for pair, (recs, gaps) in self.we.items():
            pset = {r.event_time_ns() for r in A.valid(recs)}
            count = sum(1 for t in range(first, first + 365 * DAY_NS, DAY_NS) if t in pset)
            best, s = None, first
            while s <= last:
                cov = Decimal(count) / 365
                best = cov if best is None or cov < best else best
                count += (s + 365 * DAY_NS in pset) - (s in pset)
                s += DAY_NS
            worst[pair] = str(best.quantize(Decimal("0.0001")))
        out["cv07_min_coverage_any_365d_from_2016"] = worst
        # TH-1/TH-2 re-derivation across every daily file in the full archive
        long_gaps = breaks = 0
        examples = []
        daily = sorted(x for x in csvs if x.endswith("_1440.csv"))
        for n in daily:
            recs = self.kraken_pair(n[: -len("_1440.csv")], keep=False)
            rs = sorted(A.valid(recs), key=lambda r: r.event_time_ns())
            long_gaps += sum(1 for a, b in zip(rs, rs[1:]) if (b.event_time_ns() - a.event_time_ns()) // DAY_NS - 1 > 7)
            eps = A.propose_epochs(recs)
            breaks += len(eps)
            examples += [{"pair": n[:-9], "start": ts_date(e.start_ns), **e.evidence} for e in eps]
        out["th1_th2_rederivation"] = {"pairs_scanned": len(daily), "daily_gaps_over_7d": long_gaps,
                                       "proposed_epoch_breaks": breaks, "breaks": examples}
        self.report["windows"]["W-E"] = out

    def w_f(self):
        pairs_now = json.loads((self.sample / "dl-sample-kraken" / "rest" / "assetpairs.json").read_text())["result"]
        listed = {v.get("altname") for v in pairs_now.values()}
        out = {}
        for pair in ("ANTETH", "AGLDUSD", "AIRUSD", "ANKRGBP"):
            recs = self.kraken_pair(pair)
            last = ts_date(recs[-1].event_time_ns())
            out[pair] = {"records": len(recs), "last_bar": last, "listed_in_assetpairs": pair in listed,
                         "delisting_date": f"<= {last} (upper bound)" if pair not in listed else "not delisted"}
        self.report["windows"]["W-F"] = out

    def w_g(self):
        obj, names, manifest, _ = self.kraken_container("Kraken_OHLCVT_2026Q3.zip")
        csvs = [n for n in names if re.fullmatch(r"[^/]+_\d+\.csv", n)]
        self.report["windows"]["W-G"] = {"checksum_status": obj.checksum_status, "pairs": len({n.rsplit('_', 1)[0] for n in csvs}),
                                         "csvs": len(csvs), "manifest_pairs": manifest["pairs"], "manifest_files": manifest["files"]}

    def w_h(self):
        out = {}
        for pair in ("XBTUSD", "ETHUSD"):
            p = self.sample / "dl-sample-kraken" / "rest" / f"ohlc_{pair}_1440.json"
            obj = self.store.ingest_file(p, source_id="SR-05", source_approval_id="SA-02",
                                         request=f"kraken:rest/OHLC?pair={pair}&interval=1440", retrieved_at_ns=mtime_ns(p))
            res = R.parse_kraken_rest_ohlc(self.store.read(obj.raw_id), request_pair=pair, interval_min=1440, raw=obj,
                                           ingested_at=self.now())
            self.keep(res.records)
            arch = {r.source_event_time: r for r in self.we[pair][0]}
            compared, current_rule, proposed_rule = 0, [], []
            for r in res.records:
                a = arch.get(r.source_event_time)
                if a is None:
                    continue
                compared += 1
                same = all(Decimal(a.fields[k]) == Decimal(r.fields[k]) for k in ("open", "high", "low", "close", "trade_count"))
                va, vr = Decimal(a.fields["volume"]), Decimal(r.fields["volume"])
                detail = {"date": ts_date(r.event_time_ns()), "trade_count": [a.fields["trade_count"], r.fields["trade_count"]],
                          "volume": [a.fields["volume"], r.fields["volume"]]}
                if not (same and va.quantize(Decimal("1e-8")) == vr):  # superseded 8-decimal rule, kept for comparison
                    current_rule.append(detail)
                if not (same and abs(va - vr) <= VOLUME_REL_TOL * max(abs(va), abs(vr))):  # DEC-059 rule
                    proposed_rule.append(detail)
            out[pair] = {"completed_bars": len(res.records), "dropped_incomplete": res.dropped_incomplete,
                         "late_flags": sum("late" in r.quality_flags for r in res.records),
                         "response_key": res.records[0].fields["native_response_key"], "compared_with_archive": compared,
                         "mismatches_dec059_rule": proposed_rule, "mismatches_superseded_8dp_rule": current_rule}
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
        rows = zipfile.ZipFile(base_zip).read("BTCUSDT-1d-2024-12.csv").decode().rstrip("\n").splitlines()
        lm = header_last_modified(b / "evidence", base_zip.name)
        raw = type("Raw", (), {"raw_id": "fixture", "retrieved_at_ns": mtime_ns(base_zip), "server_last_modified": lm,
                               "supersedes_raw_id": None, "member_path": None})()

        def parse(text, name="BTCUSDT-1d-2024-12.csv"):
            return R.parse_binance_klines(text.encode(), name=name, symbol="BTCUSDT", interval="1d", raw=raw,
                                          ingested_at=self.now())

        def counts(res):
            q = sum(r.quality_state == "quarantined" for r in res.records)
            return {"file_quarantined": res.file_quarantined, "file_reason": res.reason, "quarantined": q,
                    "valid": len(res.records) - q, "reasons": sorted({r.reason for r in res.records if r.reason})}

        def text_of(lines):
            t = "\n".join(lines) + "\n"
            return t, sha256_bytes(t.encode())

        base_hash = sha256_file(base_zip)
        f01 = work / base_zip.name
        data = bytearray(base_zip.read_bytes())
        data[100] ^= 0xFF
        f01.write_bytes(bytes(data))
        o = self.store.ingest_file(f01, source_id="SR-04", source_approval_id="SA-01", request="fixture:F-01",
                                   published_checksum=published_checksum(base_zip))
        fx["F-01"] = {"input": base_hash, "edited_input": sha256_file(f01), "checksum_status": o.checksum_status,
                      "quarantined": o.quarantined, "pass": o.quarantined and o.checksum_status == "mismatch"}
        n_before = len(self.store.journal_entries())
        a1 = self.store.ingest_file(base_zip, source_id="SR-04", source_approval_id="SA-01", request="fixture:F-02a")
        a2 = self.store.ingest_file(base_zip, source_id="SR-04", source_approval_id="SA-01", request="fixture:F-02a")
        outcomes = [e.outcome for e in self.store.journal_entries()[n_before:]]
        fx["F-02a"] = {"input": base_hash, "same_raw_object": a1 is a2, "journal": outcomes,
                       "pass": a1 is a2 and outcomes == ["started", "stored", "duplicate"]}
        t, h = text_of(rows + [rows[4]])
        c = counts(parse(t))
        fx["F-02b"] = {"input": h, **c, "pass": c["quarantined"] == 2 and c["valid"] == 30 and c["reasons"] == ["duplicate_timestamp"]}
        alt = rows[4].split(",")
        alt[4] = str(Decimal(alt[4]) + 1)
        t, h = text_of(rows + [",".join(alt)])
        c = counts(parse(t))
        fx["F-03"] = {"input": h, **c, "pass": c["quarantined"] == 2 and c["valid"] == 30 and c["reasons"] == ["duplicate_conflicting"]}
        recs, gaps = self.we["XBTUSD"]
        fx["F-04"] = {"input": self.full.raw_id + "#XBTUSD_1440.csv", "gaps": len(gaps),
                      "classes": sorted({g.gap_class for g in gaps}), "first": ts_date(gaps[0].interval_start),
                      "last": ts_date(gaps[-1].interval_start),
                      "pass": len(gaps) == 12 and {g.gap_class for g in gaps} == {"status_unknown"}}
        tz = zipfile.ZipFile(b / "ETHUSDT-trades-2025-01-15.zip")
        tdata = tz.read(tz.namelist()[0]).decode().rstrip("\n").splitlines()
        del tdata[999]
        t, h = text_of(tdata)
        traw = type("Raw", (), {"raw_id": "fixture", "retrieved_at_ns": raw.retrieved_at_ns, "server_last_modified": None,
                                "supersedes_raw_id": None, "member_path": None})()
        tres = R.parse_binance_trades(t.encode(), name="ETHUSDT-trades-2025-01-15.csv", symbol="ETHUSDT", raw=traw,
                                      ingested_at=self.now())
        tg = A.trade_gaps(tres.records)
        fx["F-05"] = {"input": h, "data_gaps": len(tg), "valid": len(A.valid(tres.records)),
                      "pass": len(tg) == 1 and len(A.valid(tres.records)) == 2_689_487}
        e = list(rows)
        f0 = e[0].split(",")
        f0[2] = str(Decimal(f0[3]) - 1)
        e[0] = ",".join(f0)
        f1 = e[1].split(",")
        f1[4] = "NaN"
        e[1] = ",".join(f1)
        t, h = text_of(e)
        c = counts(parse(t))
        fx["F-06"] = {"input": h, **c, "pass": c["quarantined"] == 2 and c["valid"] == 29}
        reason = R.check_naive_time("2026-10-14T08:30:00")
        fx["F-06b"] = {"input": "2026-10-14T08:30:00", "reason": reason, "pass": reason == "timezone_naive"}
        jan = zipfile.ZipFile(b / "BTCUSDT-1d-2025-01.zip").read("BTCUSDT-1d-2025-01.csv").decode().rstrip("\n").splitlines()
        j0 = jan[0].split(",")
        j0[0] = str(int(j0[0]) // 1000)
        jan[0] = ",".join(j0)
        t, h = text_of(jan)
        c = counts(parse(t, name="BTCUSDT-1d-2025-01.csv"))
        fx["F-07"] = {"input": h, **c, "pass": c["file_quarantined"] and c["file_reason"] == "unit_contradicts_era"}
        sw = list(rows)
        sw[2], sw[3] = sw[3], sw[2]
        t, h = text_of(sw)
        swapped = parse(t).records
        orig = parse(text_of(rows)[0]).records
        same = [r.source_event_time for r in A.replay_order(swapped)] == [r.source_event_time for r in A.replay_order(orig)]
        fx["F-08"] = {"input": h, "valid": len(swapped), "replay_order_same": same, "pass": same and len(swapped) == 31}
        rev = b / "readme" / "rev" / "1INCHUSDT-1d-2022-03-08.zip"
        new_csv = zipfile.ZipFile(rev).read("1INCHUSDT-1d-2022-03-08.csv").decode()
        old_fields = new_csv.split(",")
        old_fields[4] = str(Decimal(old_fields[4]) + Decimal("0.001"))
        old_path, new_path = work / "1INCHUSDT-1d-2022-03-08.old.csv", work / "1INCHUSDT-1d-2022-03-08.new.csv"
        old_path.write_text(",".join(old_fields))
        new_path.write_text(new_csv)
        lm9 = "Mon, 08 Aug 2022 21:47:53 GMT"
        t_old = R.http_date_to_ns(lm9) + DAY_NS
        t_new = mtime_ns(rev)
        o1 = self.store.ingest_file(old_path, source_id="SR-04", source_approval_id="SA-01", request="fixture:F-09",
                                    retrieved_at_ns=t_old, server_last_modified=lm9)
        o2 = self.store.ingest_file(new_path, source_id="SR-04", source_approval_id="SA-01", request="fixture:F-09",
                                    retrieved_at_ns=t_new, server_last_modified=lm9)
        mk = lambda o, text: R.parse_binance_klines(text.encode(), name="1INCHUSDT-1d-2022-03-08.csv", symbol="1INCHUSDT",
                                                    interval="1d", raw=o, ingested_at=self.now()).records
        v1, v2 = mk(o1, old_path.read_text()), mk(o2, new_csv)
        merged = A.apply_revision(v1, v2)
        before = [r.version for r in A.as_of(merged, t_new - 1)]
        after = [r.version for r in A.as_of(merged, t_new)]
        fx["F-09"] = {"inputs": [o1.raw_id, o2.raw_id], "v1_basis": v1[0].available_at_basis,
                      "v2_basis": v2[0].available_at_basis, "v2_available_at_is_retrieval": v2[0].available_at == t_new,
                      "supersedes_raw": o2.supersedes_raw_id == o1.raw_id,
                      "supersedes_record": v2[0].supersedes_record_id == v1[0].record_id,
                      "seen_before_revision": before, "seen_after_revision": after,
                      "pass": before == [1] and after == [2] and v2[0].available_at_basis == "retrieved"}
        w = self.report["windows"]
        fx["F-10"] = {"epochs": w["W-C"]["epochs"],
                      "pass": len(w["W-C"]["epochs"]) == 1 and w["W-C"]["epochs"][0]["start"] == "2022-05-31"}
        f11 = w["W-F"]["ANKRGBP"]
        fx["F-11"] = {**f11, "pass": f11["last_bar"] == "2022-12-31" and not f11["listed_in_assetpairs"]}
        rest = json.loads((self.sample / "dl-sample-kraken" / "rest" / "ohlc_XBTUSD_1440.json").read_text())["result"]["XXBTZUSD"]
        dropped_date = ts_date(rest[-1][0] * R.NS["s"])
        f12 = w["W-H"]["XBTUSD"]
        fx["F-12"] = {"completed": f12["completed_bars"], "dropped": f12["dropped_incomplete"], "dropped_bar": dropped_date,
                      "pass": f12["completed_bars"] == 57 and f12["dropped_incomplete"] == 1 and dropped_date == "2026-10-27"}
        t, h = text_of([",".join(r.split(",")[:11]) for r in rows])
        c = counts(parse(t))
        fx["F-13"] = {"input": h, **c, "pass": c["file_quarantined"] and c["file_reason"] == "schema_column_count"}
        fx["F-14"] = self.recovery_fixture("fixture:F-14", [F.Response(403, b"Access Denied")],
                                           expect_ok=False, expect_calls=1, expect_reason="http_403")
        decision = int(datetime(2025, 1, 7, tzinfo=timezone.utc).timestamp()) * R.NS["s"]
        vis_before, vis_after = len(A.as_of(orig, decision)), len(A.as_of(orig, orig[0].available_at))
        fx["F-16"] = {"input": base_hash, "visible_at_2025-01-07": vis_before, "visible_from_last_modified": vis_after,
                      "pass": vis_before == 0 and vis_after == 31}
        hdr = (self.sample / "dl-sample-context" / "cftc_deacmesf.htm.hdr").read_text()
        cot_avail = R.http_date_to_ns(re.search(r"^last-modified:\s*(.+?)\s*$", hdr, re.I | re.M).group(1))
        s15 = A.is_stale("cftc:cot", cot_avail, cot_avail + 15 * DAY_NS)
        s7 = A.is_stale("cftc:cot", cot_avail, cot_avail + 7 * DAY_NS)
        fx["F-17"] = {"input": "cftc_deacmesf.htm Last-Modified", "stale_after_15d": s15, "stale_after_7d": s7,
                      "pass": s15 and not s7}
        xrecs, _ = self.we["XBTUSD"]
        end = int(datetime(2026, 10, 1, tzinfo=timezone.utc).timestamp()) * R.NS["s"]
        start = end - 365 * DAY_NS
        drop = {start + i * DAY_NS for i in range(19)}
        thinned = [r for r in xrecs if r.event_time_ns() not in drop]
        restored = [r for r in xrecs if r.event_time_ns() not in drop or r.event_time_ns() == start]
        q346, q347 = A.qualifies(thinned, [], start, end, DAY_NS), A.qualifies(restored, [], start, end, DAY_NS)
        fx["F-18"] = {"input": self.full.raw_id + "#XBTUSD_1440.csv", "qualifies_346": q346, "qualifies_347": q347,
                      "pass": (not q346) and q347}

    def recovery_fixture(self, request, script, *, expect_ok, expect_calls, expect_reason=None, checksum=None,
                         expect_slept=()):
        transport = FakeTransport(script)
        slept = []
        res = F.fetch(request, transport, self.store, source_id="SR-99", source_approval_id="fixture",
                      published_checksum=checksum, sleep=slept.append)
        reason = res.gap.evidence if res.gap else None
        ok = ((res.raw is not None) == expect_ok and transport.calls == expect_calls
              and (expect_reason is None or reason == expect_reason) and slept == list(expect_slept))
        return {"calls": transport.calls, "slept_s": slept, "stored": res.raw is not None, "gap_reason": reason,
                "gap_state": res.gap.availability_state if res.gap else None, "pass": ok}

    def recovery(self):
        body = b"payload"
        cl = {"Content-Length": str(len(body))}
        rc = {
            "RC-01_5xx_then_ok": self.recovery_fixture("fixture:RC-01a", [F.Response(503), F.Response(200, body, cl)],
                                                       expect_ok=True, expect_calls=2, expect_slept=(30,)),
            "RC-01_all_fail": self.recovery_fixture("fixture:RC-01b", [TimeoutError(), F.Response(500), ConnectionError(),
                                                                       F.Response(502)],
                                                    expect_ok=False, expect_calls=4, expect_reason="http_502",
                                                    expect_slept=(30, 120, 600)),
            "RC-02_403": self.report["fixtures"]["F-14"],
            "RC-02_429_retry_after": self.recovery_fixture("fixture:RC-02b", [F.Response(429, b"", {"Retry-After": "60"}),
                                                                              F.Response(200, body, cl)],
                                                           expect_ok=True, expect_calls=2, expect_slept=(60,)),
            "RC-02_429_no_header": self.recovery_fixture("fixture:RC-02c", [F.Response(429)], expect_ok=False,
                                                         expect_calls=1, expect_reason="http_429"),
            "RC-03_truncated_then_ok": self.recovery_fixture("fixture:RC-03", [F.Response(200, body[:3], cl),
                                                                               F.Response(200, body, cl)],
                                                             expect_ok=True, expect_calls=2, expect_slept=(30,)),
            "RC-04_checksum_repeated": self.recovery_fixture("fixture:RC-04", [F.Response(200, body, cl)] * 4,
                                                             expect_ok=False, expect_calls=4,
                                                             expect_reason="checksum_mismatch", checksum="00" * 32,
                                                             expect_slept=(30, 120, 600)),
        }
        rc.update(self.recovery_rc05_to_rc08())
        self.report["recovery"] = rc

    def recovery_rc05_to_rc08(self):
        """RC-05 crash marker, RC-06 disk full, RC-07/RC-08 clock offset (DEC-065)."""
        import errno
        from . import live_records as LR

        class Crash(BaseException):
            pass

        orig_copy = RawStore.__dict__["_copy"]
        out = {}
        src = self.out / "fixtures" / "rc-src.bin"
        src.write_bytes(b"rc" * 500)

        def half_then_crash(a, b):
            Path(b).write_bytes(Path(a).read_bytes()[:100])
            raise Crash()

        store = RawStore(self.out / "rc05-store")
        RawStore._copy = staticmethod(half_then_crash)
        try:
            store.ingest_file(src, source_id="SR-99", source_approval_id="fixture", request="fixture:RC-05")
        except Crash:
            pass
        finally:
            RawStore._copy = orig_copy
        store.close()  # the crashed process's lock is released
        restarted = RawStore(self.out / "rc05-store")  # recover() runs on opening
        rec = restarted.last_recovery
        obj = restarted.ingest_file(src, source_id="SR-99", source_approval_id="fixture", request="fixture:RC-05")
        outcomes = [e.outcome for e in restarted.journal_entries()]
        byte_identical = restarted.read(obj.raw_id) == src.read_bytes()
        restarted.close()
        clean = RawStore(self.out / "rc05-clean")  # the same ingest with no crash
        obj2 = clean.ingest_file(src, source_id="SR-99", source_approval_id="fixture", request="fixture:RC-05")
        same_object = obj2.raw_id == obj.raw_id and clean.read(obj2.raw_id) == restarted.read(obj.raw_id)
        clean.close()
        out["RC-05_crash_marker"] = {
            "incomplete_found": len(rec["incomplete"]), "partials_removed": len(rec["partials_removed"]), "journal": outcomes,
            "reingest_byte_identical_to_source": byte_identical, "identical_to_uncrashed_ingest": same_object,
            "pass": len(rec["incomplete"]) == 1 and len(rec["partials_removed"]) == 1
            and outcomes == ["started", "recovered_incomplete", "started", "stored"] and byte_identical and same_object}

        def enospc(a, b):
            Path(b).write_bytes(b"partial")
            raise OSError(errno.ENOSPC, "No space left on device")

        store6 = RawStore(self.out / "rc06-store")
        transport = FakeTransport([F.Response(200, b"payload", {"Content-Length": "7"})] * 4)
        RawStore._copy = staticmethod(enospc)
        try:
            res = F.fetch("fixture:RC-06", transport, store6, source_id="SR-99", source_approval_id="fixture",
                          sleep=lambda s: None)
        finally:
            RawStore._copy = orig_copy
        parts = list((self.out / "rc06-store").glob("objects/*/*.part"))
        store6.close()
        out["RC-06_disk_full"] = {
            "gap_reason": res.gap.evidence if res.gap else None, "gap_state": res.gap.availability_state if res.gap else None,
            "calls": transport.calls, "partials_left": len(parts),
            "pass": res.raw is None and res.gap is not None and res.gap.evidence.startswith("write_failed")
            and res.gap.availability_state == "SOURCE_UNAVAILABLE" and transport.calls == 1 and not parts}
        t0 = 1_793_181_600_000_000_000
        frame = ('{"channel":"trade","type":"update","data":[{"symbol":"BTC/USD","side":"buy","price":1.50,'
                 '"qty":0.00000010,"ord_type":"market","trade_id":7,"timestamp":"2026-10-28T10:00:00.000001Z"}]}')

        def one(offsets, recv=t0):
            r = LR.normalize([(0, recv, frame)], offsets, raw_id="fixture", ingested_at=0)[0]
            return r.fields["timestamp_uncertainty_ms"], r.quality_flags

        cases = {"50ms": one([(t0 - 1, 50.0)]), "150ms": one([(t0 - 1, 150.0)]),
                 "minus1500ms": one([(t0 - 1, -1500.0)]), "70000ms": one([(t0 - 1, 70000.0)]),
                 "sample_after_frame": one([(t0 + 1, 50.0)]), "sample_2min_old": one([(t0 - 120 * 10**9, 50.0)]),
                 "sample_2h_old": one([(t0 - 7200 * 10**9, 50.0)])}
        r = LR.normalize([(0, t0, frame)], [(t0 - 1, 50.0)], raw_id="fixture", ingested_at=0)[0]
        out["RC-07_RC-08_clock"] = {k: {"uncertainty_ms": u, "flags": f} for k, (u, f) in cases.items()}
        out["RC-07_RC-08_clock"]["strings_kept"] = [r.fields["price"], r.fields["qty"]]
        out["RC-07_RC-08_clock"]["pass"] = (
            cases["50ms"] == (None, []) and cases["150ms"] == (150.0, [])
            and cases["minus1500ms"] == (1500.0, ["clock_abstain_intraday"])
            and cases["70000ms"][1] == ["clock_abstain_intraday", "clock_abstain_daily"]
            and cases["sample_after_frame"][1] == ["clock_offset_unknown", "clock_abstain_intraday"]
            and cases["sample_2min_old"][1] == ["clock_abstain_intraday"]
            and cases["sample_2h_old"][1] == ["clock_abstain_intraday", "clock_offset_stale"]
            and [r.fields["price"], r.fields["qty"]] == ["1.50", "0.00000010"])
        return out

    def criteria(self):
        recs = self.all_records
        objs = self.store.objects
        untraceable = sum(1 for r in recs if r.raw_id not in objs or r.rights_id is None or (
            objs[r.raw_id].container_raw_id is not None and objs[r.raw_id].container_raw_id not in objs))
        missing_times = sum(1 for r in recs if None in (r.source_event_time, r.received_at, r.ingested_at, r.available_at)
                            or not r.available_at_basis or r.source_time_unit not in R.NS)
        missing_feed = sum(1 for r in recs if not (r.venue and r.source_id and r.feed_id))
        fixtures = self.report["fixtures"]
        recovery = {k: v for k, v in self.report["recovery"].items() if isinstance(v, dict)}
        self.report["criteria"] = {
            "records_checked": len(recs), "CV-01_untraceable": untraceable, "CV-02_missing_times_or_basis": missing_times,
            "CV-08_missing_venue_feed": missing_feed, "fixtures_run": len(fixtures),
            "fixtures_passed": sorted(k for k, v in fixtures.items() if v.get("pass")),
            "fixtures_failed": sorted(k for k, v in fixtures.items() if not v.get("pass")),
            "fixtures_not_run": ["F-15 (live)"],
            "recovery_passed": sorted(k for k, v in recovery.items() if v.get("pass")),
            "recovery_failed": sorted(k for k, v in recovery.items() if not v.get("pass")),
        }

    def run(self):
        for step in (self.w_a, self.w_b, self.w_c, self.w_d, self.w_e, self.w_f, self.w_g, self.w_h, self.w_i,
                     self.fixtures, self.recovery, self.criteria):
            step()
        return self.report


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--sample-root", required=True, type=Path)
    ap.add_argument("--out", required=True, type=Path)
    args = ap.parse_args()
    report = Run(args.sample_root, args.out).run()
    (args.out / "report.json").write_text(json.dumps(report, indent=1, sort_keys=True, default=str))
    print(json.dumps({"criteria": report["criteria"]}, indent=1))


if __name__ == "__main__":
    main()
