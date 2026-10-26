# P01 data-access decision (draft, pending G01)

[Task](../../tasks/TASK-P01-005.md) · [Source registry](source-registry.md) · [Follow-ups](source-followups.md) · [Follow-ups, round 2](source-followups-2.md) · [Reassessment](source-reassessment.md) · [Acceptance objectives](acceptance-objectives.md) · [Research agenda](research-agenda.md) · [P01 phase](../../phases/01-research-and-data-access/README.md)

**Status: draft proposal for the G01 reviewer, 2026-10-24; revised 2026-10-25 (TASK-P01-007). Decision: pending.**

This is the P01 deliverable "an approved data evaluation plan and access decision, including a representative sample plan and source-dependent acceptance criteria" (P01 README). It covers P01 tasks 4 and 7.
- **What it does:** proposes a source baseline and an evaluation plan for the G01 reviewer.
- **What it does not do:** it authorises no account, key registration, download, capture, spending or trading.
- **Why it is pending:** it awaits the G01 review and the open items below. It no longer waits for Kraken: under [DEC-033](../../decisions/README.md) (2026-10-25) no reply is awaited, the draft email stays unsent, and Kraken was reassessed from its published text, with Binance Vision evaluated as the alternative ([reassessment](source-reassessment.md)).

**No `source_approval` record (L-025) exists yet for any source.** Criterion S-1 requires one, so S-1 is incomplete for every row below, even where the rights are documented.

## Proposed source baseline

This table assesses each source against criteria S-1 to S-7 in the [acceptance-objective register](acceptance-objectives.md#5-source-evaluation-criteria-for-the-p01-task-7-source-baseline).

| Need | Proposed source | S-criteria status | Pending items |
| --- | --- | --- | --- |
| Crypto daily bars (history for H-01 to H-06) | **Binance Vision daily `klines` (SR-04)**, proposed primary ([reassessment](source-reassessment.md#3-comparison-for-the-crypto-first-daily-baseline)). **Kraken OHLCVT archive (SR-05)** as a cross-venue check | SR-04 **Conditional**. S-1: use permitted by §4.1; eligibility under the broader Binance terms open (F-5b); no `source_approval` record yet. S-2: not restricted by the dataset terms; broader terms open (F-5b). S-3 free. S-4b: open and close time explicit; checksums per file. S-5 likely met (delisted symbols open). S-6: venue-local, Binance only. Derived models may not be used live without a separate licence (§2.4, §4.2). SR-05: Conditional, as before (F-4a; F-4f; F-4i) | F-5b, F-5c (delisted symbols), F-5d (W-1 quote currency, USDT), F-7b (no Binance venue status), F-8 (history and paper on different venues); for SR-05: F-4a, F-4f, F-4g, F-4h, F-4i |
| Crypto live depth and trades (H-OF1, H-OF2, H-OF3, H-OF5) | **Kraken WebSocket v2 public `book` and `trade` (SR-02)**, only if a later authorisation permits capture | Passes S-3, S-4 and S-6. Open: S-1 (F-4a; no `source_approval` record) and S-2 (F-4a) | F-4a (ambiguous; no reply awaited, DEC-033); capture authorisation (P02 boundary) |
| Crypto historical trades (H-OF3 history) | **Binance Vision `trades` and `aggTrades` (SR-04)**; Kraken public REST trades as an alternative | SR-04 as for daily bars; the aggressor side comes from `isBuyerMaker`. Kraken REST narrowed in [round 2](source-followups-2.md#f-4--kraken-data-details): 1,000 trades per call; paging back to the first trade undocumented | F-5b, F-5c; the same-venue rule (BB) applies on Binance (Binance trades against Binance bars); F-4d for Kraken |
| ETF daily bars | **None proposed** | No candidate passes S-1, S-2 and S-5 | **F-1 closed negatively on 2026-10-25** ([round 2](source-followups-2.md#f-1--free-daily-etf-bars-closed-negatively)), so DEC-029 is triggered: the daily-first baseline runs on crypto spot first. ETFs stay in scope; an ETF daily source stays a G01 dependency |
| ETF corporate actions | **None proposed** | — | F-2, F-2a |
| ETF trading calendar | NYSE hours and calendars | Conditional: the terms are unread | ETF-only; deferred with ETFs |
| Context events (W-7) | FOMC calendar, BLS CPI schedule, CFTC COT, GDELT, FRED/ALFRED (data key; DEC-028), Coin Metrics Community | S-3 passes. S-1: rights are documented (FRED and Coin Metrics for DEC-030 use), but no `source_approval` record exists. **S-2 (retention) is open for all.** S-7 is documented for FOMC (minutes timing only; no statement time), BLS (08:30), CFTC (3:30 p.m. ET) and GDELT (15 minutes), and for FRED at date granularity with a proposed rule ([round 2](source-followups-2.md#context-sources--s-7-publication-timing)); open for Coin Metrics | Retention terms per source; S-7 for Coin Metrics; the FRED rule; `source_approval` records |
| Crypto venue status (`VenueStatus`) | **Kraken REST `SystemStatus` and WebSocket v2 `status`** (no key; [round 2](source-followups-2.md#venue-status--kraken)). Coinbase is out (DEC-031) | Passes S-3. Open: S-1 and S-2 (F-4a; no `source_approval` record). History comes only from forward capture | F-4a (ambiguous; no reply awaited, DEC-033); capture authorisation. **F-7:** missing venue status blocks new entries, so a historical backtest on the Kraken archive needs a reviewer-approved treatment. **F-7b:** Binance has no venue-status source at all, and Kraken's status cannot gate Binance bars (venue-local) |
| Per-order (L3) data (H-OF4) | **None.** Kraken `level3` needs an account token, which DEC-028 excludes | — | Recorded gap ([agenda](research-agenda.md#gaps-this-agenda-records-for-g01)) |
| Second venue (H-OF6) | **Historical only:** Binance Vision trades (SR-04) against Kraken bars (SR-05); Kraken has no documented full trade history (F-4d, narrowed). No live second venue: Coinbase is out (DEC-031), and Binance live (SR-03) is Unresolved (F-5) | SR-04 Conditional (F-5b); SR-05 Conditional (F-4a) | F-5b, F-4a, F-4d; the agenda's clock and fee alignment. The live part remains a recorded gap |
| NOII and issuer holdings (H-OF7) | **None.** NOII is paid, and issuer holdings are Unresolved (F-3) | — | Recorded gap |
| Derivatives, options and liquidations (H-OF8); on-chain RPC (H-OF9) | **Out of scope until their sources close** (W-7). Coin Metrics Community is the only partial on-chain input | — | F-3 |

**Coinbase items closed or moot under DEC-031:** F-4b (full terms text), F-4c (message timestamps) and F-4e (UK availability).

## Access requirements

| Source | Account | Key | Network action needed later | Cost |
| --- | --- | --- | --- | --- |
| Binance Vision SR-04 archive | None | None | Download daily or monthly files from `data.binance.vision` and verify each `.CHECKSUM` | £0 |
| Kraken SR-05 archive and REST | None: public endpoints need "no API key" (SR-02) | None | Download archive files and verify the published SHA-256. REST pulls only on explicit invocation (`09-CONNECTORS.md` "No hidden spend") | £0 |
| Kraken SR-02 WebSocket | None | None | Only under a later capture authorisation | £0 |
| FRED/ALFRED | Registration for an API key (a data key, allowed by DEC-028) | Data key | Key registration is a user action | £0 |
| FOMC, BLS, CFTC, GDELT, Coin Metrics | None | None | Public pages or files | £0 |

## Representative sample plan

Purpose: verifying the sources, not producing research results. The plan runs **only after both** of the following:
- G01 approval;
- the user's authorisation of downloads.

The Kraken reply is no longer a precondition (DEC-033).

**0. Binance Vision sample.** For the W-1 candidate symbols, download the `1d` klines for December 2024 and January 2025 (either side of the 2025-01-01 change to microseconds), plus one day of `trades`, each with its `.CHECKSUM` file. Record:
- checksum results;
- the unit change between the two months;
- whether delisted symbols have files (F-5c);
- open/close-time alignment;
- `isBuyerMaker` coverage;
- Q-1 and Q-2 results.

Then re-download one file listed as revised in the README and compare checksums, to confirm how revisions appear (T-2a).

**1. Kraken archive sample.**
- **Download:** the latest quarterly incremental ZIP, plus the full-history multi-part ZIP. The Kraken article says the complete dataset covers "each pair from its first trade on Kraken" (SR-05). Whether the download is a single all-pairs file or one file per pair is unverified. Whichever it is, only the W-1 candidate pairs are used.
- **Integrity:** verify every part against the published SHA-256.
- **Per pair, record:**
  - the first and last bar, and the row count;
  - the share of no-trade intervals (Q-2);
  - validation failures (Q-1);
  - whether delisted pairs appear (F-4g);
  - which interval files exist, including whether 30-minute candles are present (F-4f).
- **REST comparison:** compare one week of 1440-minute candles against REST bars for the same dates, to establish whether candles are stamped at bar start or bar end (F-4i). Record any value differences as F-4h.

**2. Kraken live sample.** This needs a separate capture authorisation. Capture one hour of `book` (depth 10) and `trade` for one pair, and record:
- checksum failures and resyncs (Q-5);
- latency percentiles (T-3);
- the logged NTP offset (T-5);
- storage size (R-5).

**3. Context sample.** For one FOMC meeting, one CPI release and one COT release, compare the observed publication time with the published schedule (S-7).

Results go into P02 `capture-validation-plan.md`. They are not research evidence.

## Provenance fields

Each source gets a manifest, drawn from reinstated L-010 item 2 and L-025 `source_approval`:
- **Source and terms:**
  - provider URL;
  - terms URL, and the date the terms were read;
  - access method;
  - allowed research or commercial use (DEC-030).
- **The `source_approval` record:**
  - licence reviewed;
  - intended use;
  - date;
  - allowed retention **and redistribution**;
  - coverage;
  - sample verification.
- **Data definition:**
  - raw and adjusted definitions;
  - universe coverage;
  - interval.
- **Retrieval:**
  - rate limit;
  - retrieval date;
  - SHA-256 checksum;
  - the raw licence or receipt stored with the raw bytes (`10-DATA.md` canonical storage layout).

Fields carried by each record:
- **Market records:** the `10-DATA.md` market schema (`10-DATA.md:9`) and the T-1 timestamps.
- **Context and document records:** `published_at`, `first_available_at`, `retrieved_at`, `source_url`, `content_hash` and `licence` (`10-DATA.md:9`).
- **Context observations:** an `ObservationEnvelope` with effective-time vintages (`10-DATA.md:40`).

## Retention and redistribution

| Source | Retention | Redistribution | Status |
| --- | --- | --- | --- |
| Binance Vision | Not restricted by the dataset terms (CC §2(a)(1); downloaded Datasets keep their terms, §1.4); broader Binance terms open (F-5b) | Derivative works only with attribution to Binance Vision and under CC BY-NC-SA 4.0 (§4.5); no hosting or commercial exploitation (§4.3) | Conditional (F-5b) |
| Kraken | Not addressed in the terms read | §8 "only for your own benefit" (the coordinator's reading; whether "Our Content" covers API data is open, F-4a) | **Ambiguous** ([reassessment](source-reassessment.md#1-kraken-reassessment-from-the-published-documentation-and-terms)); no reply awaited (DEC-033) |
| FOMC, BLS, CFTC | Not established | Not established | Open (S-2); US government publications |
| GDELT | Not established | Allowed, but "must include a citation to the GDELT Project" | Open (S-2) |
| FRED/ALFRED | Not established | Third-party series need permission "beyond personal use" | Open (S-2) |
| Coin Metrics | Not established | CC BY-NC 4.0: attribution, non-commercial use only | Open (S-2) |

Under DEC-030 nothing is redistributed, but each `source_approval` record still records the terms.

## Capture-quality criteria

These are items Q-1 to Q-7 and R-1 to R-5 in the [acceptance-objective register](acceptance-objectives.md), together with its proposed values for G01. This draft adds no thresholds.

## Draft request to Kraken (unsent; not awaited)

Under DEC-033 (2026-10-25) the user keeps this draft unsent, and no decision waits for it. It is kept for reference only.

> **To:** marketdata@kraken.com
> **Subject:** Permission check: personal, non-commercial research use of public market data
>
> I am building a private, non-commercial research project for my own use. It has no product, no clients and no redistribution. The project includes developing and testing forecasting models on the data and running paper simulations; there is no live trading. Please confirm:
> 1. **Recording public channels:** may I record the WebSocket v2 `book` and `trade` channels automatically and continuously, as documented, and call the public REST OHLC and trades endpoints, for this purpose? Does §9 of the Terms of Service (bots, scripts and data extraction from "Our Content") apply to this documented API use?
> 2. **Archive download:** may I download the historical OHLCVT archive from your support site for the same purpose?
> 3. **Local retention:** may I keep the raw data locally and unaltered, so that results can be reproduced?
> 4. **Current terms:** I found the prior-permission wording for "non-personal commercial use" on your legacy API page (docs-legacy.kraken.com). Which document currently governs API market-data use?
> 5. **Other conditions:** are there any attribution or other conditions?
>
> Thank you.

## Decision record (for G01)

| Field | Value |
| --- | --- |
| Proposed baseline | Per the table above: Binance Vision SR-04 for crypto history (primary), Kraken SR-05 as a cross-check, Kraken SR-02 if capture is authorised; the context sources as listed; no ETF source yet |
| Decision | **Pending** |
| Dependencies | **Binance Vision:** F-5b (eligibility and retention under the broader Binance terms); F-5c; F-5d (W-1 quote currency); F-7b (venue status); F-8 (training and paper venues); the derived-model restriction (§2.4, §4.2: no live use without a separate licence)<br>**Kraken:** F-4a (ambiguous, recorded; no reply awaited under DEC-033); F-4d; F-4f; F-4g; F-4h; F-4i<br>**ETF:** F-1 closed negatively, so DEC-029 applies and an ETF daily source stays open; F-2 and F-2a; NYSE calendar terms<br>**Crypto venue:** venue status, on the Kraken terms (F-4a); F-7 historical venue-status coverage for archived bars<br>**Context:** context retention (S-2); S-7 for Coin Metrics; the FRED date-granularity `available_at` rule (proposed, round 2)<br>**All sources:** `source_approval` records<br>**For the G01 reviewer:** the VAL gaps recorded in the register, its proposed values, and the provisional defaults W-5 (daily first) and S-3 (£0 budget)<br>**Recorded gaps:** H-OF4, H-OF6, H-OF7; H-OF8 and H-OF9 (F-3; out of scope per W-7) |
| Kraken reply | Not awaited (DEC-033, superseding DEC-032's reply condition) |
| Reviewer | G01 reviewer not yet designated |
