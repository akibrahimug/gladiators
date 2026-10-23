# CORE — autonomous quantitative trading engine

Status: **build specification + executable offline vertical slice**, 2026-10-21. This document supersedes UI/dashboard work. No live broker connection is implemented or authorised. A runnable proof of plumbing is **not evidence of a profitable strategy**.

## Immutable product contract
- Starting account: GBP 500, target GBP 10,000 as an aspiration, not a forecast or reward signal.
- Research: ten independently versioned simulated challenger strategies; production: **at most one concurrent live position** and **at most two new live entries per session** (ceilings, not targets). Live disabled by default.
- Market hypothesis: initially liquid US equities, 15-minute/1-hour decision horizons; instruments must be legally accessible through the chosen UK account. No leverage, short selling or options in v1.
- Trading is conditional, never compulsory; abstention is valid. Operating costs paid separately from trading capital and measured against returns.
- **Terminal-only:** text, numeric tables, JSON/CSV audit files. No dashboard, charts, browser or GUI dependencies.
- The core decision loop is: timestamped data → causal features → calibrated numerical forecasts → challenger policies → realistic event simulator → independent deterministic risk veto → paper broker → reconciliation → immutable evidence → retraining/promotion. An open-weight LLM assists research and interprets evidence; it never authorises or submits orders.

## Stages, in build order, with acceptance gates

### 0. Repository and safety
Python 3.12+, modular monolith, pinned dependencies, typed contracts, pytest, CI. Distinct `research`, `paper`, and `live` configs and credentials. `live.enabled=false` by default. Configuration version/hash, git commit, seed and data snapshot on every experiment. CLI commands must be idempotent and return nonzero on errors. Gate: tests pass, live path unreachable without explicit signed enablement and a second human confirmation.

### 1. Point-in-time data lake (FIRST)
- Select a provider with documented US-equities OHLCV/corporate-action coverage, adjustment rules, historical depth, redistribution/licensing terms, costs and rate limits. Vendor choice **OPEN**; no claims of verified prices/coverage.
- Raw append-only records in `data/raw/<provider>/<symbol>/<date>.*`; normalized partitioned Parquet in `data/curated/`, queryable via DuckDB; SQLite/Postgres for catalog, lineage, event ledger and metadata. Store vendor payload, source URL/endpoint, request ID, fetched_at, checksum, schema version, adjustment basis, licence and provenance. Keep raw and adjusted series separately.
- Bar fields: `symbol, venue, interval, event_time_utc, received_at_utc, available_at_utc, open, high, low, close, volume, currency, adjustment_basis, provider, quality_flags`. Never assume candle close is observable before the interval ends. Ingestion time is not economic availability time.
- Enforce UTC, exchange calendars/DST, session breaks, monotonic timestamps, unique (symbol, interval, timestamp, provider, adjustment), OHLC consistency, nonnegative volume, splits/dividends, symbol changes/delistings, missing bars and market halts. Quarantine suspect bars; don't silently forward-fill returns or prices across halts. Prevent survivorship bias with point-in-time instrument membership.
- Snapshot immutable manifest: source partitions, hashes, earliest/latest event time, available_at watermark, adjusted/raw flag, corporate-action version and coverage metrics.
- **RAG does not feed numerical bars into the prediction engine.** Numeric models read versioned curated data/feature snapshots directly. RAG retrieves research documents, experiment reports, filings and lessons, with point-in-time metadata and citations; any retrieved claim used in an executable signal must be converted into validated structured features. This prevents context-window truncation and retrieval leakage.
- Gate: exact reproducibility from snapshot, no future-dated data in any feature, clear source provenance, failing tests for injected leakage, duplicates and splits.

### 2. Causal feature store and labels
- Build features as-of `decision_time` with explicit `available_at <= decision_time`: lagged returns, realized volatility, rolling volume, spread/liquidity proxies, momentum, regime proxies and calendar context. Shift completed bars as needed; fit scalers/imputers exclusively on training folds. Missingness is a feature or a reject condition, never silently imputed with future values.
- Forecast targets include horizon return, conditional volatility, and *policy-conditional* probability that a particular TP is reached before SL or time expiry. Label using executable entry assumptions and **future data only for training targets**, never for live features.
- Store feature definition hash, observation availability, horizon and lineage. Gate: time-travel test: a snapshot at time T is unchanged when later records are added.

### 3. Train our own quantitative predictors
- Begin with no-trade, buy-and-hold and naive baselines, then regularized logistic/linear models, gradient boosting (LightGBM/XGBoost/CatBoost after justified dependency choice), and regime/volatility estimators. Probabilistic models predict *distributions/uncertainty*, not an invented confidence score.
- Chronological train → validation → calibration → locked holdout; walk-forward and purged/embargoed splits when labels overlap. No random shuffle across time; don't reuse holdout to choose features or hyperparameters.
- Calibrate predicted probabilities on disjoint data; report Brier score, log loss, calibration error, confidence intervals, stability by regime and drift. Separate model version from policy version.
- Candidate output: `model_id, version, trained_through, snapshot_id, horizon, forecast_time, expires_at, distribution_or_event_probability, calibration_id, uncertainty, features_hash`.
- Gate: reproducible model artifact, honest out-of-sample calibration and value over simple baselines. If not, **NO TRADE**.

### 4. Research LLM and RAG (not the price oracle)
- LLM receives versioned structured forecast summaries and retrieved point-in-time research, proposes *hypotheses and experiment configurations*, and writes plain-text explanations. Read-only MCP tools: `list_snapshots`, `query_features`, `read_research`, `inspect_experiment`, `run_backtest_sandbox`, `compare_models`, `report_costs`. Never expose live credentials, `place_order`, risk-config writes or production model promotion.
- RAG pipeline: ingest document → classify provenance/licence → extract with timestamps → chunk → embed/index → retrieve with publication/availability cutoff → cite → validate structured output. Keep an append-only trade/experiment memory. Do not index future trade outcomes into earlier decision contexts.
- Fine-tuning is **optional and downstream of demonstrated value**. Use LoRA/QLoRA on curated labelled research/decision-explanation tasks, not raw candles as conversational prose. Version dataset, adapter, eval suite and licence. Evaluate against base model on held-out tasks; don't promote for fluent explanations alone.
- See `MODEL-SELECTION.md` for FinGPT, FinBERT, Qwen, Llama, Qlib and FinRL distinctions and decision process.

### 5. Ten challengers and one champion
- Ten *distinct* registered strategies (not necessarily ten GPUs or LLM instances): momentum, mean reversion, volatility breakout, trend-following, cross-sectional relative strength, volatility contraction, regime-filtered momentum, regime-filtered mean reversion, probabilistic TP-before-SL, and abstention/ensemble control. These are experiment hypotheses, not demonstrated alpha.
- Each has immutable strategy ID/version, eligible universe, horizon, feature/model dependencies, entry/exit rules, own simulated cash/positions/ledger and costs. A strategy may produce no proposals. Enforce no lookahead and identical available information across challengers.
- Champion promotion requires preregistered minimum *effective* sample, net-of-cost out-of-sample results, probability calibration, maximum drawdown, regime robustness, dependence-aware uncertainty, multiple-testing correction, and a separate forward-paper period. No forced monthly winner. Retain incumbent or no-trade if none qualifies.

### 6. Event-driven backtest / paper simulation
- Event order: market update → available features → forecast → proposal → risk veto → order → fill/cancel/reject → fees → cash/position marking → exit → audit. Model bid/ask, commission minima, spread, slippage, latency, market gaps, partial fills, rejected orders, split/dividend, FX and market calendar. For OHLC-only bars, same-bar TP/SL ordering is unknowable: use pessimistic policy or finer event data; never assume favorable ordering.
- Every fill updates an append-only double-entry-like cash/position ledger with currency and fee breakdown. Reconcile NAV to cash + marked holdings; use total return after all costs and taxes only when explicitly modelled. Stress-test 2×/3× costs, missing data and gaps.
- Report expectancy `p_win*mean_win - p_loss*mean_loss - costs` only for compatible binary outcomes; otherwise empirical mean of **all** realised net returns including time exits. Report return on deployed capital, drawdown, turnover, exposure, tail risk and holding time; do not use win rate as sole score.

### 7. Position sizing, exits and independent risk
- Provisional per-position *planned* loss budget <=1% equity (£5 at £500), with optional 0.5% research default; actual gap loss may exceed stop distance. `quantity <= min(floor(risk_budget / conservative_loss_per_share), floor(available_cash / all_in_buy_price), liquidity_limit)`; reject if denominator unknown, quote stale, order too small, fees overwhelm edge, or risk limits violated.
- Stops/TP must be specified jointly with their calibrated hitting probabilities and time horizon; support hard broker stop, ATR/volatility stop, trailing, time exit and partial exits in simulator. Never widen a stop merely to avoid crystallising loss. Add-to-winner only with new evidence and aggregate exposure/risk check. Fractional Kelly is research-only until payoff model and probability calibration validated; Kelly bankroll fraction is **not** nominal stock allocation or guaranteed stop-loss risk.
- Independent, deterministic default-deny risk gateway: cash, concentration, 1 concurrent live position, <=2 live entries/session, per-trade and aggregate planned risk, daily/weekly loss brakes, model/data staleness, trading hours, broker reconciliation, instrument eligibility and order rate. Kill switch prevents new orders, cancels pending where possible and reconciles positions; cannot guarantee liquidation price. No model can change risk policy.

### 8. Broker adapters and live canary (LATER)
- Paper and live share exact order-state contracts: client_order_id, intent, risk_decision_id, submitted/acknowledged/partially_filled/filled/cancelled/rejected/unknown states, fills, broker order ID and timestamps. Query broker before retry; deduplicate events. Reconcile cash, open orders and positions after outages. Keep API credentials isolated. Verify UK residency eligibility, tradable instruments, FX conversion, spread, exchange/regulatory/CAT charges, funding and withdrawal fees **in writing** before live activation.
- No live orders until forward paper evidence, independent risk tests, documented fees and explicit human approval. Never confuse broker paper execution with real-world fill quality.

### 9. Training/retraining, incentives and retirement
- Append trade outcomes only after fully observed; record unrealized and censored trades separately. Daily ingest/reconcile; weekly evaluation; conditional scheduled retrain with sufficient new independent samples; monthly challenger review. Do not retrain immediately after losses or optimize for raw profit/20× account growth.
- Incentive score prioritizes risk-adjusted net return, calibrated uncertainty, drawdown, operational compliance and robustness; reward abstention when expected value is not convincingly positive. Promote, probation, suspend and retire by predeclared gates; retain all failed trials to address multiple comparisons. Production models immutable until deliberate rollout; rollback always available.

### 10. Orchestration, cost and operations
- Market-session scheduler: ingest → validate → snapshot → feature → infer → challenger proposal → simulate/risk → reconcile. Off-hours: evaluate, audit, research, optional training. UTC scheduler + exchange calendar. At-least-once jobs with idempotent effects; backpressure and data-watermark checks.
- Terminal commands: `core data ingest`, `core data validate`, `core data snapshot`, `core features build`, `core train`, `core models compare`, `core backtest`, `core challengers run`, `core paper run`, `core risk check`, `core audit reconcile`, `core costs report`, `core status`, `core stop`. Output plain text or JSON with deterministic exit codes. No UI.
- Monthly line-item costs: VPS/CPU, object storage/backups, data vendor, LLM inference tokens, embeddings, GPU training hours, broker commissions/FX/market fees, transfer charges, taxes where relevant. Hard budget limit stops *discretionary* research, never reconciliation/risk controls. Starting target operating ceiling £20/month is a **budget objective**, not a verified quote or promise.
- Gate: unattended paper operation for a predefined period, outage/clock/gap drills, full ledger reconciliation and complete cost report.

## Formal outputs and decisions
- `Forecast`: model version, as-of, horizon, calibrated event probability and uncertainty.
- `Proposal`: strategy version, symbol, side, intended entry/exit, quantity suggestion, forecast reference, expiry.
- `RiskDecision`: approved/rejected, capped quantity, all rule outcomes and reason codes.
- `Fill`: order ID, timestamp, quantity, price, venue, costs and FX.
- `Experiment`: snapshot hash, code/config/model hashes, seed, all orders, metrics, failed hypotheses and promotion verdict.
- `Promotion`: independent evaluation evidence + explicit approval; no silent online production weight updates.

## Initial deliverable and truth in labelling
`runtime/` implements an **offline deterministic vertical slice**: CSV import → SQLite OHLCV storage → validation → causal feature generation → chronological logistic training (if scikit-learn installed) → basic next-bar, one-position backtest with cash/risk caps → plain terminal output. It is *not* a complete event simulator, RAG system, ten-agent trainer, broker adapter or production risk gateway. Those remain requirements above. See `RUN.md` for commands and `ACCEPTANCE.md` for implementation gates. Never treat demo returns as evidence of an edge.
