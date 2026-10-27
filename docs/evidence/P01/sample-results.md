# P01 sample-plan results (steps 0, 1 and 3)

[Task](../../tasks/TASK-P01-013.md) · [Sample plan](data-access-decision.md#representative-sample-plan) · [`source_approval` records](source-approvals.md) · [Acceptance objectives](acceptance-objectives.md) · [G01 gate record](g01-gate-record.md)

**Status: results, 2026-10-27.** The sample ran under DEC-035 and DEC-044 after G01 passed (DEC-047).
- **Purpose:** these results verify the sources. They are not research evidence, and no return, signal or model was computed.
- **Not run:** step 2 (live capture), which needs its own authorisation.
- **Where the files are:** outside the repository, in the coordinator's scratchpad. Each claim below rests on a kept file: downloads, S3 listings, HTTP header captures and checksum outputs. The scratchpad manifest lists 111 files, and its own SHA-256 is `2492dc56071513768b49cadb21a7556f9af13f4f2c464c0dca5cf2b997261aa9`.
- **Analysis:** the coordinator's own scripts, run with `python3 -I` on the downloaded files.
- **Statuses:** F and T items use the registry vocabulary. "Passes" and "met" are used only for S and Q criteria. Inferences are marked.

**Destination.** The plan sends results to P02 `capture-validation-plan.md`. That file does not exist until P02's packets are expanded, so the results are recorded here, and TASK-P02-001 should carry them forward.

**Sample choice.** The plan says "the W-1 candidate symbols". W-1 is a point-in-time selection rule with no fixed list yet, so the sample used:
- **Binance:** 10 liquid USDT symbols, chosen for verification only: BTC, ETH, BNB, SOL, XRP, ADA, DOGE, LTC, LINK and DOT;
- **Kraken:** XBTUSD and ETHUSD, plus four pairs that are missing from the current quarter.

None of these is a W-1 selection.

## Authorisation and operating conditions

| Topic | Record |
| --- | --- |
| Authorisation | **DEC-035:** steps 0, 1 and 3, public file downloads and keyless public REST calls only. DEC-035 also says "Step 1's Kraken REST comparison falls under F-4a" (Kraken's §9 and retention ambiguity). It is effective from the G01 pass (DEC-047) |
| Download size | The approved question did not state sizes. Before downloading Kraken's 9.5 GB archive, the coordinator asked the user, 2026-10-27: "Sample step 1 (Kraken archive) is larger than the approval text implied. The full history is 5 parts from assets.kraken.com (Kraken_OHLCVT_Full.zip.part00–04), 9.5 GB in total, with published SHA-256 sums. The latest quarterly file (Kraken_OHLCVT_2026Q3.zip) is 576 MB and has no published checksum. You have 310 GB free. Files stay in the scratchpad, outside the repo. Which should I download?" Option chosen: "Both, 10.1 GB (Recommended)", described as "Only the full history can be checksum-verified and can show first bars and delisted pairs (F-4g); the plan names both files." The total was 10,122,902,259 bytes |
| Load | Sequential downloads, with pauses between Binance requests |
| Robot exclusion | `data.binance.vision/robots.txt`: HTTP 404, an S3 `NoSuchKey` error. `assets.kraken.com/robots.txt`: HTTP 404, an HTML page. No exclusion is published on either host |
| REST | Three keyless Kraken calls (`OHLC` twice, `AssetPairs` once), each made on explicit invocation |
| Checksums | Every published checksum was verified (below) |
| BLS (answered 2026-10-27: not compliant, DEC-050) | `curl` received **HTTP 403** from both BLS pages (header captures kept). The coordinator then read them through the Claude Code fetch tool, which returns a model summary, not the raw page. No robots file was consulted and no CAPTCHA was involved. Whether a second read after a 403 complies with DEC-044 was for the reviewer to decide. **Answered: it did not comply (DEC-050)**; the CPI result below is dropped |
| Not done | No account, key or vendor contact |

## Step 0 — Binance Vision (SR-04, SA-01)

**Files:**
- `1d` monthly klines for December 2024 and January 2025, for the 10 symbols, each with its `.CHECKSUM`;
- one day of `trades`: `ETHUSDT-trades-2025-01-15.zip` (27,149,790 bytes, SHA-256 `0fc1d699baa63e2a28e70e044aa64ef07895b2000231fbad7763167a779cfa7d`);
- S3 listings for six symbols: WAVES, MATIC, BCC, VEN, LUNA and LUNC, each quoted in USDT;
- LUNAUSDT months around 2022-05 and LUNCUSDT 2022-09;
- the README's kline update changelog and one revised file;
- `Last-Modified` header captures for seven files.

| Item | Result | Outcome |
| --- | --- | --- |
| Checksums | 28 of 28 `.CHECKSUM` files match: 20 kline, 1 trades, and 7 in the delisting and revision checks | S-4b integrity **passes** for the files sampled |
| Unit change at 2025-01-01 | December 2024 `open_time` has 13 digits (ms); January 2025 has 16 digits (µs), for every symbol. Trades on 2025-01-15 are in µs | **Documented.** Ingest must detect the unit per file, not per symbol |
| Header row | None in klines or trades | Recorded for the P02 parser |
| Open/close alignment | `close_time − open_time` is 1 day − 1 tick in every row: 86,399,999 in ms files and 86,399,999,999 in µs files. Bars start at 00:00 UTC | **Documented.** `close_time` is the bar's last tick, not the next bar's open |
| Q-1 (daily-bar validation) | 620 rows: 0 duplicate timestamps, 0 invalid OHLC, 0 non-finite values, 0 zero-volume bars. Timestamps are UTC epoch integers | Q-1 **passes** on the sample |
| Q-2 (no-trade intervals) | 0 missing days across the 20 files | Q-2 **passes** on the sample. The sample is too liquid to exercise Q-2 |
| `isBuyerMaker` coverage | 2,689,488 trades, all with 7 columns. `True` 1,222,152, `False` 1,467,336, none empty. Trade IDs are contiguous, and times never decrease | **Documented** for this day (H-OF3) |
| F-5c (delisted symbols) | The S3 listings show files remaining for WAVESUSDT (2019-01 to 2024-06, 66 monthly files), MATICUSDT (2019-04 to 2024-09, 66), BCCUSDT (2017-11 to 2018-11, 13) and VENUSDT (2018-06 to 2018-10, 3) | **F-5c: Documented** for these symbols. *Inference:* delisted symbols keep their history, so a point-in-time universe is possible for Binance |
| Symbol reuse (new) | LUNAUSDT is a single series from 2020-08 to 2026-09 (74 monthly files):<br>- the last bar of the old asset is 2022-05-13 (close 0.00005);<br>- there are no bars from 2022-05-14 to 2022-05-30;<br>- on 2022-05-31 the series opens at 1.00;<br>- LUNCUSDT starts on 2022-09-09.<br>No field marks the change of asset | **New F-5e, Unresolved:** a symbol name does not identify an asset over time. P02 needs a per-source instrument-identity rule |
| T-2a (revisions) | The README calls its update list "exhaustive"; it has two entries:<br>- the 2022-08-08 kline changelog has 73,234 rows, 1,186 of them `1d` daily files and **none a monthly file**;<br>- the revised `1INCHUSDT-1d-2022-03-08.zip` served today has the changelog's new checksum (`f7398aba…f178016`), and its `.CHECKSUM` matches;<br>- the old version is not served; the file was replaced in place (`Last-Modified` 2022-08-08 21:47:53 UTC);<br>- the monthly file for 2022-03 has `Last-Modified` 2022-09-02 12:19:00 UTC, with no changelog entry, and its 2022-03-08 row equals the revised daily file | **Documented:** revisions replace files in place. *Inference:* monthly files were rewritten without being logged, so the list is not exhaustive for monthly files. **This contradicts SA-01's coverage line** ("revisions are announced (two listed)") and the reassessment's "both versions are kept". The archive keeps only the latest version, so earlier versions survive only if we keep them. See reviewer item 4 |
| Publication lag (T-2a evidence) | `Last-Modified`:<br>- daily files about 2 to 3 hours after the day ends: trades for 2025-01-15 at 2025-01-16 03:01:41 UTC; klines for 2026-10-25 at 2026-10-26 01:55:25 UTC;<br>- monthly files 5 to 8 days after the month ends: 2024-12 at 2025-01-08 00:50:27; 2025-01 at 2025-02-08 12:19:52; 2026-09 at 2026-10-05 11:13:54.<br>`Last-Modified` is server metadata and a lower bound on availability only if the file was not rewritten later | Under T-2a (DEC-042) a bar's default `available_at` is the archive publication time, here the daily file's `Last-Modified`, about 2 to 3 hours after the day ends. Using bar close instead needs the conditions T-2a states. **No change is made** |

## Step 1 — Kraken archive and REST (SR-05, SA-02)

**Files:**

| File | Size (bytes) | SHA-256 | Integrity |
| --- | --- | --- | --- |
| `Kraken_OHLCVT_Full.zip.part00` to `part04` | 9,546,553,626 in total | As published in `OHLCVT_Full_PARTS_SHA256SUMS.txt` | **All 5 parts OK** (`shasum -a 256 -c` output kept). The parts were deleted after being joined, so this check cannot be re-run without downloading them again |
| `Kraken_OHLCVT_Full.zip` (the parts joined, as the article instructs) | 9,546,553,626 | `bc273e9027470b07d790a7fa4df9bb43f0dfc527c20c6ecae48402e123e7b1c7` | Coordinator's own hash |
| `Kraken_OHLCVT_2026Q3.zip` | 576,348,633 | `96daae63c7b3acb522892e1f602f9c564d1a3fb659089d9b0699282f30d41226` | **No published checksum.** The README inside says `shasum -a 256 -c SHA256SUMS.txt`, but neither ZIP contains that file |
| REST `OHLC` 1440 for XBTUSD and ETHUSD, since 2026-08-31 | — | `6144e5f8…` and `7e99439c…` | — |
| REST `AssetPairs` | — | `297e258b…` | — |

| Item | Result | Outcome |
| --- | --- | --- |
| Layout | One CSV per pair and interval, with no header. Columns: `timestamp,open,high,low,close,volume,trades`. Each ZIP has a `README.md` and a `MANIFEST.json` (schema 1, release `r1`, generated 2026-10-01). The full archive covers "each pair's first trade on Kraken to 2026-09-30" | **Documented.** This answers the plan's open question about the layout |
| F-4i (timestamp semantics) | The README says "unix seconds, start of the bar". REST and the archive use identical stamps (00:00 UTC) for XBTUSD and ETHUSD, 2026-09-01 to 09-07. REST also returns today's incomplete bar | **F-4i: Documented.** Bars are stamped at bar start, so bar end (start plus one interval) is the earliest possible `available_at`. Under T-2a the default stays the archive publication time; for the quarterly archive that is quarterly (Q3 was generated 2026-10-01) |
| F-4h (values and availability) | 14 daily bars compared (7 per pair) on open, high, low, close, volume and trade count:<br>- prices and trade counts are equal;<br>- volumes agree within a relative tolerance of 10⁻⁹, but are **not equal as strings**: the archive stores binary-float values (`2586.9734754599417`) where REST gives 8 decimals (`2586.97347546`).<br>REST's VWAP has no archive column. F-4h asks about availability at bar close (round 2), and a match against today's REST response does not show what was served at bar close | **F-4h: Unresolved (narrowed):** the values match within 10⁻⁹. Availability at bar close is still unestablished. For the P02 parser: volumes need decimal rounding to 8 places before any comparison |
| F-4f (intervals) | Both READMEs list 1, 5, 15, 60, 240, 720 and 1440 minutes. Q3 has exactly those 7 intervals for each of its 1,436 pairs. The full archive also has 30-minute files for 42 pairs, which the README does not mention | **F-4f: Documented.** *Inference:* 30-minute bars cannot be relied on |
| Manifest consistency | The README and MANIFEST say 1,760 pairs; MANIFEST says 12,350 files. The ZIP holds 1,759 distinct pairs and 12,349 pair-interval CSVs. Other irregularities:<br>- `BTCUSD` has only a 1-minute file (2022-01-01 to 2023-12-31);<br>- an undocumented `BTCUSD_Daily_OHLC.csv` (3,727 rows) is present;<br>- MANIFEST gives `coverage.start` as 2013-09-11, but XBTUSD starts 2013-10-06 | A minor inconsistency, recorded. Use the PAIR_INTERVAL files and verify counts at ingest |
| First and last bars, and row counts (1440) | XBTUSD: 4,731 rows, 2013-10-06 to 2026-09-30. ETHUSD: 4,067 rows, 2015-08-07 to 2026-09-30 | Shows history length for the two main pairs. The S-5 standing is reviewer item 2 |
| Q-1 | XBTUSD, ETHUSD and four delisted pairs: 0 duplicates, 0 out of order, 0 misaligned, 0 invalid OHLC, 0 non-positive volumes, 0 non-finite values | Q-1 **passes** on the sample |
| Q-2 (no-trade intervals) | The README says "Bars with no trades are omitted entirely -- the series is sparse, not padded". Missing days:<br>- XBTUSD 12, all between 2013-10 and 2014-12;<br>- ETHUSD 6, five in 2015-08 to 2015-10 and one on 2018-01-12;<br>- the four delisted pairs, 0 % to 3.7 % of days.<br>*Inference:* some missing days may be outages rather than no-trade days, for example ETHUSD 2018-01-12; the archive cannot tell them apart | Q-2 requires "**100 % classified**" as a no-trade interval or a data gap. That is **not achievable from the archive alone**. DEC-040's status-unknown class is a third class. See reviewer item 3 |
| F-4g (delisted pairs) | **323 pairs** are in the full archive but not in Q3, counting `BTCUSD`, which has only 2022–23 one-minute data. The rest of this row covers the other **322**, which have daily files:<br>- today's `AssetPairs` lists 1,464 pairs; 311 of the 322 are absent from it, 10 are `post_only` and 1 is `cancel_only`;<br>- delisted pairs keep their full history, for example ANTETH 2020-11-24 to 2024-06-30 and ANKRGBP 2021-05-24 to 2022-12-31;<br>- **283 of the 322 last bars fall on a quarter-end day** (105 on 2025-12-31), and trading continues late on that day: ANKRGBP's last 1-minute bar is 2022-12-31 22:36 | **F-4g: Documented:** the archive holds delisted pairs. **New F-4j, Unresolved:** the archive gives no delisting date. The last bar is only an upper bound. *Inference:* the quarter-end clustering fits delistings or archive cuts made at quarter boundaries. W-1's rule needs a delisting date from another source |

## Step 3 — Context publication times (SA-04, SA-05, SA-06)

The plan asks for one FOMC, one CPI and one COT release, comparing the observed publication time with the published schedule. Only current releases were checked. **The historical release dates, for FOMC meetings and minutes, CPI and COT, were not checked. They stay P02 dependencies**, as the records allow.

| Source | Release checked | Observed | Against the schedule | Outcome |
| --- | --- | --- | --- | --- |
| FOMC statement (SA-04) | The 2026-09-16 and 2026-07-29 statements (`monetary20260916a.htm`, `ff5c4ee5…`) | Each page states "For release at 2:00 p.m. EDT". `Last-Modified` is 2026-09-16 18:00:17 UTC, which is 14:00:17 EDT. The 2019-07-31 and 2022-11-02 statements carry the same line; their `Last-Modified` dates are from 2026-02, after later edits | **New:** each statement page states its own release time, including historical statements. SA-04's "Statement release time is not documented" was true only of the calendar page | Reviewer item 5. **Answered 2026-10-27: stated times are used for historical statements (DEC-049)** |
| FOMC minutes (SA-04) | Minutes of the 2026-07-29 meeting (`fomcminutes20260729.htm`, `42a83b49…`) | States "for release at 2:00 p.m.". `Last-Modified` is 2026-08-19 18:01:21 UTC, three weeks after the meeting | Consistent with "three weeks after" | Consistent on one release. The historical dates are a P02 dependency |
| CPI (SA-05), **indirect; dropped (DEC-050)** | September 2026 CPI | Through the fetch tool, after a 403 response: "embargoed until … 8:30 a.m. (ET) Wednesday, October 14, 2026" | The current schedule begins at the October 2026 reference month, so September's scheduled row is no longer shown | **Dropped (DEC-050).** CPI timing, current and historical, is a P02 dependency |
| CFTC COT (SA-06) | The report for positions as of 2026-10-20 (`deacmesf.htm`, `0078b0e7…`) | `Last-Modified` is Friday 2026-10-23 19:27:36 UTC, which is 15:27:36 EDT | The scheduled 3:30 p.m. ET is about 2.5 minutes **after** the observed time. Setting `available_at` to 3:30 p.m. therefore introduces no lookahead | Consistent on one release. `Last-Modified` is server metadata, not proof of first visibility. The historical dates are a P02 dependency |

## Outcomes for the follow-up items

The "Before" column uses the registry statuses ([round 2](source-followups-2.md)).

| Item | Before | After |
| --- | --- | --- |
| F-4f | Unresolved | **Documented:** 7 standard intervals; 30-minute bars for 42 pairs only |
| F-4g | Unresolved | **Documented:** delisted pairs are present. Their delisting dates are not given (new F-4j) |
| F-4h | Unresolved (narrowed) | **Unresolved (narrowed):** values match within 10⁻⁹; availability at bar close is not established; the archive has no VWAP |
| F-4i | Unresolved | **Documented:** stamps are at bar start |
| F-5c | Unresolved | **Documented:** delisted symbols keep their files |
| T-2a (Binance revisions) | Documented from the README | **Documented:** files are replaced in place, and monthly rewrites are not logged (reviewer item 4) |
| **F-4j (new)** | — | **Unresolved:** Kraken delisting dates for W-1 |
| **F-5e (new)** | — | **Unresolved:** Binance symbol reuse needs an instrument-identity rule |
| F-4d | — | Not in steps 0, 1 or 3; unchanged |

## For the G01 reviewer

**Answered 2026-10-27; applied as DEC-048 to DEC-050** ([answers](#reviewer-answers-2026-10-27); [amendments](source-approvals.md#amendments-2026-10-27)). As first written, these were not applied, because some change an S- or Q-criterion standing or a record's coverage line, and the records' own rule says such changes need the reviewer's confirmation ([source approvals](source-approvals.md), sample verification).

1. *(DEC-048)* **SA-02, S-4b:** close the "timestamp semantics are open" part (F-4i and F-4f are Documented). Integrity is met for the full archive only, because the quarterly increment has no published checksum.
2. *(DEC-048)* **SA-02 and SA-01, S-5:**
   - SA-02: replace "delisted pairs are open" with "present; delisting dates not given (F-4j)", and mark S-5 met for XBTUSD and ETHUSD.
   - SA-01: close "delisted symbols are open" (F-5c), and add symbol reuse (F-5e) as a limitation.
3. *(DEC-048)* **Q-2:** "100 % classified" cannot be achieved for the archived bars of either venue. Proposal: amend Q-2 so that each missing interval is classified as no-trade, data gap or **status-unknown** (DEC-040), with 100 % of intervals in one of the three classes.
4. *(DEC-048)* **SA-01 coverage (T-2a):** replace "revisions are announced (two listed); each revision is a correction with its own `available_at`" with "revisions replace files in place; daily revisions are listed, monthly rewrites are not; we keep each retrieved version with its checksum and `Last-Modified`".
5. *(DEC-049)* **SA-04, S-7 (proposal):** historical FOMC statement events would use `available_at` = the release time stated on each statement page, instead of forward-only. The confirmed rule (DEC-047) stays in force unless the reviewer amends it.
6. *(DEC-050)* **DEC-044 and BLS:** decide whether the BLS read after a 403 complied with DEC-044. If it did not, the CPI result is dropped, and CPI release timing becomes a P02 dependency.

## Reviewer answers, 2026-10-27

The G01 reviewer (the user, DEC-034) answered three questions. Each question and the chosen option are quoted verbatim.

| Items | Question (verbatim) | Chosen option | Decision |
| --- | --- | --- | --- |
| 1 to 4 | "Sample results, items 1–4: these are record updates that only reflect what the files showed. (1) Kraken record SA-02: mark the timestamp question closed; integrity is met only for the full archive, because the quarterly file has no checksum. (2) Delisted history: for Kraken, delisted pairs are present but have no delisting dates (new F-4j); for Binance, delisted symbols keep their files, but one symbol can cover two assets over time (new F-5e, e.g. LUNAUSDT). (3) Missing-bar rule Q-2: allow a third class, 'status-unknown', since the archives can't tell a no-trade day from an outage. (4) Binance record SA-01: revisions replace files in place, monthly rewrites aren't logged, and we keep each version we download. Apply these?" | "Apply all four (Recommended)" — "Each one just records what the sample showed; none loosens a rule beyond what the data allows." | DEC-048 |
| 5 | "Item 5: every FOMC statement page, including historical ones, states 'For release at 2:00 p.m. EDT'. Should historical statement events use that stated time as available_at, replacing the forward-only rule you confirmed under DEC-047?" | "Use stated times (Recommended)" — "The time is printed on each statement page, so history becomes usable with no lookahead; it amends SA-04 and W-7." | DEC-049 |
| 6 | "Item 6: BLS returned HTTP 403 to curl, so I read the CPI pages through the fetch tool instead, which gives a model summary of the page. Was that acceptable under the download rules (DEC-044)?" | "Not OK; drop it (Recommended)" — "Treat a 403 as a refusal. Drop the indirect CPI result and make CPI timing a P02 dependency; future reads use the browser or a published file." | DEC-050 |

Unchosen options: "Apply 1, 2 and 4, not Q-2"; "Hold all for P02"; "Keep forward-only"; "OK; keep it as indirect". The applied amendments are in the [source approvals](source-approvals.md#amendments-2026-10-27) and the [register](acceptance-objectives.md).

**Coordinator's note on DEC-050:** the chosen description mentions "the browser". Whether that means the user's own browsing or an automated browser read is not settled. Until the user says, the coordinator makes no automated browser read. Until a published file is found or the user supplies the text, CPI timing stays a P02 dependency.
