# Management: orchestration and governance

Status: design specification; not a claim of implemented functionality.

## Responsibilities
Schedule research, training, competitions and promotion; maintain model registry and budgets; decide when to pause the system. Management has **no authority to waive risk controls**.

## State machine
`RESEARCH -> TRAINING -> VALIDATION -> PAPER -> ELIGIBLE -> CHAMPION -> PROBATION -> RETIRED`. Every transition requires signed evidence, reason, timestamp and rollback target. Live is separate and disabled by default.

## Cadence and feedback delays
Every completed bar: data freshness and possible core decision. Daily: reconcile paper trades and verify label maturity. Weekly: retrain candidates on matured observations; evaluate drift. Monthly: independent judge review. Retraining does not directly mutate the active champion. Delayed labels prevent immediate credit for open trades.

## Budget controls
Phase 1 provider/API/cloud/broker bill = £0. Local compute only. Later cloud requires explicit allowlist, maximum spend, experiment ID, hard timeout and fail-closed on budget exhaustion. Record total cost of ownership separately from trade P&L; evaluate whether incremental performance covers costs.

## Incidents and rollback
On bad data, drift, risk rejection spikes, model failure, broker mismatch or cost overrun: pause new intents, preserve ledger, open incident, identify cause, replay fixtures, require signoff before restart. Never recover drawdown by increasing leverage.

## CLI acceptance
`gladiator management status`; `management plan --offline`; `management promote --candidate ... --judge-report ...`; `management pause --reason ...`; `management rollback --version ...`. Unauthorized promotion rejected.

## Operational invariants
- Phase 1: zero paid external services, no live orders, no dashboard; terminal text/number output only. Use local files and explicit, free, permitted data sources. Network pulls require explicit invocation.
- Every artifact includes `run_id`, UTC `as_of`, immutable `dataset_hash`, `code_version`, `config_hash`, and relevant `model_version`.
- Reject missing, stale, future-dated, unlicensed or unverified inputs; `ABSTAIN` is valid and preferable to guessing.
- Do not infer profitability from backtests. Keep chronological holdouts, realistic costs, and independent forward-paper validation.
- No LLM, gladiator, or management agent may modify gatekeeper limits or access live broker credentials.

---

## v0.4 management change-control
New model family proposals, RD-Agent factor suggestions, new data vendors and FinRL-X integrations are **research change requests**. They cannot silently modify production training, historical data or scoring. Each request carries hypothesis, expected marginal benefit, costs, failure mode, code provenance and rollback plan.

Weekly maintenance: verify dataset/source licences and integrity, frozen experiment reproducibility, dependency advisories and model drift; daily check data freshness and ledger. Freeze champion weights until formal promotion. No auto-purchase or automatic cloud spending.
