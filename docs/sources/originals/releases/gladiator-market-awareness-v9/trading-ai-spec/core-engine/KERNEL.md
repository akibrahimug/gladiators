# THE CORE — decision kernel (not the arena)

Status: normative specification, v0.2. The **core** is the deterministic, inspectable process that turns a point-in-time market state and calibrated forecasts into one of `ENTER`, `HOLD`, `REDUCE`, `EXIT`, `ABSTAIN`. Gladiators generate forecasts or policies; the arena evaluates them; judges select; the gatekeeper vetoes; **the core decides what opportunity exists, how to act, and when to stop**. It never invents a probability or assumes a model is profitable.

## 0. Non-negotiable operating contract
- No guaranteed profitability; GBP 500 is the initial *simulated* portfolio, GBP 10,000 is an aspiration and never a training reward. Zero paid services for phase 1, no dashboard, terminal-only output.
- Initial universe: liquid US equities; UK-live tradability must be independently confirmed. 15m and 1h completed bars; only market-hours research in phase 1; no margin, shorts or derivatives. One live position maximum, two new live entries/session maximum; live **off**.
- Market observations and forecasts are point-in-time and versioned; the core can abstain. The execution/risk gateway is a separate authority and may always reject the core.
- Every decision has a reason, uncertainty, data snapshot, model version, cost assumptions, and an auditable ledger entry.

## 1. Kernel inputs and ownership
`MarketState` (snapshot ID, symbol, UTC decision timestamp, last complete bar availability, executable bid/ask if known, volatility, liquidity, regime, corporate actions); `ForecastSet` (per-model version, horizon, distribution or scenario probabilities, calibrated flag, calibration window, freshness, confidence intervals); `PortfolioState` (cash, NAV, existing exposure, pending orders, daily loss, remaining session capacity); `CostModel` (commissions, spreads, slippage, FX, borrow where relevant, model/data infrastructure costs separately); `RiskPolicy` (versioned hard constraints); `Evidence` (historical and forward-paper test results). RAG supplies cited research to *research agents*, never unvalidated numeric facts to the kernel.

## 2. Kernel execution, in strict order
1. **Synchronize**: freeze a reproducible market snapshot and exchange clock. Missing, stale, contradictory or unavailable-at-time data => `ABSTAIN`.
2. **Observe**: compute causal features from completed bars; classify regime with an explicitly trained/validated model; no future normalization.
3. **Forecast**: request each eligible gladiator's structured forecast; reject expired, uncalibrated or incompatible horizon outputs. An LLM's prose is not a probability.
4. **Synthesize**: compare forecast distributions and disagreement; combine only after correlation-aware, out-of-sample ensemble validation. No majority-vote confidence inflation.
5. **Search**: enumerate *feasible* opportunities, including `NO_TRADE`, alternative entry prices, exits, time horizons and position sizes. Do not choose an asset first and rationalize a trade afterward.
6. **Evaluate**: compute net return distribution **after executable spread, commissions, slippage, gap risk and FX**. For candidate action `a`, `EV(a) = Σ_s P(s|state,a)*PnL(s,a) - expected_cost(a)` with explicit probability source and confidence interval. For path-dependent TP/SL, estimate joint hitting events and expiry outcomes; simple `p*win-(1-p)*loss` only when truly binary.
7. **Allocate**: maximize conservative expected utility subject to cash, position, risk, concentration, liquidity and opportunity-cost constraints. A negative or uncertain edge => `ABSTAIN`. Fractional Kelly is *optional* research and must not conflate fraction wagered with stop-based account risk.
8. **Act**: produce structured `TradeIntent` (or `ABSTAIN`) and send to independent risk gateway. No broker access from the kernel or LLM. Gatekeeper returns signed approval/rejection with capped size and reasons.
9. **Manage**: for an open position, re-evaluate `HOLD`, `REDUCE`, `EXIT`, `TIGHTEN_STOP`, `ADD` on each eligible event. No widening stops merely to avoid a realized loss; adds require new evidence and aggregate risk approval. Protective stops are imperfect under gaps.
10. **Observe outcomes**: broker/paper fills -> reconciled cash, holdings and fee ledger; record forecast vs realized outcome and prediction error. Distinguish observed trade outcome from counterfactual missed opportunity.
11. **Learn safely**: append immutable evidence; detect drift, update research queue, retrain *challengers* offline; use frozen holdouts and forward paper before champion promotion. No online live-weight mutation from one loss.
12. **Protect stability**: data failures, clock skew, fee uncertainty, unbounded drawdown, model drift, reconciliation mismatch or infrastructure cost breach trigger `ABSTAIN`/kill switch. No recovery by raising risk.

## 3. Core decision mathematics
- Forecast distribution: `P(r_h | X_t, regime_t, model_version)` plus calibrated event probabilities and prediction intervals; evaluate Brier/log loss and calibration by regime.
- Risk: initial planned loss budget ≤0.5–1% of current NAV (at £500: £2.50–£5), not a guaranteed loss cap. `qty = min(floor(risk_budget / stressed_loss_per_share), floor((cash - estimated_fees)/all_in_entry_price), liquidity_cap, concentration_cap)`; if fractional shares unsupported, integer rounding may force `ABSTAIN`.
- Required edge: `lower_confidence_bound(expected_net_pnl) > 0` **and** independently validated strategy evidence; configurable conservative threshold. Beware estimated probabilities and multiple testing.
- Return on capital and opportunity cost: evaluate net expectancy, expected downside, holding time, cash utilization, capacity and uncertainty, not just win rate or R:R.
- Exit optimization: compare expected value of hold vs sell **from current time** after future costs, including time expiry, trailing stops, partial exits and re-entry rules. Optimize entry/exit jointly on training/validation, then freeze for holdout.
- Score candidate policies using hard constraints first, then risk-adjusted net results, max drawdown, tail risk, turnover, stability and calibrated forecasts. Never optimize to reach £10k by a date.

## 4. Systems-thinking feedback controls
- **Stocks:** cash, positions, realised/unrealised P&L, model evidence, confidence and risk capacity.
- **Flows:** fills, costs, capital movements, new observations, promotion/demotion, inference and training spend.
- **Reinforcing loops:** stronger validated signals can receive more *research allocation*; live capital increases only within hard risk caps.
- **Balancing loops:** drawdown throttles, model drift gates, cost ceilings, exposure limits, kill switch and mandatory abstention.
- **Delays:** labels mature after forecast horizon; retraining waits for mature outcomes; promotion waits for independent forward paper. No instant reward from unrealised mark-to-market.
- **Failure modes:** correlated gladiators, survivorship/selection bias, feedback from own fills, data revisions, regime shifts, cost drag, repeated holdout peeking and optimization of proxy metrics.
- **Leverage points:** better data provenance, calibration, evaluation design and reward rules before more complex models.

## 5. Interface contracts (canonical JSON shapes)
Input to kernel: `{decision_id, as_of_utc, snapshot_id, market:{symbol,bid,ask,bar_available_at,volatility}, forecasts:[{model_id,version,horizon,calibrated,expected_return,lower_bound_return,expires_at}], portfolio:{cash,equity,positions}, costs:{entry_fee,exit_fee,slippage_bps}, policy:{risk_fraction,max_positions,max_new_entries}}`.
Output: `{decision_id, action, symbol|null, quantity, entry_limit|null, stop|null, target|null, horizon|null, expected_net_pnl|null, uncertainty|null, reasons:[...], snapshot_id, forecast_ids:[...], policy_version}`. `ABSTAIN` is a successful output. Numeric predictions must be derived from model artifacts; example JSON is a schema sketch, not evidence of accuracy.

## 6. Responsibility boundaries
- **Qlib**: dataset/feature pipelines, numerical training, backtest/experiment infrastructure where fit for purpose. Our adapters own immutable point-in-time ingestion and audit.
- **Gladiators**: interchangeable Qlib LightGBM/XGBoost, statistical baselines, neural, FinRL (later), FinBERT+numeric, Qwen/FinGPT research agents, cloud challengers (opt-in later). Each supplies predictions/policies under the same clock and data contracts.
- **CORE**: state estimation, opportunity search, probability/uncertainty reconciliation, cost-adjusted decisions, sizing proposals, position management, abstention.
- **Arena/Judges**: fair walk-forward comparisons, dependence-aware ranking, challenger promotion, model retirement.
- **Gatekeeper**: immutable risk caps, approval/veto, broker authorization, independent kill switch.
- **Transport**: provider adapters, event bus, simulated/live broker adapter, reconciliation. The kernel must run with zero network access using recorded inputs.

## 7. Terminal-only commands and phase gates
`gladiator data pull|validate|snapshot`, `gladiator qlib prepare`, `gladiator model train|evaluate`, `gladiator core decide --snapshot ... --as-of ...`, `gladiator core explain --decision ...`, `gladiator arena run --challengers 10`, `gladiator paper replay`, `gladiator risk check`, `gladiator ledger reconcile`, `gladiator report costs`. These are **target interfaces, not currently implemented commands**.

**Phase 1 £0 external spend:** local, lawful free data -> validated immutable snapshots -> Qlib with three CPU-friendly baselines -> offline decision kernel -> fee-aware event simulator -> CLI reports -> ten registered challengers -> forward paper. No API keys, paid GPU or live orders. Cloud models enter only by explicit opt-in and cost cap after measurable out-of-sample incremental value.

**Acceptance:** (A) deterministic replay from same snapshot and model artifacts; (B) injection of future bars cannot change earlier decision; (C) fee/spread increase cannot improve identical candidate's EV; (D) stale/missing model/data => abstain; (E) no position exceeds cash or risk budget; (F) gap losses recorded without pretending stop guarantees; (G) challenger promotions cannot see locked holdout; (H) terminal reports reproduce ledger and actual model predictions; (I) kill switch prevents orders; (J) no cost-incurring network activity in phase 1.

## 8. Honest implementation status
Existing `runtime/core.py` is only CSV→SQLite→logistic regression→simplified backtest. It **does not implement this kernel** and cannot safely place orders. Next coding step is `kernel/state.py`, `kernel/forecast.py`, `kernel/opportunities.py`, `kernel/utility.py`, `kernel/position.py`, `kernel/decision.py`, with deterministic fixtures and failing acceptance tests before integration with Qlib. Do not call the architecture "working" until those tests pass.
