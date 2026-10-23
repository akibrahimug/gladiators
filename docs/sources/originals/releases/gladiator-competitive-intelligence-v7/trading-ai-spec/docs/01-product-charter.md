# 01 — Product charter and requirements

## User intent
- Engineer a low-touch autonomous trading research and execution platform rather than manually learn chart patterns.
- Begin with £500 **eventual** live capital and grow only if independently measured performance justifies it; £10,000 is a target, not a deadline.
- Own the trained predictive models and adapted open-weight financial LLM. External LLM APIs are optional tools for development/research, not the production decision authority.
- Ten paper-learning strategies compete; one live position slot for a promoted champion.
- Decisions based on mathematical expectancy, probability calibration, statistical inference, quantitative models and uncertainty.
- System should increase exposure *only* when reliable evidence and portfolio limits justify it, not because the LLM is optimistic.

## Functional requirements
FR-01 Ingest historical and live market data with timestamps, corporate actions and provenance.  
FR-02 Train, version, evaluate and deploy quantitative predictors.  
FR-03 Adapt an open-weight language model for financial research, with retrieval of verified prior experiments.  
FR-04 Run event-driven backtests with fees, spreads, slippage and order constraints.  
FR-05 Run ten logically isolated paper challengers with separate ledgers.  
FR-06 Estimate calibrated outcome distributions and stop-before-target probabilities conditional on proposed exits.  
FR-07 Generate trade proposals including rationale, uncertainty, expiry and exact risk budget.  
FR-08 Apply hard independent risk checks; never execute directly from LLM/MCP.  
FR-09 Support protective stop, target, trailing, partial exit, time exit and carefully constrained pyramiding.  
FR-10 Broker adapter supports paper/live separation, idempotency and reconciliation.  
FR-11 Automatic evaluation, demotion, retraining and human-controlled promotion.  
FR-12 Dashboard for evidence, costs, positions, drift, health and kill switch.  
FR-13 Enforce hard monthly infrastructure and API budget with alerts and shutoffs.

## Nonfunctional requirements
- Reproducible experiments: dataset snapshot/hash, code commit, random seed, configuration, model checkpoint, evaluation window.
- Traceable decisions: immutable event trail from forecast to fill and post-trade attribution.
- Resilience: stale-feed halt, broker disconnection halt, stop-order verification, restart-safe state recovery.
- Security: least privilege, encrypted secrets, segregated environments, no model-accessible live credentials.
- Research first: statistical superiority is **not presumed**.

## Explicit non-goals for v1
- High-frequency or latency-arbitrage trading.
- Guaranteed monthly returns or a fixed date for £10k.
- Unbounded autonomous self-modification of production code or live policy.
- Leverage, CFDs, options or derivatives with £500 starting capital.
- Autonomous deposits or withdrawals.

## Success metrics
Research: out-of-sample net expectancy, forecast calibration, benchmark-relative performance, drawdown, expected shortfall, turnover, sensitivity to costs, robustness across regimes.  
Operations: data completeness, delayed/stale event rate, order reconciliation accuracy, uptime, spend versus budget.  
Live: net-of-all-costs P&L, drawdown, exposure, missed/rejected orders, risk breaches (target **zero**).  
Decision: a system that **does not trade** when evidence is insufficient can be functioning correctly.
