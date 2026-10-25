# P01 crypto source reassessment: Kraken and Binance Vision

[Task](../../tasks/TASK-P01-007.md) · [Source registry](source-registry.md) · [Round 1](source-followups.md) · [Round 2](source-followups-2.md) · [Data-access decision](data-access-decision.md) · [Research agenda](research-agenda.md) · [P01 phase](../../phases/01-research-and-data-access/README.md)

**Status: research evidence for G01, 2026-10-25.** This file selects no source. It authorises no account, key registration, vendor contact, download, capture, spending or trading.

**Why this file exists.** On 2026-10-25 the user decided not to wait for a reply from Kraken, and to keep the draft email unsent ([DEC-033](../../decisions/README.md)). The user's direction:
- reassess Kraken from its published documentation and terms, identifying any concrete restriction;
- if those remain unsuitable or ambiguous, evaluate another public source. The user named Binance Vision as "a strong alternative", and noted that "broader eligibility and retention conditions still need checking before selection";
- crypto-first (DEC-029) remains the baseline plan.

> **Follow-up, 2026-10-25:** [binance-general-terms.md](binance-general-terms.md) (TASK-P01-008) reads the Binance general terms and narrows F-5b to F-5b′ and F-7b. Where it changes a status recorded here, it takes precedence.

**Precedence.** Where this file changes a status recorded in the registry, the map, rounds 1 and 2, or the [research agenda](research-agenda.md)'s data notes, this file takes precedence. The [status changes](#status-changes) table lists every change.

**Method.** Unchanged: quote the primary text. Statuses use the registry vocabulary: Documented, Conditional, Unresolved and Excluded.
- **Read on 2026-10-25:** the Kraken API overview; the Binance Vision dataset terms and README; the Creative Commons legal code; and an attempt at the Binance Terms of Use.
- **From round 1 (read 2026-10-24):** the Kraken §8 and §9 text ("Last Updated: 19 October, 2026") and the legacy API page.
- **Kraken terms page:** no dedicated Kraken API or market-data terms page was found. The current overview carries no terms text and no terms link.

## Summary

| Source | Outcome | Status |
| --- | --- | --- |
| Kraken public API and OHLCVT archive (SR-02, SR-05) | Public access with no key is confirmed. For personal, non-commercial use (DEC-030), **no concrete restriction was found**. Two ambiguities remain: §9 (bots and scripts), which the API page expressly extends to API use, and retention, on which the terms are silent | **Conditional** (unchanged). Ambiguous, so Binance Vision was evaluated |
| Binance Vision public data archive (SR-04) | The dataset terms (v1.0, "Last Updated: August 26, 2026") permit "algorithmic historical backtesting for purely personal non-production research" under CC BY-NC-SA 4.0. They place no storage limit, and downloaded datasets keep the terms in force at download. The broader Binance terms could not be read | **Conditional** (was Unresolved): use is explicitly permitted, but eligibility and retention under the broader Binance terms are open (F-5b) |

## 1. Kraken: reassessment from the published documentation and terms

| Question | Published text | Concrete restriction for DEC-030 use? |
| --- | --- | --- |
| Is market data openly accessible? | Current [API overview](https://docs.kraken.com/api/docs/guides/global-intro) (2026-10-25): "Public endpoints — no API key needed". REST [`OHLC`](https://docs.kraken.com/api/docs/rest-api/get-ohlc-data), [`Trades`](https://docs.kraken.com/api/docs/rest-api/get-recent-trades) and [`SystemStatus`](https://docs.kraken.com/api/docs/rest-api/get-system-status) set `security: []` (round 2) | **None.** Access needs no account and no key |
| Is permission needed? | [Legacy API page](https://docs-legacy.kraken.com/api/docs/guides/global-intro/) (round 1): prior permission "includes … any non-personal commercial use of data from publicly accessible endpoints, such as market data" | **None.** DEC-030 use is personal and non-commercial, so it falls outside the clause. That is a reading, not a grant (round 1) |
| What may the data be used for? | [Global terms](https://www.kraken.com/legal/global-terms) §8 (round 1): Our Content may be used "only for your own benefit" | **None** for personal research. Redistribution would need permission; DEC-030 involves none |
| May it be collected automatically? | The legacy API page (round 1): "Use of the Kraken APIs is subject to the Kraken Terms & Conditions and Privacy Notice". §9 (round 1) forbids "any web scraping, web harvesting, or data extraction methods to extract any data from Our Content", and forbids users to "create, use, operate, or employ any bots, robots, parsers, spiders, scripts, programs, routines" | **Ambiguous.** The API page expressly applies the terms, §9 included, to API use, so a literal reading forbids any script, even a client of Kraken's own documented API. Against that, the API exists for programmatic use, and §9's wording targets extraction from "Our Content". No published text settles which reading applies |
| May the data be kept? | Not addressed in the API docs, the global terms read, or the [archive article](https://support.kraken.com/hc/en-us/articles/360047124832-Downloadable-historical-OHLCVT-Open-High-Low-Close-Volume-Trades-data) | **None stated, but no grant.** S-2 (retention) cannot be marked met from silence |
| Does the archive carry terms? | The archive article has no permitted-use text (round 2), only "These materials are for general information purposes only…" | **None stated.** The API clause covers it only by inference (round 1) |

**Result.** For personal, non-commercial research, the published Kraken documentation and terms contain **no concrete restriction**. They are **ambiguous** on two points: §9's scope over documented API use, and retention. SR-02 and SR-05 stay **Conditional** (F-4a).

Under DEC-033, that ambiguity is recorded rather than waited on, and it triggers the evaluation of another public source. Kraken stays the only candidate for live depth and trades, and for venue status (W-4; round 2), because Binance Vision has no live data and no order book.

## 2. Binance Vision: evaluation

Sources, read on 2026-10-25:
- the [dataset terms](https://github.com/binance/binance-public-data/blob/master/TERMS_AND_CONDITIONS.md) ("Last Updated: August 26, 2026", version 1.0);
- the [README](https://github.com/binance/binance-public-data/blob/master/README.md);
- the [CC BY-NC-SA 4.0 legal code](https://creativecommons.org/licenses/by-nc-sa/4.0/legalcode.en).

Quotations are short excerpts; paraphrases are marked.

### Terms

| Topic | Text | Reading |
| --- | --- | --- |
| Licence | §3.1: "Datasets are provided to you under the Creative Commons Attribution-NonCommercial-ShareAlike 4.0". §3.3 (paraphrase): where the licence and the terms both impose duties, "the stricter obligation shall apply". The CC legal code, §2(a)(1), grants "a worldwide, royalty-free, non-sublicensable, non-exclusive, irrevocable license" to "reproduce and Share the Licensed Material, in whole or in part, for NonCommercial purposes only"; rights "terminate automatically" on non-compliance (§6(a)) | Non-commercial. Attribution and share-alike apply to redistributed derivatives (§4.5); DEC-030 involves no redistribution |
| Permitted use | §4.1 lists academic research, non-monetized open educational projects, non-commercial open-source data-science evaluations, and "algorithmic historical backtesting for purely personal non-production research" | GLADIATOR's research phases are personal (DEC-030) and run no live order routing (current scope), so they fit the fourth category. Whether **paper simulation** counts as "non-production" is the coordinator's reading, for the G01 reviewer |
| Prohibited use | §4.2: "You shall not use the Datasets for live proprietary trading execution", nor for signal distribution to third parties for compensation (paraphrase). §4.3: no "license, sub-license, sell, rent, lease, host, or commercially exploit the Datasets". §4.4: no integration "into commercial financial products". §3.4: "Commercial licensing is strictly excluded under this agreement"; commercial use needs a separate written enterprise licence (paraphrase) | Live trading is outside the current scope (CLAUDE.md). See derived outputs |
| Derived outputs | §2.4: "Use of any data derived from, calculated with, or extracted from the Datasets ... is strictly governed by these Vision Dataset Terms", including "charts, models, and derivative analytical indicators" | **Models trained on SR-04 inherit its limits.** With §4.2, any future live use of such a model would breach these terms unless a separate licence is obtained, and no page read says whether one is offered to individuals. Kraken's terms (above) contain no equivalent clause on derived models |
| Model training | The words "train" and "machine learning" do not appear | No separate restriction; models are covered by §2.4 |
| Retention | §1.4 (paraphrase): amendments apply only to Datasets released after they take effect, and previously downloaded Datasets stay under the terms in force when downloaded | **The dataset terms do not restrict retention.** The basis is the CC grant to "reproduce" (§2(a)(1)), which is irrevocable while its conditions are met, together with §1.4, not the absence of any wording. Retention under the broader Binance terms is open (**F-5b**) |
| Eligibility | §2.3: Binance grants "any individual or legal entity" access free of charge, subject to the terms. No section lists restricted persons or jurisdictions. §12 incorporates only the Binance Terms of Use clauses on "Notice of claim - Negotiation, then Arbitration", the agreement to arbitrate, governing law, and class-action waivers | The dataset terms carry no UK restriction. §12 does **not** import eligibility conditions. The open question is whether Binance's general or site-wide terms also govern a UK individual using `data.binance.vision`. [binance.com/en/terms](https://www.binance.com/en/terms) returned no readable terms text to automated fetch on 2026-10-25 (**F-5b**). The FCA measures on Binance Markets Ltd (registry SR-03) concern regulated activity; whether downloading a public research archive engages them is not established |
| Changes | §1.4: "Binance may amend these Vision Dataset Terms in its sole and absolute discretion at any time" | Each manifest records the terms version in force at download (provenance fields) |
| Warranty | §10.3: "Binance does not warrant that the Datasets will be error-free, uninterrupted, complete, timely" | Validation (Q-1 to Q-7) is still required |

**Registry note.** SR-04, read on 2026-10-24, quoted part of §4.1: "Permitted non-commercial uses are limited to academic research, non-monetized open educational projects". The version read on 2026-10-25 is the same v1.0 (last updated 2026-08-26). Its full §4.1 list also includes personal non-production backtesting, which the registry extract did not show. No amendment is implied.

### Data

| Topic | README text | Effect on the open questions |
| --- | --- | --- |
| Coverage | Spot `klines` at intervals including `1d`, plus `trades` and `aggTrades`, as daily and monthly files at `data.binance.vision` | Daily bars for H-01 to H-06; trades for H-OF3 history. No order book |
| Trade aggressor | `trades` columns: "trade Id", "price", "qty", "quoteQty", "time", "isBuyerMaker", "isBestMatch". `aggTrades` include "Was the buyer the maker" | The aggressor side is derivable, as H-OF3 needs |
| Bar timestamps | Kline columns: "Open time, Open, High, Low, Close, Volume, Close time, Quote asset volume, Number of trades, Taker buy base asset volume, Taker buy quote asset volume, Ignore" | **Bar start and bar end are both explicit.** For Kraken this is still open (F-4i). The taker-buy volume also gives a signed-flow proxy at bar level |
| Units | "The timestamp for SPOT Data from January 1st 2025 onwards will be in microseconds" | The unit changes on 2025-01-01, so ingestion must handle both units (a P02 validation rule) |
| Publication time | "new `daily` data becoming available the next day and new `monthly` data at the first monday of the month" | **For historical backtests,** `available_at` (T-2a) can be the daily file's publication, about one day after bar close, instead of a quarterly archive. Decision-time bars for **paper simulation** still need a live source; see section 3 |
| Integrity | "Each zip file has a `.CHECKSUM` file together in the same folder to verify data integrity" | SHA-256 per file (S-4b; provenance fields) |
| Corrections | "Archived files may be updated at a later date as a result of recently discovered issues", with two listed updates (2022-08-08 klines; 2022-04-21 aggTrades) | Revisions happen and are announced. Each is a correction with its own `available_at` (T-2a; experiment 9, 27:89), and both versions are kept |
| Delisted symbols | Not stated | Open (**F-5c**); the sample plan checks it |
| Quote currency | Not addressed in the README. Binance spot pairs are mostly quoted in USDT, not USD | W-1 ("Kraken spot pairs quoted in USD") would need revising for this source (**F-5d**) |
| Venue status | Nothing in the archive | **No venue-status source for Binance**, historical or forward, since SR-03 is Unresolved. Kraken's status cannot gate Binance bars, because status is venue-local (S-6; `10-DATA.md:40`) (**F-7b**) |

**Result.** SR-04 is **Conditional**: §4.1 explicitly permits DEC-030 use, but F-5b is open. Against the S-criteria:
- **S-1:** use is permitted by §4.1; eligibility under the broader terms is open (F-5b); no `source_approval` record exists yet.
- **S-2:** the dataset terms do not restrict retention; the broader terms are open (F-5b).
- **S-3:** free (§2.3).
- **S-4b:** timestamps are explicit, with checksums per file.
- **S-5:** likely met; delisted symbols are open (F-5c).
- **S-6:** venue-local (Binance only), stated explicitly.

Before selection: F-5b, F-5c, F-5d, F-7b and F-8 (below), and G01.

## 3. Comparison for the crypto-first daily baseline

| Criterion | Kraken SR-05 archive | Binance Vision SR-04 |
| --- | --- | --- |
| Use rights for DEC-030 | No concrete restriction; §9 and retention ambiguous | Explicitly permitted (§4.1); broader terms open (F-5b) |
| Retention | Not addressed | Not restricted by the dataset terms (CC §2(a)(1); §1.4); broader terms open |
| Use of derived models beyond research and paper | No clause found | **Restricted:** §2.4 with §4.2 and §3.4; live use needs a separate licence |
| Bar timestamp semantics | Undocumented (F-4i) | Open and close time both present |
| Publication lag | Quarterly incremental ZIPs | Next day (daily files) |
| Revisions | Not documented | Documented and announced |
| Quote currency | USD pairs (W-1 as written) | Mostly USDT (F-5d) |
| Venue status | Forward only (round 2; F-7) | None (F-7b) |
| Live data and order book | Yes (SR-02) | None in the archive; Binance live Unresolved (SR-03) |

**Design consequence: different venues for history and live (F-8).** With Binance Vision for history, models would be trained on Binance USDT bars, while paper-simulation inputs would come from Kraken USD (SR-02 or REST), because Binance live is Unresolved. The baseline rule BB already requires the same venue for each hypothesis ([research agenda](research-agenda.md)). H-01 to H-06 and paper simulation have no equivalent rule yet. The G01 reviewer needs one of:
- train and serve on one venue (Kraken for both, accepting its ambiguities);
- a stated venue-transfer assumption with a USDT/USD basis treatment (tied to F-5d), validated on overlapping periods;
- Binance for historical research only, with paper simulation deferred or run on Kraken-trained models.

**Coordinator's proposal for the G01 reviewer (not a selection).** Consider Binance Vision as the primary source for crypto daily-bar **research history**, subject to F-5b, F-5c, F-5d, F-7b and F-8, weighing the derived-model restriction (§2.4, §4.2) against Kraken's ambiguity. Keep the Kraken archive as a Conditional cross-venue check. Keep Kraken SR-02 as the only candidate for live capture and venue status, if a later authorisation permits capture. The [data-access decision](data-access-decision.md) is updated to match.

## New follow-up items

| ID | Item | Closure evidence |
| --- | --- | --- |
| F-5b | **Narrowed to F-5b′** ([follow-up](binance-general-terms.md#f-5b-eligibility-automated-access-and-retention)). Eligibility and retention or use conditions in Binance's general or site-wide terms that may govern a UK individual using `data.binance.vision`. §12 of the dataset terms imports only the dispute, arbitration, governing-law and class-action clauses | Primary text of the Binance Terms of Use and of any terms for `data.binance.vision` |
| F-5c | Whether Binance Vision keeps the files of delisted symbols | Sample plan, or the README |
| F-5d | The W-1 quote-currency rule for a USDT-quoted source, including the USDT/USD basis | G01 reviewer decision on the proposed value |
| F-7b | **Narrowed** ([follow-up](binance-general-terms.md#f-7b-binance-venue-status)). Venue status for a Binance-history baseline: no historical or forward source | A documented Binance status history, or a reviewer-approved rule (see F-7) |
| F-8 | Venue consistency between training history and paper-simulation inputs | G01 reviewer decision (options above) |

## Status changes

| Row | Before | After | Reason |
| --- | --- | --- | --- |
| SR-04 Binance Vision | Unresolved (F-5) | **Conditional** (F-5b); §4.1 explicitly permits DEC-030 use | Full dataset terms §4.1, read 2026-10-25 |
| SR-02, SR-05 Kraken | Conditional (F-4a) | Conditional; no concrete restriction found for DEC-030 use; §9 scope and retention ambiguous | Published-text reassessment (DEC-033) |
| SR-03 Binance live WebSocket | Unresolved (F-5) | Unresolved (unchanged); not evaluated here | Vision terms cover the archive only |
| DEC-032 dependency (Kraken reply) | Pending | **Removed** by DEC-033; the draft stays unsent | User decision |
| Map: daily bars; intraday bars; bar `available_at` | Conditional (SR-05, SR-04) | Conditional (SR-04 F-5b; SR-05 F-4a). SR-04 has next-day publication | This file |
| Map: historical trades | SR-04 terms unresolved; Kraken REST narrowed (F-4d) | SR-04 `trades` and `aggTrades` Conditional (F-5b); Kraken REST narrowed (F-4d) | This file |
| Agenda: H-OF6 second venue | Binance Unresolved (F-5) | Historical trades: SR-04 Conditional, beside Kraken. Kraken has no documented full trade history (F-4d, narrowed), so the comparison uses Binance trades against Kraken bars only (SR-05, Conditional), subject to the agenda's clock and fee alignment. No live second venue | This file |
| Agenda: H-OF3 history | Kraken REST (F-4d) | SR-04 `trades` Conditional (F-5b), with the same-venue rule (BB) applied on Binance | This file |
