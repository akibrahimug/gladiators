# P01 source registry — market data and core context

[Task](../../tasks/TASK-P01-001.md) · [Observability map](observability-map.md) · [P01 phase](../../phases/01-research-and-data-access/README.md) · [Baseline record](../P00/baseline-decision.md) · [Source register](../../sources/README.md)

**Status: research evidence for G01, 2026-10-24. It selects no source and authorises no access, spending, capture or trading.** Each row records what current primary documentation states, what is still unverified, and the consequence for P01.

## Research assumptions

These are the documented provisional defaults ([DEC-017](../../decisions/README.md); [baseline record](../P00/baseline-decision.md#initial-research-scope-for-p01)). They are used here as working assumptions, as the user directed on 2026-10-24. They are not commitments. G01 confirms or replaces each one with this evidence.

| Assumption | Value | Source of the default |
| --- | --- | --- |
| Universe | US ETFs and crypto spot; crypto derivatives as context only | v10 README:9, `27-ORDER-FLOW-AND-LEDGER-INTELLIGENCE.md:3` |
| Budget | £0 paid services | KERNEL:60; components 14:6, 17:11 |
| Horizon | Daily first; intraday later, if evidence supports it | 17:11, 17:33; `10-DATA.md:27` ("run daily-horizon experiments honestly") |
| Primary input | Native market events first where entitled; bars as baseline and fallback | DEC-015; file 27 "Fundamental correction" |
| Jurisdiction | The user is UK-based (source `09-CONNECTORS.md:16` "do not assume a UK user can open or fund a specific account") | Source text; the user's residence is not otherwise recorded |

## Method

- **Collected:** each source's current primary documentation, read on 2026-10-24.
- **Recorded:** the exact claim that supports each verified field.
- **Starting point:** the candidates named in the preserved sources, namely v10 `09-CONNECTORS.md`, `25-MARKET-INTELLIGENCE-SOURCE-REGISTER.csv`, `27-ORDER-FLOW-AND-LEDGER-INTELLIGENCE.md` "Source/entitlement matrix", and the reinstated L-024 and L-025.
- **Not done:** no account was opened, no data was downloaded and no endpoint was called. Access is therefore *documented*, not *demonstrated*. Per the G01 exit gate, "access not yet demonstrated remains a dependency, never an assumed capability".
- **Unconfirmed fields:** marked **Unverified**, with what is needed to close them.

Status values:
- **Documented:** primary documentation supports the fields.
- **Conditional:** documented, but depends on an unverified eligibility, entitlement or terms item.
- **Unresolved:** a required fact could not be established.
- **Excluded (£0):** paid, so recorded only as an alternative.

## Crypto spot — native market events

| ID | Source | What it provides (documented) | Access and cost | Timestamps and integrity | Terms / eligibility | Status |
| --- | --- | --- | --- | --- | --- | --- |
| SR-01 | Coinbase Advanced Trade WebSocket, public channels ([channels](https://docs.cdp.coinbase.com/coinbase-app/advanced-trade-apis/websocket/websocket-channels), [overview](https://docs.cdp.coinbase.com/coinbase-app/advanced-trade-apis/websocket/websocket-overview)) | `level2` book changes, `market_trades`, `ticker`, `candles`, `heartbeats`, `status` on `wss://advanced-trade-ws.coinbase.com` | Public: "A JWT is not required" for heartbeats, level2, market_trades and ticker; free | "Sequence numbers are increasing integer values for each product"; a gap of more than one "indicate[s] that a message has been dropped". Docs recommend `level2` "to guarantee that messages are delivered and your order book is in sync". Channels "close within 60-90 seconds when no updates arrive", so subscribe to heartbeats. A subscribe must arrive within 5 s | **Unverified:** API terms for market-data use and retention; UK availability of the developer platform | Conditional |
| SR-02 | Kraken WebSocket v2, public channels ([book](https://docs.kraken.com/api/docs/websocket-v2/book), [trade](https://docs.kraken.com/api/docs/websocket-v2/trade), [intro](https://docs.kraken.com/api/docs/guides/global-intro)) | `book` L2 at depth 10/25/100/500/1000 with a snapshot then updates; `trade` with taker `side`, `ord_type`, and `trade_id` "a sequence number, unique per book"; optional snapshot of the last 50 trades | "Public endpoints — no API key needed"; free | RFC3339 timestamps (µs shown); CRC32 checksum "of the top 10 bids and asks" on every snapshot and update; "Updates should always be processed in sequence" | **Unverified:** API or data terms for research use, retention and redistribution (general Terms of Service only located) | Conditional |
| SR-03 | Binance spot WebSocket ([streams](https://github.com/binance/binance-spot-api-docs/blob/master/web-socket-streams.md)) | Diff depth (`@depth`, `@depth@100ms`) with first and final update IDs `U`/`u`; `@trade` with buyer-is-maker flag `m`; market-data-only endpoint `wss://data-stream.binance.vision` | Free. Limits: 5 inbound messages/s, 1024 streams per connection, 300 connection attempts per 5 min per IP; 24 h connection lifetime | Documented local-book procedure: buffer, take a REST snapshot, discard events with `u` ≤ `lastUpdateId`, restart if `U` > book ID + 1. Milliseconds by default; `timeUnit=MICROSECOND` | **Unresolved:** the FCA required Binance Markets Ltd to stop UK regulated activity in 2021 ([The Block](https://www.theblock.co/post/109766/uk-fca-bans-crypto-exchange-binance)). No primary source on UK use of the public market-data API was found | Unresolved |
| SR-04 | Binance public data archive ([README](https://github.com/binance/binance-public-data/blob/master/README.md), [terms](https://github.com/binance/binance-public-data/blob/master/TERMS_AND_CONDITIONS.md)) | Spot `trades`, `aggTrades`, `klines` (1s–1mo) as daily and monthly files. **No order-book data** | Free download; daily files next day | `.CHECKSUM` SHA-256 per zip; "timestamp for SPOT Data from January 1st 2025 onwards will be in microseconds" (reinstated L-025) | **Restrictive:** "Permitted non-commercial uses are limited to academic research, non-monetized open educational projects"; "Commercial licensing is strictly excluded"; redistributed derivative work must credit Binance Vision. Whether private research fits these categories is unresolved | Unresolved |
| SR-05 | Kraken downloadable OHLCVT ([article](https://support.kraken.com/articles/360047124832-downloadable-historical-ohlcvt-open-high-low-close-volume-trades-data)) | Candles at 1–1440 min per pair, "from its first trade on Kraken through 30 June 2026", plus quarterly incremental ZIPs (2026 Q1–Q3 listed) | Free download; also "available programmatically via Kraken's public REST API" | "Only intervals in which trades occurred are included (gaps are not zero-filled)" (reinstated L-025); SHA-256 for the parts and the reassembled ZIP. The page is inconsistent on whether 30-min candles are included | **Unverified:** usage terms (none stated on the page) | Conditional |

## US ETFs — native market events and bars

| ID | Source | What it provides (documented) | Access and cost | Timestamps and integrity | Terms / eligibility | Status |
| --- | --- | --- | --- | --- | --- | --- |
| SR-06 | IEX Exchange HIST ([market data](https://iextrading.com/trading/market-data/), [2017 notice](https://iextrading.com/trading/alerts/2017/014/)) | DEEP (depth by price level) and TOPS (top of book and last sale) for **the IEX venue only**, as pcap files | Free download on a "T+1 basis"; trailing twelve months | Binary pcap per the feed specification version; files are several GB | **Unresolved:** the Historical Data Terms of Use page linked from HIST returned HTTP 404 at `iex.io/iex-historical-data-terms` on 2026-10-24. Permitted use is unknown | Unresolved |
| SR-07 | Alpaca Market Data, Basic plan ([about](https://docs.alpaca.markets/us/docs/about-market-data-api)) | Real-time equities "only the IEX exchange"; historical "since 2016" with a "latest 15 minutes" restriction; bars, trades, quotes | Free; "default option for both Paper and Live trading accounts"; WebSocket 30 symbols; 200 historical calls/min | IEX-only, not SIP. Reinstated L-024 (v5 `09-CONNECTORS.md:30`) forbids silent fallback from consolidated to IEX | **Unverified:** whether a UK individual can open a paper account (Alpaca Europe is FCA-authorised, ref. 723719, but serves businesses; [blog](https://alpaca.markets/blog/alpaca-enters-uk-and-eu-market-through-wealthkernel-acquisition/)); Alpaca's market-data subscriber terms not located | Conditional |
| SR-08 | Alpaca Algo Trader Plus (SIP) | Consolidated SIP feed | **Paid** | — | — | Excluded (£0) |
| SR-09 | Nasdaq TotalView-ITCH ([EXT-001](https://www.nasdaqtrader.com/content/technicalsupport/specifications/dataproducts/NQTVITCHSpecification_5.0.pdf)) | Order-level Nasdaq book and executions | **Paid / entitled**; Nasdaq venue only | — | — | Excluded (£0); semantics reference only |
| SR-10 | Stooq daily CSV | Daily OHLCV, per source `09-CONNECTORS.md:12` | No API; manual CSV; reported daily request quota ([forum, April 2026](https://fundmanagersoftware.com/forum/viewtopic.php?p=28752)) | Adjustment basis undocumented | **Unresolved:** no official terms of use located | Unresolved |
| SR-11 | Yahoo Finance via yfinance | Daily and intraday bars | Unofficial interface (source 09:13) | — | Source text: "never assume permission"; not verified here | Unresolved; not a candidate for an approved dataset |

## Context sources checked in this task

| ID | Source | Documented facts | Status |
| --- | --- | --- | --- |
| SR-12 | SEC EDGAR ([accessing data](https://www.sec.gov/search-filings/edgar-search-assistance/accessing-edgar-data)) | Free. "10 requests/second"; a declared User-Agent is required. Filings are accepted 6:00 a.m.–10:00 p.m. ET; submissions after 5:30 p.m. ET are disseminated the next business day, so acceptance and dissemination times differ (REQ-004) | Documented |
| SR-13 | FRED / ALFRED API ([terms](https://fred.stlouisfed.org/docs/api/terms_of_use.html)) | An API key is required. Third-party series need the owner's permission "beyond personal use". The Fed may limit bandwidth | Documented (key needed); vintages support point-in-time macro (REQ-004) |

Not checked in this task: the remaining rows of the source register `25-MARKET-INTELLIGENCE-SOURCE-REGISTER.csv`, which are the Federal Reserve FOMC calendar, BLS release schedule, GDELT, Coin Metrics Community, Deribit, Binance futures, CFTC COT, exchange holiday calendars and issuer holdings. ETF corporate-action sources and public blockchain RPC are also unchecked. They belong to the context and corporate-action follow-up (see the [observability map](observability-map.md#follow-up)).

## Findings

1. **Crypto native events are documented free from two venues without keys** (SR-01 Coinbase, SR-02 Kraken). Both have sequence and integrity mechanisms that the P02 contract can use: Coinbase sequence numbers, and Kraken CRC32 with trade IDs. Each is venue-local. Their data terms are unverified, which keeps both Conditional.
2. **No free historical crypto order-book source was found.** The archives (SR-04, SR-05) hold trades and candles only. A depth history would have to be captured forward by the project itself.
3. **Binance is unresolved for a UK-based user** (SR-03, SR-04). Its archive terms also restrict use to listed non-commercial categories.
4. **US ETF native events on £0 are IEX-only** (SR-06, SR-07). This matches the source's "critical ETF constraint" (file 27): "Full US order-by-order market coverage is unavailable on the zero-cost plan." Both routes are blocked by an unverified item: HIST terms are unreachable, and Alpaca UK eligibility is unconfirmed.
5. **No licence-clear free daily ETF bar source is established** (SR-07, SR-10, SR-11). The source asks the same open question at 17:30: "Which **lawfully usable** no-cost historical data provider meets daily coverage…". This blocks the daily-first ETF baseline, but not the crypto daily baseline, where SR-05 is Conditional. Closing it needs one of three things:
   - (a) confirm Alpaca eligibility and terms;
   - (b) find official terms for a free daily source;
   - (c) derive IEX-only daily bars from HIST once its terms are known, labelled venue-only.
   The coordinator will raise this as a decision only if every route stays closed (see the [follow-up](observability-map.md#follow-up)).
