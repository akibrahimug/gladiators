# Connectors: external and internal adapters

Status: design specification; not a claim of implemented functionality.

## Boundaries
Connectors integrate data providers, local storage, Qlib, optional RAG/LLM, and paper/live brokers. They are thin adapters; never embed decision rules. Every connector declares auth, cost, rate limits, time coverage, data rights, latency and error policy.

## Interfaces
`MarketDataConnector.fetch(symbol,start,end,interval)` returns raw immutable provider records + receipt metadata. `DocumentConnector.fetch(as_of)` preserves publication and retrieval times. `QlibAdapter.prepare(dataset_version)` returns reproducible features. `ModelAdapter.predict(snapshot)` returns structured forecast. `BrokerAdapter.submit(approved_intent)` rejects unsigned/unapproved intents. `RAGConnector.retrieve(query,as_of)` returns document IDs/citations, not numeric model features.

## Initial free provider candidates (must verify terms before use)
- Stooq daily OHLCV: public historical daily research candidate; **not** a source of 15-minute/1-hour bars or execution quotes. Corporate-action and licensing caveats.
- Yahoo Finance via yfinance: convenient prototype source, unofficial interface, intraday retention limits and usage/licence restrictions; never assume permission for commercial/live trading.
- Alpha Vantage / Twelve Data / other free tiers: quotas, history and permitted usage vary; verify current terms before selecting.
- SEC EDGAR: US company filings, not live prices; identify original filing publication/acceptance time and fair-access requirements.
- Broker-provided free historical/paper feeds: eligibility and coverage vary; do not assume a UK user can open or fund a specific account.

## No hidden spend
Phase 1 network connector allowlist must exclude paid endpoints; require `--allow-network` for pulls; `--offline` tests never open sockets. Record provider response codes, timestamps and licensing manifest. Live broker connector not instantiated until separately approved.

## Operational invariants
- Phase 1: zero paid external services, no live orders, no dashboard; terminal text/number output only. Use local files and explicit, free, permitted data sources. Network pulls require explicit invocation.
- Every artifact includes `run_id`, UTC `as_of`, immutable `dataset_hash`, `code_version`, `config_hash`, and relevant `model_version`.
- Reject missing, stale, future-dated, unlicensed or unverified inputs; `ABSTAIN` is valid and preferable to guessing.
- Do not infer profitability from backtests. Keep chronological holdouts, realistic costs, and independent forward-paper validation.
- No LLM, gladiator, or management agent may modify gatekeeper limits or access live broker credentials.

---

## v0.4 verified connector shortlist and limitations
| Connector | Phase | Key restriction | Source |
|---|---|---|---|
| Qlib | 1 | Its official bundled dataset download is currently marked temporarily disabled; bring verified custom data | https://github.com/microsoft/qlib/blob/main/README.md |
| yfinance | 1, research only | Unofficial, Yahoo data intended for personal use; confirm rights and intraday retention | https://github.com/ranaroussi/yfinance |
| Stooq | optional manual research | Automated downloading reportedly blocked/captcha-protected in 2026; confirm source terms and adjusted-price semantics before use | https://stockmarketstack.com/tools/stooq |
| Alpaca | later paper/live | Free Basic IEX-only realtime US equity feed, 200 historical calls/min, $99/mo all-exchange paid tier at review date | https://docs.alpaca.markets/us/docs/about-market-data-api |
| IBKR | later | TWS/IB Gateway and Web API; market-data permissions/subscriptions may be required | https://www.interactivebrokers.com/docs/ |
| RD-Agent | later research | Factor-generation agent; requires sandbox and resource budget | https://github.com/microsoft/RD-Agent |
| FinRL-X | later policy | Modular research/backtest/paper/live components; wrap, don't duplicate our gatekeeper | https://github.com/AI4Finance-Foundation/FinRL-Trading |

No source is approved for commercial/live use merely because its client library is open-source. Verify jurisdiction, redistribution, automated use and data retention before each promotion.
