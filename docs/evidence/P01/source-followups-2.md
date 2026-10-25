# P01 source follow-ups, round 2

[Task](../../tasks/TASK-P01-006.md) · [Round 1](source-followups.md) · [Source registry](source-registry.md) · [Observability map](observability-map.md) · [Data-access decision](data-access-decision.md) · [P01 phase](../../phases/01-research-and-data-access/README.md)

**Status: research evidence for G01, 2026-10-25.** This file selects no source. It authorises no key registration, account, vendor contact, download, capture, spending or trading.

This round follows up the items that [round 1](source-followups.md) and the [data-access decision](data-access-decision.md) left open and that public documentation can answer. Where it changes a status recorded in round 1, the registry or the map, this file takes precedence; the [status changes](#status-changes) table lists every change. Items that need Kraken's reply (DEC-032) or a later sample download stay open.

The method is unchanged: current primary documentation was read on 2026-10-25, and the text behind each claim is quoted. **Indirect** marks a claim resting on a search-engine extract or on a page that returned no readable text to automated fetch. Statuses use the registry vocabulary: Documented, Conditional, Unresolved and Excluded. "Set aside" and "narrowed" qualify a status; they are not statuses. The SR rows keep their own statuses (SR-05 stays Conditional).

## Summary

| Item | Outcome | Effect |
| --- | --- | --- |
| F-1 Free daily ETF bars | **Closed negatively.** Of the routes examined, all four remaining ones are set aside with evidence: Twelve Data (retention not established: tied to the subscription; Basic history depth undocumented), IEX HIST (IEX venue only; twelve-month range unconfirmed), Stooq (no readable terms) and Yahoo (terms forbid automated collection) | **DEC-029's condition is met for the routes examined**, recorded here by the coordinator. A newly found qualifying source reopens F-1. The daily-first baseline runs on crypto spot first; ETFs stay in scope, and an ETF daily source stays a G01 dependency |
| F-2a ETF delistings and point-in-time universe | Not researched; deferred with ETFs under DEC-029 | Unresolved; no effect on the crypto-first baseline |
| Venue status (map row) | **Kraken publishes it publicly**: REST `SystemStatus` and the WebSocket v2 `status` channel, with no key. No historical status archive was found | Conditional (Kraken terms, F-4a) going forward. Historical coverage for archived bars is a new G01 dependency (F-7) |
| F-4d Kraken REST trade history | Narrowed: 1,000 trades per call with a `since` cursor; paging back from the first trade is not documented | Unresolved (narrowed) |
| F-4f SR-05 30-minute interval | Re-confirmed: the current article still contradicts itself | Unresolved; the sample plan settles it |
| F-4h SR-05 availability at bar close | Narrowed: REST OHLC returns only the 720 most recent entries, and its last entry is not committed | Unresolved (narrowed); REST cannot replace the archive for history |
| F-4i Candle timestamp semantics | Not documented on either page; the REST example is consistent with bar start, unconfirmed | Unresolved; the sample plan settles it |
| Context S-7 | GDELT: every 15 minutes. FRED/ALFRED: vintage dates only, no time of day. Coin Metrics: daily metrics computed at 00:00 UTC (indirect) | S-7 documented for GDELT, and for FRED at date granularity with a proposed `available_at` rule; Coin Metrics stays Unresolved |

## F-1 — free daily ETF bars: closed negatively

| Route | Documented facts | Why it is set aside | Status |
| --- | --- | --- | --- |
| F-1a Twelve Data Basic ([terms](https://twelvedata.com/terms), "Last updated: January 1, 2026"; [pricing](https://twelvedata.com/pricing); [history article](https://support.twelvedata.com/en/articles/5656039-how-to-get-historical-prices)) | Basic: "800 a day" requests, "Internal non-display usage". Terms §2.3(g) forbid storing or caching Data "beyond permitted timeframes specified in the Documentation"; the [documentation](https://twelvedata.com/docs) read (first 100,000 characters of a 1.3 M-character page) states no timeframe, only "Cache responses for frequently accessed data". §16.1: "Customer may retain Data only: (a) For duration permitted by subscription". §16.2: "Upon termination or expiration: (a) All Data must be deleted within 30 days". Daily intervals "contain data for the complete history since the first trading date for most symbols"; no page says whether Basic gets that history | **S-2 (retention) is not established.** §16.1 ties retention to the subscription, and §16.2 requires deletion within 30 days of termination. The §2.3(g) timeframe was not found in the portion of the Documentation read, nor by a site search. This is weaker than Tiingo's ban on any persistent storage (round 1), but the immutable raw store (v10 `10-DATA.md:6`; reinstated L-010 item 3) cannot be planned on retention whose limit is unknown. **Basic history depth is also undocumented** (S-5). The set-aside rests on these two gaps; a documented storage timeframe and Basic history would reopen it | Unresolved; set aside |
| F-1b IEX HIST (SR-06; [2017 notice](https://iextrading.com/trading/alerts/2017/014/), [market data](https://iextrading.com/trading/market-data/)) | "HIST is a FREE market data offering"; "Data will remain available for the trailing twelve months"; "The binary output of DEEP and TOPS data are provided in pcap format". The terms page now redirects from `iexexchange.io` to `iex.io/iex-historical-data-terms`, which returned HTTP 404 on 2026-10-25 | It holds IEX-venue output only, not consolidated daily bars (registry SR-06): "Do not turn IEX-only equities into claimed SIP observations" (`09-CONNECTORS.md:29`). That ground holds whatever the terms say. The twelve-month range comes from the 2017 notice; the current page's download table showed no rows, so the current range is unconfirmed. If it is still twelve months, it is also too short for chronological training, validation and locked-test splits (`10-DATA.md:21`) | Unresolved; set aside |
| Stooq (SR-10) | `stooq.com/db/` and `stooq.com/db/h/` returned no readable text to automated fetch. Secondary sources only: an API key obtained through a CAPTCHA and a daily request quota ([API Evangelist](https://providers.apievangelist.com/providers/stooq/), indirect). No terms of use were found | No terms can be read, so no `source_approval` record (L-025) can be made. L-010 item 7 already records "Stooq automation reportedly restricted" | Unresolved; set aside |
| Yahoo via yfinance (SR-11; [Yahoo Terms](https://legal.yahoo.com/us/en/yahoo/terms/otos/index.html), first 100,000 characters read) | §2(d): users may not "access or collect data, or attempt to access or collect data, from our Services using any automated means, including but not limited to robots, spiders, scrapers, data mining tools"; "you must not reproduce, modify, rent, lease, sell, trade, distribute…" | yfinance collects data by automated means, which these terms forbid | Unresolved; set aside |

**Closure, recorded by the coordinator on 2026-10-25.** Round 1 set out the test: DEC-029 applies "only after all four routes close negatively or are set aside with evidence, and the coordinator has recorded that closure". All four are now set aside with the evidence above, and Tiingo and Alpha Vantage were set aside in round 1. Other free end-of-day services were never registered as candidates, so the closure covers **the routes examined**; a newly found qualifying source reopens F-1. **DEC-029 is therefore triggered:** the daily-first baseline (W-5) runs on crypto spot first. DEC-029 drops nothing: ETFs stay in scope, and a licence-clear ETF daily source stays a G01 dependency. A paid source would need a change to the £0 provisional default (S-3), which is the user's choice; any user decision on the ETF route supersedes this closure.

## F-2a — ETF delistings, symbol changes and point-in-time universe

Not researched. Under DEC-029, ETF data no longer feeds the first baseline, so F-2 and F-2a move with the ETF dependency. Status: **Unresolved**.

## Venue status — Kraken

**REST** ([`GET /public/SystemStatus`](https://docs.kraken.com/api/docs/rest-api/get-system-status)). The operation sets `security: []`, so no key is needed.
- `status` values: `online` ("Kraken is operating normally. All order types may be submitted and trades can occur."), `maintenance` ("The exchange is offline. No new orders or cancellations may be submitted."), `cancel_only` ("… No trades will occur.") and `post_only` ("Only post-only limit orders can be submitted. … No trades will occur.").
- `timestamp`: "Current timestamp (RFC3339)".
- `upcoming_maintenance`: advisories "within the next 72 hours", each with `expected_start_utc` and `expected_end_utc`. `emergency`: unresolved incidents, each with `started_at_utc`. The top-level status is "independent of both arrays".

**WebSocket v2** ([`status` channel](https://docs.kraken.com/api/docs/websocket-v2/status)). It is sent "on successful websocket connection and when the trading engine status changes", with `system` set to `online`, `cancel_only`, `maintenance` or `post_only`. The page does not say whether authentication is required; it is grouped with the public channels used for SR-02, but that is not confirmed.

**Reading.**
- These cover the venue-status input (`10-DATA.md:40`; the typed `VenueStatus` connector at `09-CONNECTORS.md:29`).
- `maintenance`, `cancel_only` and `post_only` all mean no trades occur, so a bar gap in those states is a venue state, not a no-trade interval. Mapping those states to a code distinct from `NO_EVENT` (`09-CONNECTORS.md:29`) is the coordinator's **proposed interpretation**: the feed is up, but the venue is not trading.
- **Status: Conditional** going forward, on the same Kraken terms as SR-02 (F-4a, DEC-032).

**F-7 (new): historical venue status for archived bars.** Nothing read here archives Kraken's past status, so it comes only from forward capture. `10-DATA.md:40` says "missing critical price/venue coverage stops new entries". Applied literally to the crypto-first daily baseline, a backtest on the SR-05 archive would have no venue-status coverage and would block every entry. This is a G01 dependency for the reviewer. Options include:
- infer venue state from archive gaps together with Kraken's published incident history, if one can be found;
- a reviewer-approved rule for historical bars, recorded as an assumption with its limitation;
- restricting evaluation to periods covered by forward capture.

## F-4 — Kraken data details

| ID | Documented facts (2026-10-25) | Outcome |
| --- | --- | --- |
| F-4d REST trades ([`Trades`](https://docs.kraken.com/api/docs/rest-api/get-recent-trades)) | "Returns the last 1000 trades by default"; `count` "up to 1000"; `since`: "Return trade data since given timestamp"; `last`: "ID to be used as since when polling for new trade data". Each trade is "[<price>, <volume>, <time>, <buy/sell>, <market/limit>, <miscellaneous>, <trade_id>]". No key | **Narrowed.** Forward polling is documented. Whether `since` can page back to a pair's first trade is not documented, and the terms are F-4a. Unresolved |
| F-4f SR-05 30-minute files ([article](https://support.kraken.com/hc/en-us/articles/360047124832-Downloadable-historical-OHLCVT-Open-High-Low-Close-Volume-Trades-data)) | One section: "1, 5, 15, 30, 60, 240, 720 and 1440 minute intervals"; "About the data": "1, 5, 15, 60, 240, 720 and 1440-minute intervals". Coverage "through 30 June 2026"; columns "timestamp, open, high, low, close, volume, trades"; "OHLCVT files do not include a header row" | **Re-confirmed; Unresolved.** Sample plan step 1 records which interval files exist |
| F-4g Delisted pairs | Neither the article nor the REST pages say | Unresolved; sample plan step 1 |
| F-4h Availability at bar close ([`OHLC`](https://docs.kraken.com/api/docs/rest-api/get-ohlc-data)) | "Returns up to 720 of the most recent entries"; older data cannot be fetched with `since`. "The last entry in the OHLC array is for the current, not-yet-committed timeframe". `last`: "ID to be used as since when polling for new, committed OHLC data" | **Narrowed.** REST can supply committed bars near bar close going forward, but only within the last 720 entries (about two years of 1440-minute bars), so it cannot replace the archive for history. The T-2a default (archive publication time) still applies to archived history. The uncommitted last entry must be excluded (a validation rule for P02). Unresolved |
| F-4i Candle timestamp semantics | The REST page lists `[int <time>, …]` without saying whether `time` is bar start or end. Its example timestamps (1688671200, 1688671260, 1688671320) are 60 s apart and on minute boundaries, which fits bar start for 1-minute bars but does not prove it. The archive article says nothing | Unresolved; sample plan step 1 (REST comparison) |

## Context sources — S-7 (publication timing)

| Source | Documented facts | S-7 outcome |
| --- | --- | --- |
| GDELT 2.0 ([announcement](https://blog.gdeltproject.org/gdelt-2-0-our-global-world-in-realtime/)) | "both the GDELT Event and Global Knowledge Graph now update every 15 minutes"; streams "begin late morning February 19, 2015, so there is not currently a historical backfile" | **Documented:** a 15-minute cadence. This settles the round-1 question (register 25's "approximately 15 minutes" against "daily updates"). History starts on 2015-02-19 |
| FRED/ALFRED ([real-time periods](https://fred.stlouisfed.org/docs/api/fred/realtime_period.html)) | "The real-time period marks when facts were true or when information was known until it changed"; `realtime_start` and `realtime_end` are "YYYY-MM-DD formatted dates" | **Documented at date granularity only.** A vintage gives the day a value became known, not the time. **Proposed rule for the G01 reviewer:** for a historical vintage, `available_at` = the start of the day after `realtime_start`, at 00:00 America/Los_Angeles. That is no earlier than the end of the `realtime_start` day in any contiguous-US time zone, so a value cannot be stamped before it existed. For forward retrieval, `available_at` = the later of that value and the observed `retrieved_at`. The rule stays until a release time is documented |
| Coin Metrics Community ([asset metrics overview](https://docs.coinmetrics.io/api-data-types/asset-metrics-overview), indirect) | Daily network metrics "are computed at 00:00 UTC time for the previous 24 hour interval" (search extract). The "Asset Completion Time" page was not read, and the [status page](https://status.coinmetrics.io/) reports delays to end-of-day metrics | **Unresolved.** 00:00 UTC is when computation starts, not when data is available. Until completion times are read, `available_at` is the observed `retrieved_at` for forward retrieval; historical use needs a documented completion time |

Retention (S-2) is still not established for any context source; none of the pages read here addresses it.

## Not done in this round

- **NYSE terms of use:** `nyse.com/terms-of-use` returned HTTP 404. The calendar is ETF-only and is deferred with ETFs under DEC-029.
- **Kraken items F-4a** (retention and §9 scope): they wait for Kraken's reply (DEC-032).
- **Halts and circuit breakers:** ETF-only; deferred with ETFs.

## Status changes

| Row | Before | After | Reason |
| --- | --- | --- | --- |
| F-1 as a whole | Narrowed, not closed | **Closed negatively** (coordinator record, 2026-10-25) | All four routes set aside with evidence |
| DEC-029 | Not triggered | **Triggered**: crypto spot first; ETFs stay in scope as a G01 dependency | F-1 closure |
| F-1a Twelve Data | Unresolved | Unresolved; set aside | S-2 not established (§16 tied to the subscription; no storage timeframe found); Basic history undocumented (S-5) |
| SR-06 IEX HIST (F-1b) | Unresolved | Unresolved; set aside | IEX venue only; twelve-month range unconfirmed; terms page still 404 |
| SR-10 Stooq | Unresolved | Unresolved; set aside | No readable terms |
| SR-11 Yahoo | Unresolved | Unresolved; set aside | Terms forbid automated collection |
| Map: venue status | Unresolved (Kraken not checked) | **Conditional** going forward (Kraken REST `SystemStatus` and WebSocket v2 `status`; terms F-4a); history is F-7 | Public, documented, no key |
| Map: news metadata (GDELT) | Documented | Documented; S-7 15-minute cadence | Announcement |
| FRED/ALFRED S-7 | Open | Documented at date granularity; proposed `available_at` rule for G01 | Real-time period docs |
| Coin Metrics S-7 | Open | Unresolved (indirect: computed at 00:00 UTC; completion time unread) | Search extract |
| F-7 historical venue status | — | **New**; Unresolved; G01 dependency | No status archive found |
| F-4d, F-4h | Unresolved | Unresolved (narrowed) | REST docs |
| F-4f, F-4g, F-4i | Unresolved | Unresolved | Not stated in the docs; the sample plan settles them |
