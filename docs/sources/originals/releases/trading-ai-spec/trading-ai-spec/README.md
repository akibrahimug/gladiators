# Autonomous Quantitative Trading Research System

**Status:** Architecture specification v0.1 — research only; no validated trading edge or approved live deployment.  
**Initial account:** £500 (segregated from research operating expenses).  
**Target:** £10,000 aspirational; **no promised timeframe**.  
**Research topology:** 10 paper-trading challengers, at most 1 concurrent live position, only after gates pass.  
**Initial research market:** US equities and ETFs; live instruments must be legally accessible to a UK retail account.

## Design thesis
Build **our own trained trading intelligence**, not a wrapper around paid trade-signal APIs: an open-weight, finance-adapted language model for research and hypothesis generation, **separately trained quantitative predictors** for calibrated outcome probabilities, a deterministic allocation and exit engine, and an independent risk/execution service. The LLM **proposes**, the numerical models **estimate**, the evaluator **validates**, the allocator **sizes**, the risk service **authorises**, and the broker **executes**.

An LLM's expressed confidence is never treated as an empirical probability. More agents, more memory, more trades, and fine-tuning do not imply profitability.

## Documentation map
1. [Product charter and requirements](docs/01-product-charter.md)
2. [Architecture and service boundaries](docs/02-architecture.md)
3. [Data, market access and broker adapters](docs/03-market-data-brokers.md)
4. [Model selection, training and RAG](docs/04-model-training.md)
5. [Quantitative mathematical core](docs/05-quant-core.md)
6. [Strategy lifecycle and champion–challenger incentives](docs/06-strategy-evaluation.md)
7. [Position sizing, stops and profit taking](docs/07-risk-exits-allocation.md)
8. [Trading schedule and ten-agent experiment](docs/08-trading-operations.md)
9. [Infrastructure, APIs and cost model](docs/09-infrastructure-costs.md)
10. [Security, compliance and failure handling](docs/10-security-compliance.md)
11. [Delivery roadmap and acceptance criteria](docs/11-roadmap.md)
12. [Data contracts, APIs and configuration](docs/12-contracts-config.md)
13. [Open decisions and assumptions](docs/13-open-decisions.md)

## Non-negotiable rules
- No live trading before statistically meaningful out-of-sample **and** forward paper-trading evidence, user approval, and verified broker eligibility.
- No autonomous increase in funding, leverage, or risk limits; no LLM permission to alter controls.
- Default to **no trade** when edge is weak, uncertain, or costs exceed expected benefit.
- Backtests use point-in-time information, adjusted corporate actions, realistic fills and costs; reserve untouched holdouts.
- Paper fills are not live fills. Stops are not guaranteed maximum losses.
- Ten paper agents are ten research policies, not necessarily ten costly LLM replicas.
- Keep full provenance: model version, dataset, strategy, forecasts, decisions, orders, fills, and evaluation.

## Suggested repository layout
```text
apps/dashboard/               # Next.js operations dashboard
services/research-agent/      # open-weight LLM orchestration
services/market-data/         # ingestion, quality, point-in-time datasets
services/quant/               # training, inference, calibration
services/backtester/          # event-driven historical simulation
services/strategy-lab/        # 10 challengers and evaluations
services/allocator/           # deterministic sizing and exit proposals
services/risk-gateway/        # isolated authorisation and broker execution
services/reconciler/          # broker positions, orders and fill reconciliation
packages/contracts/          # typed event schemas and API contracts
infra/                        # deployment, observability, secrets
configs/                      # versioned, signed live risk policy
experiments/                  # immutable research manifests and results
```

## Intended first milestone
Paper-only end-to-end vertical slice: ingest data → train a simple quant baseline → produce calibrated forecasts → simulate a strategy → validate on unseen periods → propose a trade → reject/approve via risk service → paper execution → reconcile → journal. Do **not** start with live trading or GPU fine-tuning.
