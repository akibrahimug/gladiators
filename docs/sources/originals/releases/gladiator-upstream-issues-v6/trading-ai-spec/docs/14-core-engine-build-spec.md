# 14 — Core engine: implementation specification

Status: proposed architecture; no live-trading authorisation. This document supersedes dashboard work in the roadmap.

## Non-goals
No dashboard, charting UI, manual technical-analysis workflow, high-frequency trading, guaranteed returns, or automatic live activation. Operational visibility is structured logs, CLI reports and alerts.

## Runtime and modules
Python 3.12+, `uv` for dependency management, typed `pydantic` contracts, PostgreSQL (including pgvector only when RAG is introduced), Parquet/DuckDB for research, `pytest`, and Docker Compose. Prefer a modular monolith with strict package boundaries before microservices. Broker, model, and data vendor interfaces must be replaceable. Pin all versions and seeds; record commit SHA, config hash, data snapshot, and model checkpoint per run.

Suggested layout:
```
engine/
  contracts/      # typed events, orders, forecasts, model artifacts
  data/           # ingestion, timestamps, actions, quality, calendars
  features/       # causal feature pipelines and feature snapshots
  training/       # numerical training, tuning, calibration, registry
  llm/            # optional open-weight research model, RAG, read-only tools
  strategies/     # 10 challengers, deterministic policy implementations
  simulator/      # event-driven matching, fills, corporate actions, costs
  evaluation/     # walk-forward, bootstrap, multiple-testing controls
  portfolio/      # capital, exposure, available cash, mark-to-market
  risk/           # independent, deterministic veto and kill switch
  execution/      # broker adapters, idempotency, reconciliation
  scheduler/      # exchange-calendar jobs, retries, failure handling
  audit/          # immutable decision ledger, model lineage, metrics
configs/          # explicit paper/live configs; live default OFF
experiments/      # immutable run manifests and evaluation artifacts
scripts/          # CLI entry points
```

## Core data contracts
Each market event: instrument ID, exchange, source, source event timestamp, provider receipt timestamp, ingest timestamp, currency, adjustment state, and quality flags. Each feature has a computable `available_at` timestamp. Predictions include model ID/version, data snapshot ID, forecast horizon, return distribution or calibrated event probability, uncertainty, generation timestamp and expiry. Trade proposals include strategy ID, order intent, instrument, side, quantity or risk budget, thesis reference, forecast reference, stop/target policy, and expiry. Risk decisions include rule IDs, allow/reject, capped size, and reason. Orders include deterministic client order IDs and a broker status history. Every fill records executed price, quantity, spread estimate, commission, regulatory charges, FX costs and slippage estimate.

## Stage A — Data
- Start with liquid, UK-accessible instrument candidates; eligibility must be verified before live use.
- Ingest OHLCV and corporate actions; preserve raw immutable source alongside adjusted views.
- Reject duplicate/missing/out-of-order bars; detect stale prices and anomalous splits.
- Enforce point-in-time availability, trading sessions, daylight-saving transitions and instrument delistings.
- Produce versioned datasets with manifest and checksums.
- **Gate:** deterministic reconstruction of features at historical decision timestamps; synthetic leakage tests must fail.

## Stage B — Quantitative model training
- Begin with transparent baselines: no-trade, buy-and-hold benchmark, logistic/linear models and gradient-boosted trees. No assumption that an LLM predicts price reliably.
- Targets: horizon return distribution, realised volatility, market regime, and (conditional on proposed stop/target/time policy) exit-event probabilities.
- Use chronological train/validation/test separation, purging/embargo where labels overlap, walk-forward retraining, and a locked final holdout.
- Fit probability calibration only on permitted calibration partitions; report reliability diagrams, Brier/log loss, calibration by regime, uncertainty and drift.
- Hyperparameter selection cannot use the final holdout. Register model lineage and promotion decision.
- **Gate:** reproduce model predictions from frozen artifacts; demonstrate calibration and incremental value versus baselines on unseen data. No profitability requirement can be manufactured by repeated holdout reuse.

## Stage C — Strategy challengers
- Maintain 10 independently specified paper strategies (not necessarily 10 LLM instances), each with its own ledger and versioned policy.
- Initial families may include momentum, mean reversion, volatility breakout, cross-sectional ranking and regime-conditioned abstention; these are hypotheses, not assumed edges.
- A strategy may abstain; zero-trade sessions are valid. Restrict strategies to their registered instruments, session hours and risk envelope.
- Challenger research and parameter changes create new versions; never retroactively modify historical decisions.
- **Gate:** challengers produce valid, reproducible proposals from historical and forward inputs without access to future labels.

## Stage D — Simulation and evaluation
- Event-driven simulator processes market events, signals, risk checks, order submission, fills, cancellations, corporate actions and cash accounting in timestamp order.
- Model spread, commission minima, FX, regulatory fees, market impact assumptions, latency, gaps, stop slippage, partial fills and rejected orders. Stress-test cost multipliers.
- Compare against no-trade and passive benchmarks. Report net expectancy, return distribution, drawdown, turnover, tail loss, capital utilisation and risk-adjusted metrics.
- Quantify uncertainty using time/block bootstrap or other dependence-aware methods; account for overlapping trades, multiple strategy searches and regime shifts.
- Keep a locked test partition and a separate forward-paper ledger. Paper fills are not assumed equivalent to live fills.
- **Gate:** independent reproduction of P&L from event ledger, including fees; no candidate promoted solely for headline win rate.

## Stage E — Allocation and exits
- For each proposal, estimate conditional net expectancy and uncertainty *for its specific entry/exit policy*; abstain when evidence insufficient.
- Set provisional planned loss budget at <=1% of equity per trade, subject to review, with total position notional <= available cash for unlevered accounts; no margin by default.
- Position quantity for a long share example: `min(floor(risk_budget / estimated_loss_per_share), floor(available_cash / expected_entry_price), liquidity_cap)`; estimated loss per share includes conservative gap/slippage buffer. If estimated loss is undefined or unbounded under policy, reject.
- Treat theoretical Kelly fractions as diagnostic only until forecast calibration and payoff distribution are validated; never equate wager fraction with share notional or loss budget.
- Stops, targets, trailing and time exits are strategy-versioned. Never widen a stop automatically to avoid a loss. Adding to winners requires fresh evidence and a new aggregate risk check.
- **Gate:** property tests prove no order exceeds cash, risk, exposure or concurrency caps; gap scenarios show realised loss can exceed planned loss.

## Stage F — Independent risk gateway
- Separate deterministic process/module from LLM and challenger strategy code; default deny on missing/stale data, invalid clock, broker desync, model expiry or unresolved account balance.
- One concurrent live position maximum; initial maximum 2 new live entries/session is a ceiling, not target. Add portfolio daily/weekly loss limits, per-instrument exposure, order notional and rate limits before any live activation; exact thresholds require signed policy.
- Immutable risk policy loaded from protected configuration; strategy/LLM cannot edit it.
- Broker-hosted protective orders where supported, with documented limitations; kill switch cancels pending orders, halts new orders and reconciles existing positions (it cannot guarantee an immediate or specific exit price).
- **Gate:** adversarial and failure-injection tests show rejected unsafe orders and no duplicate live orders on retries.

## Stage G — Broker execution
- Paper adapter first, with identical proposal -> risk -> order -> event contract used for live adapter.
- Idempotent client order IDs, durable order state machine, retry with broker query-before-resubmit, position and cash reconciliation, market calendar checks and outage recovery.
- Maintain separate research, paper and live credentials; live permission disabled by default and requires explicit human enablement after independent evidence review.
- **Gate:** integration tests for partial fills, duplicate callbacks, rejected stops, stale quotes, disconnects, overnight gaps and manual broker-side changes.

## Stage H — Learning, promotion and retraining
- Daily append-only observations and trade outcomes. Weekly research review and conditional scheduled numerical retraining; no training on individual losses in production.
- Champion/challenger promotion requires preregistered criteria, minimum effective sample size, net-of-cost out-of-sample performance, calibration, drawdown and stability across periods. A fixed calendar does not force promotion.
- Keep model registry states: candidate -> validated -> paper champion -> eligible live -> suspended -> retired. Rollback retains prior checkpoints and decisions.
- Optional LoRA/QLoRA fine-tuning of open-weight research LLM only after establishing a curated task dataset and proving incremental utility over the base model; GPU budget and licence review required. LLM has read-only research tools and no order-placement privileges.
- **Gate:** full reproducibility and no degradation on locked evaluation; otherwise retain incumbent or no-trade.

## Stage I — Operations and cost accounting
- During market hours: ingest/validate bars; update features; run inference; evaluate challengers; run risk gateway; reconcile paper/live broker state. Outside hours: training, backtests, reporting and data audits.
- Emit JSON logs, traces, model metrics, per-provider usage/cost ledger and daily CLI reports. Alerts for stale data, model drift, order divergence, daily risk breach, cost budget breach.
- Budget ceilings must fail closed for discretionary LLM research, not interrupt broker reconciliation or emergency controls.
- **Gate:** unattended paper operation with recovery drills and reproducible daily account reconciliation.

## Implementation order (no UI)
1. Repo scaffold, contracts, config and deterministic tests.
2. Data ingestion, point-in-time feature store and snapshots.
3. Event-driven simulator and net-of-cost ledger.
4. Baseline quantitative training, calibration and walk-forward evaluation.
5. Ten versioned challenger strategies and paper ledgers.
6. Independent risk gateway and paper broker integration.
7. Continuous forward-paper operations, audits, failure injection.
8. Open-weight LLM research layer and optional fine-tuning *only if measurable value*.
9. Independent live-readiness review and UK broker/instrument/fee verification.
10. Human-approved, small live canary; default remains paper-only.

## Required CLI examples
`engine data ingest --config configs/research.yaml`
`engine features build --snapshot SNAPSHOT_ID`
`engine train --config configs/baseline.yaml`
`engine backtest --strategy challenger_01 --snapshot SNAPSHOT_ID`
`engine evaluate --cohort challengers_v1`
`engine paper run --config configs/paper.yaml`
`engine audit reconcile --date YYYY-MM-DD`
`engine costs report --month YYYY-MM`

## Open implementation choices
Data vendor and licensing, eligible instrument universe, actual broker eligibility and charges, risk limits beyond per-trade provisional ceiling, numerical model stack, chosen open-weight LLM/size, GPU rental rates, and thresholds for champion promotion must be resolved and recorded as dated decisions before depending on them.
