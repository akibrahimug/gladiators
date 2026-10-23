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


## Upstream dependency intelligence
Before admitting or upgrading a gladiator, follow [upstream issue review and fork policy](19-UPSTREAM-ISSUES-AND-FORK-POLICY.md). Record affected versions, P0/P1 defects, reproduction evidence, local mitigations and rollback plans.


## Algorithm research backlog

Maintain the priority register [22-ALGORITHM-REGISTER.csv](22-ALGORITHM-REGISTER.csv), evidence dossiers and external peer review records per [21](21-ALGORITHM-RESEARCH-AND-REVERSE-ENGINEERING.md) and [23](23-CORE-ASSURANCE-AND-PEER-REVIEW.md).

## Market intelligence programme (v0.9 amendment)
Management owns coverage and feed-rights registers, release-calendar correctness, event-detection incident reviews, false-alarm/latency scorecards, stale-feed budgets, market blackout experiments and monitoring of unobserved domains per [24](24-MARKET-AWARENESS-AND-REGIME-DETECTION.md). Management cannot override market-state vetoes; it can propose audited policy upgrades after held-out/paper evidence. Plans must distinguish continuously running collectors from offline/replay experiments.
