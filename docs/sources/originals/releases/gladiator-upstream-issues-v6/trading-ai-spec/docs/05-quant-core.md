# 05 — Quantitative mathematical core

## Objective
Maximise **conservative net risk-adjusted portfolio utility**, subject to independent loss, concentration, liquidity and drawdown constraints. Never maximise raw win rate or short-term P&L alone.

## Probability and expected value
For a simplified stop-or-target trade:

`EV = p_target * gain - (1 - p_target) * loss - expected_costs`.

Here `p_target` is **conditional on that specific entry, stop, target, time horizon and market state**. If stop or target changes, recompute the probability. Real trades have additional outcomes: partial fills, timeout, gap, stop slippage, corporate action, early discretionary exit. Production uses a scenario/return distribution, not only the binary formula.

For candidate action `a` at time `t`:

`NetUtility(a) = E[net_PnL(a) | F_t] - lambda_tail * ES_alpha(loss(a)) - lambda_turnover * turnover(a)`

where `F_t` contains only information available by time `t`, and `ES_alpha` is expected shortfall in the worst alpha tail. Coefficients are hyperparameters validated out of sample, not tuned on live P&L.

## Statistical pipeline
1. Construct causal features: returns, realised volatility, volume/liquidity, spreads, market regime, macro events available at decision time.
2. Define labels: horizon-specific net return distribution and first-passage outcome for each *candidate* stop/target pair; model censoring/time exits.
3. Train baseline and challenger models on chronological windows; purge overlapping labels and embargo adjacent periods.
4. Calibrate probabilities (e.g. isotonic or Platt on validation) and estimate uncertainty via block bootstrap or appropriate time-series methods.
5. Estimate net costs and market impact conservatively; account for uncertainty in fills.
6. Evaluate against cash, buy-and-hold and simple signal baselines using untouched chronological holdout and walk-forward periods.
7. Correct for strategy search/multiple comparisons; log all rejected trials and dataset peeks.
8. Reassess drift, calibration and costs before any trade.

## Numerical model candidates
- Logistic regression / gradient boosting for directional or first-passage probabilities.
- Quantile regression or distributional models for return tails.
- GARCH/realised-volatility baselines for risk forecasting.
- Hidden Markov or change-point regime detectors (treat regimes as uncertain).
- Monte Carlo/bootstrap stress tests with dependence-preserving resampling.
- Constrained allocation using portfolio covariance and tail-risk estimates.

## Model agreement
Do not count correlated signals as independent votes. Measure error correlation, diversify model families and calibrate ensemble predictions on untouched validation periods. If inputs are redundant, reduce conviction.

## Decision thresholds
Only trade if conservative lower-confidence expected utility is positive **and** a predefined minimum margin above costs and benchmark is met. Thresholds chosen on validation and frozen before forward evaluation. `NO_TRADE` is a first-class action.

## Evaluation metrics
Net P&L after costs, expected value in R-multiples, Brier/log loss, calibration slope/intercept, risk-adjusted return, worst drawdown, expected shortfall, turnover, exposure, time-in-market, cost sensitivity, regime breakdown and comparison to passive/cash benchmark. Do not use a single Sharpe estimate as proof of edge.

## Edge invalidation
Stop new entries when data quality fails, model drift exceeds precommitted threshold, confidence bounds cross zero, realised costs exceed assumptions, or regime falls outside validation support. Resume only after revalidation.
