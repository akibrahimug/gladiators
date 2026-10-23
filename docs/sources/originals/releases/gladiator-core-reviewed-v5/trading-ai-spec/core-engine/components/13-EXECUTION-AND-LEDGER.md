# Execution simulator and reconciled ledger

Status: design specification; not a claim of implemented functionality.

## Simulator first
Event-driven, cash-aware paper broker. Process bar/quote availability, intent, gatekeeper approval, order acceptance, partial fill, fees, position update, stop/target/time exit, settlement and reconciliation in chronological order. Avoid filling at the same close used to generate a signal unless an executable order could genuinely have reached that price.

## Execution realism
Commission minimums, bid/ask spread, price impact, slippage, FX, tick/lot sizes, insufficient cash, rejected orders, holidays, trading halts, overnight gaps, partial fills, order latency, and corporate actions. A stop is an order trigger, not a guaranteed execution price. Do not assert quote-level realism from daily OHLC alone; represent intrabar order ambiguity conservatively.

## Ledger
Append-only events for deposits, orders, fills, fees, FX, dividends, splits, realised and unrealised P&L, cash, positions, equity, outstanding orders. Reconcile accounting identity after every event; quarantine mismatch. Separate strategy P&L from external operating costs and capital deposits.

## Interface
`submit(approved_intent)`; `on_market_event(event)`; `get_state(as_of)`; `reconcile()`. Every order has idempotency key and originating model/core/gatekeeper evidence. No live connector during phase 1.

## Tests
Cash never negative without explicit margin (margin disabled); no duplicate fill; gap loss can exceed planned stop risk; same-bar TP/SL ambiguity not optimistically resolved; failed order cannot become position; replay ledger balances exactly.

## Operational invariants
- Phase 1: zero paid external services, no live orders, no dashboard; terminal text/number output only. Use local files and explicit, free, permitted data sources. Network pulls require explicit invocation.
- Every artifact includes `run_id`, UTC `as_of`, immutable `dataset_hash`, `code_version`, `config_hash`, and relevant `model_version`.
- Reject missing, stale, future-dated, unlicensed or unverified inputs; `ABSTAIN` is valid and preferable to guessing.
- Do not infer profitability from backtests. Keep chronological holdouts, realistic costs, and independent forward-paper validation.
- No LLM, gladiator, or management agent may modify gatekeeper limits or access live broker credentials.

## v0.5 execution accounting invariants
- No same-bar optimistic ordering when OHLC alone cannot establish whether stop or target hit first. Use lower-bound/worst-case assumptions or reject ambiguous cases.
- Enforce order state machine `NEW -> ACCEPTED -> PARTIAL -> FILLED|CANCELLED|REJECTED`; cancellation races and retries must reconcile before further entry.
- Distinguish quoted spread, paid spread, fees, slippage, FX and funding; report all separately. For spot crypto, model maker/taker and minimum size; for ETFs, model exchange calendar and corporate actions.
