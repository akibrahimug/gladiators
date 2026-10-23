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

---

## v0.4 Qlib/RD-Agent integration and version policy
Qlib is the primary quant research framework. Its main branch includes ongoing unreleased changes; documentation warns that source `main` may differ from tagged/PyPI builds, including artifact-loading trust restrictions. **Pin an exact tested release and lock dependency versions**; never load untrusted serialized Python objects or models. Verify installed Python/macOS support with an installation smoke test instead of trusting a stale doc page.

Qlib's official dataset is temporarily disabled. Implement a deterministic importer from our clean Parquet/SQL layer into Qlib-compatible structures, with round-trip checks for prices, timestamps, labels and corporate actions.

RD-Agent integration is **opt-in**: generate candidate factors in a sandbox, statically validate feature causality, enforce time/CPU/memory budgets, require reproducible tests, then evaluate through the exact same Qlib/Judges protocol as hand-built factors. Agent-generated code has no filesystem, credential or broker access outside a constrained workspace.

FinRL-X is a candidate for later sequential-policy evaluation, but must pass common-tape equivalence and execution-accounting tests before admission.
