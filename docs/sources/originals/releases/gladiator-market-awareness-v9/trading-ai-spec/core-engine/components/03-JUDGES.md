# Judges: statistical evidence and promotion

Status: design specification; not a claim of implemented functionality.

## Responsibility
Judges evaluate evidence independently of gladiators, kernel and management. They do not execute orders or change risk policy.

## Hard disqualifiers
Lookahead/leakage; invalid labels; untracked dataset revisions; impossible fills; missing costs; broken calibration; unsupported asset access; unexplained data gaps; risk violations; test-set tuning; statistically meaningless sample; or inability to replay results.

## Scorecard (no single magic weighted score)
Report net compounded return, P&L per trade, downside and max drawdown, tail loss/CVaR, turnover, fees/slippage, time in market, capital utilisation, benchmark-relative return, regime consistency, calibration (Brier/log loss/reliability), uncertainty intervals, dependence-adjusted effective sample size and model operational cost. Include paper/live tracking error.

## Statistical procedure
Chronological nested walk-forward; compare strategies on aligned timestamps and identical costs; block bootstrap or other dependence-aware confidence intervals; adjust for repeated searches/multiple hypotheses; pre-register decision thresholds. No promise of a reliable universal sample-size cutoff. A challenger must pass *all* gates, not merely have a higher Sharpe.

## Outcomes
`REJECT`, `MORE_EVIDENCE`, `PAPER_ELIGIBLE`, `PROMOTION_RECOMMENDED`, `PROBATION`, `RETIRE`. Only management can schedule approved deployments and gatekeeper retains veto. Judges sign evidence manifest, test dates, metric table and caveats.

## CLI acceptance
`gladiator judges score --arena-run ...`; `judges compare --candidate ... --champion ...`; `judges audit-leakage ...`. Unit test: 100% win rate with catastrophic tail losses fails hard tail-risk gate.

## Operational invariants
- Phase 1: zero paid external services, no live orders, no dashboard; terminal text/number output only. Use local files and explicit, free, permitted data sources. Network pulls require explicit invocation.
- Every artifact includes `run_id`, UTC `as_of`, immutable `dataset_hash`, `code_version`, `config_hash`, and relevant `model_version`.
- Reject missing, stale, future-dated, unlicensed or unverified inputs; `ABSTAIN` is valid and preferable to guessing.
- Do not infer profitability from backtests. Keep chronological holdouts, realistic costs, and independent forward-paper validation.
- No LLM, gladiator, or management agent may modify gatekeeper limits or access live broker credentials.


## Algorithm correctness authority

Judges independently check algorithm invariants, trial multiplicity, event time, costs and the adversarial catalogue in [23 — assurance](23-CORE-ASSURANCE-AND-PEER-REVIEW.md). See [21 — research protocol](21-ALGORITHM-RESEARCH-AND-REVERSE-ENGINEERING.md).

## Event detector scoring (v0.9 amendment)
Judges independently compare price-only, event-only and fused market-change detectors on locked as-of replay streams. Score missed high-impact shifts, detection latency distributions, false alarms, opportunity cost, inappropriate liquidations, coverage gaps and post-cost outcomes. A detector that labels every day `SHOCK` is not robust. Separate anticipatory event windows from unexpected observations and narrative explanations. See [24](24-MARKET-AWARENESS-AND-REGIME-DETECTION.md).
