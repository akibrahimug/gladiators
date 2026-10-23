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

---

## v0.4 independent audit updates
Qlib currently has publicly reported issues concerning first-period maximum drawdown and volume unit interpretation in market-impact calculations. Treat these as **reports, not confirmed defects in the installed pinned release**. Cross-check all official framework metrics against independent, fixture-based implementations.

Required test fixtures: (a) initial loss on first observation; (b) buy/sell cash ledger with exact per-order fees; (c) volume shares versus currency notional; (d) split/dividend handling; (e) gap through stop; (f) missing-bar non-execution; (g) partial fills; (h) overlapping labels and correlated trades.

Judges publish confidence intervals via block/bootstrap or regime-aware methods as appropriate, control multiple comparisons, and mark insufficient evidence **INCONCLUSIVE**, never PASS. Any new RD-Agent factor must be compared against a pre-registered baseline on unseen data.
