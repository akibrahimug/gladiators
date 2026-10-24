# P01 workload and acceptance-objective register

[Task](../../tasks/TASK-P01-003.md) · [Research agenda](research-agenda.md) · [Source follow-ups](source-followups.md) · [Observability map](observability-map.md) · [Acceptance scenarios](../../validation/acceptance-scenarios.md) · [P01 phase](../../phases/01-research-and-data-access/README.md)

**Status: proposal for the G01 reviewer, 2026-10-24. Nothing here has been measured or accepted.**

This is the P01 deliverable "a workload and acceptance-objective register defining selected instrument/event scope, latency measurement points and percentiles, clock uncertainty, quality/recovery targets and evaluation methods before measurement" (P01 README). It covers P01 task 6.

Each objective has one of three kinds:

- **Invariant (source)**: a rule that the preserved sources already make binding. It is quoted, and it has no numeric tolerance.
- **Proposed value**: something the sources do not settle. The coordinator proposes it, and the G01 reviewer approves or replaces it **before any measurement**. This follows the G01 exit gate's "justified thresholds" and file 24's warning that example values "are **illustrative only**, not research-calibrated thresholds" (24:142).
- **Provisional default**: a DEC-017 default that is "not accepted". G01 decides it.

**Capture boundary.** Nothing here authorises capture, spending or trading. Any capture needs later authorisation under the P02 implementation boundary.

## 1. Instrument and event scope (workload)

| ID | Objective | Kind | Value | Justification |
| --- | --- | --- | --- | --- |
| W-1 | Daily-bar universe, crypto | Proposed value | Kraken spot pairs quoted in USD, chosen by a rule fixed before any data is seen. **Point-in-time selection:** at the start of each walk-forward fold, rank the pairs by traded notional using only data before that fold. The selected set is used only for periods that start on or after its selection date. **Delisted pairs** stay in the universe until their delisting date, and the delisting is recorded | Prevents lookahead and survivorship bias: "prevent lookahead in … universe selection" (`10-DATA.md:20`, step 9); "Prevent today's surviving stocks from becoming yesterday's entire universe" (L-010 item 4); "Do not use today's ETF constituents as historical universe without point-in-time evidence" (L-025). Whether the SR-05 archive includes delisted pairs is unverified (new follow-up item F-4g, recorded here) |
| W-2 | Universe size N | Proposed value | **N = 10** per fold | The source's first-experiment scale is "10–20 liquid US shares" (L-010 item 1). It also fits the CPU-only resource policy (`11-QLIB-AND-TRAINING.md:15`) |
| W-3 | ETF daily-bar universe | Deferred | Not set until F-1 closes. If F-1 closes negatively, DEC-029 applies | [Follow-ups](source-followups.md#f-1--free-daily-etf-bars) |
| W-4 | Live-capture scope, if a later authorisation permits capture (for H-OF1, H-OF2, H-OF3 and H-OF5) | Proposed value | The **2** most liquid pairs from the current W-1 fold. Kraken `book` at depth **10**, plus `trade` | Kraken's [book channel](https://docs.kraken.com/api/docs/websocket-v2/book) gives depth 10 as the default, and the checksum covers "the top 10 bids and asks". Two pairs keep the "retention/size budgets" (27:67) small. With 2 pairs, H-OF3 at the daily horizon has very few observations until F-4d supplies history; this is a power caveat |
| W-5 | Horizon | **Provisional default** (DEC-017; G01 decides) | Daily first | 17:33 says "Start daily bars, change horizon only with evidence". This conflicts with 20:21 and CORE:8 ("15-minute/1-hour"), as recorded in the [baseline record](../P00/baseline-decision.md#initial-research-scope-for-p01) |
| W-6 | Market event types | Invariant (file 27 contracts) | For W-4: book snapshots, updates and trades, using the `NativeMarketEvent` and `BookState` fields classified in the [map](observability-map.md#contract-fields). For W-1: daily OHLCV in the `10-DATA.md` market schema | 27:50–56; `10-DATA.md:9` |
| W-7 | Context events | Proposed value | **In scope:** FOMC meetings and minutes, CPI releases, CFTC COT, GDELT news metadata, FRED/ALFRED macro vintages and Coin Metrics Community metrics, which are the Documented rows in the [follow-ups](source-followups.md#f-3--context-sources). Each uses `available_at` = first publication or release time (COT: the Friday release; FRED: the vintage date). **Out of scope until their sources close:** derivatives, options, liquidations, issuer holdings and on-chain RPC | G01 requires "every required event or context input in the selected scope" to map to a source. DEC-015 puts events first |

## 2. Time, latency and clock

| ID | Objective | Kind | Value | Justification |
| --- | --- | --- | --- | --- |
| T-1 | Timestamps preserved | Invariant | For every live event, keep the source event time, local receive time, ingest time and `available_at`, each in native precision with no padding | "preserve source/event/receive/ingest/available timestamps" (27:61) |
| T-2 | Causal availability | Invariant | A feature's `available_at` must be ≤ the decision time, including latency, propagation and correction delays | 27:61 |
| T-2a | `available_at` for historical bars | Proposed value | The earliest time the bar was retrievable from the venue (REST, from bar close), if the venue documents it. Otherwise the archive publication time. Each record states its basis | The map applies T-2 to archives. Using archive publication time alone would make quarterly-published history unusable for daily evaluation. The coordinator chose this rule, so the reviewer decides it |
| T-3 | Latency measurement points | Proposed value | Report `local_receive − source_event` and `ingest − local_receive` per pair and day as p50, p95, p99 and maximum. The first measure **includes the local clock offset** (bounded by T-5) | "quantified end-to-end latency" (27:67). Reported, not required, because no latency claim is made at the daily horizon |
| T-4 | No anticipatory claim | Invariant | The Arena reports no anticipatory advantage from delayed or public data | Falsification experiment 4 (27:84). "A standard retail cloud/home connection cannot claim colocated HFT edge" (27:67) |
| T-5 | Clock offset monitoring | Proposed value | The host clock is disciplined by NTP, and the offset is logged at least hourly. While the last logged absolute offset exceeds **100 ms**, every event gets `timestamp_uncertainty_ms` = that offset | The field `timestamp_uncertainty_ms` exists (27:52) |
| T-6 | Clock-skew abstention | Invariant (rule) + Proposed value (threshold) | Clock skew triggers `ABSTAIN` for dependent decisions (invariant). Proposed skew thresholds: an absolute offset **> 1 s** for intraday-dependent decisions and **> 60 s** for daily decisions | The rule is "clock skew … trigger `ABSTAIN`" (KERNEL:26). The source gives no number |

## 3. Data quality

| ID | Objective | Kind | Value | Justification |
| --- | --- | --- | --- | --- |
| Q-1 | Daily-bar validation | Invariant | Reject duplicate timestamps, invalid OHLC, timezone-naive timestamps, nonfinite values, and stale or future-available observations. Rejected records go to quarantine, never to the clean set | ACCEPTANCE.md:5; `10-DATA.md` steps 3 and 5 |
| Q-2 | No-trade intervals | Invariant | Classify every missing Kraken interval as either a venue no-trade interval or a data gap. **100 % classified**; nothing is filled silently | L-025; 27:62 ("Gaps are **not** zero trading activity") |
| Q-3 | Coverage report per snapshot | Invariant | Report counts of raw, accepted, quarantined, duplicate and missing records, plus coverage. The snapshot fails closed when coverage is inadequate | L-010 item 6; `10-DATA.md` step 8 |
| Q-4 | Coverage for inclusion | Proposed value | **Before** a fold, a pair qualifies only if ≥ **95 %** of its calendar days in the fold's look-back are present or classified as no-trade. **During** a test period, shortfalls are *reported*, never used to exclude a pair after the fact. A delisting ends the pair's series at its delisting date (W-1) | Avoids survivorship from ex-post exclusion. The source gives no number ("fail closed when coverage is inadequate", L-010 item 6) |
| Q-5 | Book integrity | Invariant | On a checksum mismatch or sequence gap: invalidate the book, rebuild it from a fresh snapshot, and publish no feature during the uncertain interval. **Zero** books are accepted after an unresolved mismatch | 27:60 ("No silent reuse of a broken book"); experiment 3 (27:83) |
| Q-6 | Replay determinism | Invariant | Byte-identical feed events rebuild identical book state and features, and reordered events are detected | 27:63 |
| Q-7 | Venue-local labelling | Invariant | Every record carries its venue and feed identity. None is presented as cross-venue or consolidated | `09-CONNECTORS.md:29`; experiments 6 and 7 (27:86–87) |

## 4. Recovery and availability

| ID | Objective | Kind | Value | Justification |
| --- | --- | --- | --- | --- |
| R-1 | Outage recording | Invariant | Every disconnect or outage interval is persisted as `SOURCE_UNAVAILABLE`, distinct from `NO_EVENT` | `09-CONNECTORS.md:29` |
| R-2 | Recovery behaviour | Invariant | Reconnect, resubscribe with a snapshot, and resume only once book integrity holds (Q-5). Mark the pre- and post-recovery intervals | 27:60 |
| R-3 | Recovery time | Proposed value | Report the time from disconnect to a valid book as p50, p95 and maximum. Objective: **p95 ≤ 60 s**. Breaches are recorded, and no decision is ever made on an invalid book | The source gives no number. P02 task 5 ("select quantitative capture criteria") may refine it |
| R-4 | Capture completeness | Proposed value | Share of wall-clock time with a valid book per pair. Objective: **≥ 99 %**, excluding venue-declared maintenance. Shortfalls narrow the evaluation window and are never imputed | The source gives no number |
| R-5 | Retention budget | Proposed value | Raw storage per pair per day. Cap: **≤ 2 GB** (compressed). If the cap is exceeded, reduce depth or pairs, never the integrity checks | "retention/size budgets" (27:67); 11:15. Not yet checked against any sample |

## 5. Source evaluation criteria (for the P01 task-7 source baseline)

Each criterion applies to the source classes listed. A source of a listed class that fails a criterion cannot be part of the approved baseline.

| ID | Criterion | Applies to | Basis |
| --- | --- | --- | --- |
| S-1 | Rights documented for the intended use (DEC-030), with a `source_approval` record | All | L-025 |
| S-2 | Retention of raw data is permitted | All | `10-DATA.md` storage layout and step 2; L-010 item 3 |
| S-3 | £0 cost, and no broker or trading-account key | All | "zero paid external services" (`10-DATA.md:33`); DEC-028. **The budget itself is a provisional default** (DEC-017; CORE:71 says £20/month) decided at G01 |
| S-4 | Documented timestamp semantics, plus an integrity mechanism (sequence or checksum) | Live event feeds | 27:60, 27:61 |
| S-4b | Documented bar timestamp semantics (start or end) and file integrity | Historical bars | `10-DATA.md:9`, step 2 |
| S-5 | History long enough for chronological train, validation and locked test | Historical bars (W-1 sources) | `10-DATA.md:21`, step 10 |
| S-6 | Venue-local or consolidated status stated explicitly | Market data | Q-7 |

**Current standing (information only):**
- **SR-02** (live): passes S-3, S-4 and S-6. S-1 and S-2 are open (F-4a).
- **SR-05** (bars): passes S-3 and S-6. S-1 and S-2 are open (F-4a). S-4b is open: the candle timestamp semantics and the 30-minute inconsistency are F-4f. S-5 is likely met ("from its first trade on Kraken"), but unconfirmed per pair.
- **Context sources:** S-1 to S-3 per the follow-ups.
- **ETF candidates:** none passes S-1, S-2 and S-5 (F-1).

## 6. Evaluation methods

| Objective | Method | Scenario or evidence item |
| --- | --- | --- |
| T-1 timestamps preserved | Trace normalized events back to raw payloads, checking all four timestamps | VAL-002 (G02) |
| T-2, T-2a causality | Late-delivery and future-bar injection fixtures | VAL-004; VAL-007 for context (G04) |
| T-3, T-5, T-6 latency and clock | Measured during any authorised capture against the logged NTP offset | P02 `capture-validation-plan.md` |
| T-4 no anticipatory claim | Experiment 4 (27:84) | VAL-012 (G06, latency uncertainty) |
| Q-1, Q-2 bar validation | Fixture corpora with invalid OHLC, nonfinite values, naive timestamps, duplicates and no-trade intervals | **Gap: no VAL scenario covers bar validation.** Recorded for G01; proposed as P02 `capture-validation-plan.md` fixtures |
| Q-3, Q-4 coverage | Coverage report per snapshot, using pre-fold coverage | **Gap: no VAL scenario.** Recorded for G01; P02 `capture-validation-plan.md` |
| Q-5, Q-6 book integrity and replay | Dropped-update and reordered-event fixtures; double replay with hash comparison | VAL-003, VAL-005; experiment 3 (27:83) |
| Q-7 venue labelling | Experiments 6 and 7 (27:86–87) | **Gap: no VAL scenario.** Recorded for G01; P02 `event-contract.md` (venue fields) |
| R-1 to R-4 recovery | Forced disconnect drills during any authorised capture | VAL-004 (G02); P02 `capture-and-recovery.md` |
| R-5 retention | Size of the first authorised sample | P02 `capture-and-recovery.md` |

## Deferred to P06

Model-evaluation thresholds stay with the P06 pre-registration ([research agenda](research-agenda.md#evaluation-protocol-links)) and are not set here:
- calibration bounds (H-04);
- holdout dates;
- multiple-testing adjustments;
- the forecast-to-position rule.

## For the G01 reviewer

Approve or replace these before any measurement:
- **Proposed values:** W-1 (point-in-time selection and delisting rule), W-2 (N = 10), W-4 (2 pairs, depth 10), W-7 (context scope), T-2a (bar `available_at` basis), T-3 (percentiles reported), T-5 (100 ms), T-6 (> 1 s intraday / > 60 s daily skew thresholds), Q-4 (95 % pre-fold coverage), R-3 (p95 ≤ 60 s), R-4 (≥ 99 %), R-5 (≤ 2 GB per pair per day).
- **Provisional defaults:** W-5 (daily first) and the S-3 budget (£0).
- **Recorded gaps:** no VAL scenario covers Q-1/Q-2, Q-3/Q-4 or Q-7.

None of these has been measured.
