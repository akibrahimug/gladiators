# 06 — Strategy lifecycle, incentives and champion–challenger system

## Roles
- **Research agent:** generates falsifiable hypotheses, not trading commands.
- **10 challengers:** separate strategy policies/paper ledgers; not necessarily separate LLM instances.
- **Evaluator:** independent scoring and validation; cannot be overridden by model output.
- **Champion:** approved version eligible for one live position slot after human activation.

## States
`IDEA -> BACKTESTING -> HOLDOUT_REVIEW -> FORWARD_PAPER -> ELIGIBLE -> LIVE_CHAMPION -> PROBATION -> RETIRED`.
Any state can transition to `SUSPENDED` for security/risk incidents. Failed ideas remain in a searchable immutable archive; deletion would bias research.

## Incentive/reward design
Use **gated, risk-adjusted utility**, not a naive fixed weighted sum. Hard rule violations invalidate a candidate. Among eligible candidates rank: conservative net expected utility, out-of-sample robustness, probability calibration, expected shortfall/drawdown, execution realism, turnover/cost and benchmark-relative returns. Penalise excessive testing and model complexity. Reward correct abstention where no validated opportunity exists.

## Promotion policy
- Pre-register strategy hypothesis, universe, feature set, horizon, costs, evaluation metrics and failure criteria.
- Validate on chronologically unseen periods; reserve a final holdout never used to revise the candidate.
- Conduct forward paper trading across sufficiently varied market conditions; a minimum trade count alone is not proof.
- Test sensitivity to worse spreads, fills, missed orders and alternate regimes.
- Confirm no hard risk violations, reasonable calibration, stable performance, acceptable tail loss.
- Require explicit operator approval and versioned policy for first live deployment and material strategy changes.

## Demotion policy
- **Immediate suspension:** hard risk breach, stale market data, broker reconciliation mismatch, missing protection, security incident, order duplication.
- **Probation/review:** precommitted evidence of calibration drift, excessive costs, performance deterioration or regime mismatch; freeze new entries during review.
- **Retirement:** repeated independently verified failure, unacceptable tail risk or superior validated replacement.
- Losing trades are expected; do not retrain/demote on every loss. Preserve confidence intervals and sample-size limitations.

## Avoiding selection bias
Log all tested ideas and configurations; apply multiple-testing-aware selection, walk-forward testing, embargo, no future news leakage, realistic execution, and locked holdout periods. Never repeatedly tune against the same final test set.

## Retraining cadence
Candidate quant retraining may run weekly if there is sufficient new data; model drift can trigger evaluation earlier. Finance LLM fine-tuning is infrequent and contingent on quality of curated examples. Production champion never mutates weights during an open trade.

## Evidence bundle for promotion
Dataset and code hashes, strategy definition, training and calibration reports, backtest report, holdout report, forward paper report, cost sensitivity, failure scenarios, risk review, operator approval, model card and rollback target.
