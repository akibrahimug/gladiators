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

---

## v0.4 cost verification (2026-10-21)
Phase 1 remains **£0 paid services**, not literally zero electricity/time cost. Disable API-key-dependent paid calls and all cloud training by default. Local Qlib/LightGBM/XGBoost/SQLite/DuckDB are first-line components.

Potential future costs (not phase-1 commitments): Alpaca Algo Trader Plus lists **$99/month** for consolidated US equity coverage versus free IEX-only Basic; IBKR US stocks list tiered **$0.0035/share, $0.35 minimum/order**, fixed **$0.005/share, $1 minimum/order**, plus possible exchange/clearing/regulatory charges. FX conversion, funding/withdrawal, UK eligibility and tax must be separately checked.

Any cloud LLM/RL/GPU challenger requires a signed experiment budget: max GPU-hours, token cap, storage/egress allowance, kill switch, receipt and net benefit over local baseline. An expensive model has no privileged rank.

Sources: https://docs.alpaca.markets/us/docs/about-market-data-api ; https://www.interactivebrokers.co.uk/en/pricing/commissions-stocks.php ; https://www.interactivebrokers.co.uk/en/pricing/market-data-pricing.php . Prices are dated, may change and are not approved live costs.
