# 24 — Market awareness, event intelligence and regime-change detection

**Status:** v0.9 design / research specification (22 October 2026). Not implemented. No claim of zero market losses or complete information access.

**Microstructure extension:** See [27 — Order flow and ledger intelligence](27-ORDER-FLOW-AND-LEDGER-INTELLIGENCE.md). Prefer exchange-native trades, quotes and order lifecycle where reliable, but never treat revocable orders or blockchain transfers as confirmed inflows.

## Mission and epistemic boundary

GLADIATOR must detect when observed market conditions differ from those that justified a forecast, whether or not a news story explains the shift. This is a **continuous market-observation and safety function**, not an LLM tasked with knowing every market mover. Unpublished information, private flows, hidden liquidity, unexpected events, missing feeds, latency, structural model error and gaps make total observability and zero losses impossible.

The engineering target is **near-zero preventable errors**: never knowingly trade on stale/invalid data, unapproved risk, unverified model outputs or untested regime assumptions. Market risk remains.

**Architecture amendment:** introduce `Market Intelligence` as an independent, versioned subsystem between verified data/connectors and the Core/Gatekeeper. It is not an eleventh Gladiator. It may output `UNKNOWN`; this is a first-class state.

```text
     PLANNED EVENTS                  UNPLANNED EVENTS                   DIRECT MARKET OBSERVATION
     Fed/BLS/Treasury                filings/breaking news             trades/quotes/depth/bars
     issuer calendars               crypto listing/incidents         liquidity/vol/flows
     exchange closures              chain alerts/venue outages       cross-asset prices
           |                               |                                  |
     Calendar collector              Event collector                    Market sensors
           |                               |                                  |
           +---------- Source/rights/time verification, immutable event log ---------+
                                               |
                                Point-in-time observation fusion
                                  /                         \
                         Observable regime         Event candidates + uncertainty
                                 \                         /
                                   Market State + coverage report
                                               |
                          +--------------------+--------------------+
                          |                    |                    |
                      Core Kernel          Gatekeeper          Management/Judges
                     opportunity         independent           drift/incident
                     reassessment         fail-closed          and replay tests
                                               |
                                   Ledger/forward evidence
```

**Three independent questions:**
1. **Anticipation:** what publicly scheduled event might create volatility (event clock, exposure, expected impact as a hypothesis)?
2. **Detection:** did market microstructure, volatility, distribution, correlation or venue health actually change?
3. **Explanation:** what verifiable causal hypotheses could explain it, and what is still unknown? LLMs assist only with (3). Never require (3) before a safety response to (2).

## Required observability map — US ETFs and crypto spot

The following are monitoring *classes*, not promises that a legal, complete free feed exists. Cost/coverage and permitted use require explicit verification in `25-MARKET-INTELLIGENCE-SOURCE-REGISTER.csv`.

| Information domain | What it changes | ETF relevance | Crypto relevance | Phase-1 posture |
|---|---|---|---|---|
| Venue trades, quotes, spreads, trading halts, depth | executable liquidity, slippage, volatility | Critical | Critical | Primary sensor. Alpaca Basic **IEX-only** for real-time US equities; crypto public venue feeds; measure coverage limits |
| Price/volume returns, realized volatility, gaps, momentum | observed regime change | Critical | Critical | Deterministic sensor; independent of headlines |
| Related-asset and cross-venue moves | ETF exposures, dollar/rates/sector beta, crypto contagion | High | High | Observe grounded available proxy feeds; record absent ones |
| Macro policy: Fed, CPI, jobs, GDP, PCE | repricing of rates/risk | Critical | High | Free official calendars/releases; distinguish scheduled time from release data |
| Rates, yields, dollar, commodities, VIX/volatility | changing exposures and risk appetite | High | High | Historical macro via FRED/ALFRED; real-time entitlement often **unresolved** |
| ETF holdings, split/dividend, issuer announcements, NAV and flows | instrument economics, sector exposure, valuation | High | Indirect | Issuer and SEC documents; frequency and history vary; NAV and holdings may be delayed |
| Company reports and large constituent filings | broad and sector ETF shocks | High | Indirect | SEC EDGAR filings; match ETF holdings and release time |
| Market calendars, exchange status, circuit breakers | execution eligibility | Critical | Critical venue status | Official calendars/status; no presumed ability to trade during a halt |
| Earnings calendars and index rebalances | sector/ETF exposure, liquidity | High | Moderate | Sources and full rights/coverage unresolved; mark gaps |
| Breaking financial/geopolitical/regulatory news | event risk and cross-asset shock | High | High | Official releases + permitted aggregated metadata (GDELT delayed ~15 minutes); never promise breaking coverage |
| Derivatives: options implied vol, term structure, skew | forward uncertainty pricing | High | High | Generally partial/paid for US options; optional Deribit public crypto summary where available |
| Futures funding, open interest, liquidations, basis | leveraged crypto stress affecting spot | Indirect | High | Venue public derivatives feeds if lawful; no assumption of complete global liquidations |
| Spot order-book imbalance and exchange solvency/status | local microstructure and venue-specific risk | Indirect | Critical | Exchange-specific; never merge venues naively |
| On-chain flows, stablecoin supply/peg, network congestion | liquidity, protocol, bridge and custody risks | Minimal | High | Public chain data and permitted community metrics; attribution/latency limitations |
| Security incidents, hacks, delistings, exchange maintenance | discontinuous trading/settlement risk | Moderate | Critical | Official exchange status and incident notices, plus corroboration |
| Social-media sentiment and rumours | sometimes early, often misleading | Medium | Medium | Research only; no unverified social post may autonomously cause a live trade |
| Positioning/flows reports (CFTC COT) | slower structural context | Medium | Medium via futures | **Weekly and delayed**, not an intraday alarm |

**Out of scope for complete real-time monitoring in free Phase 1:** consolidated SIP US equities, full OPRA options, reliable tick-by-tick consolidated global order books, comprehensive ETF creation/redemption flows, proprietary institutional positions, private dealer flows, universal crypto liquidation data and all publisher news. Record these gaps explicitly; do not replace with fabricated proxies.

## Source hierarchy and connection rules

- **Tier A — official first party:** exchange market streams and outage/status notices, central-bank and statistical release calendars, SEC EDGAR, issuer corporate actions, verified blockchain data. Preserve payload and original URL/identifier.
- **Tier B — documented aggregators:** approved broker market-data feeds, FRED/ALFRED vintages, Coin Metrics Community (licence restrictions), GDELT event metadata (15-minute update granularity). Apply coverage and rights checks.
- **Tier C — reporting, commentary, social:** corroboration, research hypotheses and narrative context. Never authoritative for executable prices or factual causal inference without independent evidence.
- Prefer two independent sources for **cause claims** when possible. A direct exchange market-shock sensor can trigger a risk response with only one trusted executable market feed. Never wait for a second news article while losses accumulate.
- No scraping through authentication, paywalls, anti-bot controls or terms-of-service restrictions; no assumption that public means redistributable/commercially usable.

### Verified examples (source docs checked 2026-10-22)

- Federal Reserve FOMC calendars: https://www.federalreserve.gov/monetarypolicy/fomccalendars.htm
- BLS CPI schedule/calendar: https://www.bls.gov/schedule/news_release/cpi.htm ; official release clock includes 08:30 US Eastern for CPI dates.
- SEC `data.sec.gov`: https://www.sec.gov/search-filings/edgar-application-programming-interfaces ; public submissions/XBRL and filings, fair access and identifiable User-Agent; not prices.
- FRED/ALFRED real-time/vintage support: https://fred.stlouisfed.org/docs/api/fred/ ; prefer *what was known as of* the simulated decision time, not latest revised macro values.
- Alpaca Basic stock data: https://docs.alpaca.markets/us/docs/about-market-data-api ; IEX real-time, not all-US-exchange SIP coverage.
- Coinbase WebSocket: https://help.coinbase.com/en/developer-platform/websocket-feeds/advanced-trade ; trade/order-book updates on selected products, connection and sequence recovery tests required.
- Binance derivatives public market data: https://developers.binance.info/en/docs/catalog/core-trading-derivatives-trading-usd-s-m-futures/api/rest-api/market-data ; funding/open interest **market-specific** and potentially delayed or incomplete.
- Coin Metrics Community: https://gitbook-docs.coinmetrics.io/packages/coin-metrics-community-data ; free subset and limits with usage/rights review.
- GDELT events: https://gdeltproject.org/data.html ; GDELT 2.0 event/GKG updates approximately every 15 minutes. Not a source of instant news or ground-truth trade direction.
- CFTC COT: https://www.cftc.gov/MarketReports/CommitmentsofTraders/ReleaseSchedule/index.htm ; normally published Friday for positions as of Tuesday, with holiday exceptions.

## Market intelligence data contracts (normative)

### `ObservationEnvelope`

```json
{
  "observation_id": "sha256-or-provider-key",
  "domain": "exchange_quote|bar|macro_release|news|filing|onchain|venue_status|event_calendar",
  "market": "US_ETF|CRYPTO_SPOT|CROSS_ASSET",
  "venue": "IEX|COINBASE|KRAKEN|BINANCE|OFFICIAL|NA",
  "symbol": "SPY|BTC-USD|US_CPI|NA",
  "source_id": "registered-provider-id",
  "source_event_time_utc": "2026-10-22T13:00:00Z",
  "published_at_utc": "2026-10-22T13:00:01Z",
  "first_available_at_utc": "2026-10-22T13:00:02Z",
  "ingested_at_utc": "2026-10-22T13:00:03Z",
  "original_event_timezone": "America/New_York",
  "payload_hash": "sha256-hex",
  "source_revision": "r0",
  "rights_profile_id": "provider-license-v1",
  "verification_status": "VERIFIED|UNVERIFIED|QUARANTINED",
  "quality_flags": [],
  "coverage_scope": "IEX_ONLY|VENUE_SPECIFIC|CONSOLIDATED|DOCUMENT|UNKNOWN"
}
```

The above timestamps and values are **schema examples, not real collected observations**. For scheduled events, `scheduled_at_utc` is separate from `published_at_utc` and observed data; an upcoming appointment cannot imply a future released figure. `first_available_at_utc` must conservatively reflect source availability *and* any recorded collection delay; `decision_time >= first_available_at_utc` is mandatory for replay. Distinguish reference period, event occurrence, publication, revision, ingestion, decision and label maturity.

### `MarketIntelligenceSnapshot`

```json
{
  "snapshot_id": "hash-of-all-input-ids-and-config",
  "as_of_utc": "2026-10-22T13:00:05Z",
  "market": "CRYPTO_SPOT",
  "instruments": ["BTC-USD"],
  "state": "WATCH",
  "detectors": [{"name": "realized_vol_shift", "version": "v1", "value": 2.1,
                 "baseline": "train-period-fitted", "result": "FLAG", "calibration_id": "detector-c1"}],
  "events": ["event-id-or-empty"],
  "explanations": [{"hypothesis": "unknown", "evidence_ids": [], "confidence": null}],
  "coverage": [{"domain": "macro_release", "status": "AVAILABLE", "freshness_ms": 2000},
               {"domain": "order_book", "status": "MISSING", "freshness_ms": null}],
  "data_health": "DEGRADED",
  "missing_critical_inputs": ["order_book"],
  "policy_version": "market-awareness-policy-v1",
  "source_receipts": ["observation-id-1"]
}
```

Example detector value `2.1` and freshness `2000` are **illustrative only**, not research-calibrated thresholds. Every detector needs a specific threshold, fitting window, false-alarm estimate and revalidation schedule before promotion. `confidence=null` is preferable to fake certainty.

## Detection engine: independent sensors, not an LLM verdict

1. **Venue/quote health:** gaps, crossed/locked markets, stale or duplicate sequence, book reconstruction errors, spreads, executable volume, trading suspensions, abnormal latency. Book data is venue-specific; partial depth is not global liquidity.
2. **Price/volatility shocks:** completed-bar realised vol and intrabar quote/trade excursions; jumps, downside tails, range expansion, gap size relative to historically comparable sessions. Calibrate separately for ETFs (regular/pre/post hours) and 24/7 crypto.
3. **Change-point / concept drift:** research CUSUM, Page–Hinkley, ADWIN, Bayesian online change-point, robust distribution-shift tests; compare alarm precision/latency and false positives under nonstationarity. Never hard-code an arbitrary detector threshold as a truth.
4. **Cross-market / cross-venue stress:** correlations and vol co-movement of SPY/QQQ/TLT/GLD and approved rates/USD proxies versus BTC/ETH and spot-perpetual basis. Dynamic, lag-aware; missing data is recorded, not imputed as normality.
5. **External event monitor:** map known scheduled events and official releases, venue incidents, filings and corroborated news to exposed instruments. Timestamp exact availability and distinguish magnitude from merely negative/positive sentiment.
6. **Forecast reliability:** model residuals and calibration on **matured labels only**, changes in feature distribution, increased model disagreement; a drift alarm is not itself evidence that a trading counterstrategy is profitable.
7. **Availability sensor:** heartbeat, latency, source licensing, rights, quotas, provider outages and clock drift. Distinguish `NO_EVENT` from `SOURCE_UNAVAILABLE`. Unknown coverage is an actual system hazard.

No retroactive explanation can be used as a contemporaneous feature. All detectors themselves are evaluated on event-time replays and held-out periods. Correlated alarms are not independent confirmations.

## Market state machine and policy separation

| State | Meaning | Core response | Gatekeeper independent minimum |
|---|---|---|---|
| `NORMAL` | feeds sufficient; no validated major alarm | normal research evaluation | enforce all existing hard limits |
| `WATCH` | planned high-impact event approaching or mild validated shift | recalculate scenario stress; permit abstention | versioned pre-event tightening if approved; no rule auto-loosening |
| `SHOCK` | abrupt volatility/liquidity/correlation change confirmed by market sensor | recompute every open position; suspend affected new opportunities | block affected new entries until independent policy permits; allow authorised risk-reducing orders |
| `DISLOCATED` | unreliable spreads, halts, extreme venue inconsistency | do not infer executable prices from last trade | reject new orders; exits require fresh executable evidence and approved emergency handling |
| `DATA_BLIND` | required critical feed missing, stale, conflicting or unverifiable | `ABSTAIN` for dependent decisions, log incident | veto new entries; preserve broker-native protective orders where appropriate; require reconciliation for exits |
| `HALTED` | operator/independent risk kill switch or unresolved severe incident | only audit/recovery workflows | no new risk; controlled reduction per policy |

State priorities, transitions, debounce/hysteresis and cool-down periods must be versioned. `DATA_BLIND` cannot silently become `NORMAL` because the news feed has no headlines. A market shock detector must work with the LLM offline. No forced liquidation based solely on a stale quote; brokers/venues may be unable to fill orders during halts or gaps. Risk actions, including closing an existing position, can realise losses.

## Coverage and confidence budget

A **coverage report** is mandatory for every decision and every backtest: domain × instrument × session × observation window, with `AVAILABLE|DELAYED|MISSING|STALE|UNLICENSED|OUT_OF_SCOPE`. Management tracks per-domain uptime, effective latency (event -> availability -> ingestion -> decision), source independence, missed events, time-to-detection and false-alert rate. A weighted observability score can help prioritise engineering work but **must never imply a calibrated probability that all relevant events are known**.

For every unobserved domain, policy declares `required_for_entry`, `required_for_exit`, `research_optional` or `not_applicable`. Missing critical market price/liquidity and venue health blocks new orders. Missing optional slow-onchain data need not prohibit an ETF paper trade. Do not demand every theoretical input for every trade: classify impact and use enforceable limits.

## Backtest, Arena, Judges and peer-review contract

- Retain original event stream including missing spans and feed disconnects; replay in **historical publication/availability order**, not event occurrence order alone.
- Macro economic figures must use point-in-time vintages; filings must use acceptance/publication time; ETF holdings data must match the holdings version available then.
- Benchmark a **price-only** detector, an **external-events-only** detector and a **fused** detector on the same periods; require demonstrated incremental value after false alarms, spread/slippage and opportunity cost. News coverage itself is not alpha.
- Test with positive, negative and **unexplained** market shocks, including sources missing at the worst possible moment, false news, stale timestamps, delayed macro revisions and crypto exchange divergence.
- Track detector latency distributions, missed-impact events, false positives per market/day, inappropriate intervention, avoided and introduced losses. Avoid judging detectors only by how many events they flagged.
- Freeze thresholds and weights before locked backtests. Prevent hindsight label leakage: an event's eventual market move is not an input to the event detector at the earlier time.
- Review at least two adversarial alternative explanations for any newly proposed causal factor; require independently invoked models for claims of external AI peer review.

## Phased admission

**Research P0 (no network):** construct source/rights matrix, synthetic event-time adversarial fixtures (explicitly labelled synthetic), define typed contracts, alarm metrics and market state machine. **Phase 1 (free sources):** historical FOMC/BLS/SEC/GDELT/ALFRED + verified crypto venue data and ETF IEX coverage where user access/terms permit. **Phase 2:** forward paper event collection, replay, calibration and blackout drills. **Phase 3:** pay for better real-time breadth or news/options only when quantified blind spots justify cost and the user approves. Real-time 24/7 crypto coverage requires an actually running and monitored collector; a powered-off local machine cannot deliver continuous protection.

## Acceptance cases (specification targets, not implemented tests)

- A known CPI release on calendar but no figure yet: `WATCH`, **not** a fabricated surprise or prediction.
- A surprise crypto liquidity crash with all news feeds silent: price/liquidity sensor triggers `SHOCK` or `DISLOCATED`; unknown cause retained.
- A delayed news story published after a 15-minute crypto decline: cannot become the cause or feature available before its publication.
- Macro series revised six months later: replay of original trade still sees only the original vintage.
- IEX quote with no SIP entitlement: mark `IEX_ONLY`; never claim whole-market best bid/offer.
- Overnight ETF news while primary equity market closed: warn of opening-gap risk; stop price does not guarantee fill.
- Coinbase disconnected during a BTC shock: move affected instrument to `DATA_BLIND`; no new entries.
- False social media claim: evidence uncertain; cannot directly authorise an order.
- Completely unknown event followed by rapid volatility change: price-only path must function with research LLM unplugged.
- 100 correlated headlines about one event: deduplicate by event cluster and primary source; do not multiply confidence 100-fold.
- Exchange halt, no executable bids: no fictitious stop-price fills; ledger records pending state.
- Cross-venue BTCUSD and BTCUSDT dislocation: currency/venue conversion and clock agreement required before calling it arbitrage or signal.
- Backtest that omits an unavailable feed period fails a coverage audit rather than selecting only easy periods.
- Restart with missing event-stream segments must not claim continuous market observation; reconciliation and catch-up required.

## Open questions / design blockers

1. Which executable US ETF and crypto brokers/exchanges are accessible to this UK account, what assets are permitted, and what hours/quotes do their APIs actually cover?
2. What free, contractually permitted news and ETF intraday feeds have **sufficient history** to support rigorous as-of backtesting? GDELT coverage alone is not evidence of low-latency news detection.
3. Are paid consolidated US equities, options-implied volatility and real-time rates worth their subscription cost on £500 risk capital?
4. What data and independent sources can verify a crypto exchange failure if its own API is silent?
5. What false-alarm and time-to-detection budgets are acceptable per event class/horizon? Must be established empirically, not invented.
6. Which risks are best avoided by scheduled-event blackout policy versus continuous price sensor? Requires unseen tests.

**Release criterion:** no market-aware live trading based on a generic promise of 'all data'. Demonstrate bounded latency and measured blind spots for supported instruments, plus safe response to genuinely unknown shocks.

## Broader event-domain watchlist (coverage inventory; not a promise of access)

- **Policy and law:** central-bank surprises; fiscal announcements; government debt ceilings; tariffs; sanctions; export controls; financial-market and crypto regulations; court decisions.
- **Political/geopolitical:** elections, wars, conflict escalation, diplomatic disputes, international trade restrictions, sudden government changes.
- **Physical economy:** major energy or commodity disruptions, supply-chain failures, shipping bottlenecks, weather disasters and infrastructure outages.
- **Market plumbing:** clearing/settlement issues, broker disruptions, exchange halts, index changes, ETF creations/redemptions, options/futures expiration, funding stress.
- **Crypto-native:** stablecoin depegs and redemptions, token unlocks, protocol upgrades, custody failures, major bridge exploits, validator consensus problems, chain congestion, exchange insolvency rumours and confirmed incidents.
- **Position-dependent:** actual ETF holdings and concentration, sector/issuer weight, rates duration, FX exposure, geographic exposure, correlated crypto instruments. Never presume that a broad ETF or a large crypto asset is diversified against the shock.

The exposure map must be dynamic and versioned; an event matters only to the extent it can affect the **actual portfolio/instruments and time horizon**. Unknown causal factors are surfaced via market observations, not retroactively invented explanations. Legally restricted material and material non-public information are not admissible data sources.
