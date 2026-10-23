# Choosing the core model: concrete candidates and decision gates

## Critical design decision
The **predictive core** should be a trainable numeric model, not a conversational LLM. The **research core** can be an open-weight LLM with RAG. These have separate objective functions, datasets, inference costs and evaluation criteria. No pretrained financial LLM is known to confer a verified tradable edge merely by downloading it.

| Candidate | What it actually is | Proposed role | Limitation |
|---|---|---|---|
| **Microsoft Qlib** | Open-source quantitative research/data/model/backtest framework | Research framework or reference implementation for numeric pipeline | Not a pretrained money-making LLM; inspect data conventions and licenses |
| **FinRL** | Reinforcement-learning research framework for financial trading | Later benchmark for policy optimisation | Sim-to-live gap, reward hacking, regime instability |
| **FinGPT** | Open-source finance-oriented LLM research ecosystem, with variants/adapters | Candidate research/financial-text baseline | Version/checkpoint/license/quality vary; not automatically a numeric predictor |
| **FinBERT** | Finance-domain language classifier/sentiment model family | Turn timestamped news into candidate sentiment features | Sentiment != future price; news availability and data rights matter |
| **Qwen open-weight instruct family** | General-purpose instruction LLMs with local inference/fine-tuning options | Primary **candidate** for research/RAG, subject to exact checkpoint benchmark | GPU memory, licence and model-specific cost must be measured |
| **Llama open-weight instruct family** | General-purpose instruction LLM family | Alternative research/RAG candidate | Model licence/use terms, memory and cost vary |
| **Logistic regression / boosted trees** | Numeric supervised predictors trained on our point-in-time features | **First predictive champion candidate** | Weak edge possible; careful calibration and walk-forward required |

## Recommendation and decision sequence
1. **Build clean data first**, and a numerical baseline with logistic regression and boosted trees; establish reproducible leakage-free out-of-sample results. No LLM required for this gate.
2. Evaluate **Qlib** for feature/model experiment management against our own contracts; integrate only if it saves work without losing provenance or causal controls.
3. Evaluate **FinBERT** on timestamped text only if a legally usable news feed is available; no news, no sentiment feature.
4. Compare one small **Qwen** instruct checkpoint with a **FinGPT** variant on a frozen 100–300-case research benchmark: accurate tool use, refusal to invent prices/probabilities, correct numeric interpretation, JSON contract adherence, hallucination rate, latency, VRAM and £/1,000 decisions. Keep exact model identifiers and licences in registry before download/deployment.
5. Use LoRA/QLoRA only after a dataset of verified task examples exists and the adapter improves held-out evaluation; keep base model as rollback. Fine-tuning does not imply continual online learning.
6. Consider **FinRL** only after deterministic supervised baselines and realistic simulator exist; RL reward is net risk-adjusted outcome with compliance constraints, never raw profits alone.

## Why no single LLM selected today
Checkpoint-specific context size, VRAM, availability, pricing, licence, quantisation quality and task performance need actual measurements on the intended machine. Choosing a model name without a benchmark would create lock-in before we know its usefulness. **Default engineering choice:** numeric logistic baseline first; Qwen small instruct model as the first *research-layer benchmark*, not as an automatic trade signal.

## Reproducible model bake-off
Record for each candidate: exact repo and commit/checkpoint SHA, tokenizer, licence, weights checksum, quantisation, hardware, peak RAM/VRAM, cold/warm latency, input/output tokens, cost per evaluation, correctness, abstention, calibration (numeric models only), time-to-train, data leakage checks and performance against simple baselines. Choose on evidence, not branding.
