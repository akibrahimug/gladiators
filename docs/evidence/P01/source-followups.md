# P01 source follow-ups F-1 to F-5

[Task](../../tasks/TASK-P01-004.md) · [Source registry](source-registry.md) · [Observability map](observability-map.md) · [P01 phase](../../phases/01-research-and-data-access/README.md)

**Status: research evidence for G01, 2026-10-24. It selects no source and authorises no key registration, account, contact with a vendor, spending, capture or trading.**

This file follows up the open items in the [observability map](observability-map.md#follow-up). Where it changes a status recorded in the [source registry](source-registry.md) (TASK-P01-001), this file takes precedence. The registry stays as originally reviewed, apart from a pointer note.

The method is the same as for the registry: current primary documentation read on 2026-10-24, with the exact supporting text quoted. Two kinds of source are marked as indirect: a claim taken from a search-engine extract of the official page, and a page blocked to automated fetch.

## Summary

| Item | Outcome | Status change |
| --- | --- | --- |
| F-1 Free daily ETF bars | **No qualifying source found.** The one complete free source found, Tiingo, forbids persistent storage on its free plan. Alpha Vantage's free tier returns only the latest 100 points. The Twelve Data, Stooq, Yahoo and IEX HIST terms remain unestablished | The DEC-029 condition is met for planning purposes: the daily baseline runs on crypto first, and the ETF daily source becomes a G01 dependency |
| F-2 ETF corporate actions | No free source with retention rights found; tied to F-1 | Unresolved; deferred with ETFs under DEC-029 |
| F-3 Context sources | Of 12 rows: 5 Documented, 3 Conditional, 4 Unresolved; the full list is under F-3 | Several rows move from Unresolved to Documented or Conditional |
| F-4 Crypto venue terms | **Kraken:** prior permission is needed only for "non-personal commercial use". **Coinbase:** use is limited to "personal or research purposes" and model training is restricted (indirect evidence) | SR-02 is the leading crypto source. SR-01 is unsuitable for model research without Coinbase's written consent |
| F-5 Binance | No new primary evidence | Stays Unresolved and is not relied on |

## F-1 — free daily ETF bars

| Candidate | Documented facts | Fit with the source requirements | Status |
| --- | --- | --- | --- |
| Tiingo Starter ([pricing](https://www.tiingo.com/about/pricing), [EOD docs](https://www.tiingo.com/documentation/end-of-day), [terms](https://app.tiingo.com/tos/), "Last Updated Date: October 6th, 2026") | "$0/month"; price history "30+ Years"; limits of 50 requests/hour, 1,000/day and 500 unique symbols/month. Fields are raw `open/high/low/close/volume`, `adjOpen…adjClose`, `adjVolume`, `divCash` and `splitFactor`, adjusted by "the CRSP methodology". "Most US Equity prices are available at 5:30 PM EST, however exchanges may send corrections until 8 PM EST". A token is required (a data key, allowed by DEC-028) | **Storage conflict.** Terms §1.6(a) for Starter: "You may process Tiingo Data only transiently in volatile memory or in a temporary, non-persistent cache … only to complete the calculation"; "You must permanently remove the Tiingo Data from that memory or cache immediately after the calculation". That contradicts the source's immutable raw store and reproducible snapshots (v10 `10-DATA.md` "Canonical storage layout" and steps 2 and 8; reinstated L-010 item 3). The licence is "Internal Use Only", meaning "your own personal use" | **Unsuitable** for an approved dataset on £0. Paid plans are Excluded (£0) |
| Alpha Vantage ([documentation](https://www.alphavantage.co/documentation/)) | `TIME_SERIES_DAILY`: "The "compact" outputsize is available to both free and premium API keys"; "The "full" outputsize is available to premium keys"; compact returns the latest 100 data points. `TIME_SERIES_DAILY_ADJUSTED` "is a premium API function" | 100 daily points is too short for chronological training, validation and holdout (`10-DATA.md` step 10). The terms PDF could not be extracted | **Unsuitable** (history length) |
| Twelve Data Basic ([pricing](https://twelvedata.com/pricing), [terms](https://twelvedata.com/terms)) | "800 a day" requests; described as "For testing and side projects"; "Internal non-display usage" included. The terms forbid using "Free Tier data for commercial purposes" and storing data "beyond permitted timeframes specified in the Documentation" | History depth and the permitted storage timeframe are not stated | Unresolved (F-1a) |
| Stooq, Yahoo (SR-10, SR-11) | No change | — | Unresolved |
| IEX HIST (SR-06) | No change; the terms page still returns 404 | — | Unresolved (F-1b) |

**Consequence:** the condition in DEC-029 is met for planning. The daily-first baseline runs on crypto spot first; ETFs stay in scope, and a licence-clear ETF daily source is a **G01 dependency** recorded in the data-access decision. F-1a and F-1b remain open routes. Neither DEC-028 nor DEC-029 permits a paid plan or a broker account.

## F-2 — ETF corporate actions

No free source was found that both carries split and dividend events and permits retention. Tiingo carries `divCash` and `splitFactor`, but its storage terms apply (F-1). The source requires raw and adjusted series kept separately, with corporate actions tracked in the ledger (L-010 item 4; L-025). **Status: Unresolved.** It is deferred together with the ETF daily source under DEC-029.

## F-3 — context sources

| Source | Documented facts | Terms | Status |
| --- | --- | --- | --- |
| Federal Reserve FOMC calendar ([page](https://www.federalreserve.gov/monetarypolicy/fomccalendars.htm)) | 2026 meetings: Jan 27–28, Mar 17–18\*, Apr 28–29, Jun 16–17\*, Jul 28–29, Sep 15–16\*, Oct 27–28, Dec 8–9\*. "The minutes of regularly scheduled meetings are released three weeks after the date of the policy decision". "Each meeting date is tentative until confirmed" | US government publication; no restriction found | Documented. Statement release *times* are not on the page, so event time must be captured at publication (REQ-004) |
| BLS CPI schedule ([page](https://www.bls.gov/schedule/news_release/cpi.htm)) | Releases at "08:30 AM"; only Oct–Dec 2026 reference months are listed (Nov 10 and Dec 10, 2026; Jan 13, 2027); "updated as needed … usually at least a week before" | US government publication | Documented. The schedule horizon is short, so re-read it before each release window |
| CFTC Commitments of Traders ([schedule](https://www.cftc.gov/MarketReports/CommitmentsofTraders/ReleaseSchedule/index.htm)) | "released at 3:30 p.m. Eastern time", "usually released on Friday", "usually includes data from the previous Tuesday"; "Federal holidays may delay release by one or two days" | US government publication | Documented. `available_at` is the Friday release, not the Tuesday as-of date |
| NYSE hours and calendars ([page](https://www.nyse.com/markets/hours-calendars)) | 2026 and 2027 holidays and early closes (2026: Nov 27 and Dec 24 at 1:00 p.m. ET) | The page links a "Terms of Use" that was not read | Conditional (terms unread) |
| GDELT ([about](https://www.gdeltproject.org/about.html)) | "available for unlimited and unrestricted use for any academic, commercial, or governmental use"; "any use or redistribution of the data must include a citation to the GDELT Project"; the about page says "daily updates" | Free; citation required | Documented. The update frequency of GDELT 2.0 (register 25 says ~15 min) was not confirmed on this page |
| Coin Metrics Community ([docs](https://gitbook-docs.coinmetrics.io/packages/coin-metrics-community-data)) | "API key is not required when accessing community endpoints"; 10 requests per 6-second window per IP; Atlas Community has "limited assets and 30 days of history" | "Available to the community under the Creative Commons license" (linked: CC BY-NC 4.0) | Documented for personal, non-commercial research. NC licence |
| CME daily volume and open interest ([page](https://cmegroup.com/market-data/volume-open-interest.html), via search extract) | Reports are "available free of charge". The daily report is "preliminary"; official figures appear in the Daily Bulletin the following morning | Terms not found | Conditional (indirect; terms not found). Context only |
| Deribit | The docs landing page does not state public-method authentication or terms | — | Unresolved |
| iShares holdings | The landing page does not state holdings downloads or reuse terms | — | Unresolved (deferred with ETFs) |
| Binance futures | Same as F-5 | — | Unresolved |
| Public blockchain RPC and indexers | Not checked; chain-specific | — | Unresolved |
| FRED third-party series (SR-13) | No change: permission is needed "beyond personal use" | — | Conditional |

## F-4 — crypto venue terms

| Venue | Evidence | Consequence | Status |
| --- | --- | --- | --- |
| Kraken (SR-02, SR-05) | [API docs (legacy page)](https://docs-legacy.kraken.com/api/docs/guides/global-intro/): "Use of the Kraken APIs is subject to the Kraken Terms & Conditions and Privacy Notice". "You must seek our prior permission for certain uses of the Kraken API's", which "includes … any non-personal commercial use of data from publicly accessible endpoints, such as market data"; requests go to "marketdata@kraken.com". The current docs page did not show this text on a direct fetch, so the legacy page is the source | Personal, non-commercial research use of public market data needs no prior permission. Retention is not addressed. Any later commercial use needs permission, which would be a user action | **Documented** for personal research (SR-02 and SR-05 move from Conditional). Retention and the 30-min candle inconsistency stay open (F-4a) |
| Coinbase (SR-01) | [Market Data Terms of Use](https://www.coinbase.com/legal/market_data). The page returned HTTP 403 to automated fetch, so this evidence is **indirect**, from search-engine extracts of the official page. Use is "exclusively for you or your entity's personal or research purposes", and Market Data "may not be used to build an application intended for use by end users beyond you or your officers and employees". The restrictions list includes a ban, "absent prior express written consent", on using Market Data to develop or train models; the extract is cut off at "fine-" | GLADIATOR trains and validates forecasting models (CMP-13, v10 `11-QLIB-AND-TRAINING.md`). Coinbase data therefore appears unusable for model research without Coinbase's written consent. Seeking that consent would be outward contact, so it is a user action, not a coordinator one | **Unsuitable for model research** pending the full text and consent. Observation-only use (for example, cross-venue checks) is unresolved |
| Coinbase message timestamps | The channels page does not include payload examples; the AsyncAPI spec was not read | — | Unresolved (F-4b) |

## F-5 — Binance

No new primary evidence. Binance stays **Unresolved and is not relied on**.

## Resulting crypto-first source picture (planning only)

| Need | Leading candidate | Remaining condition |
| --- | --- | --- |
| Crypto daily bars (baseline) | Kraken OHLCVT archive and REST (SR-05) | Retention not addressed in the terms (F-4a) |
| Crypto live depth and trades | Kraken WebSocket v2 (SR-02) | F-4a; forward capture only |
| Cross-venue comparison | None usable for model research | Coinbase consent (a user action), or Binance (F-5) |
| Macro and event context | FRED (Conditional), FOMC, BLS, CFTC, GDELT, Coin Metrics | As listed |

The data-access decision (P01 task 7) uses this picture. It is not a selection.
