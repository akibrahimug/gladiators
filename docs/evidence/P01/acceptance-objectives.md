# P01 workload and acceptance-objective register

[Task](../../tasks/TASK-P01-003.md) · [Research agenda](research-agenda.md) · [Source follow-ups](source-followups.md) · [Observability map](observability-map.md) · [Acceptance scenarios](../../validation/acceptance-scenarios.md) · [P01 phase](../../phases/01-research-and-data-access/README.md)

**Status: proposal for the G01 reviewer, 2026-10-24. Nothing here is measured or accepted yet.**

This is the P01 deliverable "a workload and acceptance-objective register defining selected instrument/event scope, latency measurement points and percentiles, clock uncertainty, quality/recovery targets and evaluation methods before measurement" (P01 README). It covers P01 task 6.

Each objective is marked with one of two kinds:
- **Invariant (source):** a rule the preserved sources already make binding. It is quoted, and it allows no numeric tolerance.
- **Proposed value:** a number the sources do not give. The coordinator proposes it from documented facts. The G01 reviewer approves or replaces it **before any measurement**; this follows the G01 exit gate, "justified thresholds", and file 24's warning that its example values "are **illustrative only**, not research-calibrated thresholds" (24:142).

No value here authorises capture, spending or trading. P02 performs the capture, after G01.

## 1. Instrument and event scope (workload)

| ID | Objective | Kind | Value | Justification |
| --- | --- | --- | --- | --- |
| W-1 | Daily-bar universe, crypto | Proposed value | Kraken spot pairs quoted in USD. Selection is by a **rule fixed before data**: the top N pairs by traded notional over a stated look-back that ends on a stated *selection date*. The universe is then frozen for every test period after that date | The source warns against survivorship ("Do not use today's ETF constituents as historical universe", L-025). The same applies to crypto. N is set in W-2 |
| W-2 | Universe size N | Proposed value | **N = 10** | Matches the source's first-experiment scale ("10–20 liquid US shares", L-010 item 1). It fits the CPU-only resource policy (`11-QLIB-AND-TRAINING.md:15`) |
| W-3 | Daily-bar ETF universe | Deferred | Not set until F-1 closes. If F-1 closes negatively, DEC-029 applies | [Follow-ups](source-followups.md#f-1--free-daily-etf-bars) |
| W-4 | Live capture scope (P02 forward capture for H-OF1, H-OF2, H-OF3, H-OF5) | Proposed value | The **2** most liquid pairs from W-1. Kraken `book` at depth **10**, plus `trade` | Depth 10 is Kraken's default and the depth its CRC32 covers ("top 10 bids and asks", SR-02). Two pairs keep the "retention/size budgets" (27:67) small on a home connection |
| W-5 | Horizon | Invariant (DEC-017 default; 17:33) | Daily first; intraday only "with evidence" | "Start daily bars, change horizon only with evidence" (17:33) |
| W-6 | Event types required | Invariant (file 27 contracts) | For W-4: book snapshots, book updates and trades, with the `NativeMarketEvent` and `BookState` fields classified in the [map](observability-map.md#contract-fields). For W-1: daily OHLCV with the `10-DATA.md` market schema | 27:50–56; `10-DATA.md:9` |

## 2. Time, latency and clock

| ID | Objective | Kind | Value | Justification |
| --- | --- | --- | --- | --- |
| T-1 | Timestamps preserved | Invariant | Every live event keeps the source event time (Kraken RFC3339), local receive time, ingest time and `available_at`. Native precision is kept and never padded | "preserve source/event/receive/ingest/available timestamps" (27:61) |
| T-2 | Causal availability | Invariant | A feature's `available_at` ≤ decision time, including latency, propagation and correction delays. Historical bars use their **archive publication time**, not the bar end | 27:61; [map](observability-map.md) "Bar `available_at`" |
| T-3 | Latency measurement points | Proposed value | Report `local_receive − source_event` and `ingest − local_receive` per pair and per day as p50, p95 and p99, plus the maximum | Satisfies "quantified end-to-end latency" (27:67). The values are reported, not required, because the daily horizon makes no latency claim |
| T-4 | No anticipatory claim | Invariant | Arena reports no anticipatory advantage from delayed or public data | Falsification experiment 4 (27:84). "A standard retail cloud/home connection cannot claim colocated HFT edge" (27:67) |
| T-5 | Local clock uncertainty | Proposed value | The host clock is disciplined by NTP, and its offset is logged at least hourly. An event is flagged `timestamp_uncertainty_ms` above **100 ms** whenever the last logged offset exceeds 100 ms | The `BookState` field `timestamp_uncertainty_ms` exists (27:52). 100 ms is coarse relative to the daily horizon, but it would make any intraday order-flow claim visibly uncertain. The reviewer may tighten it before measurement |
| T-6 | Clock-anomaly handling | Invariant | Clock skew triggers `ABSTAIN` for dependent decisions | "clock skew … trigger `ABSTAIN`" (KERNEL:26) |

## 3. Data quality

| ID | Objective | Kind | Value | Justification |
| --- | --- | --- | --- | --- |
| Q-1 | Daily-bar validation | Invariant | Reject duplicate timestamps, invalid OHLC, timezone-naive timestamps, nonfinite values, and stale or future-available observations. Rejected records go to quarantine, never to the clean set | ACCEPTANCE.md:5; `10-DATA.md` steps 3 and 5 |
| Q-2 | No-trade intervals | Invariant | Every missing Kraken interval is classified as a venue no-trade interval or a data gap before use. **100 % classified**; none is filled silently | L-025 ("omit intervals with no trades"); 27:62 ("Gaps are **not** zero trading activity") |
| Q-3 | Coverage report per snapshot | Invariant | Counts of raw, accepted, quarantined, duplicate and missing records, with coverage. The snapshot fails closed when coverage is inadequate | L-010 item 6; `10-DATA.md` step 8 |
| Q-4 | Minimum daily coverage per pair | Proposed value | A pair enters a test period only if at least **95 %** of its calendar days in that period are present or classified no-trade. Otherwise it is excluded *for that period*, with the reason recorded | Source: "fail closed when coverage is inadequate" (L-010 item 6), with no number given. 95 % is a proposal |
| Q-5 | Book integrity | Invariant | On a checksum mismatch or sequence gap: invalidate the book, rebuild from a fresh snapshot, and publish no feature during the uncertain interval. **Zero** books accepted after an unresolved mismatch | 27:60 ("No silent reuse of a broken book"); falsification experiment 3 (27:83) |
| Q-6 | Replay determinism | Invariant | Byte-identical feed events rebuild identical book state and features. Reordered events are detected | 27:63; VAL-003 |
| Q-7 | Venue-local labelling | Invariant | Every record carries its venue and feed identity, and none is presented as cross-venue or consolidated | `09-CONNECTORS.md:29`; falsification experiments 6 and 7 |

## 4. Recovery and availability

| ID | Objective | Kind | Value | Justification |
| --- | --- | --- | --- | --- |
| R-1 | Outage recording | Invariant | Every disconnect or outage interval is persisted as `SOURCE_UNAVAILABLE`, distinct from `NO_EVENT` | `09-CONNECTORS.md:29` |
| R-2 | Recovery behaviour | Invariant | Reconnect, resubscribe with a snapshot, and resume only after book integrity holds (Q-5). The intervals before and after recovery are marked | 27:60 |
| R-3 | Recovery time | Proposed value | Report the time from disconnect to a valid book as p50, p95 and maximum per capture day. Proposed objective: **p95 ≤ 60 s**. Breaches are recorded, and decisions are never made on an invalid book | No source number. The value is proposed so that P02 recovery evidence has a pre-set target. It does not affect the daily horizon |
| R-4 | Capture completeness | Proposed value | Report the share of each capture day with a valid book per pair. Proposed objective: **≥ 99 %** of wall-clock time, excluding venue-declared maintenance | No source number. This makes P02's order-flow datasets usable; shortfalls narrow the evaluation window rather than being imputed |
| R-5 | Retention budget | Proposed value | Record the storage per pair per day for W-4. Proposed cap: **≤ 2 GB per pair per day** raw (compressed). If the cap is exceeded, depth or pairs are reduced, never the integrity checks | "retention/size budgets" (27:67); the resource policy (11:15). The proposal is to be checked against the first P02 sample |

## 5. Source evaluation criteria (for the P01 task-7 source baseline)

The P01 task-7 source baseline applies these criteria in order. A source that fails any of S-1 to S-5 cannot be part of the approved baseline.

| ID | Criterion | Basis |
| --- | --- | --- |
| S-1 | Rights documented for the intended use (DEC-030), with a `source_approval` record | L-025 |
| S-2 | Retention of raw data permitted | `10-DATA.md` storage layout and step 2; L-010 item 3 |
| S-3 | £0 cost, and no broker or trading-account key | DEC-017, DEC-028 |
| S-4 | Documented timestamp semantics and an integrity mechanism (sequence or checksum) for event feeds | 27:60, 27:61 |
| S-5 | Coverage adequate for W-1 and W-2 (history length is enough for chronological train, validation and locked test) | `10-DATA.md` step 10 |
| S-6 | Venue-local or consolidated status stated explicitly | Q-7 |

**Current standing, for information only:**
- **Kraken (SR-02, SR-05):** passes S-3, S-4 and S-6. S-1 and S-2 are still open under F-4a, which covers retention and the §9 scope.
- **ETF candidates:** none passes S-1 to S-5 (F-1).

## 6. Evaluation methods

| Objective group | Method | Scenario |
| --- | --- | --- |
| Time and causality (T-1, T-2, T-6) | Late-delivery and future-bar injection fixtures | VAL-004, VAL-007 |
| Latency and clock (T-3, T-5) | Measured during the first P02 capture against the logged NTP offset; reported only | P02 evidence |
| Quality (Q-1 to Q-4) | Fixture corpora with known violations, and a coverage report per snapshot | VAL-002, VAL-004 |
| Book integrity and replay (Q-5, Q-6) | Dropped-update and reordered-event fixtures; double replay with hash comparison | VAL-003, VAL-005; experiment 3 (27:83) |
| Recovery (R-1 to R-4) | Forced disconnect drills during P02 capture | VAL-004 (G02) |
| Retention (R-5) | Size of the first P02 sample per pair per day | P02 evidence |

## For the G01 reviewer

The proposed values that need approval or replacement before measurement are:
- W-1 (selection rule);
- W-2 (N = 10);
- W-4 (2 pairs, depth 10);
- T-3 (percentiles reported);
- T-5 (100 ms);
- Q-4 (95 %);
- R-3 (p95 ≤ 60 s);
- R-4 (≥ 99 %);
- R-5 (≤ 2 GB per pair per day).

None has been measured.
