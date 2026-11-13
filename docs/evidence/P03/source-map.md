# P03 source map: market state and the own-account ledger

[Task](../../tasks/TASK-P03-005.md) · [P03 phase](../../phases/03-market-state-and-ledger/README.md) · [Baseline](../P00/baseline-decision.md) · [P02 event contract](../P02/event-contract.md) · [Capture and recovery](../P02/capture-and-recovery.md)

**Status: preparation, 2026-11-13.**
- **What it is:** every statement in the accepted baseline that constrains the market-state and book-replay component (CMP-03) or the own-account ledger (CMP-04), and the open choices the two P03 contracts must settle.
- **Scope limits:** it drafts neither contract and decides nothing. P03 stays Proposed, and cannot be accepted, until G02 passes and the event contract is accepted.
- **How it was made:** `gladiator-spec-reader` read master `3a76174` read-only; the coordinator wrote this page.

**Citation roots.** These are paths, not links, because the release folder names contain spaces.
- **`V10`:** `docs/sources/originals/releases/gladiator-order-flow-ledger-v10 (1)/trading-ai-spec/`.
  - `c/NN` is `V10/core-engine/components/NN-*.md`.
  - `CORE`, `KERNEL` and `ACC` are `V10/core-engine/CORE.md`, `KERNEL.md` and `ACCEPTANCE.md`.
  - `d/NN` is `V10/docs/NN-*.md`.
- **`v5`, `v4`:** the sibling release folders `gladiator-core-reviewed-v5` and `gladiator-core-research-update-v4`.
- **Project paths** are relative to `docs/`.

**Classes:**
- **N:** baseline-normative, meaning v10 or a section reinstated under DEC-020.
- **D:** a recorded decision, or a G01-approved value (DEC-042, DEC-047).
- **P:** a project proposal or interpretation.

## 1. Market state and book replay (CMP-03)

| # | Constraint | Source | Class |
| --- | --- | --- | --- |
| B1 | `BookState` fields: venue, instrument, `snapshot_update_id`, `latest_applied_update_id`, best bid and ask, `depth_by_level`, `observed_age_ms`, `gap_count`, `resync_count`, `book_health`, `sequence_integrity`, `timestamp_uncertainty_ms` | `c/27:52` | N |
| B2 | Snapshot plus delta: initialise per the source docs, buffer, apply ordered updates, detect missing sequences, invalidate and rebuild on gaps. "No silent reuse of a broken book" | `c/27:60` | N |
| B3 | Keep the source, event, receive, ingest and available timestamps; a feature's `available_at` is at or before decision time | `c/27:61` | N |
| B4 | These are validation failures: outages, stale quote clocks, crossed books, zero denominators, unknown side semantics, non-positive sizes, bad currency conversions. "Gaps are not zero trading activity" | `c/27:62` | N |
| B5 | Byte-identical feed events rebuild identical book state and features; tests catch event-order mutations | `c/27:63` | N |
| B6 | New entries fail closed on stale or invalid depth; exits use independent fallback prices | `c/27:64` | N |
| B7 | Falsification cases: experiment 1 (a displayed wall is cancelled, with no inflow credit), experiment 3 (a dropped update leads to invalidation, a fresh snapshot, and no feature over the uncertain interval), experiment 9 (as-of replay). Acceptance: deterministic property and replay tests | `c/27:81`, `:83`, `:89`, `:92` | N |
| B8 | Primitives: mid, relative spread, top-of-book imbalance; quote-currency notional; point-in-time FX; native precision stored | `c/27:32` | N |
| B9 | Venue-local crypto books are never presented as global books; `NO_EVENT` and `SOURCE_UNAVAILABLE` are kept distinct | `c/09:29` | N |
| B10 | Ordering per symbol and stream; idempotency; durable replay from raw events; a crash or restart resumes from a durable cursor; an unknown schema is quarantined | `c/08:9`, `:15`, `:18` | N |
| B11 | Replay sorts by availability and sequence; late data go to a dead letter and are never backfilled into the past | `v4 c/08:30` (L-008) | N, reinstated |
| B12 | Four distinct times; delayed events are not treated as current; an append-only journal; replay from immutable snapshots | `v5 c/08:28–30` (L-023) | N, reinstated |
| B13 | Replay in historical publication or availability order; a restart with missing segments must not claim continuous observation | `c/24:177`, `:204` | N |
| B14 | `DATA_BLIND` when a critical feed is missing or stale; it cannot silently become `NORMAL`; the state machine is versioned | `c/24:164`, `:167` | N, owned by CMP-06 ([components](../../traceability/components.md)) |
| B15 | Ingestion checkpoints are persisted; the state is `DATA_BLIND` until reconciliation | `c/26:35` | N |
| B16 | The snapshot manifest carries an `available_at` watermark and coverage metrics | `CORE:23` | N |
| B17 | One venue's book is never presented as the market; historical L2 depth is unavailable, so book history starts at the first capture | [observability map](../P01/observability-map.md) | D (G01) |
| B18 | Q-5: invalidate on a checksum mismatch or sequence gap, rebuild from a fresh snapshot, and accept zero books after an unresolved mismatch. Q-6: replay is deterministic and reordering is detected. R-2, R-3 | [acceptance objectives](../P01/acceptance-objectives.md) | D (DEC-042) |
| B19 | Contract row "Book state and replay checkpoint": snapshot or version, watermark, venue coverage, depth semantics, reconstruction status, contributing events. Failures: gap or stale invalidation, snapshot recovery, trade corrections | [contracts](../../architecture/contracts.md) | P |
| B20 | CMP-03 reconstructs the supported venue state, and outputs a versioned book, checkpoints and validity to CMP-06 and CMP-10. Requirements REQ-001, REQ-004, REQ-005 | [components](../../traceability/components.md) | P |
| B21 | VAL-003 replays twice under the "agreed determinism rule" (G03). VAL-005 applies add, change, remove, trade and correction events, and reconciles them with authoritative snapshots | [acceptance scenarios](../../validation/acceptance-scenarios.md) | P |
| B22 | Unknown, stale and invalid states stay explicit; the book and the account have distinct contracts | [architecture](../../architecture/README.md) | P |

## 2. Own-account ledger (CMP-04)

| # | Constraint | Source | Class |
| --- | --- | --- | --- |
| L1 | Append-only events for deposits, orders, fills, fees, FX, dividends, splits, realised and unrealised P&L, cash, positions, equity and outstanding orders. The accounting identity is reconciled after every event, and a mismatch is quarantined. Strategy P&L is kept separate from operating costs and deposits | `c/13:12` | N |
| L2 | Interface: `submit(approved_intent)`, `on_market_event(event)`, `get_state(as_of)`, `reconcile()`. Every order has an idempotency key and the originating model, core and gatekeeper evidence | `c/13:15` | N |
| L3 | Tests: cash is never negative (margin disabled); no duplicate fill; a gap loss can exceed the stop risk; a same-bar take-profit and stop-loss are not resolved optimistically; a failed order cannot become a position; a replayed ledger balances exactly | `c/13:18` | N |
| L4 | Artifact identity: `run_id`, UTC `as_of`, `dataset_hash`, `code_version`, `config_hash`, `model_version` | `c/13:22`, `c/00:28` | N |
| L5 | Order state machine `NEW → ACCEPTED → PARTIAL → FILLED`, `CANCELLED` or `REJECTED`. Cancellation races and retries are reconciled before any further entry. Quoted spread, paid spread, fees, slippage, FX and funding are reported separately. Crypto maker/taker fees and minimum size | `v5 c/13:28–30` (L-028) | N, reinstated |
| L6 | Append-only, "double-entry-like" cash and position ledger with a currency and fee breakdown; NAV reconciles to cash plus marked holdings | `CORE:52` | N |
| L7 | Paper and live share the order-state contract (`client_order_id`, `risk_decision_id`, … and `unknown` states) | `CORE:61` | N; the live part is out of scope |
| L8 | Cash + marked holdings − liabilities = equity; realised and unrealised P&L and fees are reconciled independently on every event. P0 priority: "Ledger and integer tick arithmetic" | `c/21:54`, `:27` | N |
| L9 | Sizing uses `floor_to_lot(...)`; an order is rejected if FX or account state is unknown | `c/21:49` | N; consumers CMP-07, CMP-12 |
| L10 | Units are explicit; no floating-point money (decimals or integer minor units) | `d/12:26` | N |
| L11 | The cost ledger keeps `trade_costs`, `research_costs` and `capital_flows` separate, each with currency and rate source and date | `c/14:9` | N |
| L12 | Every flow has a source, a delay and a conservation or accounting rule | `c/16:6` | N |
| L13 | Fees are not hardcoded; dated official schedules are used | `d/03:12` | N |
| L14 | T05: a fill delivered twice leaves the ledger unchanged (idempotent). T14: a ledger and broker disagreement stops new orders. T17: a lot-rounding shortfall leads to abstention | `c/23:20`, `:29`, `:32` | N; T06 and T14 apply only to the paper broker (reconciliation packet c, C-072) |
| L15 | A halt with no bids gives no fictitious fills; the ledger records a pending state | `c/24:201` | N |
| L16 | The gatekeeper rejects unreconciled positions, and fetches an immutable portfolio and fee schedule | `c/05:9`, `:12` | N; consumer CMP-12 |
| L17 | The simulation stage uses a deterministic order, fee and cash ledger | `ACC:10` | N |
| L18 | Dividends are cash events; splits adjust quantity and basis | `v5 c/10:43` (L-025) | N; ETF scope deferred (DEC-029, DEC-043) |
| L19 | REQ-006 separates the market book from our own cash, positions and orders; other ledger meanings are named separately | [requirements](../../requirements.md); DEC-004, DEC-018 | D |
| L20 | The own-account ledger is the "simulated cash, position, order and fee journal" | [baseline](../P00/baseline-decision.md) | D |
| L21 | CMP-04 inputs: CMP-10 fills plus an "accepted accounting convention". Outputs: ledger version and reconciliation state, to CMP-07, CMP-12, CMP-08 and CMP-11. P03 verifies with fixtures; simulator integration comes at P06 | [components](../../traceability/components.md) | P |
| L22 | Account journal contract fields; "Define ledger reconciliation equations for the selected accounting convention"; "Choose exact numeric representation … avoid unstated rounding" | [contracts](../../architecture/contracts.md) | P |
| L23 | VAL-006: duplicate fills, fees, adjustments and missing entries; ledger stage at G03 | [acceptance scenarios](../../validation/acceptance-scenarios.md) | P |
| L24 | The quote currency is kept per source and never mixed: USD on Kraken, USDT on Binance | DEC-039 | D |
| L25 | GBP 500 of simulated equity and the risk defaults are provisional, decided at G05 | [baseline](../P00/baseline-decision.md); DEC-017 | D, provisional |

**Phase and gate (P):**
- **G03 passes only when:** the two contracts are kept separate; every invariant has an expected outcome; identical inputs and configuration give identical outputs; and any tolerance has a stated rationale and approval ([P03 phase](../../phases/03-market-state-and-ledger/README.md)).
- **G03 needs G02** ([milestones](../../milestones.md)).

## 3. What P03 needs from P02

**Used as provided:**
- **Event contract, envelope (§3):** `record_key`, `record_id`, the four times and `available_at_basis` (DEC-052), `raw_id` and `raw_locator`, `version`, `quality_state` and `quality_flags`, `rights_id`.
- **Event contract, values:**
  - decimal strings are kept exactly as received (C15, proposed);
  - DEC-059 sets the volume tolerance.
- **Event contract, live book `NativeMarketEvent`:**
  - `message_type` is a snapshot or an update;
  - a snapshot's `source_event_time` is its receive time, flagged as such;
  - `native_sequence` is null;
  - a CRC32 checksum covers the top 10 levels;
  - events are in receive order.
- **Event contract, live trades and other records:**
  - live trades, with `trade_id` as `native_sequence`, and side meaning the taker;
  - `VenueStatus`;
  - `GapInterval` with `NO_EVENT` and `SOURCE_UNAVAILABLE`;
  - replay order (DEC-054) and the as-of rule.
- **Capture and recovery:**
  - clock offset (RC-07, RC-08);
  - disconnects (RC-09, with DEC-071's gap rule);
  - checksum mismatch leading to a `data_gap` (RC-10);
  - maintenance (RC-11, refined by DEC-074).
  - The design hands "the book-state builder and replay checkpoints" to P03.
- **Implemented:**
  - clock flags `clock_offset_unknown`, `clock_abstain_intraday` (DEC-067), `clock_abstain_daily` and `clock_offset_stale`, plus `timestamp_uncertainty_ms` (`src/gladiator_capture/live_records.py`);
  - the live key `native_seq = recv_ns * 100 + index`;
  - depth 10, the checksum, `book_invalid` and `book_valid` events, and a resync cap of 6 a minute (`src/gladiator_capture/live.py`).

**Not provided yet:**

| # | Gap | Source |
| --- | --- | --- |
| G-1 | G02 has not passed, and the event contract is still a proposed contract. P03 needs an accepted one | [milestones](../../milestones.md); [event contract](../P02/event-contract.md) |
| G-2 | Book validity is not a contract record. `book_invalid` and `book_valid` exist only in the capture's operational `events.jsonl`, stamped with the local clock rather than `recv_ns`. Only frame segments are stored in the raw store. `normalize()` emits book and trade records only: no `VenueStatus`, no live `GapInterval`, no validity record. DEC-071's invalid intervals exist only in analysis reports | `src/gladiator_capture/live.py`; `src/gladiator_capture/live_records.py`; [live analysis](../P02/live-analysis.md) |
| G-3 | The live sections of the event contract (§4.4, F-15) and capture mode C still read as "not authorised", although DEC-057, DEC-062 and DEC-064 authorised capture | [event contract](../P02/event-contract.md); [capture and recovery](../P02/capture-and-recovery.md) |
| G-4 | The live ordering key is undecided: DEC-054 says live book ordering "is set when capture is authorised", and no decision records the implemented `recv_ns * 100 + index` key | DEC-054 |
| G-5 | Live and archive instrument identity differ: live records use the WebSocket name `BTC/USD` (`instrument_id` `kraken:BTC/USD:1`), while archive and REST records use `XBTUSD`. The proposed `AssetPairs` alias table is not applied to live records | [event contract](../P02/event-contract.md) §3.2; `src/gladiator_capture/records.py` |
| G-6 | Kraken books have no snapshot or update IDs, so `snapshot_update_id`, `latest_applied_update_id` and `sequence_integrity` (B1) have no source | [observability map](../P01/observability-map.md) |
| G-7 | No numeric staleness limit exists for books (`observed_age_ms`); S-17's lag limit is for other records | [event contract](../P02/event-contract.md) |
| G-8 | No crossed-book check (B4) and no trade-correction semantics (B19). Whether Kraken v2 issues trade corrections is unverified | — |
| G-9 | Price and quantity precisions come from a 2026-10-27 `AssetPairs` snapshot in code, not from records. Tick and lot sizes and fee tiers are not records either | `src/gladiator_capture/cli.py` |
| G-10 | `causation_id` and `correlation_id` are reserved for internal events from P05 onward, but the P03 ledger fixtures need order and fill IDs before then (L2, L5) | [event contract](../P02/event-contract.md) |

## 4. Open choices the contracts must settle

| ID | Choice | Affected IDs |
| --- | --- | --- |
| Q1 | **Sequence or checksum.** B2 requires missing-sequence detection, but Kraken books have none (G-6); validity rests on the CRC32 of the top 10 levels. Which `BookState` fields are null, and what does `sequence_integrity` mean? | REQ-005; CMP-03; Q-5; DEC-054 |
| Q2 | **Supported depth.** The capture is 10 levels (DEC-057). Nothing beyond 10 levels can be inferred, so `depth_by_level` stops at 10. Does CMP-03 claim anything beyond the top 10? | REQ-001, REQ-002; CMP-03 |
| Q3 | **Where validity comes from.** Either P03 re-derives it from raw frames with DEC-071 and DEC-074, or P02 adds validity, `VenueStatus` and live `GapInterval` records (G-2) | CMP-02, CMP-03; RC-09 to RC-11; G02 |
| Q4 | **Replay checkpoint.** Format, watermark and cursor semantics are unspecified (B10, B15, B16, B19) | REQ-004; CMP-03, CMP-11; VAL-003 |
| Q5 | **Determinism rule** for VAL-003 and G03: which fields are excluded from the comparison (for example `ingested_at`, which `records.py` already treats as a clock field) | REQ-004; CMP-03, CMP-04; G03 |
| Q6 | **Staleness and crossed-book thresholds** for books. No source gives a number, so values need approval before any measurement | REQ-005; CMP-03; consumers CMP-06, CMP-12 |
| Q7 | **Order state machine.** Three versions conflict: L-028 (`NEW …`), `d/03:38` (`proposed → … → reconciled`) and `CORE:61` (which adds `unknown`); `c/08:12` also has a `LEDGER_RECONCILED` route. DEC-024 lets component files refine CORE and KERNEL, but L-028 is a reinstated v5 section | REQ-006; CMP-04, CMP-10; DEC-020, DEC-024 |
| Q8 | **Accounting convention.** The options are "double-entry-like" (`CORE:52`) or the identity in `c/21:54` with NAV = cash + marked holdings. No convention is selected | REQ-006; CMP-04; VAL-006 |
| Q9 | **Marking price** for unrealised P&L: mid, bid, or bar close. Any of these adds a CMP-03 or bar input to CMP-04 that the component register does not list (CMP-04's only input is CMP-10) | CMP-03, CMP-04, CMP-10; REQ-006 |
| Q10 | **Account currency and FX.** Equity is GBP (provisional, DEC-017), while instruments are in USD or USDT and never converted (DEC-039), yet B8 requires point-in-time FX. No FX source is approved in P01 | REQ-006, REQ-009; CMP-04; DEC-017, DEC-039 |
| Q11 | **Fees.** L5 requires maker/taker fees and minimum size, and L13 requires dated schedules, but no Kraken fee-schedule source is recorded in P01. Fixtures could use declared assumptions | REQ-010; CMP-04, CMP-10 |
| Q12 | **Rounding.** Decimals or minor units (L10) and integer tick arithmetic (L8). The rounding direction for fees and lots is unstated (L22). Event values are decimal strings (C15, proposed) | REQ-006; CMP-04 |
| Q13 | **Ledger cardinality.** One ledger, or one per challenger (`CORE:47`; FR-05 "refines CMP-04" in [reconciliation packet a](../P00/v1.0-reconciliation-a.md)) | REQ-006; CMP-04, CMP-14 |
| Q14 | **What reconciliation means.** A broker as the source of truth (`d/02:42`) is out of scope (DEC-021; DEC-028 excludes paper broker keys). P03 reconciliation can only compare the internal journal, replayed state and simulator fills | REQ-006, REQ-012; CMP-04; DEC-021, DEC-028 |
| Q15 | **Dropped lineage.** A second, independent accounting implementation (L-019) and fee reference cases (L-013) were proposed in [reconciliation packet c](../P00/v1.0-reconciliation-c.md), but are not in the baseline. Only a new decision could add them | CMP-04; DEC-020 |
| Q16 | **Traceability mismatch.** The P03 page lists REQ-002 and REQ-009, but the CMP-03 and CMP-04 rows do not. REQ-003 (provenance) is not listed for P03, although both contracts need raw lineage | REQ-002, REQ-003, REQ-009; CMP-03, CMP-04 |
| Q17 | **Live ordering key and instrument join** (G-4, G-5) need decisions | DEC-054; event contract §3.2; CMP-02, CMP-03, CMP-04 |

## 5. Scope boundaries

**A book is not the market's ledger:**
- A reconstructed book or trade history is a market-data view, not the market's money ledger ([P03 phase](../../phases/03-market-state-and-ledger/README.md)).
- Public books do not expose all capital, and a displayed order is revocable intent (`c/27:7`).
- Inferred flows are estimates, and gross notional is not net inflow (`c/27:18`).
- Single-venue flow is never presented as consolidated (`c/27:46`, `c/09:29`), and consolidated global books are out of scope (`c/24:69`).
- REQ-002, REQ-020 and DEC-018 carry the same boundary, as does G01's Q-7 venue-local labelling.

**Live trading is out of scope:**
- Real accounts and live orders stay outside scope, and this setup implements no engines ([P03 phase](../../phases/03-market-state-and-ledger/README.md)).
- There is no live connector and there are no live orders (`c/13:15`, `c/13:21`).
- No API keys, paid GPU or live orders (`KERNEL:60`); DEC-028 amends this for data keys only.
- DEC-001, DEC-007, DEC-021, DEC-028 and DEC-058 record the same exclusion.

## 6. Stale text found

- **"Original v1.0 reconciliation is required before this phase can be accepted"** appears on the P03, P04, P06 and P07 phase pages. It is stale:
  - the [v1.0 reconciliation](../P00/v1.0-reconciliation.md) and its packets a to c exist;
  - G00 passed on 2026-10-24 (DEC-027);
  - P03's own page already cites the reconciliation's output (DEC-020, L-028).
- `phases/README.md` says P02 to P07 are "not started", but P02 has been in progress since 2026-10-28.
- [Architecture](../../architecture/README.md) still asks the CMP-04 question "What did 'ledger' mean in original v1.0?". DEC-018 answered it.
- The live sections of the event contract and the capture design (G-3).
- The stale `live_records.py` DEC-067 docstring is fixed by TASK-P02-013 ([#39](https://github.com/akibrahimug/gladiators/pull/39)).

## 7. Proposed follow-ups

The coordinator owns the cards; none of them passes a gate.

1. **Decision requests before the ledger contract:** convention (Q8), order state machine (Q7), marking price (Q9), account currency and FX (Q10), cardinality (Q13).
2. **Decision request on where validity comes from (Q3),** before the market-state contract.
3. **P02 documentation fix:** mark §4.4, F-15 and mode C as authorised; record the live ordering key and the WebSocket-name alias (G-3 to G-5), each after a decision.
4. **Documentation hygiene:** the stale lines in section 6.
5. **Source research** for a Kraken fee schedule and an FX source under published terms (Q10, Q11), without waiting on vendors.
