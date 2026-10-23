# 07 — Allocation, stop-loss, take-profit and dynamic conviction

## Distinguish capital, risk and reward
A £100 share entry with a £96 stop and £108 target commits £100, plans a £4 loss and targets £8 gain per share (2:1 reward-to-risk). **It does not guarantee the loss is capped at £4**; gap/slippage can exceed the stop and a long share could lose its full value. Size by **both** capital available and loss budget.

## Initial research policy (not empirically optimised)
- Account £500; one live open position maximum.
- Planned loss budget per trade: 0.5–1% of account (£2.50–£5) **only after approval**.
- Maximum new live entries per day: 2, with zero acceptable.
- No margin/leverage, shorting, CFDs, options or futures in v1.
- No increase to hard risk cap or additional capital without explicit human approval.
- Additional daily loss, portfolio drawdown, liquidity and overnight exposure thresholds **must be set and approved before live launch**; see open decisions.

## Entry and size algorithm
1. Candidate strategy provides conditional return distribution and calibrated uncertainty.
2. Determine entry, stop, target, horizon, available liquidity and realistic costs.
3. Calculate conservative expected net return and tail-risk; reject if evidence insufficient.
4. `risk_budget = account_equity * approved_risk_fraction`.
5. `units_by_stop = floor(risk_budget / abs(entry - stop))` (adjust for fees, FX, gaps and lot rules).
6. `units_by_cash = floor(available_cash / fully_loaded_entry_cost)` (fractional shares only if broker supports).
7. `units_by_liquidity` and `units_by_portfolio` enforce concentration, market impact and global loss caps.
8. `approved_units = min(all_limits)`; reject if below broker minimum or insufficient benefit after costs.
9. Record proposed size, rejected alternatives and versioned risk policy.

## Conviction-based scaling
Confidence must be **empirical**: calibrated probability, uncertainty interval, independent model evidence, regime support, costs and available portfolio capacity. Consider capped fractional Kelly **only as an auxiliary diagnostic**, never direct unconstrained sizing. Kelly is fragile to misestimated probabilities and tail events. An apparently high-confidence signal can still receive zero allocation.

## Stop-loss
- Evaluate fixed, ATR/volatility-based and hypothesis-invalidation stops as distinct, pre-registered exit policies.
- Use broker-hosted protective orders when supported; verify active order state and correct quantity.
- LLM may request an early exit or tighter stop; it may **not** widen stop or remove protection autonomously.
- Gaps and stop-market slippage mean planned loss is not guaranteed; stop-limit orders may fail to fill.

## Take-profit and exits
- Test fixed bracket, volatility-adjusted target, trailing exit, time-based exit, partial profit taking and conditional exit based on updated return distribution.
- Every changed stop/target/horizon requires a fresh first-passage probability and expected-value estimate.
- Compare `HOLD`, `REDUCE`, `CLOSE`, `TIGHTEN_STOP`, `ADD`, `NO_TRADE` using net expected portfolio utility from the **current** state.
- Do not force take-profit merely because position is positive; do not indefinitely hold losers hoping for recovery.

## Pyramiding
Adding to winners is disabled initially. Later eligibility: strategy prevalidated for adding, current portfolio downside recomputed including all open lots, existing stop protection remains effective, net conservative utility positive, total risk and concentration below caps, and explicit operator enablement. Never average down automatically.

## Risk gateway failure cases
Stale quotes, bad spreads, earnings halts, market closed, missing stop, duplicate order, broker timeout, unacknowledged bracket, unavailable FX quote, risk policy mismatch or daily loss breach -> reject new entry, alert operator, reconcile broker state. Emergency shutdown must not blindly cancel protective stops on open positions.
