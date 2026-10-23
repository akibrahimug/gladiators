# 11 — Delivery roadmap and acceptance criteria

## Phase 0 — Research constraints and vendor due diligence
Deliver: approved research universe, data rights, UK broker eligibility matrix, dated fee schedule, operational budget, risk policy draft.  
**Exit:** no unresolved provider/licence blockers for paper trading.

## Phase 1 — Data and reproducibility
Deliver: ingestion, point-in-time historical storage, quality checks, versioned datasets, corporate actions, exchange calendar, dashboards.  
**Exit:** reproducible bars/features and automated detection of leakage/stale data.

## Phase 2 — Mathematical baseline
Deliver: simple predictors, calibration, benchmark, event-driven simulator, realistic fees/spreads/slippage, walk-forward evaluation.  
**Exit:** independently reproducible backtests and explicit no-trade baseline; no requirement to show profit.

## Phase 3 — Research LLM and RAG
Deliver: selected licensed open-weight model, retrieval store, read-only MCP tools, structured hypothesis schema, prompt-injection tests.  
**Exit:** LLM cannot directly execute or change risk policy; hypotheses reproducibly convert to backtest configurations.

## Phase 4 — Ten challengers and incentives
Deliver: ten strategy policies, independent paper ledgers, model registry, promotion/demotion evaluator, immutable failed experiments.  
**Exit:** statistically defensible ranking, holdout discipline and correct abstention.

## Phase 5 — Allocation and exits
Deliver: calibrated first-passage probability per stop/target, conservative sizing, fixed/ATR/trailing/time exit comparisons, portfolio limits, paper order reconciler.  
**Exit:** deterministic risk gateway blocks unsafe and duplicate orders; stop handling tested for gaps and outages.

## Phase 6 — Forward paper trading
Deliver: live-feed paper operations, monitoring, cost reporting, independent evaluation across multiple market conditions.  
**Exit:** predefined evidence gates met, including net-of-cost performance, calibration, tail risk, no critical risk violations; if not met, remain paper-only indefinitely.

## Phase 7 — Finance model fine-tuning (conditional)
Deliver: curated dataset, LoRA/QLoRA candidate, benchmark against base model, GPU bill, rollback checkpoint.  
**Exit:** demonstrable incremental research utility justifies expense; otherwise retain base model.

## Phase 8 — Conditional live activation
Deliver: UK-eligible broker/account/instrument, verified all-in costs, broker-hosted protections, signed risk policy, human approval, single live slot.  
**Exit:** small live canary with full audit and automatic suspension; no promised return.

## Phase 9 — Scale only on evidence
Deliver: monthly champion review, realised cost comparison, drift checks, staged position sizing and operator-approved capital changes.  
**Exit:** preserve capital and evidence quality. £10,000 remains an aspirational outcome, not a deliverable.

## Implementation work order
1. Contracts and repository scaffold.
2. Point-in-time data ingestion and quality tests.
3. Baseline backtester and numerical model.
4. Risk policy and broker paper adapter.
5. Challenger registry and experiment evaluator.
6. Open-weight LLM and RAG integration.
7. Dashboard, alerts and cost accounting.
8. Forward-paper validation; only then consider live account.

## Critical tests
Lookahead leakage, survivorship bias, market calendar DST, split adjustment, correlated challenger samples, cost stress, partial fills, gaps, stop failures, duplicate order retries, broker reconciliation, kill-switch behaviour, API spend limits, prompt injection, model rollback and data drift.
