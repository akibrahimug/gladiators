# Gladiators: model contracts and roster

Status: design specification; not a claim of implemented functionality.

## Definition
A gladiator is a versioned **predictor or trading policy** implementing one shared interface; not necessarily an LLM. Local, cloud, CPU and GPU entrants use the same evidence contract. Gladiators do not trade directly.

## Initial roster and phases
1 Spartacus: Qlib LightGBM returns; 2 Maximus: Qlib XGBoost; 3 Leonidas: Qlib neural time series (later); 4 Achilles: FinRL RL (later); 5 Ares: regime-aware ensemble; 6 Athena: FinBERT sentiment + quant (only if time-stamped text exists); 7 Caesar: local Qwen research agent (later); 8 Hannibal: FinGPT experiment (later); 9 Brutus: relative-value/statistical model; 10 Titan: opt-in cloud challenger (disabled in £0 phase). Fill unavailable slots with **honestly named simple baselines**, not fake LLM deployments. Frameworks are not proven profitable models.

## Forecast contract
`predict(snapshot_id, as_of_utc, horizon, feature_version) -> {model_id,version,train_end_utc,feature_hash,forecast_distribution,calibration_id,expires_at,uncertainty,provenance}`. Policies additionally emit candidate actions and predicted outcomes, never broker orders. Abstention is allowed.

## Training and admission
Train on past-only data; label horizons must mature; nested validation; model card describes target, features, hardware, licence, cost and failure regimes. Arena admission requires reproducible artifacts, time budget, memory budget, deterministic seed when possible and validated schema. Qwen/FinGPT agents may propose hypotheses but cannot assert made-up win probabilities.

## Cost and maintenance
CPU baselines first; serialize heavyweight model runs; optional GPU/cloud only by explicit user approval. Check model drift, calibration decay, dependency security and model-card updates. Archive every retired gladiator's failures for learning.

## Operational invariants
- Phase 1: zero paid external services, no live orders, no dashboard; terminal text/number output only. Use local files and explicit, free, permitted data sources. Network pulls require explicit invocation.
- Every artifact includes `run_id`, UTC `as_of`, immutable `dataset_hash`, `code_version`, `config_hash`, and relevant `model_version`.
- Reject missing, stale, future-dated, unlicensed or unverified inputs; `ABSTAIN` is valid and preferable to guessing.
- Do not infer profitability from backtests. Keep chronological holdouts, realistic costs, and independent forward-paper validation.
- No LLM, gladiator, or management agent may modify gatekeeper limits or access live broker credentials.

---

## v0.4 roster and integration decision
**Qlib** supplies training/evaluation workflows. **RD-Agent** is an optional *research gladiator* that proposes factors/model improvements; it does not earn a live slot without independent testing. **FinRL-X** (FinRL-Trading) is the current modular RL/portfolio-framework candidate; the original FinRL repository labels itself the earlier educational/research implementation.

**FinGPT** should be judged on actual financial NLP tasks, not presumed trading profitability. Published evaluation finds useful sentiment/classification performance but weaker complex reasoning and numerical tasks. **FinBERT** is a sentiment feature producer, not a price forecaster. **Qwen** is a candidate general research LLM, not a proven alpha source.

Phase 1 (strict £0): ten *CPU-compatible* entrants drawn from linear/boosting/regime/simple-policy baselines, with no requirement to instantiate ten LLMs. Phase 2: opt-in local LLM; Phase 3: opt-in cloud challenger with per-run capped spend and separate budget. All entrants use the same versioned `Forecast`/`PolicyProposal` schema and cannot execute orders.
