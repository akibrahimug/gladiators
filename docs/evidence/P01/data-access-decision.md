# P01 data-access decision (draft, pending)

[Task](../../tasks/TASK-P01-005.md) · [Source registry](source-registry.md) · [Follow-ups](source-followups.md) · [Follow-ups, round 2](source-followups-2.md) · [Acceptance objectives](acceptance-objectives.md) · [Research agenda](research-agenda.md) · [P01 phase](../../phases/01-research-and-data-access/README.md)

**Status: draft proposal for the G01 reviewer, 2026-10-24. Decision: pending.**

This is the P01 deliverable "an approved data evaluation plan and access decision, including a representative sample plan and source-dependent acceptance criteria" (P01 README). It covers P01 tasks 4 and 7.
- **What it does:** proposes a source baseline and an evaluation plan for the G01 reviewer.
- **What it does not do:** it authorises no account, key registration, download, capture, spending or trading.
- **Why it is pending:** the Kraken items below need confirmation from Kraken, which the user will request ([DEC-032](../../decisions/README.md)).

**No `source_approval` record (L-025) exists yet for any source.** Criterion S-1 requires one, so S-1 is incomplete for every row below, even where the rights are documented.

## Proposed source baseline

This table assesses each source against criteria S-1 to S-7 in the [acceptance-objective register](acceptance-objectives.md#5-source-evaluation-criteria-for-the-p01-task-7-source-baseline).

| Need | Proposed source | S-criteria status | Pending items |
| --- | --- | --- | --- |
| Crypto daily bars (history for H-01 to H-06) | **Kraken OHLCVT archive (SR-05)**, plus Kraken public REST for incremental bars | Passes S-3 and S-6. S-5 is likely met but unconfirmed for each pair. Open: S-1 (F-4a and the Kraken confirmation; no `source_approval` record), S-2 (F-4a) and S-4b (F-4i timestamp semantics; F-4f 30-minute inconsistency) | F-4a (also covers the legacy-page provenance); DEC-032 reply; F-4f, F-4g (delisted pairs), F-4h (availability at bar close), F-4i |
| Crypto live depth and trades (H-OF1, H-OF2, H-OF3, H-OF5) | **Kraken WebSocket v2 public `book` and `trade` (SR-02)**, only if a later authorisation permits capture | Passes S-3, S-4 and S-6. Open: S-1 (F-4a; no `source_approval` record) and S-2 (F-4a) | F-4a; DEC-032 reply; capture authorisation (P02 boundary) |
| Crypto historical trades (H-OF3 history) | Kraken public REST trades | Not assessed | F-4d (history and terms) |
| ETF daily bars | **None proposed** | No candidate passes S-1, S-2 and S-5 | **F-1 closed negatively on 2026-10-25** ([round 2](source-followups-2.md#f-1--free-daily-etf-bars-closed-negatively)), so DEC-029 is triggered: the daily-first baseline runs on crypto spot first. ETFs stay in scope; an ETF daily source stays a G01 dependency |
| ETF corporate actions | **None proposed** | — | F-2, F-2a |
| ETF trading calendar | NYSE hours and calendars | Conditional: the terms are unread | ETF-only; deferred with ETFs |
| Context events (W-7) | FOMC calendar, BLS CPI schedule, CFTC COT, GDELT, FRED/ALFRED (data key; DEC-028), Coin Metrics Community | S-3 passes. S-1: rights are documented (FRED and Coin Metrics for DEC-030 use), but no `source_approval` record exists. **S-2 (retention) is open for all.** S-7 is documented for FOMC (minutes timing only; no statement time), BLS (08:30) and CFTC (3:30 p.m. ET), and open for GDELT, FRED and Coin Metrics | Retention terms per source; S-7 for three sources; `source_approval` records |
| Crypto venue status (`VenueStatus`) | **Kraken REST `SystemStatus` and WebSocket v2 `status`** (no key; [round 2](source-followups-2.md#venue-status--kraken)). Coinbase is out (DEC-031) | Passes S-3. Open: S-1 and S-2 (F-4a; no `source_approval` record). History comes only from forward capture | F-4a; DEC-032 reply; capture authorisation. Missing venue status still blocks new entries |
| Per-order (L3) data (H-OF4) | **None.** Kraken `level3` needs an account token, which DEC-028 excludes | — | Recorded gap ([agenda](research-agenda.md#gaps-this-agenda-records-for-g01)) |
| Second venue (H-OF6) | **None.** Coinbase is out (DEC-031), and Binance is Unresolved (F-5) | — | Recorded gap |
| NOII and issuer holdings (H-OF7) | **None.** NOII is paid, and issuer holdings are Unresolved (F-3) | — | Recorded gap |
| Derivatives, options and liquidations (H-OF8); on-chain RPC (H-OF9) | **Out of scope until their sources close** (W-7). Coin Metrics Community is the only partial on-chain input | — | F-3 |

**Coinbase items closed or moot under DEC-031:** F-4b (full terms text), F-4c (message timestamps) and F-4e (UK availability).

## Access requirements

| Source | Account | Key | Network action needed later | Cost |
| --- | --- | --- | --- | --- |
| Kraken SR-05 archive and REST | None: public endpoints need "no API key" (SR-02) | None | Download archive files and verify the published SHA-256. REST pulls only on explicit invocation (`09-CONNECTORS.md` "No hidden spend") | £0 |
| Kraken SR-02 WebSocket | None | None | Only under a later capture authorisation | £0 |
| FRED/ALFRED | Registration for an API key (a data key, allowed by DEC-028) | Data key | Key registration is a user action | £0 |
| FOMC, BLS, CFTC, GDELT, Coin Metrics | None | None | Public pages or files | £0 |

## Representative sample plan

Purpose: verifying the sources, not producing research results. The plan runs **only after all three** of the following:
- the Kraken reply (DEC-032);
- G01 approval;
- the user's authorisation of downloads.

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
| Kraken | Not addressed in the terms read | §8 "only for your own benefit" (the coordinator's reading; whether "Our Content" covers API data is open, F-4a) | **Pending the Kraken reply (DEC-032)** |
| FOMC, BLS, CFTC | Not established | Not established | Open (S-2); US government publications |
| GDELT | Not established | Allowed, but "must include a citation to the GDELT Project" | Open (S-2) |
| FRED/ALFRED | Not established | Third-party series need permission "beyond personal use" | Open (S-2) |
| Coin Metrics | Not established | CC BY-NC 4.0: attribution, non-commercial use only | Open (S-2) |

Under DEC-030 nothing is redistributed, but each `source_approval` record still records the terms.

## Capture-quality criteria

These are items Q-1 to Q-7 and R-1 to R-5 in the [acceptance-objective register](acceptance-objectives.md), together with its proposed values for G01. This draft adds no thresholds.

## Draft request to Kraken (for the user to send; the coordinator has not sent it)

Under DEC-032, whether and when to send this is the user's decision.

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
| Proposed baseline | Per the table above: Kraken SR-05, and SR-02 if capture is authorised; the context sources as listed; no ETF source yet |
| Decision | **Pending** |
| Dependencies | **Kraken:** DEC-032 reply; F-4a (including provenance); F-4d; F-4f; F-4g; F-4h; F-4i<br>**ETF:** F-1 closed negatively, so DEC-029 applies and an ETF daily source stays open; F-2 and F-2a; NYSE calendar terms<br>**Crypto venue:** venue status, on the Kraken terms (F-4a)<br>**Context:** context retention (S-2); S-7 for Coin Metrics; the FRED date-granularity `available_at` rule (proposed, round 2)<br>**All sources:** `source_approval` records<br>**For the G01 reviewer:** the VAL gaps recorded in the register, its proposed values, and the provisional defaults W-5 (daily first) and S-3 (£0 budget)<br>**Recorded gaps:** H-OF4, H-OF6, H-OF7; H-OF8 and H-OF9 (F-3; out of scope per W-7) |
| If Kraken does not reply, or replies negatively | Return to the user for a decision (DEC-032) |
| Reviewer | G01 reviewer not yet designated |
