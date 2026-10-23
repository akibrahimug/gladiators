# Costs, reliability and terminal operations

Status: design specification; not a claim of implemented functionality.

## Phase 1 hard budget
No external recurring subscriptions, hosted model inference, paid market-data feeds, paid cloud GPUs or broker funding. Local hardware/electricity/time have real economic cost but no provider bill. Disable automatic billable endpoints and default to offline mode. Any future cloud trial needs explicit per-run max cost and manual approval.

## Cost ledger
Separate `trade_costs` (commission, spread, slippage, FX, regulatory, borrow if ever applicable), `research_costs` (compute, storage, model/API calls, data licences), and `capital_flows` (deposits/withdrawals). Record currency, billing unit, usage, rate source/date, tax, budget and actual bill. Never use stale quoted broker pricing as settled fact; verify broker jurisdiction, eligibility, account minimums and current schedules before live.

## Runtime operations
Commands output human-readable ASCII tables or `--format json`; logs to local append-only files. Health checks: source freshness, training age, calibration drift, queue backlog, model load, disk capacity, integrity, event reconciliation, cost ceiling. Kill switch default on for live. Daily backups of metadata/ledger and reproducible snapshots; test restore monthly.

## Financial feasibility
£500 -> £10,000 is 20x; cannot project a reliable completion date without validated positive net returns. Report gross trading P&L, net trading P&L and net-after-research-cost separately. Do not optimise a fixed deadline or guaranteed monthly return.

## Operational invariants
- Phase 1: zero paid external services, no live orders, no dashboard; terminal text/number output only. Use local files and explicit, free, permitted data sources. Network pulls require explicit invocation.
- Every artifact includes `run_id`, UTC `as_of`, immutable `dataset_hash`, `code_version`, `config_hash`, and relevant `model_version`.
- Reject missing, stale, future-dated, unlicensed or unverified inputs; `ABSTAIN` is valid and preferable to guessing.
- Do not infer profitability from backtests. Keep chronological holdouts, realistic costs, and independent forward-paper validation.
- No LLM, gladiator, or management agent may modify gatekeeper limits or access live broker credentials.
