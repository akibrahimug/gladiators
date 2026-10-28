# P02 capture validation plan

[Task](../../tasks/TASK-P02-004.md) · [Event contract](event-contract.md) · [Capture and recovery](capture-and-recovery.md) · [Sample results](../P01/sample-results.md) · [Acceptance objectives](../P01/acceptance-objectives.md) · [Validation scenarios](../../validation/acceptance-scenarios.md)

**Status: proposed plan, 2026-10-28, for the reviewer.** This is P02 task 5: "Select quantitative capture criteria and recovery scenarios from source behavior; obtain approval before evaluating results". It is also the P02 deliverable "a replay fixture and validation plan tied to the approved source baseline". The [sample plan](../P01/data-access-decision.md#representative-sample-plan) said its results would go into this file; [§5](#5-p01-sample-results-carried-forward) carries them forward.

- **No measurement yet:** nothing in this plan has been measured against the criteria below. The thresholds in [§3](#3-thresholds) are fixed **before** any measurement, and each needs the reviewer's approval.
- **No authorisation:** this plan authorises no capture. Running it needs an authorised implementation (TASK-P02-002), and live windows need a capture authorisation.

## 1. Criteria

Each criterion is checked against the evidence named in its row, at a stated revision.

| ID | Criterion | Source | Evidence | VAL |
| --- | --- | --- | --- | --- |
| CV-01 | Every normalized record traces to its raw bytes, retrieval and source approval | T-1; REQ-003 | Trace 100 % of records in each window | VAL-002 |
| CV-02 | All four times and the basis are present on every record, in native units | DEC-052; T-1 | Schema check, 100 % | VAL-002 |
| CV-03 | Every fixture F-01 to F-17 gives exactly its expected result | Event contract §5 | Fixture run | VAL-004 |
| CV-04 | Q-1: invalid rows are quarantined, never cleaned. Covers F-02b, F-03, F-06 and F-06b | Q-1 | Fixture run, plus the counts in each window | **New: closes the Q-1 VAL gap** (DEC-042) |
| CV-05 | Q-2: 100 % of missing intervals are classified into one of the three classes | Q-2 as amended | `GapInterval` count = expected-grid gaps | VAL-004 |
| CV-06 | Q-3 coverage report per snapshot (raw, accepted, quarantined, duplicate and missing counts). It fails closed when coverage is inadequate | Q-3 | A report for each window | **New: closes the Q-3 VAL gap** |
| CV-07 | Q-4: a pair qualifies for a fold only if ≥ 95 % of its look-back days are present or `no_trade` | Q-4 | Computed per pair and fold; **reported** only, with no selection | **New: closes the Q-4 VAL gap** |
| CV-08 | Q-7: every record has `venue`, `source_id` and `feed_id`; none is labelled consolidated | Q-7 | Schema check, 100 % | **Closes the Q-7 gap** (event contract §3) |
| CV-09 | Replay determinism: two replays of the same raw objects give byte-identical output | Q-6; DEC-054 | Output hash equality | VAL-003 (G03); checked here for the normalized layer |
| CV-10 | As-of correctness: no record is visible before its `available_at` (F-16), and an older version is visible before its revision (F-09) | T-2; DEC-053 | Fixture run | VAL-004 |
| CV-11 | Recovery: scenarios RC-01 to RC-08 and RC-12 behave as specified, under injected faults | capture-and-recovery §3 | Fault-injection run | VAL-004 |
| CV-12 | *(Live; Conditional)* R-3: recovery p95 ≤ 60 s. R-4: valid-book time ≥ 99 %. Q-5: zero books accepted after a mismatch. R-5: ≤ 2 GB per pair per day. T-3: latency percentiles reported. T-5 and T-6 apply | R-3, R-4, R-5, Q-5, T-3, T-5, T-6 | A live window | VAL-004 |

## 2. Representative windows

These windows are fixed now, before any measurement.

| Window | Data | Why |
| --- | --- | --- |
| W-A | Binance `1d` klines for the 10 sample symbols, 2024-12 and 2025-01 | The ms→µs unit change (S-07) |
| W-B | Binance `1INCHUSDT` 2022-03 (daily and monthly) | A logged revision (S-09) |
| W-C | Binance `LUNAUSDT` 2022-04 to 2022-09, plus `LUNCUSDT` 2022-09 | Symbol reuse (S-10) |
| W-D | Binance `ETHUSDT` trades, 2025-01-15 | Trade continuity (S-05) |
| W-E | Kraken full archive: `XBTUSD` and `ETHUSD`, all intervals, full history | Gaps (S-04), first bars, scale |
| W-F | Kraken full archive: 4 delisted pairs (ANTETH, AGLDUSD, AIRUSD, ANKRGBP) | Delisting (S-11) |
| W-G | Kraken 2026Q3 ZIP, all pairs | Manifest counts (S-13); a file with no published checksum |
| W-H | Kraken REST `OHLC` (1440) for XBTUSD and ETHUSD, one week overlapping W-E | The incomplete bar (S-12) and the F-4h comparison |
| W-I | Context: one FOMC statement, one set of minutes, one COT report | `stated_release` and `first_published` |
| W-J | *(Live; Conditional)* Kraken WebSocket: 2 pairs, `book` depth 10 plus `trade`. First one hour (sample step 2), then 7 days | CV-12 |

W-A to W-I reuse the P01 sample files, identified by SHA-256 in the sample results. No new download is needed except for W-J.

## 3. Thresholds

**Approved P01 values** (DEC-042), applied unchanged:

| Value | Approved |
| --- | --- |
| T-3 | Latency percentiles p50/p95/p99/max reported; no requirement |
| T-5 | 100 ms clock-offset flag; offset logged at least hourly |
| T-6 | Abstain at > 1 s (intraday) and > 60 s (daily) |
| Q-4 | ≥ 95 % pre-fold coverage |
| R-3 | Recovery p95 ≤ 60 s |
| R-4 | ≥ 99 % valid-book time |
| R-5 | ≤ 2 GB per pair per day |

**New values for the reviewer.** These are the placeholders from the event contract and the recovery design. Each is **Proposed** and must be approved before measurement.

| ID | Value | Proposed | Basis |
| --- | --- | --- | --- |
| TH-1 | *G*: epoch gap (days) | **7** | The LUNAUSDT gap was 17 days; normal Binance and Kraken daily gaps were ≤ 3 days in the sample |
| TH-2 | *K*: epoch price factor | **10×** | LUNAUSDT went from 0.00005 to 1.00 (×20,000). Ordinary daily moves are far below 10× |
| TH-3 | *N_retry*: retries on transient failure | **3**, with delays 30 s, 2 min, 10 min | DEC-044 reasonable load |
| TH-4 | `last_modified_after_period` limit, Binance | Daily file: **> 48 h** after the day ends. Monthly file: **> 14 days** after the month ends. A file listed in the changelog is always flagged | Observed: daily 2 to 3 h; monthly 5 to 8 days (sample results) |
| TH-5 | Stale-observation limit (S-17) | **2 ×** the source's documented update interval: COT 14 days, FOMC minutes not applicable (one per meeting), Coin Metrics 2 days, GDELT 30 min | v10 ACCEPTANCE:5, "stale … observations" |
| TH-6 | Lag limit for late records (S-17) | Daily bars: **`available_at` − `bar_end` > 7 days** is flagged as late | Binance monthly publication runs 5 to 8 days; Kraken archives are quarterly and are covered separately by T-2a |

## 4. F-4h closure route

The event contract (§8) notes that Kraken archive history becomes available only from its 2026-10-01 publication date until F-4h is closed. T-2a allows bar-close timing only if Kraken documents availability at bar close **and** the archive matches what was served then.

**Proposed route:**
1. **Forward record.** For 30 days, pull Kraken REST `OHLC` (1440) for the W-1 Kraken pairs once a day, shortly after 00:00 UTC. Record each completed bar with `available_at` = `received_at` (`live_receive`).
2. **Compare with the next archive.** When the next quarterly archive is published (2026Q4, expected about 2027-01-01, by analogy with Q3's 2026-10-01), compare its bars for those 30 days with the forward record, using the event contract §4.1 comparison rule.
3. **Close or not.**
   - If every bar matches, the evidence supports the second T-2a condition for the period sampled. The first condition, that the venue documents availability at bar close, still needs a Kraken documentation statement. Without one, F-4h stays Unresolved, and the reviewer decides whether forward evidence alone is enough.
   - Any mismatch is a correction (T-2a; experiment 9).

**This route needs an authorisation.** A scheduled daily REST pull is not covered by DEC-035, which allows one-off pulls on explicit invocation. It is put to the reviewer with the thresholds.

**F-4j.** An `AssetPairs` snapshot taken with each REST pull dates future Kraken delistings to within a day. Past delisting dates stay upper bounds.

## 5. P01 sample results carried forward

The P01 sample-plan results ([sample results](../P01/sample-results.md)) are this plan's starting evidence. They are not evaluations against §3: they were taken before these criteria were fixed.

| Window | P01 result |
| --- | --- |
| W-A | 28 of 28 checksums verified; ms→µs change confirmed |
| W-B | Revision replaced in place; the monthly rewrite was not logged |
| W-C | Symbol reuse found (F-5e) |
| W-D | Trade IDs contiguous |
| W-E | XBTUSD 12 and ETHUSD 6 missing days |
| W-F | Quarter-end last bars (F-4j) |
| W-G | 1,436 pairs; no checksum published |
| W-H | Values match within 10⁻⁹ |
| W-I | Stated times found on FOMC pages |

## 6. Evaluation procedure

1. The reviewer approves §3 and the §4 authorisation question, before any run.
2. An authorised implementation (TASK-P02-002) runs W-A to W-I and the fixtures, at a recorded revision.
3. The results are reported per criterion, at that revision. A failure is not re-run with changed thresholds. Under the P02 rework rule, it is fixed, and the affected validation is repeated.
4. W-J runs only after a capture authorisation.
5. G02 is sought only with that evidence, together with the reviewer's dated approval.
