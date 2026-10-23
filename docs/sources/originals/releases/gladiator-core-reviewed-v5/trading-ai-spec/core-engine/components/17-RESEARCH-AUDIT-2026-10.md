# GLADIATOR research audit — 21 October 2026

Status: evidence-based updates to the v0.3 specifications. No claim that new integrations are implemented. External facts must be rechecked before live trading.

## Executive decisions
1. **Retain Qlib** as the quantitative experimentation foundation; it is not itself a trained alpha-producing model. The independent Core Kernel remains the trade decision authority.
2. **Add RD-Agent as an optional research gladiator** for automatic factor discovery/model optimisation, behind sandboxing and the same independent holdout tests. Qlib links to it in the current README.
3. **Evaluate FinRL-X (FinRL-Trading)**, released 25 March 2026, as a later modular RL/portfolio policy adapter. Do not substitute its broker/risk implementation for our own Gatekeeper without independent audit.
4. **Keep FinGPT and FinBERT as specialised NLP challengers**, not proven profitable traders. Published FinGPT evaluations show useful sentiment/classification and limitations in numerical reasoning.
5. **Require independent metric reference implementations.** Qlib's issue tracker currently contains reports about first-period drawdown and trading-volume unit calculations. Treat as reports until reproduced against the pinned version.
6. **First phase is £0 paid-service**, local CPU baselines, daily bars, no cloud models, no broker. Allow future opt-in cloud gladiators only after a per-run cost ceiling is approved.
7. **Data provider remains provisional.** Qlib's official dataset is temporarily unavailable. Yahoo via yfinance describes personal-use restrictions; Stooq access and automation may be unreliable. No provider is approved for production until rights and quality are established.
8. **Do not assume full-market execution-quality data from free feeds.** Alpaca Basic covers IEX US equity realtime; all-exchange plan is $99/mo at time of review. IBKR market-data permissions/subscriptions are account-dependent.

## Evidence register
| ID | Evidence | Source | Decision impact | Confidence |
|---|---|---|---|---|
| E01 | Qlib README introduces RD-Agent and notes disabled official dataset | https://github.com/microsoft/qlib/blob/main/README.md | Optional research agent; custom data importer | High, primary source |
| E02 | Qlib install documentation warns unreleased main differs from releases; model artifact loading trust changes | https://github.com/microsoft/qlib/blob/main/docs/start/installation.rst | Pin versions, safe serialization, smoke tests | High, source caveat |
| E03 | FinRL repo points to FinRL-X; FinRL-Trading v1.0.0 released March 2026 | https://github.com/AI4Finance-Foundation/FinRL ; https://github.com/AI4Finance-Foundation/FinRL-Trading/releases | RL adapter evaluation | High, primary source |
| E04 | Qlib issue reports drawdown/volume calculation concerns | https://github.com/microsoft/qlib/issues | Independent judge reference fixtures | Medium, unverified reports |
| E05 | yfinance project says Yahoo data intended for personal use | https://github.com/ranaroussi/yfinance | Research-only provisional provider | High, primary source |
| E06 | Alpaca Basic IEX-only and Algo Trader Plus $99/month | https://docs.alpaca.markets/us/docs/about-market-data-api | No full-market assumption, paid feed deferred | High, primary source |
| E07 | Alpaca documentation describes non-US/UK signup route | https://alpaca.markets/learn/live-trading-account-non-us | Eligibility possible, not guaranteed | Medium, eligibility subject to approval |
| E08 | IBKR UK stock commissions and data fees | https://www.interactivebrokers.co.uk/en/pricing/commissions-stocks.php ; https://www.interactivebrokers.co.uk/en/pricing/market-data-pricing.php | Cost ledger; no blanket zero-fee claim | High, primary source |
| E09 | FinGPT task benchmark reports limitations for numerical reasoning | https://arxiv.org/abs/2507.08015 | NLP only until trading edge proven | Medium, single study |
| E10 | Third-party October 2026 Stooq automated access issues | https://stockmarketstack.com/tools/stooq | Do not depend on unattended scraper | Low-to-medium, secondary source |

## Unresolved questions / no guessing
- Which **lawfully usable** no-cost historical data provider meets daily coverage, corporate-action completeness, reproducibility and intended-use rights? Must validate with real downloaded samples and terms.
- Which pinned Qlib version works end-to-end on the user's Intel macOS environment? Must run install smoke tests; online docs are inconsistent about Python support.
- How much incremental predictive or trading benefit do RD-Agent, FinGPT, FinRL-X and local/cloud LLMs deliver **after costs**? Unknown until controlled tournaments.
- Is 15-minute/1-hour data sufficiently deep and licensed for the desired US-equity universe at zero cost? Not established. Start daily bars, change horizon only with evidence.
- Exact current UK broker eligibility, instrument availability, fees, FX, tax and funding: revalidate before live enablement.
- Does a statistically durable edge exist? No evidence yet. £500 to £10,000 has no defensible deadline.

## Implementation order
P0: Source manifest, immutable raw data, validation, calendar, split/dividend audit and dataset snapshot hashes.
P1: Qlib-compatible importer, CPU baselines, chronological walk-forward forecasts and model registry.
P2: Core Kernel + independent cost-aware simulator + Judge fixtures + Gatekeeper; no-trade baseline.
P3: Ten paper challengers, deterministic Arena, honest statistical comparisons and maintenance.
P4: Optional RD-Agent factor proposals and FinRL-X adapter, both sandboxed and independently validated.
P5: Optional local LLM/RAG, later capped cloud challenger; live remains OFF until separately approved.

## What this audit does NOT claim
It does not claim the revised specifications are executable, that a data provider has been fully verified, that Qlib's reported bugs are present in the installed version, or that any model makes money.
