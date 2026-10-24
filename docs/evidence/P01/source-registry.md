# P01 source registry — market data and core context

[Task](../../tasks/TASK-P01-001.md) · [Observability map](observability-map.md) · [P01 phase](../../phases/01-research-and-data-access/README.md) · [Baseline record](../P00/baseline-decision.md) · [Source register](../../sources/README.md)

**Status: research evidence for G01, 2026-10-24. It selects no source and authorises no access, account, spending, capture or trading.** For each source, a row records what current primary documentation states, what is still unverified and the consequence for P01.

## Research assumptions and source constraints

The defaults below come from DEC-017 ([baseline record](../P00/baseline-decision.md#initial-research-scope-for-p01)). As the user directed on 2026-10-24, they are used as working assumptions, not commitments. G01 confirms or replaces each one using this evidence.

| Item | Value | Basis |
| --- | --- | --- |
| Universe | US ETFs and crypto spot; crypto derivatives as context only | DEC-017 default; v10 README:9; `27-ORDER-FLOW-AND-LEDGER-INTELLIGENCE.md:3` |
| Budget | £0 paid services | DEC-017 default; KERNEL:6 ("Zero paid services for phase 1"), KERNEL:60; components 14:6, 17:11 |
| Keys and accounts | KERNEL:60 says "No API keys, paid GPU or live orders", and 17:11 says "no broker". By [DEC-028](../../decisions/README.md), free read-only **data** keys are allowed as a research assumption. Broker or trading-account keys, Alpaca paper included, stay out | Source constraint, amended by DEC-028; CLAUDE.md scope (no trading credentials) |
| Horizon | Daily first; intraday later if evidence supports it. If no licence-clear ETF daily source is found, the daily baseline runs on crypto first while ETFs stay in scope ([DEC-029](../../decisions/README.md)) | DEC-017 default; 17:11, 17:33; `10-DATA.md:27` ("run daily-horizon experiments honestly") |
| Primary input | Native market events first where entitled; bars as baseline and fallback | DEC-015; file 27 "Fundamental correction" |
| Venue accessibility | **Source constraint, not a DEC-017 default:** "live instruments and venues must be legally accessible to a UK retail account" (README:9); "do not assume a UK user can open or fund a specific account" (`09-CONNECTORS.md:16`) | Source text. The user's residence is not recorded in the workspace |

## Method

**Sources read.** I read each source's current primary documentation on 2026-10-24 and recorded the exact claim behind every verified field.

**Starting point.** The candidates came from the preserved sources:
- v10 `09-CONNECTORS.md`
- `25-MARKET-INTELLIGENCE-SOURCE-REGISTER.csv`
- the "Source/entitlement matrix" in `27-ORDER-FLOW-AND-LEDGER-INTELLIGENCE.md`
- the reinstated L-010 (v4 `10-DATA.md:41`), L-024 and L-025

**Nothing exercised.** No account was opened, no key was requested, no data was downloaded and no endpoint was called. Access is therefore *documented*, not *demonstrated*. Under the G01 exit gate, "access not yet demonstrated remains a dependency, never an assumed capability".

**Status values** (the observability map's classes are given in brackets):

| Registry status | Meaning | Observability-map class |
| --- | --- | --- |
| Documented | Primary documentation supports the fields, and no eligibility or terms item is open | Accessible |
| Conditional | Documented, but depends on an unverified eligibility, entitlement or terms item | Conditional |
| Unresolved | A required fact could not be established, or the documented terms may not permit the intended use | Unresolved |
| Excluded | Paid (£0 assumption), or needs a broker or trading credential (DEC-028); recorded only as an alternative | Unavailable under the current assumptions |

## Crypto spot — native market events

| ID | Source | What it provides (documented) | Access and cost | Timestamps and integrity | Terms / eligibility | Status |
| --- | --- | --- | --- | --- | --- | --- |
| SR-01 | Coinbase Advanced Trade WebSocket, public channels ([channels](https://docs.cdp.coinbase.com/coinbase-app/advanced-trade-apis/websocket/websocket-channels), [overview](https://docs.cdp.coinbase.com/coinbase-app/advanced-trade-apis/websocket/websocket-overview)). These pages replace the `help.coinbase.com` URLs given in file 27 and register 25 | `level2` book changes, `market_trades`, `ticker`, `candles`, `heartbeats` and `status` on `wss://advanced-trade-ws.coinbase.com` | Public: "A JWT is not required" for heartbeats, level2, market_trades and ticker; free; no key | "Sequence numbers are increasing integer values for each product"; a jump of more than one "indicate[s] that a message has been dropped". The docs recommend `level2` "to guarantee that messages are delivered and your order book is in sync". Channels "close within 60-90 seconds when no updates arrive", so subscribe to heartbeats. A subscribe must arrive within 5 s. **Unverified:** whether messages carry an exchange event timestamp separate from receive time | **Unverified:** the API terms for market-data use and retention (F-4); whether the developer platform is available to a UK retail user (F-4) | Conditional |
| SR-02 | Kraken WebSocket v2, public channels ([book](https://docs.kraken.com/api/docs/websocket-v2/book), [trade](https://docs.kraken.com/api/docs/websocket-v2/trade), [intro](https://docs.kraken.com/api/docs/guides/global-intro)) | `book` level 2 at depth 10/25/100/500/1000, a snapshot followed by updates. `trade` carries the taker `side`, `ord_type` and a `trade_id` that is "a sequence number, unique per book"; an optional snapshot gives the last 50 trades | "Public endpoints — no API key needed"; free | RFC3339 timestamps (µs shown) for "the book order update time"; a CRC32 checksum "of the top 10 bids and asks" on every snapshot and update; "Updates should always be processed in sequence" | **Unverified:** API or data terms covering research use, retention and redistribution. Only the general Terms of Service were located (F-4) | Conditional |
| SR-03 | Binance spot WebSocket ([streams](https://github.com/binance/binance-spot-api-docs/blob/master/web-socket-streams.md)) | Diff depth (`@depth`, `@depth@100ms`) with first and final update IDs `U`/`u`. `@trade` carries the buyer-is-maker flag `m`. A market-data-only endpoint is `wss://data-stream.binance.vision` | Free. Limits: 5 inbound messages/s, 1024 streams per connection, 300 connection attempts per 5 min per IP, 24 h connection lifetime | A documented local-book procedure: buffer events, take a REST snapshot, discard events with `u` ≤ `lastUpdateId`, restart if `U` > book ID + 1. Milliseconds by default; `timeUnit=MICROSECOND` gives microseconds | **Unresolved:** the FCA's [First Supervisory Notice](https://www.fca.org.uk/publication/supervisory-notices/first-supervisory-notice-binance-markets-limited.pdf) of 25 June 2021 barred Binance Markets Ltd from UK regulated activity, and the FCA's [consumer warning](https://www.fca.org.uk/news/news-stories/consumer-warning-binance-markets-limited-and-binance-group) says those requirements "remain in place". I found no primary statement on UK use of the public market-data API (F-5) | Unresolved |
| SR-04 | Binance public data archive ([README](https://github.com/binance/binance-public-data/blob/master/README.md), [terms](https://github.com/binance/binance-public-data/blob/master/TERMS_AND_CONDITIONS.md)) | Spot `trades`, `aggTrades` and `klines` (1s–1mo) as daily and monthly files. **No order-book data** | Free download. Daily files appear the next day; monthly files on the first Monday of the month | A `.CHECKSUM` SHA-256 file per zip. "The timestamp for SPOT Data from January 1st 2025 onwards will be in microseconds", which corroborates reinstated L-025 | The terms say "Permitted non-commercial uses are limited to academic research, non-monetized open educational projects", "Commercial licensing is strictly excluded", and a redistributed derivative work must credit Binance Vision. **Unresolved:** whether private research falls within the permitted categories (F-5) | Unresolved |
| SR-05 | Kraken downloadable OHLCVT ([article](https://support.kraken.com/articles/360047124832-downloadable-historical-ohlcvt-open-high-low-close-volume-trades-data)) | Candles at 1–1440 min for each pair, "from its first trade on Kraken through 30 June 2026", plus quarterly incremental ZIPs (2026 Q1–Q3 listed) | Free download; the same data is "available programmatically via Kraken's public REST API" | "Only intervals in which trades occurred are included (gaps are not zero-filled)", which corroborates L-025. SHA-256 for the parts and the reassembled ZIP. Quarterly drops mean `available_at` lags the bar end by up to a quarter. **Unverified:** whether 30-min candles are included; the page is inconsistent (F-4) | **Unverified:** usage terms; none are stated on the page (F-4) | Conditional |

## US ETFs — native market events and bars

| ID | Source | What it provides (documented) | Access and cost | Timestamps and integrity | Terms / eligibility | Status |
| --- | --- | --- | --- | --- | --- | --- |
| SR-06 | IEX Exchange HIST ([market data](https://iextrading.com/trading/market-data/), [2017 notice](https://iextrading.com/trading/alerts/2017/014/)) | DEEP (depth by price level) and TOPS (top of book and last sale), **for the IEX venue only**, as pcap files | Free download on a "T+1 basis"; trailing twelve months; no key stated | Binary pcap decoded per the feed specification version; files run to several GB. T+1 publication sets `available_at` | **Unresolved:** the Historical Data Terms of Use page linked from HIST returned HTTP 404 at `iex.io/iex-historical-data-terms` on 2026-10-24, so permitted use is unknown (F-1) | Unresolved |
| SR-07 | Alpaca Market Data, Basic plan ([plan table](https://docs.alpaca.markets/us/docs/about-market-data-api), [bars reference](https://docs.alpaca.markets/reference/stockbars)) | Real-time "IEX" only. Historical data "Since 2016", limited to the "latest 15 minutes". The bars endpoint's `feed` defaults to `sip` ("all US exchanges"), and its 15-minute default applies "if the user doesn't have real-time access for the feed". So consolidated historical bars outside the latest 15 minutes are **probably** available on Basic; Alpaca has not confirmed this | Free, but "all market data endpoints require authentication" except historical crypto; keys come from an account | IEX real-time is not SIP; reinstated L-024 (v5 `09-CONNECTORS.md:30`) forbids silent fallback from consolidated to IEX | Keys belong to a broker or paper-trading account, which DEC-028 excludes. **Unverified:** whether a UK individual can open an account. Alpaca Europe is FCA-authorised (ref. 723719) but serves businesses ([blog](https://alpaca.markets/blog/alpaca-enters-uk-and-eu-market-through-wealthkernel-acquisition/)). Subscriber terms were not located | Excluded (DEC-028). It is the strongest alternative if the credentials boundary is reopened |
| SR-08 | Alpaca Algo Trader Plus | "All US Stock Exchanges", real time | "$99 / month" ([plan table](https://docs.alpaca.markets/us/docs/about-market-data-api)) | — | — | Excluded (£0) |
| SR-09 | Nasdaq TotalView-ITCH ([EXT-001](https://www.nasdaqtrader.com/content/technicalsupport/specifications/dataproducts/NQTVITCHSpecification_5.0.pdf)) and Nasdaq depth overview (file 27:42) | Order-level Nasdaq book and executions; full displayed depth and auction imbalance | Source text calls it "**Paid/entitled**" (27:41). **Unverified:** a current Nasdaq price list | — | — | Excluded (£0); semantics reference only |
| SR-10 | Stooq daily CSV | Daily OHLCV, per `09-CONNECTORS.md:12` | No API; manual CSV; a reported daily request quota ([forum, April 2026](https://fundmanagersoftware.com/forum/viewtopic.php?p=28752), secondary) | The adjustment basis is undocumented | **Unresolved:** no official terms of use were located. Reinstated L-010 (v4 `10-DATA.md:41`, item 7) records "Stooq automation reportedly restricted" (F-1) | Unresolved |
| SR-11 | Yahoo Finance via yfinance | Daily and intraday bars | An unofficial interface (`09-CONNECTORS.md:13`) | — | L-010 item 7: "yfinance describes Yahoo data as personal-use". It cannot become an approved dataset until its terms are verified (L-025 `source_approval`) (F-1) | Unresolved |

## Context sources checked in this task

| ID | Source | Access and cost | Timestamps | Terms | Status |
| --- | --- | --- | --- | --- | --- |
| SR-12 | SEC EDGAR ([accessing data](https://www.sec.gov/search-filings/edgar-search-assistance/accessing-edgar-data)) | Free; "10 requests/second"; a declared User-Agent is required | Accepts filings 6:00 a.m.–10:00 p.m. ET. "Some filing submissions that begin after 5:30 p.m. ET … will be disseminated the next business day", so acceptance and dissemination times can differ (REQ-004) | Fair-access policy as stated | Documented |
| SR-13 | FRED / ALFRED API ([terms](https://fred.stlouisfed.org/docs/api/terms_of_use.html)) | "You must have register for an API Key" (a read-only data key, allowed by DEC-028); no fee stated | Vintages support point-in-time macro data (REQ-004) | Third-party series need the owner's permission "beyond personal use"; the Fed may limit bandwidth. **Unverified:** whether the research use counts as personal use (F-3) | Conditional |

## Named candidates not checked in this task

| Candidate | Where named | Why not checked | Closure |
| --- | --- | --- | --- |
| Alpha Vantage, Twelve Data, other free tiers | `09-CONNECTORS.md:14` | Free tiers need data keys, which are now allowed by DEC-028. They are candidates for the ETF daily-bar gap | F-1 |
| Broker-provided free historical or paper feeds other than Alpaca | `09-CONNECTORS.md:16` | Broker accounts are excluded by DEC-028 | Reopen only if DEC-028 changes |
| Binance SBE market data | 27:39 | Binance access is unresolved (SR-03), and the source marks SBE "Later optional" | F-5 |
| CME daily volume and open interest | 27:43 | Context only: end-of-day, "not leading real-time ETF flow" | F-3 |
| Public blockchain RPC and indexers | 27:44 | Chain-specific; research only in the source | F-3 |
| The 9 remaining register-25 rows: FOMC calendar, BLS schedule, GDELT, Coin Metrics Community, Binance futures, Deribit, CFTC COT, exchange holiday calendars, issuer holdings | `25-MARKET-INTELLIGENCE-SOURCE-REGISTER.csv` | Context and calendar sources for a follow-up task | F-3 |
| ETF corporate-action and dividend sources | `10-DATA.md` market schema; L-010 item 1; L-025 | No candidate is named in the source | F-2 |

## Findings

1. **Free crypto native events from two venues, no key needed.** Coinbase (SR-01) and Kraken (SR-02) document these, together with sequence and integrity mechanisms the P02 contract can use. Each feed is venue-local, and its data terms are unverified, so both stay Conditional.
2. **No free historical crypto order book.** The archives (SR-04, SR-05) hold trades and candles only. Any depth history would come from the project's own forward capture.
3. **Binance is unresolved** against the UK retail-account constraint (SR-03), and its archive terms limit use to listed non-commercial categories (SR-04).
4. **ETF native events on £0 without broker keys are IEX-only, at T+1** (SR-06), and the HIST terms are unreachable. This matches the source's "critical ETF constraint" (file 27). The only route found to consolidated historical ETF bars is Alpaca Basic (SR-07), and DEC-028 excludes it.
5. **No licence-clear free daily ETF bar source exists under the current assumptions** (SR-06, SR-10, SR-11). The source poses the same open question at 17:30: "Which **lawfully usable** no-cost historical data provider meets daily coverage…". The candidates still to check are the free data-key tiers (F-1). If none qualifies, the daily baseline runs on crypto first while ETFs stay in scope (DEC-029).
