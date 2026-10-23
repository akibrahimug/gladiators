# 27 — Order flow, market microstructure and ledger intelligence

**Status:** architecture revision v1.0 (2026-10-22); research-backed, NOT implemented, NOT proof of predictive advantage. **Applies to:** US ETFs and crypto spot; crypto derivatives as contextual stress sensors only.

## Fundamental correction

A chart is a visual aggregation of market observations, not the source of the market. Prefer timestamped native **orders/quotes, executions, depth changes, venue status, settlement and on-chain events** over rendered indicators whenever their provenance and latency warrant it. However, neither public order books nor blockchain ledgers expose all the capital committed to markets. In US ETFs, orders are fragmented across venues, hidden liquidity is not fully visible, and a single venue's full-depth feed is *not* an all-market ledger. A displayed order is a revocable intention; a trade is completed execution; a blockchain transfer is an asset movement, not proof of an exchange buy/sell. A chart built from direct trades can be essentially contemporaneous, so do not claim an inherent multi-stage chart lag independent of the chosen aggregation.

## Four distinct observational layers

| Layer | Represents | Can precede a price change? | Key limitation |
|---|---|---|---|
| 0. Private decisions/order-routing intentions | Investor/market-maker decisions before order submission | Yes | Not generally observable or legally available |
| 1. Public resting orders and quotes (L2/L3) | Displayed *intent* to trade at price/size | Sometimes | Can cancel; spoofing, hidden orders, partial venue coverage |
| 2. Native prints and aggressor-side estimates | Trades actually matched; realised turnover | Price is formed here | Liquidity may refill; labels are venue/algorithm dependent |
| 3. Net positions, settlements, holdings, chain transfers | Asset ownership/custody/settlement | Usually retrospective or ambiguous | Lag, attribution, off-chain internalisation |

**Rule:** GLADIATOR must label all inferred 'money flows' as estimates and specify what was actually observed. Every purchase has a seller; gross trade notional is NOT net cash entering an asset. ETFs additionally have creation/redemption mechanisms; reported fund flows and intraday exchange trades answer different questions.

## Canonical signals — hypotheses to test, NOT assumed alpha

1. **Order flow imbalance (OFI):** eventwise signed changes at best bid/ask with unit tests for limit additions, cancellations, and trades. Implement published definitions precisely; compare with baseline returns. Do not substitute simplistic bid-minus-ask *stock* without labeling.
2. **Queue imbalance:** `(bid_qty - ask_qty)/(bid_qty + ask_qty)` at defined book levels; guard zero denominator and rapid cancellation. Static depth alone is not aggressive buying.
3. **Aggressor signed trade notional:** price × amount with trustworthy trade direction; never infer total-market directional investment from it.
4. **Cancellation/addition/execution ratios:** order lifetime and genuine execution versus fleeting depth; robust to hidden liquidity and venue-specific message semantics.
5. **Market impact and resilience:** measure price response to signed flow, spreads, depth depletion, replenishment and reversal; test across regimes.
6. **Cross-venue price/flow divergence:** timestamp-align exchange feeds, exchange-specific fees/currencies and clock uncertainty; apparent arbitrage may be latency or stale quotes.
7. **ETF auction imbalance and primary-market information:** issuer published holdings and fund flows by *publication time*; Nasdaq NOII for supported auctions, not claimed comprehensive flow.
8. **Crypto funding, basis, OI changes and liquidation prints:** derivatives positioning clues, with venue coverage and latency; no claim that open interest indicates long or short directional sentiment on its own.
9. **On-chain exchange inflow/outflow:** label attribution confidence, chain finality/reorgs, bridge movements, custodial reshuffling and transfers occurring after exchange trading; treat as weak contextual hypothesis until validated.

**Canonical numerical primitives:** midquote `(bid+ask)/2`, relative spread `(ask-bid)/mid`, top-of-book imbalance, trade notional in quote-currency units, event-time versus receive-time lag; all quote-currency conversions use point-in-time rates. Store source and native precision.

## Source/entitlement matrix

| Venue | Source / documentation | Observability | Phase-1 admission |
|---|---|---|---|
| Binance spot | https://github.com/binance/binance-spot-api-docs/blob/master/web-socket-streams.md | Raw trade messages, best bid/ask, depth deltas, snapshot-sync update IDs | Candidate free experiment feed, but confirm region/availability/rights; record disconnected intervals; do not train on incomplete depth |
| Binance SBE | https://github.com/binance/binance-spot-api-docs/blob/master/sbe-market-data-streams.md | 20ms depth differences and faster native market messages for eligible connections | Later optional; investigate access, network, parsing costs |
| Coinbase Advanced | https://help.coinbase.com/en/developer-platform/websocket-feeds/advanced-trade | `market_trades`, level2 book changes, connection heartbeats | Candidate free exchange-specific spot observability; validate replay/sequence handling |
| Nasdaq TotalView/ITCH | https://nasdaqtrader.com/content/technicalsupport/specifications/dataproducts/NQTVITCHspecification.pdf | Native Nasdaq order lifecycle, executions, cancels, auction indicators | **Paid/entitled**; no free assumption; also incomplete across off-exchange venues |
| Nasdaq depth overview | https://www.nasdaq.com/products/data/equities/nasdaq-totalview/depth-data | Full displayed Nasdaq-book depth and auction imbalance | Research reference only without data entitlement |
| CME daily volume/OI | https://www.cmegroup.com/market-data/volume-open-interest.html | Published reports of futures volume/OI | Context only: end-of-day/delayed, **not leading real-time ETF flow** |
| Public blockchain RPC/indexers | Chain-specific documented RPC and third-party indexer licensing | Public, finalised transactions/transfers/contracts | Research-only until chain-specific attribution, finality and provenance verified |

**Critical ETF constraint:** an IEX-only broker feed cannot establish full US ETF liquidity, order imbalance or true national price discovery. Phase 1 may study **sampled single-venue flow** with coverage metadata, but must not present it to Judges as consolidated flows. Full US order-by-order market coverage is unavailable on the zero-cost plan.

## Mandatory event contracts

`NativeMarketEvent`: `source_id`, `venue`, `instrument`, `native_symbol`, `message_type`, `native_sequence`, `exchange_event_ns`, `local_receive_ns`, `ingest_ns`, `price`, `size`, `size_unit`, `quote_currency`, `side_semantics`, `raw_payload_hash`, `source_version`, `rights_id`. Preserve integer/decimal precision; nullable fields reflect nonapplicability rather than guesses.

`BookState`: `venue`, `instrument`, `snapshot_update_id`, `latest_applied_update_id`, `best_bid`, `best_ask`, `depth_by_level`, `observed_age_ms`, `gap_count`, `resync_count`, `book_health`, `sequence_integrity`, `timestamp_uncertainty_ms`.

`FlowFeature`: `feature_name`, `value`, `window_start`, `window_end`, `available_at`, `venue_coverage`, `source_lineage`, `confidence`, `estimation_method`, `market_regime`.

`OnChainEvent`: `chain_id`, `block_height`, `tx_hash`, `log_index`, `block_time`, `observed_at`, `finality_status`, `token_contract`, `amount`, `from_address`, `to_address`, `entity_label`, `label_source`, `attribution_confidence`, `reorg_status`.

## Data-plane correctness and safety invariants

- **Snapshot + delta:** initialise native order books exactly per source docs. Buffer events, apply ordered updates, detect missing sequences, invalidate and rebuild on gaps. No silent reuse of a broken book.
- **Time:** preserve source/event/receive/ingest/available timestamps. A model's feature `available_at` must be <= decision time, including latency, propagation, and correction delays.
- **Data completeness:** outages, stale quote clocks, crossed books, zero denominators, unknown side semantics, non-positive sizes and bad currency conversions raise validation failures. Gaps are **not** zero trading activity.
- **Replay:** byte-identical feed events must rebuild identical book state and derived features; mutations in event order must be caught by tests.
- **Risk:** fail closed for *new* entries on stale/invalid depth if depth is a required input. Exits use independent fallback prices and venue-health-aware execution, not an absolute blanket halt.
- **Manipulation:** test order spoof/cancel churn, wash-trading, fake crypto volume, quote stuffing, iceberg/hidden liquidity and self-trades; distrust synthetic volume without source-quality evidence.
- **No information fantasy:** public chain transfers and large displayed resting orders are not confirmed future institutional orders. No LLM may promote speculation to execution evidence.
- **Operational fit:** high-frequency streams require durable recording, retention/size budgets and quantified end-to-end latency. A standard retail cloud/home connection cannot claim colocated HFT edge. Prefer horizons where signal decay > observable latency and fees.

## Core and governance changes

- **Market Intelligence** owns normalised event feeds and microstructure regime alarms.
- **Gladiators** may generate calibrated forecasts from lag-safe flow features; all feature definitions, venues, costs, and clock semantics versioned.
- **Core** fuses flow evidence with expected net edge and execution feasibility; it may abstain on ambiguous flow.
- **Gatekeeper** can veto trades based on stale books, spread/depth collapse, inaccessible execution venue, or missing entitlements.
- **Arena** tests whether microstructure features beat a price-and-volume baseline **out of sample after realistic costs**, with per-venue and per-regime breakdowns.
- **Judges** audit event replay, source availability, feature leakage, fee/slippage sensitivity, market impact, false alarms and strategy-oversearch.
- **Management** budgets recordings, vendor/licensing, schema upgrades, feed health and capacity; no promotion on simulation-only paper alpha.

## Mandatory falsification experiments before promoting this approach

1. **Displayed wall deception:** simulate a massive bid cancelled before execution. No directional 'capital inflow' credit; feed health stays valid unless depth quality flags trigger.
2. **Confirmed aggressive prints:** high trade volume but balanced aggressors: cannot infer net new money or guaranteed positive return.
3. **Data drop:** remove an intermediate depth update. Book invalidates, synchronises from fresh snapshot, and no feature published during uncertain interval.
4. **Latency:** delay public order book data until after a realised market move. Arena must not report an anticipatory advantage.
5. **On-chain false attribution:** exchange wallet internal transfer marked as uncertain, not 'whale buying'.
6. **Cross-venue disagreement:** large flow on Binance but none on Coinbase; label venue-specific signal, not market-wide conviction.
7. **Etf partial coverage:** IEX-only data never reported as all-venue US ETF order flow.
8. **Cost collapse:** positive gross signal but negative net after fees, spread, slippage and fills must be rejected.
9. **As-of replay:** original reception timestamps vs corrected historical data; historical corrections not visible at decision time.
10. **Control experiment:** verify flow-based signal improves on bar-based baseline on purged, time-forward and untouched market/regime partitions; otherwise reject extra complexity.

**Acceptance:** all invariants proven with deterministic property/replay tests; source rights verified; no known critical errors; adversarial test matrix passes; independent review documents residual risks. Prediction value remains an empirical question and cannot be established from architectural plausibility.
