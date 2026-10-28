# P02 capture validation plan

[Task](../../tasks/TASK-P02-004.md) · [Event contract](event-contract.md) · [Capture and recovery](capture-and-recovery.md) · [Sample results](../P01/sample-results.md) · [Acceptance objectives](../P01/acceptance-objectives.md) · [Validation scenarios](../../validation/acceptance-scenarios.md)

**Status: proposed plan, 2026-10-28, for the G02 reviewer (the user, DEC-034).** This is P02 task 5, "Select quantitative capture criteria and recovery scenarios from source behavior; obtain approval before evaluating results". It also delivers P02's "replay fixture and validation plan tied to the approved source baseline". The [sample plan](../P01/data-access-decision.md#representative-sample-plan) sent its results here, and [§5](#5-p01-sample-results-carried-forward) carries them forward.

**Before any measurement:** nothing here has been measured against these criteria. The thresholds in [§3](#3-thresholds) are fixed first, and each needs the user's approval. An agent review is not approval.

**Authorisation:** this plan authorises no capture, download or REST call. Running it needs an authorised implementation (TASK-P02-002), and the new retrievals listed in [§2](#2-representative-windows) and [§4](#4-f-4h-closure-route) need their own authorisation.

## 1. Criteria

| ID | Criterion | Source | Pass condition | VAL |
| --- | --- | --- | --- | --- |
| CV-01 | Every normalized record traces to its raw bytes, retrieval and source approval | T-1; REQ-003 | 100 % of records in each window | VAL-002 |
| CV-02 | All four times and the basis are present on every record, in native units | DEC-052; T-1 | 100 % (schema check) | VAL-002 |
| CV-03 | Every fixture F-01 to F-18 gives exactly its expected result | Event contract §5; F-18 below | All fixtures pass | VAL-004 |
| CV-04 | Q-1: invalid rows are quarantined, never cleaned (fixtures F-02b, F-03, F-06, F-06b) | Q-1 | The fixtures pass. In W-A, 620 rows, of which 0 are quarantined | **New: closes the Q-1 VAL gap** (DEC-042) |
| CV-05 | Q-2: every missing interval is classified into one of the three classes | Q-2 as amended | `GapInterval` count equals the expected-grid gaps. W-E: XBTUSD 12 and ETHUSD 6, all `status_unknown`. W-A: 0 | VAL-004 |
| CV-06 | Q-3: one coverage report per snapshot (raw, accepted, quarantined, duplicate and missing counts). **Fails closed** when coverage is inadequate | Q-3 | The report exists for each window, with counts equal to the expected values: W-A 620 / 620 / 0 / 0 / 0; W-E XBTUSD 4,731 rows and 12 gaps, ETHUSD 4,067 rows and 6 gaps. Fail-closed trigger: a pair below Q-4's 95 %, or any `status_unknown` interval on the decision day (DEC-040), blocks new entries on that pair, and the report says so | **New: closes the Q-3 VAL gap** |
| CV-07 | Q-4 pre-fold coverage: ≥ 95 % of look-back days present or `no_trade`. A pair listed partway through the look-back counts only days since listing, and must meet the minimum training length. A delisting ends the series | Q-4 | F-18 passes. On W-E, XBTUSD and ETHUSD qualify for any 365-day look-back starting after 2015-12-31: at most 1 missing day (ETHUSD 2018-01-12) | **New: closes the Q-4 VAL gap** |
| CV-08 | Q-7: every record has `venue`, `source_id` and `feed_id`, and none is labelled consolidated | Q-7 | 100 % (schema check) | **Closes the Q-7 gap** (event contract §3) |
| CV-09 | Normalized-layer replay determinism: two replays of the same raw objects give byte-identical output | Q-6; DEC-054 | The output hashes are equal | VAL-003 (G03), checked here for the normalized layer |
| CV-10 | As-of correctness. F-16: no record is visible before its `available_at`. F-09: an older version is visible before its revision | T-2; DEC-053 | The fixtures pass | VAL-004 |
| CV-11 | Recovery: RC-01 to RC-08 and RC-12 behave as specified under injected faults | capture-and-recovery §3 | Every scenario gives its recorded outcome | VAL-004 |
| CV-12 | *(Live; Conditional)* R-1 to R-5, Q-5, T-3, T-5, T-6, as approved | Those rows | As approved ([§3](#3-thresholds)) | VAL-004 |

**F-18 (Q-4 fixture).** Input: `XBTUSD_1440.csv` (full ZIP `bc273e90…`), with a 365-day look-back ending 2026-09-30. Edit: delete 19 days, which brings coverage below 95 % (346/365 = 94.8 %). Expected: the pair is disqualified for that fold. Restoring 1 day gives 347/365 = 95.1 %, and the pair qualifies.

## 2. Representative windows

These windows are fixed before any measurement.

| Window | Data | Why | Files held? |
| --- | --- | --- | --- |
| W-A | Binance `1d` klines for the 10 sample symbols, 2024-12 and 2025-01 | The ms→µs unit change (S-07) | Yes: 20 files, each matching its `.CHECKSUM`. **`Last-Modified` is held for only 2 of them** (the two BTCUSDT files). The other 18 fall back to `retrieved` under event contract §3.1 unless HEAD requests are authorised (§2a) |
| W-B | Binance `1INCHUSDT` 2022-03, daily and monthly | A logged revision (S-09) | Yes |
| W-C | Binance `LUNAUSDT` 2022-04, -05, -06 and -09, plus `LUNCUSDT` 2022-09 | Symbol reuse (S-10) | Yes (the months held; 2022-07 and -08 are not) |
| W-D | Binance `ETHUSDT` trades, 2025-01-15 | Trade continuity (S-05) | Yes |
| W-E | Kraken full archive: `XBTUSD` and `ETHUSD`, all intervals, full history; plus the manifest counts | Gaps (S-04), first bars, manifest mismatch (S-13), scale | Yes |
| W-F | Kraken full archive: 4 delisted pairs (ANTETH, AGLDUSD, AIRUSD, ANKRGBP) | Delisting (S-11) | Yes |
| W-G | Kraken 2026Q3 ZIP, all pairs | A file with no published checksum | Yes |
| W-H | Kraken REST `OHLC` (1440) for XBTUSD and ETHUSD, one week overlapping W-E | The incomplete bar (S-12); the F-4h comparison | Yes |
| W-I | Context: the 2026-09-16 FOMC statement, the minutes of 2026-07-29, and the COT report for positions as of 2026-10-20 | `stated_release`; `first_published` | Yes |
| W-J | *(Live; Conditional)* Kraken WebSocket: 2 pairs, `book` depth 10 plus `trade`. One hour (sample step 2), then 7 days | CV-12 | No; needs capture authorisation |

**§2a. Retrievals beyond the held files (each needs authorisation):**
- HEAD requests for the 18 W-A kline files whose `Last-Modified` is not held. These are optional; without them the files fall back to `retrieved`.
- The W-J live capture.
- The §4 F-4h route.

## 3. Thresholds

**Approved P01 values** (DEC-042), applied unchanged. Each is quoted in full in the [acceptance objectives](../P01/acceptance-objectives.md):
- **T-3:** report `local_receive − source_event` and `ingest − local_receive` per pair and day, as p50, p95, p99 and maximum. These are reported, not required.
- **T-5:** NTP-disciplined clock; offset logged at least hourly. While the last logged offset exceeds 100 ms, `timestamp_uncertainty_ms` = that offset.
- **T-6:** dependent decisions `ABSTAIN` at an absolute offset > 1 s (intraday-dependent) or > 60 s (daily). The logging interval drops to ≤ 1 min whenever intraday-dependent decisions exist.
- **Q-4:** as quoted in CV-07.
- **R-3:** time from disconnect to a valid book, as p50, p95 and maximum. Objective: p95 ≤ 60 s. Breaches are recorded.
- **R-4:** ≥ 99 % of wall-clock time with a valid book per pair, excluding venue-declared maintenance. Shortfalls narrow the evaluation window and are never imputed.
- **R-5:** ≤ 2 GB compressed per pair per day. If it is exceeded, reduce depth or pairs, never the integrity checks.

**New values for the user.** Each is **Proposed** and must be approved before any measurement.

| ID | Value | Proposed | Basis and expected behaviour on held data |
| --- | --- | --- | --- |
| TH-1 | *G*: epoch gap (days) | **7** | LUNAUSDT's gap was 17 days, and the six sampled Kraken pairs have gaps of at most 3 days. **Across the full Kraken archive there are 427 daily gaps longer than 7 days** (the reviewer's unrecorded scan of the held file; the implementation re-derives it before the figures are relied on). With TH-2, this proposes **14 epoch breaks** (for example ETHJPY ×9,700, XLMUSD after 177 days ×24, SSVUSD after 864 days). Some may be data faults rather than asset changes. All are held for review (`InstrumentEpoch.review_status = proposed`), so none takes effect without confirmation |
| TH-2 | *K*: epoch price factor | **10×** | LUNAUSDT went from 0.00005 to 1.00. The largest adjacent-bar factor in the sampled pairs is 1.5 |
| TH-3 | *N_retry*: retries on transient failure or checksum mismatch | **3**, at 30 s, 2 min and 10 min | DEC-044 reasonable load |
| TH-3b | 429 handling | Wait for `Retry-After` if present and ≤ 10 min, then retry once. Otherwise stop and record | DEC-044 reasonable load. DEC-044 itself says nothing about 429 |
| TH-4 | Binance rewrite flag (`last_modified_after_period`) | **No lag threshold.** The flag is set only when the file is in the README changelog, or a re-retrieval finds new bytes | In the retained S3 listings, **98 of 271 monthly files** have a `Last-Modified` more than 14 days after their month ends; 81 of them are dated 2021-06-22, a bulk backfill. Monthly lags elsewhere range from 0.2 days (LUNAUSDT 2022) to 281 days (LUNCUSDT 2024-07). A lag threshold would flag about 36 % of normal files, so lag is not evidence of a rewrite. Expected flags on held data: W-B's daily file (in the changelog) only. **Trade-off:** W-B's unlogged monthly rewrite is not flagged on first retrieval. That creates no lookahead, because its `available_at` is its `Last-Modified` (2022-09-02), which is conservative |
| TH-5 | Stale-observation limit (S-17) | **2 ×** the source's documented update interval: COT 14 days; Coin Metrics 2 days; GDELT 30 minutes; FRED/ALFRED 2 × the series' release frequency. FOMC minutes and statements: not applicable, since each is a one-off release | "stale … observations" (v10 ACCEPTANCE:5). F-17 uses COT at more than 14 days |
| TH-6 | Late-record flag (S-17) | Applies **only to daily files, REST and live records**: flag when `available_at` − the covered period's end > **48 hours**. **Exempt:** monthly files and Kraken quarterly or full archives. Their `available_at` is set by T-2a, and their lateness is a recorded consequence (event contract §8), not a per-record flag | Daily files were observed at 2 to 3 hours after the day ends. Without the exemption, every bar from a monthly file would be flagged (for example, BTCUSDT 2024-12's last bar has a lag of 7.03 days). **Expected on held data:** W-H, about 55 of its 57 completed bars, which were all received on 2026-10-27 and are correctly flagged late. W-D: none. W-B: as observed |

## 4. F-4h closure route

The event contract (§8) notes that Kraken archive history counts as available only from its 2026-10-01 publication. T-2a allows bar-close timing only when **both** conditions hold:
- the venue documents availability at bar close;
- the archive matches what was served at that time.

**What the route can and cannot do.** It can show, for the bars it records, whether the archive matches what was served at bar close. **It cannot do the same for history before its start**, because nobody recorded what was served then. At most, it makes Kraken bars usable at bar close **from the route's start onwards**. Existing history stays available only from the archive's 2026-10-01 publication.

**Proposed route:**
1. **Forward record.** For 30 days, pull Kraken REST `OHLC` (1440) for XBTUSD and ETHUSD (as in W-H; W-1 has no fixed list yet) once a day, shortly after 00:00 UTC. Store each completed bar with `available_at` = `received_at` (`live_receive`).
2. **Compare.** Download the next quarterly archive. *Inference:* by analogy with Q3, which was generated on 2026-10-01, the 2026Q4 archive is expected about 2027-01-01. Compare its bars for those 30 days with the forward record, using the event contract §4.1 rule.
3. **Outcome.**
   - If the bars match, T-2a's second condition is met for the recorded period.
   - The first condition still needs a Kraken documentation statement. **Treating forward evidence alone as enough would amend T-2a (DEC-042) and needs its own recorded decision.**
   - Any mismatch is a correction (T-2a; experiment 9).

**Authorisation needed:**
- (a) the scheduled daily REST pull for 30 days, with an `AssetPairs` snapshot on each pull (F-4j);
- (b) the 2026Q4 archive download when it is published.

DEC-035 covers only the sample plan's own steps.

**F-4j.** An `AssetPairs` snapshot taken with each REST pull dates future Kraken delistings to within a day. Past delisting dates stay upper bounds.

## 5. P01 sample results carried forward

The P01 sample results ([sample results](../P01/sample-results.md)) are this plan's starting evidence. They were taken before these criteria were fixed, so they are not evaluations against §3.

| Window | P01 result |
| --- | --- |
| W-A | 20 of 20 kline checksums verified (28 of 28 across step 0); ms→µs change confirmed |
| W-B | Revision replaced in place; monthly rewrite not logged |
| W-C | Symbol reuse (F-5e) |
| W-D | Trade IDs contiguous |
| W-E | XBTUSD 12 and ETHUSD 6 missing days; the MANIFEST says 1,760 pairs, but the archive has 1,759 |
| W-F | Last bars on quarter-ends (F-4j) |
| W-G | 1,436 pairs; no checksum published |
| W-H | Values match within 10⁻⁹ |
| W-I | Stated release times on the FOMC pages |

## 6. Evaluation procedure

1. The user approves §3 and decides on the §2a and §4 authorisations before any run.
2. An authorised implementation (TASK-P02-002) runs W-A to W-I and the fixtures at a recorded revision.
3. Results are reported per criterion, at that revision. A failure is not re-run with changed thresholds; it is reworked and the affected validation repeated (P02 failure and rework rule).
4. W-J runs only after a capture authorisation.
5. G02 is sought only with this evidence and the user's dated approval.
