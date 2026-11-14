# P03 own-account ledger contract (draft): simulated cash, positions, orders, fills and fees

[Task](../../tasks/TASK-P03-008.md) · [P03 phase](../../phases/03-market-state-and-ledger/README.md) · [Source map](source-map.md) · [Market-state contract (draft, #42)](https://github.com/akibrahimug/gladiators/pull/42) · [Kraken fee schedule (#41)](https://github.com/akibrahimug/gladiators/pull/41)

**Status: draft for review, 2026-11-14; revised after review the same day.** This is preparation only.
- It is accepted only with G03, after G02, and it implements nothing.
- Values marked **Proposed** need approval before anything is measured.
- `L` and `Q` numbers refer to the [source map](source-map.md).

**Scope.** This contract covers the system's **own simulated account**: CMP-04, "the simulated cash, position, order and fee journal" (L20). It is separate from the market book (REQ-006, DEC-004, DEC-018).
- There is one CMP-04 contract with isolated instances: the own account is one, and each paper challenger has its own (DEC-078, L27).
- Real accounts, broker keys, live orders and capital are out of scope (DEC-001, DEC-021, DEC-028, DEC-058). So is reconciliation against a broker (Q14). P03 reconciles the journal against a replay of itself and against the simulator's fills. T14 ("ledger/broker disagreement stops new orders") is applied here **by analogy**: the simulator stands in for the broker (source map L14).

## 1. Conventions (decided)

| Item | Rule | Basis |
| --- | --- | --- |
| Bookkeeping | **Double-entry.** Every event posts entries that sum to zero **in every currency, base assets included**. The identity is also checked after every event (§5); a failure quarantines the instance | DEC-076, L1, L8 |
| Order states | `NEW`, `ACCEPTED`, `PARTIAL`, `FILLED`, `CANCELLED`, `REJECTED`, plus `UNKNOWN` (§4.2) | DEC-077, L5, L7 |
| Currency | Each instance keeps its venue's quote currency: **USD** for Kraken. P03 uses no FX; GBP reporting and an FX source come at G05 | DEC-080, DEC-039 |
| Marks | Longs at best bid, from a `VALID` book only (market-state contract §4). Otherwise the mark is `null` and equity is reported `stale`. P03 has no shorts: there is no margin, and a sell needs a position. So the "shorts at best ask" half of DEC-079 does not arise | DEC-079 |
| Independent check | Reference fixtures with hand-computed results at every step (§7) | DEC-081, L26 |
| Fees | Kraken Pro's published schedule as read on 2026-11-14, tier 1, undiscounted: **0.40 % maker, 0.80 % taker**. The schedule is versioned by its read date | DEC-082, L13 |

## 2. Numbers (Q12)

All of these rules are **Proposed**.

- **Representation:** exact decimals, never binary floats (L10). They are stored as decimal strings at a fixed scale:
  - USD journal amounts: 8 decimals;
  - BTC and ETH: 8 decimals (`lot_decimals`, `AssetPairs`).
- **Prices:** each price must be a multiple of the pair's `tick_size`, which is 0.1 for BTC/USD and 0.01 for ETH/USD. Prices are kept at `pair_decimals`. An off-tick price is `REJECTED`. This is L8's integer tick arithmetic: a price is held as ticks × `tick_size`.
- **Minimums:** below `ordermin` (BTC 0.00006, ETH 0.002) or `costmin` (USD 0.5), an order is `REJECTED`. This is a backstop only: sizing and abstention happen upstream in CMP-07 and CMP-12 (L9, T17), and they should not send such an order.
- **Fees, rounded on the running total:** after fill *k* of an order, the fee charged so far is `round_half_up(rate × cumulative notional, 8)`. Each fill's fee is that total minus the fees already charged. So the fee total equals the fee on the order's whole notional, and splitting a fill cannot change it. A fee that rounds to 0 below 5 × 10⁻⁹ USD of fee is recorded as 0.
- **Buy reservation:** `r = ceil_8(limit price × qty × (1 + taker rate))`, the worst case. The running-total rounding keeps fees within it.
- **Order types:** the ledger accepts **limit orders only** in P03. A market order's reservation rule belongs to the simulator (CMP-10, P06) and is listed in §8.
- **Fee currency:** a **declared assumption**. The fee is charged in USD on the fill's quote notional. Kraken's page does not say which currency is charged, and Kraken's order API may charge in the base currency (fee record, #41). `fee_currency` is an explicit field, so a later change is a new convention version.
- **Cost basis:** average cost. On a partial sell, `cost_basis` is reduced by `round_half_up(average cost × qty, 8)`. When a position reaches zero, the whole remaining `cost_basis` is released, so no rounding residue stays behind.

## 3. Accounts (chart)

These accounts exist in each instance. A posting names an account, a currency and an amount (debit +, credit −), and its event.

| Account | Currency | Meaning |
| --- | --- | --- |
| `cash` | USD | Settled cash |
| `cash_reserved` | USD | Cash held for open buy orders |
| `position:<asset>` | BTC, ETH | Holdings, in base units |
| `position_reserved:<asset>` | BTC, ETH | Holdings held for open sell orders |
| `trade_clearing:<asset>` | BTC, ETH | The contra account for base-asset fills: −q on a buy, +q on a sell. Its balance is minus the net quantity bought |
| `cost_basis:<asset>` | USD | The average-cost basis of current holdings |
| `fees` | USD | Trading fees paid (`trade_costs`, L11) |
| `realised_pnl` | USD | Realised P&L, excluding fees. Its balance is minus the realised total |
| `adjustments` | USD or base | Corrections, each with a reason (§4.1) |
| `capital` | USD | Deposits and withdrawals of simulated capital (`capital_flows`, L11), kept apart from P&L (L1). Its balance is minus the net capital paid in |

**Not in this chart:**
- `research_costs` (L11) belong to the cost ledger, not to an instance.
- Unrealised P&L is not posted. It is computed at a mark: `unrealised = marked holdings − cost_basis`.

## 4. Events

Events are append-only (L1). Each carries:
- `event_id`, `instance_id`, `as_of` (UTC ns), `source` and `delay`. These give each flow its source and delay (L12).
- `causation_id`: the event or market record that caused it.
- `correlation_id`: the order.
- the idempotency key (L2).

The envelope follows the P02 contract (§3) and the reinstated L-008 and L-023 envelope (source map B11, B12, G-10).

**Order fields** (L7, `CORE:61`): `client_order_id` (also the idempotency key), `risk_decision_id`, `intent_id`, the model, core and gatekeeper evidence (L2), the simulator's order ID, side, limit price, quantity, `submitted_at`, `acknowledged_at` and the last-update time.

### 4.1 Postings

| Event | Postings (debit +, credit −) |
| --- | --- |
| `Deposit(a)` | `cash` +a; `capital` −a |
| `Withdrawal(a)` | `capital` +a; `cash` −a. Refused if `cash` < a |
| `OrderSubmitted`, buy | `cash` −r; `cash_reserved` +r. Refused, as `REJECTED` with no postings, if `cash` < r. Cash never goes negative: there is no margin (L3) |
| `OrderSubmitted`, sell | `position` −q; `position_reserved` +q. Refused if `position` < q |
| `Fill`, buy (qty q at price p, fee f) | USD: `cash_reserved` −(p·q + f); `cost_basis` +p·q; `fees` +f. Base: `position` +q; `trade_clearing` −q |
| `Fill`, sell | USD: `cash` +(p·q − f); `cost_basis` −c, where c is the average cost × q, or the whole remaining basis at zero; `realised_pnl` −(p·q − c); `fees` +f. Base: `position_reserved` −q; `trade_clearing` +q |
| Order ends `FILLED`, `CANCELLED` or `REJECTED` after acceptance | The remaining reservation goes back: `cash_reserved` −x and `cash` +x, or `position_reserved` −x and `position` +x |
| `Adjustment(reason, causation_id)` | A reversing set for the corrected postings, then the replacement set, both linked to the original by `causation_id`. A correction never edits an earlier event. It also covers a fill correction from the simulator (L23) |
| `Mark(book_state)` | No postings. Equity is recomputed |

Every row sums to zero in each currency. For example, the buy fill's USD legs are −(p·q + f) + p·q + f = 0, and its base legs are +q − q = 0.

**Cost reporting (L5).** Each fill record carries these as **report lines, not postings**:
- the reference mid at decision time and at submission time, taken from CMP-03;
- the quoted spread;
- the paid spread (fill price against the mid);
- slippage (fill price against the limit price, and against the decision mid).

Funding is 0 in P03, since there is no margin, and it is reported as 0.

### 4.2 Order transitions

| From | Event | To | Postings |
| --- | --- | --- | --- |
| — | `OrderSubmitted`, checks pass | `NEW` | Reserve (§4.1) |
| — | `OrderSubmitted`, a check fails (cash, position, tick, minimum, duplicate key) | `REJECTED` | None |
| `NEW` | `OrderAccepted` | `ACCEPTED` | — |
| `NEW`, `ACCEPTED` | `OrderRejected` | `REJECTED` | Release the reservation |
| `ACCEPTED`, `PARTIAL` | `Fill`, quantity left | `PARTIAL` | Fill |
| `ACCEPTED`, `PARTIAL` | `Fill`, nothing left | `FILLED` | Fill; release any residual (a maker fee or a better price) |
| `NEW`, `ACCEPTED`, `PARTIAL` | `OrderCancelled` | `CANCELLED` | Release the remainder |
| any open state | No acknowledgement or status within the simulator's timeout, or conflicting reports | `UNKNOWN` | **The reservation is kept** |
| `UNKNOWN` | A simulator status query (query before resubmit, L28; T06) answers `ACCEPTED`, `PARTIAL`, `FILLED`, `CANCELLED` or `REJECTED` | That state | As that state's row |
| `UNKNOWN` | `Fill` | Stays `UNKNOWN` | The fill is applied, so the order can be reconciled |
| `ACCEPTED`, `PARTIAL` | A fill due when no bids exist (L15) | Unchanged, flagged `pending_liquidity` | None; no fictitious fill |

**Rules:**
- **While any order is `UNKNOWN`,** the instance submits **no new order for that instrument**, and a resubmit with the same `client_order_id` is refused (L5: cancellation races and retries reconcile before further entry).
- **Duplicate fills:** a fill whose fill ID was already applied changes nothing (T05).
- **Failed orders:** a rejected or failed order never becomes a position (L3).
- **Same-bar take-profit and stop-loss, and gap losses:** these are the simulator's rules (CMP-10, P06). The ledger books the fills it receives at their prices.

## 5. Reconciliation (L1, L8, L22)

These checks run after every event, per instance:

1. **Balance:** postings sum to zero per currency, in USD, BTC and ETH.
2. **Mark-free identity** (always run): `cash + cash_reserved + cost_basis = −capital − realised_pnl − fees`. This follows from check 1 in USD, so it holds without a mark.
3. **Equity, when a valid mark exists:**
   - `equity = cash + cash_reserved + Σ (position + position_reserved) × mark − liabilities`. In P03, liabilities = 0.
   - Equivalently, `equity = (−capital) + (−realised_pnl) − fees + unrealised`, where `unrealised = Σ (position + position_reserved) × mark − cost_basis`.
   - With no valid mark, equity is reported as `stale` and no number is given.
4. **Positions:** for each asset, `position + position_reserved = −trade_clearing`.
5. **Replay:** replaying the journal from empty gives exactly the same balances (L3).

**Failure and quarantine:**
- **On a failure** (L6, T14 by analogy), the failing event is kept, with its postings, and flagged.
- **What stops:** the instance stops accepting new orders, while open orders and fills continue to be booked.
- **Lifting it:** only an `Adjustment` that restores the checks, with its reason and causation, lifts the quarantine. It is recorded.

## 6. Interface and outputs (L2, L21)

- `submit(approved_intent)` takes the order fields of §4.
- `on_market_event(event)` applies fills and corrections from CMP-10 and marks from CMP-03.
- `get_state(as_of)` returns, from events with `as_of` at or before the requested time:
  - balances, positions and open orders;
  - equity, or `stale`;
  - `ledger_version`, the hash of the journal so far;
  - `reconciliation_state`: `reconciled`, `quarantined` or `stale`.
- `reconcile()` runs §5.

Every output carries:
- the identity in L4: `run_id`, `as_of`, `dataset_hash`, `code_version`, `config_hash`, `model_version`;
- `fee_schedule_version` (2026-11-14) and `convention_version`.

**Determinism (Q5, Proposed).** The same events and the same config give the same journal and the same states, serialised as canonical JSON with decimal strings. No field comes from the replay's own clock.

## 7. Reference fixtures (DEC-081)

Every fixture is hand-computed. Its values are USD unless marked BTC, and all are at 8 decimals.

| Fixture | Steps | Expected after each step |
| --- | --- | --- |
| LF-01 | 1. Deposit 500. 2. Limit buy 0.001 BTC at 60,000.0. 3. Taker fill at 60,000.0. 4. Mark at bid 59,990.0 | **1:** cash 500; capital −500. **2:** r = 60.48000000; cash 439.52, reserved 60.48. **3:** fee 0.48000000; reserved 0, with no residual; BTC position 0.001, clearing −0.001; cost basis 60.00; fees 0.48; mark-free identity 439.52 + 0 + 60 = 500 − 0 − 0.48. **4:** marked holdings 59.99; equity 499.51; unrealised −0.01; check 3: 500 + 0 − 0.48 − 0.01 = 499.51 |
| LF-02 | LF-01, then 5. limit sell 0.001 at 61,000.0, and 6. a maker fill | **5:** BTC position 0, reserved 0.001. **6:** proceeds 61.00, fee 0.24400000; cash 500.27600000; cost basis 0; realised P&L 1.00 (balance −1.00); fees 0.72400000; clearing 0; equity 500.27600000 = 500 + 1 − 0.724 |
| LF-03 | The LF-01 fill delivered twice | As LF-01 step 3; the second is ignored (T05) |
| LF-04 | Deposit 500; limit buy 0.002 at 60,000.0; taker fill of 0.001; cancel | r = 120.96000000, so cash 379.04. After the fill: reserved 60.48, BTC 0.001, fees 0.48. After the cancel: reserved 0, cash 439.52, state `CANCELLED` |
| LF-05 | Deposit 500; limit buy 0.01 at 60,000.0 | r = 604.80000000 > 500, so `REJECTED`, no postings; cash 500 (L3) |
| LF-06 | Deposit 500; limit buy 0.00005 BTC at 60,000.0 | Below `ordermin` 0.00006, so `REJECTED` (a backstop; T17 abstention is upstream) |
| LF-07 | As LF-01 to step 2; the acknowledgement is lost | `UNKNOWN`; cash 439.52 and reserved 60.48 are kept. A resubmit with the same key is refused, and so is any new BTC order. The query answers `ACCEPTED`, so the state is `ACCEPTED`. The fill then gives LF-01 step 3 |
| LF-08 | LF-01 to step 3, then a mark while the book is `INVALID` | Equity `stale`, with no number. The mark-free identity holds: 439.52 + 0 + 60 = 499.52 = 500 − 0.48 |
| LF-09 | Replay of LF-01 to LF-04 from empty | Identical balances at every step (check 5) |
| LF-10 | LF-01 with the `cost_basis` posting of step 3 removed | Check 1 fails in USD by −60. The instance is quarantined, a new order is refused, and open fills are still booked |
| LF-11 | Two instances, A runs LF-01 and B runs LF-05 | A as LF-01; B cash 500. No posting crosses instances (DEC-078) |
| LF-12 | Deposit 500; limit buy 0.001 at 60,000.0; **maker** fill at 60,000.0 | r = 60.48. Fill fee 0.24, so the reserved balance is 60.48 − 60.24 = 0.24 and the residual is released when filled. Cash 439.76, reserved 0, fees 0.24, cost basis 60.00 |
| LF-13 | Deposit 500; limit buy 0.003 at 60,000.0, filled as taker in three fills of 0.001 | Fees 0.48 each; running total 1.44 = 0.8 % of 180.00. r = 181.44, all used; cash 318.56 |
| LF-14 | LF-01, then an `Adjustment` correcting the fill price to 59,990.0 (a simulator correction) | Reversal of step 3, then a replacement fill: fee 0.47992000, cost basis 59.99. The 0.00008 fee difference and the 0.01 price difference go back to `cash_reserved` and are released, so cash 439.53008000. All checks hold |

## 8. Still open

| Item | Owner / gate |
| --- | --- |
| Scales, tick rule, fee rounding on the running total, the reservation ceiling, average cost | Proposed; approval at G03 |
| Fee currency (USD assumption) | Checked against Kraken's order documentation before G03 |
| Whether BTC/USD and ETH/USD get the −0.02 % pair discount | Unknown; the fixtures use the undiscounted rate |
| The reservation rule for market orders | CMP-10 (simulator), P06 |
| The simulator timeout that moves an order to `UNKNOWN` | CMP-10, P06 |
| CMP-03 as an input to CMP-04 (marks) in the [component register](../../traceability/components.md) | Register update on acceptance |
| GBP reporting and FX | G05 (DEC-080) |
| Dividends and splits (L18) | Not applicable to crypto; deferred with the ETF scope (DEC-029, DEC-043) |

**Relation to TASK-P03-002.** Board candidate TASK-P03-002 ("Separate simulated-account ledger contract, accounting convention and fixtures") is the acceptance-stage task for this subject. This draft is its preparation. After G02, TASK-P03-002 carries it forward.
