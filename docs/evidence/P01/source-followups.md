# P01 source follow-ups F-1 to F-5

[Task](../../tasks/TASK-P01-004.md) · [Source registry](source-registry.md) · [Observability map](observability-map.md) · [P01 phase](../../phases/01-research-and-data-access/README.md)

**Status: research evidence for G01, 2026-10-24.** This file selects no source. It authorises no key registration, account, vendor contact, spending, capture or trading.

This file follows up the open items in the [observability map](observability-map.md#follow-up). Where it changes a status recorded in the [source registry](source-registry.md) or the map (both from TASK-P01-001), this file takes precedence. The [status changes](#status-changes) table lists every change. The registry and map are otherwise unchanged from their reviewed versions, apart from a pointer note.

The method is the same as the registry's. Current primary documentation was read on 2026-10-24, and the text behind each claim is quoted. A claim is marked **indirect** when it rests on a search-engine extract of the official page, or on a page that blocked automated fetching. Statuses use only the registry vocabulary: Documented, Conditional, Unresolved and Excluded.

## Summary

| Item | Outcome | Effect |
| --- | --- | --- |
| F-1 Free daily ETF bars | **Narrowed, not closed.** No qualifying source has been found yet. Tiingo's free plan forbids persistent storage, and Alpha Vantage's free tier gives only 100 points. Still open: Twelve Data (F-1a), IEX HIST (F-1b), Stooq and Yahoo | **DEC-029 is not yet triggered**; it applies only when F-1 closes negatively. Crypto evidence is further along at present, but no ordering decision is drawn from that |
| F-2 ETF corporate actions | **Splits and dividends:** no free source with retention rights has been found. **Delistings, symbol changes and point-in-time dates:** not researched (F-2a) | Unresolved |
| F-3 Context sources | Of 12 rows: 6 Documented (2 of them for DEC-030 use), 2 Conditional, 4 Unresolved | See [F-3](#f-3--context-sources) |
| F-4 Crypto venue terms | **Kraken:** the prior-permission clause does not appear to cover personal non-commercial use. Retention and the scope of "Our Content" remain open. **Coinbase:** use is limited to "personal or research purposes", and there is a model-training restriction (indirect evidence) | SR-02 and SR-05 stay Conditional. SR-01 becomes Unresolved and is not relied on for model research |
| F-5 Binance | No new primary evidence | Unresolved; not relied on |

## F-1 — free daily ETF bars

| Candidate | Documented facts | Fit with the source requirements | Status |
| --- | --- | --- | --- |
| Tiingo Starter ([pricing](https://www.tiingo.com/about/pricing), [EOD docs](https://www.tiingo.com/documentation/end-of-day), [terms](https://app.tiingo.com/tos/), "Last Updated Date: October 6th, 2026") | "$0/month"; history "30+ Years"; 50 requests/hour, 1,000/day, 500 unique symbols/month. Fields: raw `open/high/low/close/volume`, `adjOpen…adjClose`, `adjVolume`, `divCash`, `splitFactor`; adjustments follow "the CRSP methodology". "Most US Equity prices are available at 5:30 PM EST, however exchanges may send corrections until 8 PM EST". A token is required (a data key, which DEC-028 allows) | **Storage conflict.** Terms §1.6(a) for Starter: "You may process Tiingo Data only transiently in volatile memory or in a temporary, non-persistent cache … only to complete the calculation"; "You must permanently remove the Tiingo Data from that memory or cache immediately after the calculation". This contradicts the immutable raw store (v10 `10-DATA.md:6`, step 2 at :13, step 8 at :19; reinstated L-010 item 3). Licence: "Internal Use Only" = "your own personal use" | Unresolved: the terms do not permit the required retention. Not relied on. Paid plans are Excluded (£0) |
| Alpha Vantage ([documentation](https://www.alphavantage.co/documentation/)) | `TIME_SERIES_DAILY`: "The "compact" outputsize is available to both free and premium API keys"; "The "full" outputsize is available to premium keys"; compact returns the latest 100 data points. `TIME_SERIES_DAILY_ADJUSTED` "is a premium API function" | 100 daily points is too few for chronological training, validation and locked-test splits (`10-DATA.md:21`). The terms PDF could not be extracted | Unresolved: free-tier coverage is insufficient. Not relied on |
| Twelve Data Basic ([pricing](https://twelvedata.com/pricing), [terms](https://twelvedata.com/terms)) | "800 a day" requests; "For testing and side projects"; "Internal non-display usage". The terms forbid using "Free Tier data for commercial purposes" and storing it "beyond permitted timeframes specified in the Documentation" | History depth and the permitted storage timeframe are not stated | Unresolved (F-1a) |
| Stooq, Yahoo (SR-10, SR-11) | No change | — | Unresolved |
| IEX HIST (SR-06) | No change; the terms page still returns 404 | — | Unresolved (F-1b) |

**Consequence.** F-1 stays open on routes F-1a and F-1b, and on Stooq and Yahoo (SR-10, SR-11), which are unlikely to qualify (L-010 item 7). DEC-029's condition, "F-1 closing negatively", is **not met**. The coordinator will treat it as met only after all four routes close negatively or are set aside with evidence, and will record that closure. The user may also choose to apply DEC-029 earlier.

## F-2 — ETF corporate actions

**Splits and dividends.** No free source was found that both carries split and dividend events and permits retention. Tiingo carries `divCash` and `splitFactor`, but its storage terms apply (see F-1). The source requires raw and adjusted series to be kept separately, with corporate actions tracked in the ledger (L-010 item 4; L-025). Status: **Unresolved**.

**Delistings, symbol changes and point-in-time universe (F-2a).** Not researched in this task. Status: **Unresolved**.

## F-3 — context sources

| Source | Documented facts | Terms | Status |
| --- | --- | --- | --- |
| Federal Reserve FOMC calendar ([page](https://www.federalreserve.gov/monetarypolicy/fomccalendars.htm)) | 2026 meetings: Jan 27–28, Mar 17–18\*, Apr 28–29, Jun 16–17\*, Jul 28–29, Sep 15–16\*, Oct 27–28, Dec 8–9\*. "The minutes of regularly scheduled meetings are released three weeks after the date of the policy decision". "Each meeting date is tentative until confirmed" | US government publication; no restriction found | Documented. Statement release times are not on the page, so capture the event time at publication (REQ-004) |
| BLS CPI schedule ([page](https://www.bls.gov/schedule/news_release/cpi.htm)) | Releases at "08:30 AM". The page as fetched listed the Oct–Dec 2026 reference months (Nov 10, Dec 10, 2026; Jan 13, 2027), "updated as needed … usually at least a week before". Whether earlier months appear elsewhere was not checked | US government publication | Documented. Re-read the page before each release window |
| CFTC Commitments of Traders ([schedule](https://www.cftc.gov/MarketReports/CommitmentsofTraders/ReleaseSchedule/index.htm)) | "released at 3:30 p.m. Eastern time", "usually released on Friday", "usually includes data from the previous Tuesday"; "Federal holidays may delay release by one or two days" | US government publication | Documented. `available_at` is the Friday release, not the Tuesday as-of date |
| GDELT ([about](https://www.gdeltproject.org/about.html)) | "available for unlimited and unrestricted use for any academic, commercial, or governmental use"; "any use or redistribution of the data must include a citation to the GDELT Project". The about page says "daily updates"; register 25 says approximately 15 minutes (not confirmed) | Free; citation required | Documented |
| NYSE hours and calendars ([page](https://www.nyse.com/markets/hours-calendars)) | 2026 and 2027 holidays and early closes (2026: Nov 27 and Dec 24 at 1:00 p.m. ET) | A "Terms of Use" link was not read | Conditional (terms unread) |
| Coin Metrics Community ([docs](https://gitbook-docs.coinmetrics.io/packages/coin-metrics-community-data)) | "API key is not required when accessing community endpoints"; 10 requests per 6-second window per IP; Atlas Community: "limited assets and 30 days of history" | "Available to the community under the Creative Commons license" (linked: CC BY-NC 4.0) | Documented for the personal, non-commercial use of DEC-030 (CC BY-NC) |
| FRED third-party series (SR-13) | "beyond personal use" needs permission; DEC-030 records personal use | — | Documented for DEC-030 use |
| CME daily volume and open interest ([page](https://cmegroup.com/market-data/volume-open-interest.html); indirect) | Reports are "available free of charge". The daily report is "preliminary"; official figures appear in the Daily Bulletin the following morning | Terms not found | Conditional (indirect; terms not found). Context only |
| Deribit | The docs landing page states neither public-method authentication nor terms | — | Unresolved |
| iShares holdings | The landing page states neither holdings downloads nor reuse terms | — | Unresolved |
| Binance futures | As F-5 | — | Unresolved |
| Public blockchain RPC and indexers | Not checked; chain-specific | — | Unresolved |

**F-6, closed by [DEC-030](../../decisions/README.md).** For Kraken, Coinbase, FRED third-party series and Coin Metrics, the terms turn on whether GLADIATOR's research counts as personal or non-commercial use. On 2026-10-24 the user decided that it is personal and non-commercial (DEC-030), which is consistent with the source's personal research engine (KERNEL:6: "GBP 500 is the initial *simulated* portfolio"). Coin Metrics and FRED move to Documented for this use. Any commercial use reopens their terms.

## F-4 — crypto venue terms

### Kraken (SR-02; SR-05 by inference) — Conditional

**API documentation** ([legacy page](https://docs-legacy.kraken.com/api/docs/guides/global-intro/)). The current docs page did not show this text on a direct fetch.
- "Use of the Kraken APIs is subject to the Kraken Terms & Conditions and Privacy Notice".
- "You must seek our prior permission for certain uses of the Kraken API's", which "includes … any non-personal commercial use of data from publicly accessible endpoints, such as market data". Permission requests go to "marketdata@kraken.com".

**General Terms of Service** ([global terms](https://www.kraken.com/legal/global-terms), "Last Updated: 19 October, 2026"). These apply unless the user lives in Brazil, Canada or the EEA; UK users contract with Payward Ltd., London.
- §8 permits use of Our Content "only for your own benefit": "If you wish to use Our Content for any other purpose you must seek prior permission".
- §9 forbids using "any web scraping, web harvesting, or data extraction methods to extract any data from Our Content", and forbids users to "create, use, operate, or employ any bots, robots, parsers, spiders, scripts, programs, routines".

**Reading.**
- The prior-permission clause does not appear to cover personal non-commercial use. That is a reading of the clause, not an affirmative grant.
- It is unclear whether "Our Content" in §9 includes data from the sanctioned public API. If it does, automated capture would conflict with §9.
- Retention is not addressed.
- SR-05 is a support-site download, not the API, so the API clause covers it only by inference.

**Status: Conditional.** Retention, the §9 scope and the legacy-page provenance are open (F-4a).

### Coinbase (SR-01) — Unresolved

**Indirect evidence.** The [Market Data Terms of Use](https://www.coinbase.com/legal/market_data) returned HTTP 403 to automated fetch. These extracts come from a search engine's copy of the official page:
- use is "exclusively for you or your entity's personal or research purposes";
- Market Data "may not be used to build an application intended for use by end users beyond you or your officers and employees";
- the restrictions list a ban, "absent prior express written consent", on using Market Data to develop or train models. The extract is cut off at "fine-", so the full scope is unknown.

**Reading.** GLADIATOR trains and validates forecasting models (CMP-13; v10 `11-QLIB-AND-TRAINING.md:6–13`). Coinbase data therefore appears unusable for model research without written consent. Seeking that consent would be outward contact, so it is a user action.

**Status: Excluded from model research by [DEC-031](../../decisions/README.md)** (user, 2026-10-24: keep it out; no consent is sought). F-4b is closed with it.

### Still open under F-4

| ID | Item |
| --- | --- |
| F-4a | Kraken retention and §9 scope |
| F-4b | The full text of the Coinbase terms |
| F-4c | Coinbase message timestamps (the AsyncAPI spec was not read) |
| F-4d | Kraken REST trade history and its terms |
| F-4e | UK retail availability of the Coinbase developer platform |
| F-4f | The SR-05 30-min inconsistency |

## F-5 — Binance

No new primary evidence. Binance stays **Unresolved and is not relied on**.

## Status changes

| Registry or map row | Before (TASK-P01-001) | After | Reason |
| --- | --- | --- | --- |
| SR-01 Coinbase | Conditional | **Excluded** from model research (DEC-031) | Model-training restriction (indirect), plus the user's decision |
| SR-02 Kraken WebSocket | Conditional | Conditional (terms partly read) | F-4a |
| SR-05 Kraken OHLCVT | Conditional | Conditional | F-4a, F-4f |
| SR-13 FRED | Conditional | Documented for DEC-030 use | DEC-030 |
| Map: venue L2 depth (live) | Conditional (Coinbase, Kraken) | Conditional (Kraken); Coinbase not relied on | F-4 |
| Map: venue trades (live) | Conditional | Conditional (Kraken); Coinbase not relied on | F-4 |
| Map: venue status | Conditional (Coinbase `status`) | **Unresolved**: Coinbase not relied on; Kraken status not checked | F-4 |
| Map: daily bars (ETF, licence-clear) | Unresolved | Unresolved; Tiingo and Alpha Vantage ruled out on terms or coverage | F-1 |
| Map: corporate actions; delistings | Unresolved | Unresolved | F-2, F-2a |
| Map: trading calendar, halts | Unresolved | Conditional (NYSE calendar, terms unread); halts and circuit breakers not checked | F-3 |
| Map: weekly positioning (COT) | Unresolved | **Documented** (Accessible) | F-3 |
| Map: scheduled events (FOMC, CPI) | Unresolved | **Documented** (Accessible) | F-3 |
| Map: news metadata (GDELT) | Unresolved | **Documented** (Accessible) | F-3 |
| Map: on-chain metrics (Coin Metrics) | Unresolved | Documented (Accessible) for DEC-030 use (limited history and assets) | F-3, DEC-030 |
| Map: derivatives, options, liquidations | Unresolved | Unresolved | F-3 |
| Map contract fields citing Coinbase (`native_sequence`, `exchange_event_ns`) | Conditional | Kraken only; Coinbase not relied on | F-4 |

## New follow-up items

| ID | Item | Closure evidence |
| --- | --- | --- |
| F-1a / F-1b | Twelve Data history and storage terms; IEX HIST terms | Primary terms and documented coverage |
| F-2a | ETF delistings, symbol changes and point-in-time universe | Primary documentation |
| F-4a–F-4f | As listed under F-4 | Terms or schema text |
| F-6 | Personal or non-commercial use | **Closed** by DEC-030 |

## Candidate picture (planning only; not a selection)

| Need | Leading candidate | Remaining conditions |
| --- | --- | --- |
| Crypto daily bars | Kraken OHLCVT archive and REST (SR-05) | F-4a, F-4f |
| Crypto live depth and trades | Kraken WebSocket v2 (SR-02) | F-4a; forward capture only |
| Cross-venue comparison | None usable for model research | Coinbase is out (DEC-031); Binance unresolved (F-5) |
| ETF daily bars | None found | F-1a, F-1b; otherwise DEC-029 |
| Macro and event context | FOMC, BLS, CFTC, GDELT, FRED, Coin Metrics (Documented; the last two for DEC-030 use) | — |

The data-access decision (P01 task 7) uses this picture.
