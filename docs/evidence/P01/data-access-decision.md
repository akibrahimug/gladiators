# P01 data-access decision (draft, pending)

[Task](../../tasks/TASK-P01-005.md) · [Source registry](source-registry.md) · [Follow-ups](source-followups.md) · [Acceptance objectives](acceptance-objectives.md) · [Research agenda](research-agenda.md) · [P01 phase](../../phases/01-research-and-data-access/README.md)

**Status: draft proposal for the G01 reviewer, 2026-10-24. Decision: pending.**

This is the P01 deliverable "an approved data evaluation plan and access decision, including a representative sample plan and source-dependent acceptance criteria" (P01 README), covering P01 tasks 4 and 7. It is a proposal, not an approval.
- **What it proposes:** a source baseline and an evaluation plan for the G01 reviewer.
- **What it authorises:** nothing. No account, key registration, download, capture, spending or trading.
- **Why it is pending:** the Kraken items below need confirmation from Kraken, which the user requests ([DEC-032](../../decisions/README.md)).

## Proposed source baseline

Each component is assessed against criteria S-1 to S-7 from the [acceptance-objective register](acceptance-objectives.md#5-source-evaluation-criteria-for-the-p01-task-7-source-baseline).

| Need | Proposed source | S-criteria status | Pending items |
| --- | --- | --- | --- |
| Crypto daily bars: history for H-01 to H-06 | **Kraken OHLCVT archive (SR-05)**, plus Kraken public REST for incremental bars | Passes S-3 and S-6. S-5 is likely met but unconfirmed for each pair. Open: S-1 and S-2 (F-4a, Kraken confirmation) and S-4b (F-4i: candle timestamp semantics; F-4f: 30-min inconsistency) | DEC-032 confirmation; F-4f, F-4g (delisted pairs), F-4h (availability at bar close), F-4i |
| Crypto live depth and trades: H-OF1, H-OF2, H-OF3, H-OF5 | **Kraken WebSocket v2 public `book` and `trade` (SR-02)**, only if a later authorisation permits capture | Passes S-3, S-4 and S-6. Open: S-1 and S-2 (F-4a) | DEC-032 confirmation; capture authorisation (P02 boundary) |
| ETF daily bars | **None proposed** | No candidate passes S-1, S-2 and S-5 | F-1a (Twelve Data), F-1b (IEX HIST). If both close negatively, DEC-029 applies |
| ETF corporate actions | **None proposed** | — | F-2, F-2a |
| Context events (W-7) | FOMC calendar, BLS CPI schedule, CFTC COT, GDELT, FRED/ALFRED (data key; DEC-028), Coin Metrics Community | S-3 passes. S-1 is documented (FRED and Coin Metrics for DEC-030 use). **S-2 (retention) is open for all.** S-7 is documented for FOMC, BLS and CFTC, and open for GDELT, FRED and Coin Metrics | Retention terms per source; S-7 for three sources |
| Crypto venue status (`VenueStatus`) | **None.** Kraken status is not checked, and Coinbase is out (DEC-031) | — | A required input that is still unresolved: until it closes, missing venue status blocks new entries |

## Access requirements

| Source | Account | Key | Network action needed later | Cost |
| --- | --- | --- | --- | --- |
| Kraken SR-05 archive and REST | None ("no API key needed" for public endpoints, SR-02) | None | Download archive files and verify their published SHA-256; REST pulls run only with explicit invocation (`09-CONNECTORS.md` "No hidden spend") | £0 |
| Kraken SR-02 WebSocket | None | None | Only under a later capture authorisation | £0 |
| FRED/ALFRED | Registration for an API key, which counts as a data key under DEC-028 | Data key | Key registration is a user action, not a coordinator action | £0 |
| FOMC, BLS, CFTC, GDELT, Coin Metrics | None | None | Public pages or files | £0 |

## Representative sample plan

This plan is for verifying the sources, not for research results. It runs only after G01 approval and the user's authorisation of downloads.

1. **Kraken archive sample.**
   - **Files:** one quarterly incremental ZIP (the latest available) and the full-history part list for the W-1 candidate pairs.
   - **Integrity:** check the published SHA-256 for each file.
   - **Content:** record per pair the first and last bar, the row count, the share of no-trade intervals (Q-2), any validation failures (Q-1), and whether delisted pairs appear (F-4g).
   - **Timestamp semantics:** compare one week of 1440-minute candles with REST bars for the same dates to establish whether candles are stamped at bar start or bar end (F-4i). Any value differences go to F-4h.
2. **Kraken live sample.** This step requires a separate capture authorisation. Capture one hour of `book` (depth 10) and `trade` data for one pair, and record:
   - checksum failures and resyncs (Q-5);
   - latency percentiles (T-3);
   - the logged NTP offset (T-5);
   - storage size (R-5).
3. **Context sample.** For one FOMC meeting, one CPI release and one COT release, record the publication time as observed against the published schedule, to confirm S-7.

The sample results go into P02's `capture-validation-plan.md`. They do not count as research evidence.

## Provenance fields (manifest per source)

These fields come from the reinstated L-010 item 2 and L-025:
- **Source and terms:** provider URL; terms URL and the date the terms were read; access method; allowed research or commercial use (DEC-030); the `source_approval` record (licence reviewed, intended use, date, allowed retention and redistribution, coverage, sample verification).
- **Data definition:** raw and adjusted definitions; universe coverage; interval.
- **Retrieval:** rate limit; retrieval date; SHA-256 checksum.

Every record also carries the `10-DATA.md` market schema (`10-DATA.md:9`) and the T-1 timestamps.

## Retention constraints

| Source | Constraint | Status |
| --- | --- | --- |
| Kraken | Not addressed in the terms that have been read | **Pending: Kraken confirmation (DEC-032)** |
| Context sources | Not established for any source | Open (S-2) |
| GDELT | Use and redistribution need "a citation to the GDELT Project" | Attribution is required wherever the data is used |
| Coin Metrics | CC BY-NC 4.0 | Attribution is required, and use must be non-commercial (DEC-030) |

## Capture-quality criteria

These are the [acceptance-objective register](acceptance-objectives.md) items Q-1 to Q-7 and R-1 to R-5, plus the proposed values listed there for G01. This draft adds no new thresholds.

## Draft request to Kraken (for the user to send; not sent by the coordinator)

Per DEC-032, the user decides whether to send this text, and when.

> **To:** marketdata@kraken.com
> **Subject:** Permission check: personal, non-commercial research use of public market data
>
> I am building a private, non-commercial research project for my own use. There is no product, there are no clients, and nothing is redistributed. I would like to confirm the following:
> 1. **Collection:** may I collect data from Kraken's documented public market-data endpoints for this personal research? These are the WebSocket v2 `book` and `trade` channels, and the public REST OHLC and trades endpoints, accessed through Kraken's published API documentation. Does §9 of the Terms of Service, on bots, scripts and data extraction from "Our Content", apply to this documented API use?
> 2. **Archive:** may I download the historical OHLCVT archive from your support site for the same purpose?
> 3. **Retention:** may I keep the raw data locally, unaltered, so that results can be reproduced?
> 4. **Further conditions:** are there any attribution or other conditions?
>
> Thank you.

## Decision record (for G01)

| Field | Value |
| --- | --- |
| Proposed baseline | The table above: Kraken SR-05 (and SR-02 if capture is authorised); context sources as listed; no ETF source yet |
| Decision | **Pending.** It needs the DEC-032 confirmation, and the G01 reviewer's approval of the proposed values in the acceptance-objective register |
| Dependencies | DEC-032; F-1a and F-1b (otherwise DEC-029); F-2 and F-2a; F-4f, F-4g, F-4h and F-4i; venue status; context retention (S-2) and S-7; the VAL gaps recorded in the register |
| Reviewer | G01 reviewer not yet designated |
