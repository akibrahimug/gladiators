# Gatekeeper: independent risk and permissions

Status: design specification; not a claim of implemented functionality.

## Role
Independent deterministic policy engine. Only it can approve a proposed order. It never accepts policy changes from a gladiator, LLM or core output. Paper broker must enforce approvals too.

## Hard rules (initial research defaults, configurable and versioned)
£500 simulated equity; cash account, long-only shares, no leverage, shorting or derivatives. One position maximum for eventual live operation; max two new live entries per session; live off. Initial intended per-trade loss budget 0.5–1% NAV (£2.50–£5 at £500); cannot guarantee actual loss due to gaps. Cap gross exposure, order notional, liquidity participation, total daily loss, stale-data tolerance and simultaneous pending orders. Reject absent bid/ask/cost estimates, unsupported instrument, expired approval or unreconciled positions.

## Approval path
Receive `TradeIntent`; independently fetch immutable portfolio, fee schedule and policy; validate idempotency, available cash and stressed loss; reduce quantity or veto; issue time-limited signed approval with decision ID and exact order parameters. Transport/broker accepts only approved intents; reconciliation confirms fills and fees. Kill switch always overrides.

## Exit safety
Protective stop submitted through broker when supported, with explicit gap/slippage caveat; timeouts and partial fills handled; exit intents can reduce risk even if entry paused. No adding to a losing position without independently approved policy; no stop widening solely to avoid loss.

## Failure tests
Duplicated intent produces one order; disconnected broker prevents entry; stale data veto; gap simulation may exceed planned risk and must appear in ledger; kill switch blocks all new entries; model cannot write risk config.

## Operational invariants
- Phase 1: zero paid external services, no live orders, no dashboard; terminal text/number output only. Use local files and explicit, free, permitted data sources. Network pulls require explicit invocation.
- Every artifact includes `run_id`, UTC `as_of`, immutable `dataset_hash`, `code_version`, `config_hash`, and relevant `model_version`.
- Reject missing, stale, future-dated, unlicensed or unverified inputs; `ABSTAIN` is valid and preferable to guessing.
- Do not infer profitability from backtests. Keep chronological holdouts, realistic costs, and independent forward-paper validation.
- No LLM, gladiator, or management agent may modify gatekeeper limits or access live broker credentials.

## Independent regime/availability veto (v0.9 amendment)
Gatekeeper independently validates the `MarketIntelligenceSnapshot` and affected symbols at order time; it does not trust the Core's claimed regime. `DATA_BLIND|DISLOCATED|HALTED` prevent new exposure; `SHOCK` blocks affected new entries until versioned policy conditions clear. Existing positions require a distinct risk-reducing-exit policy with fresh executable quotes when obtainable; a missing feed is **not** permission to fabricate a market fill or blindly liquidate at last price. Exchange halts, broker-native stops, gap loss and reconciliation remain explicit. Thresholds need replay calibration, not LLM edits. See [24](24-MARKET-AWARENESS-AND-REGIME-DETECTION.md).
