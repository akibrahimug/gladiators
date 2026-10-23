# Thinking in Systems: causal governance

Status: design specification; not a claim of implemented functionality.

## Stocks and flows
Stocks: cash, positions, outstanding orders, training evidence, model registry, risk capacity, compute budget. Flows: fills, realised losses, fees, new data, label maturity, promotion/demotion, retraining and infrastructure spend. Each flow has source, delay and conservation/accounting rule.

## Feedback loops
Reinforcing: successful backtests -> more tuning -> higher apparent score -> selection bias; counter with untouched holdout and multiple-testing correction. Successful paper results -> more research allocation, not automatic live leverage. Balancing: drawdown -> risk throttle -> fewer orders; stale data -> abstention; rising research costs -> reduced experiments.

## Delays and nonlinearities
Forecast labels mature only after horizon; execution quality may degrade with size; broker latency and market impact grow nonlinearly; regime changes make recent wins unreliable. Monitor delays explicitly and avoid retraining from incomplete outcomes.

## Leverage points and diagnostics
Prioritise objectives, information integrity, incentive design, constraints and evaluation quality ahead of model size. Keep causal-loop register: hypothesis, expected feedback, leading indicator, unintended effect, monitoring and rollback. Quarterly review system boundary assumptions, correlated model errors and whether the optimisation objective matches capital preservation plus long-run net expectancy.

## Operational invariants
- Phase 1: zero paid external services, no live orders, no dashboard; terminal text/number output only. Use local files and explicit, free, permitted data sources. Network pulls require explicit invocation.
- Every artifact includes `run_id`, UTC `as_of`, immutable `dataset_hash`, `code_version`, `config_hash`, and relevant `model_version`.
- Reject missing, stale, future-dated, unlicensed or unverified inputs; `ABSTAIN` is valid and preferable to guessing.
- Do not infer profitability from backtests. Keep chronological holdouts, realistic costs, and independent forward-paper validation.
- No LLM, gladiator, or management agent may modify gatekeeper limits or access live broker credentials.
