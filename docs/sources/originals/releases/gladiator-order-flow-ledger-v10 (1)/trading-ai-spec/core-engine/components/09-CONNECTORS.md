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

## Market intelligence connectors (v0.9 amendment)
Add typed connectors for `ScheduledEvent`, `OfficialRelease`, `MarketMicrostructure`, `CrossAssetProxy`, `VenueStatus`, `CryptoDerivatives`, `OnChain`, and `NewsMetadata`. Each publishes `ObservationEnvelope` with occurrence, first actual availability, publisher timestamp, ingestion timestamp, instrument/venue, licensing, coverage scope, revision and heartbeat. Persist `NO_EVENT` versus `SOURCE_UNAVAILABLE` distinctly. Do not turn IEX-only equities into claimed SIP observations or venue-local crypto books into global order books. Source candidates and known blind spots: [24](24-MARKET-AWARENESS-AND-REGIME-DETECTION.md), [25](25-MARKET-INTELLIGENCE-SOURCE-REGISTER.csv).
