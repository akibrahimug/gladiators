# 08 — Trading schedule and ten learning agents

## Market hours
US regular equities session: 09:30–16:00 America/New_York, Monday–Friday excluding exchange holidays. UK conversion is **usually** 14:30–21:00 but differs during the US/UK daylight-saving mismatch. Use IANA exchange calendar, not hardcoded UK hours. No extended-hours trading in v1.

## Frequency and horizon
- Ingest live bars/quotes on data-provider schedule; evaluate signals at completed 15-minute bars and hourly bars initially.
- Model strategy horizons: intraday hours or multi-session only where overnight risk is explicitly supported.
- No fixed minimum number of trades; at most two new live entries/day and one concurrent position.
- Research/backtesting can run outside trading hours; live trading only when session and policy permit.
- Quant challenger training: candidate weekly if sufficient data; LLM adapter training less frequently after evaluation.

## Ten logical challengers
Use a diverse, pre-registered research portfolio: trend/momentum, mean reversion, volatility breakout, regime-conditioned trend, cross-sectional ranking, volume/liquidity anomaly, post-event response, volatility contraction/expansion, cross-asset relationship and baseline/no-trade comparator. **These are hypotheses, not validated edges**. Keep paper ledger, forecast records, cost model and evaluation per challenger.

## One live slot
Champion may open **zero** trades if no signal passes. Live position can be held overnight only if strategy and broker support are explicitly approved. Do not interpret one slot as one trade per day. Additional positions are rejected while slot occupied.

## Daily lifecycle
- Pre-market: check feeds, corporate actions, calendar, model version, broker balances and protective-order support.
- Session: bar-close inference → opportunity assessment → allocation → hard risk gate → paper/live route → reconciliation.
- Close: verify positions/orders, log fills and costs, evaluate paper agents and drift, alert on anomalies.
- After hours: research, candidate training, backtests, RAG indexing and cost reporting. No unattended live model promotion.

## Weekly/monthly lifecycle
Weekly: data-quality audit, challenger retraining if warranted, cost sensitivity, candidate scorecards.  
Monthly: champion review, forward-paper evidence, model calibration, infrastructure spend, benchmark and drawdown assessment.  
Event-driven: immediate suspension on hard safety triggers.

## Statistical caution
10 agents × 2 trades × 20 sessions = 400 simulated trade records, **not** 400 independent samples. Shared market events, common features and strategy correlations reduce effective sample size. Do not set promotion solely by a raw trade-count threshold.
