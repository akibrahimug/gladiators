# P01 sample-plan results (steps 0, 1 and 3)

[Task](../../tasks/TASK-P01-013.md) · [Sample plan](data-access-decision.md#representative-sample-plan) · [`source_approval` records](source-approvals.md) · [Acceptance objectives](acceptance-objectives.md) · [G01 gate record](g01-gate-record.md)

**Status: results, 2026-10-27.** The sample ran under DEC-035 and DEC-044 after G01 passed (DEC-047).
- **Purpose:** these results verify the sources. They are not research evidence, and no return, signal or model was computed.
- **Not run:** step 2 (live capture), which needs its own authorisation.
- **Where the files are:** outside the repository, in the coordinator's scratchpad. They are identified below by name and SHA-256, and a full manifest of 54 files was kept with them.
- **Analysis:** the coordinator's own scripts, run with `python3 -I` on the downloaded files.
- **Destination:** the plan sends results to P02 `capture-validation-plan.md`. That file does not exist until P02's packets are expanded, so the results are recorded here, and TASK-P02-001 should carry them forward.

**Operating conditions (DEC-044).**
- **Downloads:** sequential, with pauses between Binance requests. `data.binance.vision/robots.txt` returns 404 (no exclusion published). `assets.kraken.com/robots.txt` returns an HTML page, not a robots file.
- **Checksums:** every published checksum was verified (below).
- **REST calls:** three keyless Kraken calls (`OHLC` twice, `AssetPairs` once), each made on explicit invocation.
- **No contact:** no account, key or vendor contact.
- **BLS:** BLS pages return HTTP 403 to `curl`. They were read through the fetch tool instead; no bot-detection was bypassed.
- **Kraken download size:** the plan's wording did not state sizes. The full Kraken archive is 9.5 GB, so the coordinator asked the user before downloading it. On 2026-10-27 the user chose "Both, 10.1 GB (Recommended)".

## Step 0 — Binance Vision (SR-04, SA-01)

**Files.**
- **Daily bars:** `1d` monthly klines for December 2024 and January 2025, for 10 sample symbols, with their `.CHECKSUM` files. The symbols are BTC, ETH, BNB, SOL, XRP, ADA, DOGE, LTC, LINK and DOT, each quoted in USDT. They were chosen for verification only and are not a W-1 selection.
- **Trades:** one day of `trades`, `ETHUSDT-trades-2025-01-15.zip` (27,149,790 bytes, SHA-256 `0fc1d699baa63e2a28e70e044aa64ef07895b2000231fbad7763167a779cfa7d`).
- **Delisting check:** S3 listings for five delisted or renamed symbols, and LUNAUSDT and LUNCUSDT months around 2022-05.
- **Revision check:** the README's kline update changelog, and one revised file.

| Item | Result | Outcome |
| --- | --- | --- |
| Checksums | 21 of 21 `.CHECKSUM` files match (20 kline files and 1 trades file), plus 7 more in the delisting and revision checks | **Passes S-4b** for the files sampled |
| Unit change at 2025-01-01 | December 2024 `open_time` has 13 digits (ms); January 2025 has 16 digits (µs), in every symbol. Trades on 2025-01-15 are in µs | **Documented and observed.** Ingest must detect the unit per file, not per symbol |
| Header row | None in klines or trades | Recorded for the P02 parser |
| Open/close alignment | `close_time − open_time` = 1 day − 1 tick in every row: 86,399,999 in ms files, 86,399,999,999 in µs files. Bars start at 00:00 UTC | **Observed.** `close_time` is the last tick of the bar, not the next bar's open |
| Q-1 (daily-bar validation) | 620 rows: 0 duplicate timestamps, 0 invalid OHLC, 0 non-finite values, 0 zero-volume bars. Timestamps are UTC epoch integers, so none is timezone-naive | **Passes** on the sample |
| Q-2 (no-trade intervals) | 0 missing days across all 20 files | **Passes** on the sample; the sample is too liquid to exercise Q-2 |
| `isBuyerMaker` coverage | 2,689,488 trades, all with 7 columns. `isBuyerMaker` is `True` in 1,222,152 and `False` in 1,467,336, with none empty. Trade IDs are contiguous, and times never decrease | **Documented** for this day (H-OF3) |
| F-5c (delisted symbols) | Files remain for delisted symbols: WAVESUSDT (2019-01 to 2024-06), MATICUSDT (2019-04 to 2024-09), BCCUSDT (2017-11 to 2018-11) and VENUSDT (2018-06 to 2018-10) | **F-5c: Documented.** Delisted symbols keep their history, so a point-in-time universe is possible |
| Symbol reuse (new) | LUNAUSDT is one series from 2020-08 to 2026-09. Its last old-asset bar is 2022-05-13 (close 0.00005). Then nothing until 2022-05-31, when it opens at 1.00. The old asset reappears separately as LUNCUSDT from 2022-09-09. The archive has no field marking the change of asset | **New item F-5e (Unresolved):** a symbol name does not identify an asset over time. P02 needs a per-source instrument-identity rule, for example breaking a series at a gap of more than *n* days or a price discontinuity, and checking against listing announcements |
| T-2a (revisions) | The README's update list is "exhaustive" and has two entries. The 2022-08-08 kline changelog has 73,234 rows: 1,186 are `1d` daily files and none is a monthly file. The revised `1INCHUSDT-1d-2022-03-08.zip` served today has the **new** checksum (`f7398aba…f178016`), and its `.CHECKSUM` matches. The old file is not served; it was replaced in place (`Last-Modified` 2022-08-08 21:47 UTC). The monthly file for 2022-03 was rewritten on 2022-09-02 without a changelog entry; its 2022-03-08 row equals the revised daily file | **Documented, with a limitation.** Revisions appear only as an in-place replacement plus a changelog row. Earlier versions survive only if we keep them. Monthly rewrites are not logged, so P02 should record each file's checksum and `Last-Modified` at retrieval |
| Publication lag (new evidence for T-2a) | `Last-Modified`: daily files about 2 to 3 hours after the day ends (trades 2025-01-15 → 2025-01-16 03:01 UTC; klines 2026-10-25 → 2026-10-26 01:55 UTC). Monthly files 5 to 8 days after the month ends (2024-12 → 2025-01-08; 2025-01 → 2025-02-08; 2026-09 → 2026-10-05) | Recorded. It does not change T-2a: bar `available_at` follows the bar's end, and archive retrieval time is provenance |

## Step 1 — Kraken archive and REST (SR-05, SA-02)

**Files.**

| File | Size (bytes) | SHA-256 | Integrity |
| --- | --- | --- | --- |
| `Kraken_OHLCVT_Full.zip.part00` to `part04` | 9,546,553,626 in total | The published `OHLCVT_Full_PARTS_SHA256SUMS.txt` | **All 5 parts: OK** |
| `Kraken_OHLCVT_Full.zip` (parts joined, as the article instructs) | 9,546,553,626 | `bc273e9027470b07d790a7fa4df9bb43f0dfc527c20c6ecae48402e123e7b1c7` | Coordinator's own hash |
| `Kraken_OHLCVT_2026Q3.zip` | 576,348,633 | `96daae63c7b3acb522892e1f602f9c564d1a3fb659089d9b0699282f30d41226` | **No published checksum.** The README inside says `shasum -a 256 -c SHA256SUMS.txt`, but neither ZIP contains that file |
| REST `OHLC` 1440, XBTUSD and ETHUSD (since 2026-08-31) | — | `6144e5f8…` and `7e99439c…` | — |
| REST `AssetPairs` | — | `297e258b…` | — |

| Item | Result | Outcome |
| --- | --- | --- |
| Layout | One CSV per pair and interval, with no header. Columns `timestamp,open,high,low,close,volume,trades`. Each ZIP has a `README.md` and a `MANIFEST.json` (schema 1, release `r1`, generated 2026-10-01). The full archive covers "each pair's first trade on Kraken to 2026-09-30" | **Documented** (resolves the plan's open question about the layout) |
| F-4i (timestamp semantics) | README: "unix seconds, start of the bar". For XBTUSD and ETHUSD, 2026-09-01 to 09-07, REST and the archive use the same stamps (00:00 UTC). REST also returns today's incomplete bar | **F-4i: Documented.** Bars are stamped at their start; a bar's `available_at` is its start plus one interval |
| F-4h (value differences) | 14 daily bars compared on open, high, low, close, volume and trade count: **0 differences**. REST's VWAP has no archive column | **F-4h: Documented** for the sample. No VWAP in the archive |
| F-4f (intervals) | Both READMEs list 1, 5, 15, 60, 240, 720 and 1440 minutes. Q3 has exactly those 7 intervals for each of 1,436 pairs. The full archive also has 30-minute files for 42 pairs, which the README does not mention | **F-4f: Documented.** 30-minute bars are not generally available |
| Manifest consistency | The full archive's README and MANIFEST say 1,760 pairs and 12,350 files. The ZIP holds 1,759 distinct pairs and 12,349 pair-interval CSVs. `BTCUSD` has only a 1-minute file (2022-01-01 to 2023-12-31). An undocumented `BTCUSD_Daily_OHLC.csv` (3,727 rows) is also present. Manifest `coverage.start` is 2013-09-11; XBTUSD starts 2013-10-06 | Recorded as a minor inconsistency. Use the PAIR_INTERVAL files only, and verify counts at ingest |
| First and last bars, row counts (1440) | XBTUSD: 4,731 rows, 2013-10-06 to 2026-09-30. ETHUSD: 4,067 rows, 2015-08-07 to 2026-09-30 | **S-5: met** for the two main pairs |
| Q-1 | XBTUSD, ETHUSD and four delisted pairs: 0 duplicates, 0 unsorted, 0 misaligned, 0 invalid OHLC, 0 non-positive volumes, 0 non-finite values | **Passes** on the sample |
| Q-2 (no-trade intervals) | Missing days: XBTUSD 12, all from 2013-10 to 2014-12. ETHUSD 6, five in 2015-08 to 2015-10 and one on 2018-01-12. The four delisted pairs miss 0 % to 3.7 % of days. The archive cannot tell a no-trade day from an outage | Under DEC-040 each missing day is status-unknown, with no new entries. **Q-2 classification is not possible from the archive alone**, so missing days go to the status-unknown class. This applies the accepted rule; nothing changes |
| F-4g (delisted pairs) | 322 pairs are in the full archive but not in Q3. Today's `AssetPairs` lists 1,464 pairs. Of the 322, 311 are absent from it, 10 are `post_only` and 1 is `cancel_only`. Delisted pairs keep their full history (for example ANTETH 2020-11-24 to 2024-06-30; ANKRGBP 2021-05-24 to 2022-12-31). **But 283 of the 322 last bars fall on a quarter-end day** (105 on 2025-12-31). Trades continue late on that day (ANKRGBP's last 1-minute bar is 2022-12-31 22:36) | **F-4g: Documented**, with a new limitation. The archive holds delisted pairs, but it does not give a delisting date. The last bar is an upper bound, and it clusters at quarter-ends, which is consistent with delistings or archive cuts made at quarter boundaries. This is **new item F-4j (Unresolved):** W-1's rule needs a delisting date from another source, such as Kraken announcements or a forward `AssetPairs` snapshot |

## Step 3 — Context publication times (SA-04, SA-05, SA-06)

| Source | Release checked | Observed | Compared with the schedule | Outcome |
| --- | --- | --- | --- | --- |
| FOMC statement (SA-04) | 2026-09-16 and 2026-07-29 statements (`monetary20260916a.htm`, `ff5c4ee5…`) | Each page says "For release at 2:00 p.m. EDT". `Last-Modified` 2026-09-16 18:00:17 UTC, which is 14:00:17 EDT. The 2019-07-31 and 2022-11-02 statements carry the same line; their `Last-Modified` dates are from 2026-02, from later edits | **New:** each statement page states its own release time, historical ones included. SA-04 records "Statement release time is not documented", which held for the calendar page only | **Proposal for the reviewer** (below). The forward-only rule stays in force until then |
| FOMC minutes (SA-04) | Minutes of the 2026-07-29 meeting (`fomcminutes20260729.htm`, `42a83b49…`) | "for release at 2:00 p.m.". `Last-Modified` 2026-08-19 18:01:21 UTC, three weeks after the meeting | Matches "three weeks after" | **S-7: confirmed** for the sample |
| CPI (SA-05) | September 2026 CPI | "embargoed until 8:30 a.m. (ET) Wednesday, October 14, 2026" | The current schedule begins with the October 2026 reference month, so September's scheduled row is no longer shown. The release states 8:30 a.m. ET | **S-7: consistent.** Historical release dates remain a P02 dependency (BLS archive pages) |
| CFTC COT (SA-06) | Report for positions as of 2026-10-20 (`deacmesf.htm`, `0078b0e7…`) | `Last-Modified` Friday 2026-10-23 19:27:36 UTC, which is 15:27:36 EDT | About 2.5 minutes **before** the scheduled 3:30 p.m. ET | **S-7: consistent.** The 3:30 p.m. `available_at` is not earlier than true availability by more than minutes, which is immaterial at the daily horizon (W-5). `Last-Modified` is server metadata, not proof of first visibility |

## Outcomes for the follow-up items

| Item | Before | After |
| --- | --- | --- |
| F-4f | Open (sample) | **Documented:** 7 standard intervals; 30-minute bars for 42 pairs only |
| F-4g | Open (sample) | **Documented:** delisted pairs present; delisting dates not given (new F-4j) |
| F-4h | Narrowed | **Documented:** 0 differences in 14 bars; no VWAP column |
| F-4i | Open (sample) | **Documented:** bar-start stamps |
| F-5c | Open | **Documented:** delisted symbols keep their files |
| T-2a (Binance revisions) | Documented from README | **Documented and observed:** replaced in place; monthly rewrites unlogged |
| S-7 (FOMC minutes, CPI, COT) | Documented | **Confirmed** on one release each |
| **F-4j (new)** | — | **Unresolved:** Kraken delisting dates for W-1 |
| **F-5e (new)** | — | **Unresolved:** Binance symbol reuse (LUNAUSDT) needs an instrument-identity rule |
| F-4d | — | Not part of steps 0, 1 or 3; unchanged |

## For the G01 reviewer

These results do not change any accepted limitation. They do change some S-criterion standings in the records, and under the records' own rule (sample verification, [source approvals](source-approvals.md)) such changes need the reviewer's confirmation. They are listed here and **not yet applied** to the records:
1. **SA-02, S-4b:** the "timestamp semantics are open" part closes, because F-4i and F-4f are documented. The quarterly increment has no published checksum, so integrity is met for the full archive only.
2. **SA-02, S-5:** "delisted pairs are open" becomes "delisted pairs are present; delisting dates are not given (F-4j)".
3. **SA-01, S-5:** "delisted symbols are open" closes (F-5c), and a new limitation is added: symbol reuse (F-5e).
4. **SA-04, S-7 (proposal):** historical statement events could use `available_at` = the release time stated on each statement page, instead of forward-only. The confirmed rule (DEC-047) stays in force unless the reviewer amends it.
