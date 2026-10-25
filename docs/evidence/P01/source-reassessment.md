# P01 crypto source reassessment: Kraken and Binance Vision

[Task](../../tasks/TASK-P01-007.md) · [Source registry](source-registry.md) · [Round 1](source-followups.md) · [Round 2](source-followups-2.md) · [Data-access decision](data-access-decision.md) · [P01 phase](../../phases/01-research-and-data-access/README.md)

**Status: research evidence for G01, 2026-10-25.** This file selects no source. It authorises no account, key registration, vendor contact, download, capture, spending or trading.

**Why this file exists.** On 2026-10-25 the user decided not to wait for a reply from Kraken and to keep the draft email unsent ([DEC-033](../../decisions/README.md)). Kraken is to be reassessed from its published documentation and terms, identifying any concrete restriction. If those remain unsuitable or ambiguous, another public source is to be evaluated, with Binance Vision named as the alternative. Crypto-first (DEC-029) remains the baseline plan.

Where this file changes a status recorded in the registry, the map, or rounds 1 and 2, this file takes precedence. The [status changes](#status-changes) table lists every change. The method is unchanged: current primary text was read on 2026-10-25 and is quoted. Statuses use the registry vocabulary: Documented, Conditional, Unresolved and Excluded.

## Summary

| Source | Outcome | Status |
| --- | --- | --- |
| Kraken public API and OHLCVT archive (SR-02, SR-05) | Public access with no key is confirmed. For personal, non-commercial use (DEC-030), **no concrete restriction was found**. Two ambiguities remain: the scope of ToS §9 (bots and scripts) over the documented API, and the silence of the terms on retention | **Conditional** (unchanged). Ambiguous, so Binance Vision was evaluated |
| Binance Vision public data archive (SR-04) | The dataset terms (v1.0, "Last Updated: August 26, 2026") permit "algorithmic historical backtesting for purely personal non-production research" under CC BY-NC-SA 4.0. No storage limit appears, and downloaded datasets keep the terms in force when they were downloaded | **Documented** for DEC-030 personal, non-production research. Open before selection: eligibility under the incorporated Binance Terms of Use (F-5b), delisted symbols (F-5c), and the quote-currency effect on W-1 (F-5d) |

## 1. Kraken: reassessment from the published documentation and terms

| Question | Published text | Concrete restriction for DEC-030 use? |
| --- | --- | --- |
| Is market data openly accessible? | Current [API overview](https://docs.kraken.com/api/docs/guides/global-intro): "Public endpoints — no API key needed". REST [`OHLC`](https://docs.kraken.com/api/docs/rest-api/get-ohlc-data), [`Trades`](https://docs.kraken.com/api/docs/rest-api/get-recent-trades) and [`SystemStatus`](https://docs.kraken.com/api/docs/rest-api/get-system-status) set `security: []` (round 2) | **None.** Access needs no account and no key |
| Is permission needed? | [Legacy API page](https://docs-legacy.kraken.com/api/docs/guides/global-intro/) (round 1): prior permission "includes … any non-personal commercial use of data from publicly accessible endpoints, such as market data". The current overview has no terms text and no terms link | **None.** DEC-030 use is personal and non-commercial, so it falls outside the clause. This is a reading, not a grant (round 1) |
| What may the data be used for? | [Global terms](https://www.kraken.com/legal/global-terms) §8 (round 1): Our Content may be used "only for your own benefit" | **None** for personal research. Redistribution would need permission; DEC-030 involves none |
| May it be collected automatically? | §9 (round 1) forbids "any web scraping, web harvesting, or data extraction methods to extract any data from Our Content", and forbids users to "create, use, operate, or employ any bots, robots, parsers, spiders, scripts, programs, routines" | **Ambiguous.** Read literally, §9 forbids any script, including a client of Kraken's own documented API. Read in context, it targets scraping of the website, since the API exists for programmatic use. No published text settles which reading applies |
| May the data be kept? | Not addressed in the API docs, the global terms read, or the [archive article](https://support.kraken.com/hc/en-us/articles/360047124832-Downloadable-historical-OHLCVT-Open-High-Low-Close-Volume-Trades-data) | **None stated, but no grant.** S-2 (retention) cannot be marked met from silence |
| Does the archive carry terms? | The archive article has no permitted-use text (round 2), only "These materials are for general information purposes only…" | **None stated.** The API clause covers it only by inference (round 1) |

**Result.** For personal, non-commercial research, the published Kraken documentation and terms contain **no concrete restriction**. They are **ambiguous** on two points: §9's scope over documented API use, and retention. SR-02 and SR-05 stay **Conditional** (F-4a). Under DEC-033, that ambiguity is the trigger for evaluating another public source, so the ambiguity is recorded rather than awaited. Kraken stays the only candidate for live depth and trades and for venue status (W-4; round 2), since Binance Vision holds no live data and no order book.

## 2. Binance Vision: evaluation

Sources: [dataset terms](https://github.com/binance/binance-public-data/blob/master/TERMS_AND_CONDITIONS.md) ("Last Updated: August 26, 2026", version 1.0) and the [README](https://github.com/binance/binance-public-data/blob/master/README.md), both read on 2026-10-25. Quotations are short excerpts; the paraphrases are marked as such.

### Terms

| Topic | Text | Reading |
| --- | --- | --- |
| Licence | §3.1: "Datasets are provided to you under the Creative Commons Attribution-NonCommercial-ShareAlike 4.0". §3.3 (paraphrase): where the licence and the terms both impose duties, "the stricter obligation shall apply" | Non-commercial; attribution and share-alike apply to redistributed derivatives (§4.5). DEC-030 involves no redistribution |
| Permitted use | §4.1 lists academic research, non-monetized open educational projects, non-commercial open-source data-science evaluations and "algorithmic historical backtesting for purely personal non-production research" | GLADIATOR's research and paper phases are personal and non-production (DEC-030; the current scope excludes live order routing). This fits the fourth category. That is the coordinator's reading |
| Prohibited use | §4.2: "You shall not use the Datasets for live proprietary trading execution", nor for signal distribution to third parties for compensation (paraphrase). §4.3: no "license, sub-license, sell, rent, lease, host, or commercially exploit the Datasets". §4.4: no integration "into commercial financial products". §3.4: "Commercial licensing is strictly excluded under this agreement" | Live trading is outside the current scope (CLAUDE.md). **Any future live use, or any commercial use, would breach these terms** and needs a separate licence. That is a constraint to record for P07 and beyond |
| Derived outputs | §2.4: "Use of any data derived from, calculated with, or extracted from the Datasets ... is strictly governed by these Vision Dataset Terms", including "charts, models, and derivative analytical indicators" | Models trained on these datasets inherit the same non-commercial, non-production limits |
| Model training | The words "train" and "machine learning" do not appear | No explicit restriction. Models are covered by §2.4 as derived outputs |
| Retention | The words "store", "retain" and "delete" do not appear. §1.4 (paraphrase): amendments apply only to Datasets released after they take effect, and previously downloaded Datasets stay under the terms in force when downloaded | **No storage limit, and downloaded data keeps its terms.** This supports the immutable raw store (`10-DATA.md:6`; L-010 item 3). The terms also incorporate the CC BY-NC-SA 4.0 licence, whose grant is "irrevocable" ([legal code](https://creativecommons.org/licenses/by-nc-sa/4.0/legalcode.en) §2(a)(1)), although rights "terminate automatically" on non-compliance (§6(a)) |
| Eligibility | §2.3: Binance grants "any individual or legal entity" access free of charge, subject to the terms. No section lists restricted persons or jurisdictions. §12 incorporates the Binance Terms of Use clauses on "Notice of claim - Negotiation, then Arbitration", governing law and class-action waivers | The dataset terms contain no UK restriction. Whether the incorporated Terms of Use carry an eligibility condition was not read (**F-5b**). The FCA measures on Binance Markets Ltd (registry SR-03) concern regulated activity; downloading a public research archive is not obviously one, but that is not established |
| Changes | §1.4: "Binance may amend these Vision Dataset Terms in its sole and absolute discretion at any time" | Each manifest records the terms version in force at download (provenance fields) |
| Warranty | §10.3: "Binance does not warrant that the Datasets will be error-free, uninterrupted, complete, timely" | Validation (Q-1 to Q-7) is still required |

**Registry note.** SR-04 quoted an earlier wording ("Permitted non-commercial uses are limited to academic research, non-monetized open educational projects"). The current version adds personal non-production backtesting, which is why F-5 can now be narrowed for SR-04.

### Data

| Topic | README text | Effect on the open questions |
| --- | --- | --- |
| Coverage | Spot `klines` at intervals including `1d`, `trades` and `aggTrades`, as daily and monthly files at `data.binance.vision` | Daily bars for H-01 to H-06; trades for H-OF3 history. No order book |
| Timestamp semantics | Kline columns: "Open time, Open, High, Low, Close, Volume, Close time, Quote asset volume, Number of trades, Taker buy base asset volume, Taker buy quote asset volume, Ignore" | **Both bar start and bar end are explicit.** This is the question that stays open for Kraken (F-4i). Taker-buy volume also gives a signed-flow proxy at bar level |
| Units | "The timestamp for SPOT Data from January 1st 2025 onwards will be in microseconds" | The unit changes on 2025-01-01. Ingestion must handle both units (a P02 validation rule) |
| Publication time | "new `daily` data becoming available the next day and new `monthly` data at the first monday of the month" | `available_at` for history (T-2a) can be the daily file's publication, about one day after bar close, instead of a quarterly archive. Daily evaluation is then usable without relying on REST |
| Integrity | "Each zip file has a `.CHECKSUM` file together in the same folder to verify data integrity" | SHA-256 per file, as the provenance fields require |
| Corrections | "Archived files may be updated at a later date as a result of recently discovered issues", with two listed updates (2022-08-08 klines; 2022-04-21 aggTrades) | Revisions happen and are announced. Each is a correction with its own `available_at` (T-2a; experiment 9, 27:89); keep both versions |
| Delisted symbols | Not stated | Open (**F-5c**); the sample plan checks it |
| Quote currency | Not addressed in the README. Binance spot pairs are mostly quoted in USDT, not USD | W-1 ("Kraken spot pairs quoted in USD") would need revising for this source (**F-5d**), a proposed value for the G01 reviewer |

**Result.** SR-04 is **Documented** for DEC-030 personal, non-production research. Against the S-criteria:
- S-1: the rights are documented, but no `source_approval` record exists yet.
- S-2: retention is not restricted, and downloaded data keeps its terms.
- S-3: free (§2.3).
- S-4b: timestamps are explicit.
- S-5: likely met; delisted symbols are open.
- S-6: checksums and announced corrections.

Selection still waits on F-5b, F-5c and F-5d, and on G01.

## 3. Comparison for the crypto-first daily baseline

| Criterion | Kraken SR-05 archive | Binance Vision SR-04 |
| --- | --- | --- |
| Use rights for DEC-030 | No concrete restriction; §9 and retention ambiguous | Explicitly permitted (§4.1) |
| Retention | Not addressed | No limit; downloaded data keeps its terms (§1.4) |
| Bar timestamp semantics | Undocumented (F-4i) | Open and close time both present |
| Publication lag | Quarterly incremental ZIPs | Next day (daily files) |
| Revisions | Not documented | Documented and announced |
| Quote currency | USD pairs (W-1 as written) | Mostly USDT (F-5d) |
| Live data, order book, venue status | Yes (SR-02; round 2) | None in the archive |

**Coordinator's proposal for the G01 reviewer (not a selection).** Use Binance Vision as the proposed primary source for crypto daily-bar history, subject to F-5b, F-5c and F-5d. Keep the Kraken archive as a Conditional cross-venue check. Keep Kraken SR-02 as the only candidate for live capture and venue status, if a later authorisation permits capture. The [data-access decision](data-access-decision.md) is updated to match.

## New follow-up items

| ID | Item | Closure evidence |
| --- | --- | --- |
| F-5b | Eligibility conditions in the Binance Terms of Use incorporated by §12, for a UK individual using the public archive | Primary text of the Terms of Use |
| F-5c | Whether Binance Vision keeps the files of delisted symbols | Sample plan, or the README |
| F-5d | The W-1 quote-currency rule for a USDT-quoted source, including how the USDT/USD basis is treated | G01 reviewer decision on the proposed value |

## Status changes

| Row | Before | After | Reason |
| --- | --- | --- | --- |
| SR-04 Binance Vision | Unresolved (F-5) | **Documented** for DEC-030 personal, non-production research; selection waits on F-5b to F-5d | Current dataset terms §4.1 |
| SR-02, SR-05 Kraken | Conditional (F-4a) | Conditional; no concrete restriction found for DEC-030 use; §9 scope and retention ambiguous | Published-text reassessment (DEC-033) |
| SR-03 Binance live WebSocket | Unresolved (F-5) | Unresolved (unchanged); not evaluated here | Vision terms cover the archive only |
| DEC-032 dependency (Kraken reply) | Pending | **Removed** by DEC-033; the draft stays unsent | User decision |
| Map: daily bars; intraday bars; bar `available_at` | Conditional (SR-05, SR-04) | SR-04 Documented for DEC-030 use (next-day publication); SR-05 Conditional | This file |
| Map: historical trades | Observed; SR-04 terms unresolved; Kraken REST narrowed (F-4d) | SR-04 `trades` and `aggTrades` Documented for DEC-030 use | This file |
