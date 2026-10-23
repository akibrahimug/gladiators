# 04 — Model selection, training and RAG

## Two distinct owned model families
**A. Quantitative predictors (trade probabilities):** start with logistic regression and gradient-boosted trees; expand to time-series volatility/regime models, calibrated ensembles and potentially RL only after baselines. Train on causal features and point-in-time labels. These produce numerical forecasts used by the allocator.

**B. Finance-adapted open-weight LLM (research):** choose a small model from an appropriately licensed Qwen/Llama-family checkpoint after checking current licences, context length, inference footprint, benchmark results and hardware cost. It proposes testable hypotheses, uses MCP tools, reads research memory and creates structured reports. It cannot authorise execution.

## Training stages
**T0 Data audit:** establish data licence, universe, survivorship, corporate actions, `available_at` timestamps, splits, market calendars, benchmark.

**T1 Baseline predictors:** trivial no-trade, buy-and-hold benchmark, volatility baseline, logistic/boosting; time-based train/validation/test with purging and embargo where labels overlap.

**T2 Probability calibration:** reliability curves, Brier score, log loss, calibration per regime and horizon, confidence/credible intervals, distribution shift. Calibrate on held-out validation data, not test.

**T3 Financial LLM adaptation:** curate verified financial documents and supervised examples of valid hypotheses, correct tool usage, uncertainty reporting and refusal to fabricate forecasts. Start with retrieval and prompt/evaluation baselines; run LoRA/QLoRA only if measurable improvement justifies GPU spend.

**T4 Strategy lab:** LLM suggests strategies; deterministic simulator scores them; freeze hypotheses and record trials. No reward from in-sample P&L alone.

**T5 Offline outcome learning:** transform audited decisions, costs, market states and outcomes into curated examples. Evaluate preference optimisation or RL only with safe reward and offline benchmarks; guard against reward hacking and simulation exploitation.

**T6 Challenger retraining:** weekly candidate training if sufficient new evidence; periodic LLM adapter updates (e.g., monthly/quarterly) only when validated; keep champion immutable until promotion.

**T7 Forward evaluation:** paper-only shadow decisions on live incoming data with immutable model version and precommitted metrics.

**T8 Controlled promotion:** independent evaluator and operator approval; canary with one live slot only after all readiness gates.

**T9 Monitoring and rollback:** drift, calibration decay, unexpected cost, data changes, drawdown, risk incidents trigger suspension; revert to prior validated checkpoint or no-trade.

## RAG design
- Collections: public filings/research (time stamped), strategy specifications, experiment reports, trade journal, failure analyses, broker rules.
- Every chunk: `source_id`, `document_version`, `published_at`, `available_at`, `licence`, `content_hash`, `embedding_version`.
- Retrieval enforces `available_at <= simulated_decision_time` for backtests; avoid hindsight leakage.
- Model text and retrieved content are untrusted. Never allow documents to issue instructions to tools.
- RAG stores experience; **does not update model weights**. Fine-tuning/retraining is a separate versioned offline process.

## Training budget gates
- First quantify CPU baselines and data quality; GPU spend = £0.
- Before LoRA: record model size, VRAM, token count, expected GPU hours, hourly price, storage and egress, licence and total spending cap.
- Never run ten 24/7 GPUs for ten agents; prefer shared weights + adapters/policies.
- Compare adapted LLM against unadapted model on held-out finance reasoning tasks and end-to-end strategy research utility.

## Model registry
Fields: `model_id`, `family`, `base_checkpoint`, `adapter_hash`, `dataset_hash`, `training_code_commit`, `seed`, `train_window`, `validation_window`, `test_window`, `calibration_version`, `cost`, `metrics`, `approval_state`, `created_at`.
