# Core decision kernel

Status: design specification; not a claim of implemented functionality.

## Purpose
The core is the **single authority for opportunity decisions**, not for final order authorisation. It takes a point-in-time market state, eligible model forecasts, a portfolio state and a fee/risk policy; outputs `ENTER|HOLD|REDUCE|EXIT|ABSTAIN` with rationale and uncertainty. A kernel without forecasts abstains.

## Submodules (separate Python modules)
- `observe.py`: exchange calendar, completed bars, liquidity, market regime and stale checks.
- `forecast.py`: verify calibration, horizons, provenance, expiry; ensemble only if validated and correlation-aware.
- `opportunity.py`: enumerate symbol/direction/horizon/entry/exit candidates and mandatory no-trade baseline.
- `utility.py`: estimate *net* outcome distribution using path-dependent exits, commissions, bid/ask, slippage, gaps and FX; conservative confidence bound.
- `allocation.py`: propose size constrained by available cash, expected stressed loss, liquidity and opportunity cost. Kelly only after empirical validation and never a bypass of risk caps.
- `position.py`: re-evaluate hold/reduce/exit/tighten/add on each eligible event; no stop widening to hide losses.
- `decision.py`: pure orchestration; return traceable intent; no broker SDK imports.

## Mathematical contract
`EV(a)=sum_s p(s|x,a)*PnL(s,a)-E[cost(a)]`; uncertainty and covariance matter. Require conservative positive net EV and independently validated strategy before entry. Compute break-even costs and abstain if confidence interval spans negative outcomes under the approved threshold. Do not treat model confidence scores as calibrated probabilities.
`risk_budget = equity * risk_fraction`; `qty <= floor(risk_budget / stressed_loss_per_share)` and `qty <= floor(available_cash / all_in_price)` for integer shares; additional liquidity/position caps apply. A stop is an intended exit, not a guaranteed loss cap.

## Terminal acceptance
`gladiator core decide --snapshot fixtures/known.json --model artifacts/model-id --offline` prints action, quantity, expected net P&L, risk, evidence IDs and reasons. Repeat gives byte-identical result with fixed config. Future-bar injection, stale quote, contradictory predictions, zero cash and excessive fees must each lead to correct abstention/rejection.

## Operational invariants
- Phase 1: zero paid external services, no live orders, no dashboard; terminal text/number output only. Use local files and explicit, free, permitted data sources. Network pulls require explicit invocation.
- Every artifact includes `run_id`, UTC `as_of`, immutable `dataset_hash`, `code_version`, `config_hash`, and relevant `model_version`.
- Reject missing, stale, future-dated, unlicensed or unverified inputs; `ABSTAIN` is valid and preferable to guessing.
- Do not infer profitability from backtests. Keep chronological holdouts, realistic costs, and independent forward-paper validation.
- No LLM, gladiator, or management agent may modify gatekeeper limits or access live broker credentials.

## v0.5 decision invariants (22 October 2026)
- Every opportunity carries `forecast_target`, `forecast_horizon`, `forecast_as_of`, `first_executable_at`, `expected_holding_period`, and `model_calibration_version`; an end-of-bar feature may not execute at that same bar's earlier price.
- Probability of a positive return is **not** probability of reaching a stop/target first. Path-dependent barrier probabilities require path-aware labels/simulation; otherwise abstain from claiming such probabilities.
- Calculate incremental utility of ENTER, HOLD, REDUCE, EXIT and ABSTAIN on the **same decision timestamp**. Existing exposure, fees and tax assumptions are state inputs.
- Core returns a decision proposal and audit trace; it never chooses which dataset/model version is approved and never writes broker orders.
