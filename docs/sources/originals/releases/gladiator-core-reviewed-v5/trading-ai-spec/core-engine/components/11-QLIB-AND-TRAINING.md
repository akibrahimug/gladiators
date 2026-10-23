# Qlib and the training pipeline

Status: design specification; not a claim of implemented functionality.

## Core decision
Use Microsoft Qlib for quantitative feature/model research and its workflows where appropriate, but wrap with our own point-in-time data audit, simulation validation, judge gates and execution-risk boundaries. Qlib is not a guaranteed profitable model or a substitute for the decision kernel.

## Pipeline
`clean versioned data -> Qlib-compatible dataset -> past-only features -> target labels (horizon and maturation) -> chronological split -> fit baselines -> predict -> calibrate on separate validation -> freeze -> backtest on unseen -> register artifact`. Start logistic regression, LightGBM and XGBoost. Later neural, RL and text features if incremental performance survives costs.

## Training protocol
Pre-register horizon, universe, features and costs. Use walk-forward windows, train-only transforms, purged labels for overlapping horizons, seed control, dependency lockfile and model metadata. Quantify uncertainty and calibration by regime. Avoid test-set hyperparameter selection; log all failed trials and multiple comparisons. A model version includes dataset hash, code hash, hyperparameters, calibration object, training cutoff, licence and inference runtime.

## Resource policy
CPU training on existing Intel iMac; sequential/limited parallelism, bounded RAM; no mandatory LLM or GPU. Local Qwen/FinGPT is a research option later, not the initial forecasting authority. Cloud GPU is optional only after explicit budget approval and proven incremental value.

## Tests
Known fixture yields identical features; future data edits do not alter earlier predictions; calibrator trained only on validation; model cannot forecast before its own training cutoff; no training labels from uncompleted horizons.

## Operational invariants
- Phase 1: zero paid external services, no live orders, no dashboard; terminal text/number output only. Use local files and explicit, free, permitted data sources. Network pulls require explicit invocation.
- Every artifact includes `run_id`, UTC `as_of`, immutable `dataset_hash`, `code_version`, `config_hash`, and relevant `model_version`.
- Reject missing, stale, future-dated, unlicensed or unverified inputs; `ABSTAIN` is valid and preferable to guessing.
- Do not infer profitability from backtests. Keep chronological holdouts, realistic costs, and independent forward-paper validation.
- No LLM, gladiator, or management agent may modify gatekeeper limits or access live broker credentials.

## v0.5 dependency security and versioning
- Qlib **v0.9.8** release notes describe security hardening: restricted expression parsing, explicit trust for loading executable recorder artifacts and local `.py` configuration imports. Pin and smoke-test the exact installed distribution; do not infer release/PyPI parity. Source: https://github.com/microsoft/qlib/releases
- Treat model artifacts, generated factors and research-agent code as untrusted unless verified. Avoid pickle-style executable loads from unknown origin.
- Keep separate target definitions for daily ETF returns, intraday ETF returns, and 24/7 crypto returns; no shared calendar or silent horizon conversion.
