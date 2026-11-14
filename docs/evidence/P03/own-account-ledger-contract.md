# P03 own-account ledger contract (draft): simulated cash, positions, orders, fills and fees

[Task](../../tasks/TASK-P03-008.md) · [P03 phase](../../phases/03-market-state-and-ledger/README.md) · [Source map](source-map.md) · [Market-state contract (draft, #42)](https://github.com/akibrahimug/gladiators/pull/42) · [Kraken fee schedule (#41)](https://github.com/akibrahimug/gladiators/pull/41)

**Status: draft for review, 2026-11-14. This is preparation only.**
- **Acceptance:** it is accepted only with G03, after G02. It implements nothing.
- **Values:** values marked **Proposed** need approval before anything is measured.
- **References:** `L` and `Q` numbers refer to the [source map](source-map.md).

**Scope.** This contract covers the system's **own simulated account**: CMP-04, "the simulated cash, position, order and fee journal" (L20). It is kept separate from the market book (REQ-006, DEC-004, DEC-018).
- **Instances:** one CMP-04 contract with isolated instances. The own account is one instance, and each paper challenger has its own (DEC-078; L27).
- **Out of scope:** real accounts, broker keys, live orders and capital (DEC-001, DEC-021, DEC-028, DEC-058). Reconciliation against a broker is out of scope (Q14). P03 reconciles the journal against a replay of itself and against the simulator's fills.

## 1. Conventions (decided)

| Item | Rule | Basis |
| --- | --- | --- |
| Bookkeeping | **Double-entry.** Every event posts balanced entries per currency. The identity `cash + marked holdings − liabilities = equity` holds by construction, and is also checked after every event; a failure quarantines the instance (L1, L8) | DEC-076 |
| Order states | `NEW → ACCEPTED → PARTIAL → FILLED`, `CANCELLED` or `REJECTED`, plus `UNKNOWN`. A lost acknowledgement is never assumed filled or cancelled | DEC-077, L5, L7 |
| Currency | Each instance is kept in its venue's quote currency: **USD** for Kraken. No FX in P03; GBP reporting and an FX source are decided at G05 | DEC-080, DEC-039 |
| Marks | Longs at best bid, shorts at best ask, from a `VALID` book only (market-state contract §4). Otherwise the mark is `UNKNOWN` and equity is flagged `stale` | DEC-079 |
| Independent check | Reference fixtures with hand-computed expected results (§7) | DEC-081, L26 |
| Fees | Kraken Pro's published schedule read 2026-11-14, tier 1: **0.40 % maker, 0.80 % taker**, undiscounted. Versioned by read date | DEC-082, L13 |

## 2. Numbers (Q12)

**Proposed:**
- **Representation:** amounts are exact decimals, never binary floats (L10). They are stored as decimal strings, with scale fixed per asset:
  - USD: 8 decimals in the journal;
  - BTC and ETH: 8 decimals (`lot_decimals`, `AssetPairs`).
- **Prices:** kept at the pair's `pair_decimals` (BTC/USD 1, ETH/USD 2).
- **Fee rounding:** half-up to the USD journal scale (8 decimals), computed per fill on that fill's quote notional, so fees never round to zero by splitting a fill.
- **Lot sizing:** `floor_to_lot` (L9); the remainder is not traded. A shortfall below `ordermin` (BTC 0.00006, ETH 0.002) or `costmin` (USD 0.5) means the order is **rejected** (T17, L14).
- **Fee currency:** a **declared assumption**. The fee is charged in USD on the fill's quote notional. Kraken's page does not state the currency (fee record, #41). `fee_currency` stays an explicit field, so a later change is a convention version, not an edit.

## 3. Accounts (chart)

These accounts exist per instance. Each posting names an account, a currency, an amount (debit +, credit −) and the event that caused it.

| Account | Currency | Meaning |
| --- | --- | --- |
| `cash` | USD | Settled cash |
| `cash_reserved` | USD | Cash held for open buy orders (price × qty + maximum fee) |
| `position:<asset>` | BTC, ETH | Holdings, in base units |
| `position_reserved:<asset>` | BTC, ETH | Holdings held for open sell orders |
| `cost_basis:<asset>` | USD | The cost of the current holdings (average cost, **Proposed**) |
| `fees` | USD | Trading fees paid (a `trade_costs` line, L11) |
| `realised_pnl` | USD | Realised P&L, excluding fees |
| `capital` | USD | Deposits and withdrawals of simulated capital (`capital_flows`, L11), kept separate from P&L (L1) |

**Not in this chart:**
- **`research_costs`** (L11) belong to the cost ledger, not to an account instance.
- **Unrealised P&L** is not posted. It is computed at each mark as `marked holdings − cost basis` (§5).

## 4. Events and postings

Events are append-only (L1). Each has:
- `event_id`, `instance_id` and `as_of` (UTC ns);
- `causation_id`: the event or market record that caused it;
- `correlation_id`: the order;
- the idempotency key (L2).

The event envelope follows the P02 contract (§3) and the reinstated L-008 and L-023 envelope (source map B11, B12, G-10).

| Event | Postings | State change |
| --- | --- | --- |
| `Deposit(amount)` | `cash` +a; `capital` −a | — |
| `OrderSubmitted(intent)` | Buy: `cash` −r, `cash_reserved` +r, where r = limit price × qty × (1 + taker fee). Sell: `position` −q, `position_reserved` +q | `NEW`. Rejected at once (state `REJECTED`, no postings) if cash or position is short. Cash never goes negative, since there is no margin (L3) |
| `OrderAccepted` | — | `NEW → ACCEPTED` |
| `Fill(qty, price, liquidity)` | Buy: `cash_reserved` −(price × qty + fee); `position` +qty; `cost_basis` +price × qty; `fees` +fee. Sell: `position_reserved` −qty; `cash` +(price × qty − fee); `cost_basis` −average cost × qty; `realised_pnl` −(price × qty − average cost × qty); `fees` +fee | `ACCEPTED`/`PARTIAL → PARTIAL` or `FILLED` |
| `OrderCancelled` / `OrderRejected` | The remaining reservation is released to `cash` or `position` | `→ CANCELLED` / `REJECTED` |
| `OrderStatusUnknown` | — | `→ UNKNOWN`. No new entry until it is resolved (L5: cancellation races and retries reconcile before further entry) |
| `Mark(book_state)` | None (a valuation, not a posting) | Equity recomputed; `stale` if the mark is `UNKNOWN` |

**Rules:**
- **Duplicate fills:** a fill whose idempotency key (the simulator's fill ID) was already applied changes nothing (T05, L14).
- **Failed orders:** a failed or rejected order never becomes a position (L3).
- **No fictitious fills:** if no bids exist when a fill is due, the order stays open and the ledger records a pending state (L15).
- **Same-bar take-profit and stop-loss:** these are not resolved optimistically (L3). That is the simulator's rule (CMP-10, P06); the ledger only receives fills.

## 5. Reconciliation equations

These are checked after every event, per instance and per currency (L1, L8, L22):

1. **Double-entry balance:** the sum of all postings is 0, per currency.
2. **USD identity:** `equity = cash + cash_reserved + Σ marked holdings − liabilities`. In P03, liabilities = 0, since there is no margin and no borrowing.
3. **Capital and P&L:** `equity = −capital + realised_pnl_total − fees_total + unrealised`, where `unrealised = Σ (marked holdings − cost_basis)` and `realised_pnl_total = −balance(realised_pnl)`.
4. **Positions:** for each asset, `position + position_reserved` equals the sum of filled quantities.
5. **Replay:** replaying the journal from empty gives exactly the same balances (L3, "replay ledger balances exactly").

If any check fails, the instance is **quarantined**. New orders stop (T14), and the event is kept for audit. With no valid mark, check 2 uses `UNKNOWN`, and equity is reported as `stale` rather than as a number.

## 6. Interface (L2)

- `submit(approved_intent)` takes an intent carrying its model, core and gatekeeper evidence (L2) and an idempotency key.
- `on_market_event(event)` applies fills from CMP-10 and marks from CMP-03.
- `get_state(as_of)` returns balances, positions, open orders and equity at `as_of`, from events with `as_of` at or before it.
- `reconcile()` runs the §5 checks.

Every output carries the instance's identity (L4): `run_id`, `as_of`, `dataset_hash`, `code_version`, `config_hash`, `model_version`, plus `fee_schedule_version` (2026-11-14) and `convention_version`.

## 7. Reference fixtures (DEC-081)

Each fixture has hand-computed expected balances at every step, written before any implementation exists.

| Fixture | Scenario | Expected |
| --- | --- | --- |
| LF-01 | Deposit USD 500; buy 0.001 BTC at 60,000.0, as taker | Cost 60.00000000. Fee 0.80 % = 0.48000000. Cash 439.52000000, BTC 0.00100000, cost basis 60.00000000, fees 0.48000000; identity holds |
| LF-02 | LF-01, then sell 0.001 BTC at 61,000.0, as maker | Proceeds 61.00000000. Fee 0.40 % = 0.24400000. Cash 500.27600000, realised P&L 1.00000000, fees 0.72400000, equity 500.27600000 |
| LF-03 | The LF-01 fill delivered twice | Balances as LF-01 (T05) |
| LF-04 | A buy that is partly filled, then cancelled | The remaining reservation is released exactly; state `CANCELLED` |
| LF-05 | A buy larger than cash | `REJECTED`, no postings, cash unchanged (L3) |
| LF-06 | A buy of 0.00005 BTC (below `ordermin`) | `REJECTED` (T17) |
| LF-07 | An acknowledgement lost | `UNKNOWN`; a second submit is refused until resolved |
| LF-08 | Mark while the book is `INVALID` | Mark `UNKNOWN`, equity `stale`, no number |
| LF-09 | Replay of LF-01 to LF-04's journal from empty | Identical balances (check 5) |
| LF-10 | A posting removed from the journal | Check 1 fails; instance quarantined; new orders refused (T14) |
| LF-11 | Two challenger instances trading the same records | Balances independent; no posting crosses instances (DEC-078) |

**Gap loss beyond stop risk (L3)** is a simulator case (CMP-10, P06). LF fixtures cover only the ledger's side: a fill below the stop price is booked at its fill price.

## 8. Still open

| Item | Status |
| --- | --- |
| Average cost (or FIFO) for `cost_basis` | Proposed: average cost |
| Decimal scales and fee rounding (§2) | Proposed |
| Fee currency | Declared assumption (USD) until Kraken's convention is checked |
| Whether BTC/USD and ETH/USD get the −0.02 % pair discount | Unknown; the fixtures use the undiscounted rate |
| CMP-03 as an input of CMP-04 (marks), missing from the [component register](../../traceability/components.md) | Open; register update on acceptance |
| GBP reporting and FX | Deferred to G05 (DEC-080) |
| Dividends and splits (L18) | Not applicable to crypto; deferred with the ETF scope (DEC-029, DEC-043) |
