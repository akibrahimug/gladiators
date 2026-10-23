# The Arena: rules and maintenance

Status: design specification; not a claim of implemented functionality.

## Purpose
Fair, reproducible competition for model/strategy configurations, never unrestricted autonomous trading. Ten challengers initially; one qualified champion can eventually hold the single live slot.

## Match rules
- Same point-in-time eligible universe, bars, calendar, corporate actions, fee/slippage simulator and capital constraints for all entrants.
- Chronological train/validation/locked test split; purging/embargo for overlapping labels; walk-forward evaluation and unseen forward paper.
- Never use future revised data, delisted-name omissions or today's constituent lists in historical selection without point-in-time evidence.
- Benchmarks: no trade, buy-and-hold where relevant, simple momentum/mean-reversion and random policy sanity check.
- Separate *prediction* tournaments (calibration/error) from *policy* tournaments (net realised simulation). Compare equal risk budgets and capacity.
- Track correlated positions and overlapping outcomes; do not count 10 near-identical agents as 10 independent successes.

## Tournament lifecycle
`REGISTER -> ELIGIBILITY -> TRAIN -> VALIDATE -> LOCK -> REPLAY -> SCORE -> PAPER -> JUDGE -> PROMOTE/PROBATION/RETIRE`. Each run persists seeds, data and code hashes, config, fees, fills and decisions. Promotion requires independent approval from judges and gatekeeper; no automatic promotion from one leaderboard.

## Maintenance
Daily after session: ingest/validate new matured labels, reconcile simulated fills, check clock/data drift, export results. Weekly: run challenger experiments, investigate failures and dependency changes. Monthly: review frozen evaluation sets, false discovery risk, correlated exposures and costs. Rotate test periods carefully; keep an untouched final holdout and log each access. Archive losing strategies and reasons, never erase them.

## CLI and acceptance
`gladiator arena register --config ...`; `arena run --dataset ... --as-of ... --seed 42`; `arena leaderboard --run ...`; `arena audit --run ...`. An entrant with leaked features is disqualified. Identical inputs reproduce identical rankings; altered fees change outcomes appropriately.

## Operational invariants
- Phase 1: zero paid external services, no live orders, no dashboard; terminal text/number output only. Use local files and explicit, free, permitted data sources. Network pulls require explicit invocation.
- Every artifact includes `run_id`, UTC `as_of`, immutable `dataset_hash`, `code_version`, `config_hash`, and relevant `model_version`.
- Reject missing, stale, future-dated, unlicensed or unverified inputs; `ABSTAIN` is valid and preferable to guessing.
- Do not infer profitability from backtests. Keep chronological holdouts, realistic costs, and independent forward-paper validation.
- No LLM, gladiator, or management agent may modify gatekeeper limits or access live broker credentials.

---

## v0.4 tournament design and maintenance
- **Two leagues:** Forecast League compares calibration, log loss/Brier and horizon-specific directional/return errors; Policy League compares *net* executable simulated P&L and risk. A good classifier is not automatically a profitable trading policy.
- **Common tape:** immutable point-in-time snapshots and identical order/fill/cost simulator. For text agents, documents must be available before decision time.
- **Ten slots are not ten GPUs:** initial CPU baselines/strategies fill all slots; Qwen/FinGPT/FinRL-X/Titan are admitted only after functioning adapters and resource approvals.
- **Data isolation:** lock a final test window before experimentation; keep a separate chronological forward-paper stage. Track how many hypotheses and hyperparameter combinations were tried. Purge/embargo overlapping labels; assess correlated model returns and effective sample size.
- **Maintenance:** weekly dataset checksum and replay test; each tournament records code/data/feature/model/cost versions, random seeds, failures, compute use and judge sign-off. Do not re-rank retroactively when the data vendor revises history; create a new tournament.
- **Adversarial matches:** rising/falling/range regimes, crash/gap, halted market, stale data, fee doubling, spread widening, liquidity shock, provider outage and corrupted model output.
