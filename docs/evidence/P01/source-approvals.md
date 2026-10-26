# P01 `source_approval` records (draft)

[Task](../../tasks/TASK-P01-010.md) · [G01 gate record](g01-gate-record.md) · [Data-access decision](data-access-decision.md) · [Source registry](source-registry.md) · [Acceptance objectives](acceptance-objectives.md#5-source-evaluation-criteria-for-the-p01-task-7-source-baseline)

**Status: draft, 2026-10-26, awaiting the G01 reviewer's confirmation (DEC-046).** These records are prepared under DEC-038. They are frozen only when the reviewer confirms them. They authorise no account, key registration, download, capture, spending or trading; downloads follow DEC-035 and DEC-044 once G01 passes.

**Basis.** Reinstated L-025 (v5 `10-DATA.md:39`) says: "Freeze a `source_approval` record (licence reviewed, intended use, date, allowed retention/redistribution, coverage, sample verification). A free endpoint is not automatically an approved dataset." Each record below has those six fields, plus its open items. Under the amended §5 rule (DEC-038), a limitation recorded here and accepted by the reviewer satisfies S-1 or S-2 for personal, non-commercial research (DEC-030). Any change of use reopens the record.

**Common to every record:**
- **Intended use:** DEC-030, personal and non-commercial research and paper simulation, with no product, clients or redistribution.
- **Sample verification:** pending. It comes from the sample plan (DEC-035), so each record is approved for planning and sampling, with its data-semantics items carried to P02 (DEC-045).
- **Disclaimer:** terms readings are the coordinator's, not legal advice.

## Crypto market data

| Field | SA-01 Binance Vision archive (SR-04) | SA-02 Kraken OHLCVT archive and public REST (SR-05) | SA-03 Kraken WebSocket v2 public and REST status (SR-02) |
| --- | --- | --- | --- |
| Role (decisions) | Primary daily-bar and historical-trade source for research (DEC-036) | Cross-check for research; history for any model used in paper simulation (DEC-036, DEC-037) | Live depth, trades and venue status, **only under a later capture authorisation** (not yet given) |
| Licence reviewed | Dataset terms v1.0 ("Last Updated: August 26, 2026"), CC BY-NC-SA 4.0; Binance general terms BT-1 to BT-4 ([reassessment](source-reassessment.md), [general terms](binance-general-terms.md)) | Kraken global terms ("Last Updated: 19 October, 2026") §8 and §9; the legacy API page ([round 1](source-followups.md#f-4--crypto-venue-terms), [reassessment](source-reassessment.md)) | As SA-02 |
| Date reviewed | 2026-10-25 | 2026-10-24 and 2026-10-25 | 2026-10-24 and 2026-10-25 |
| Use permitted | §4.1 "algorithmic historical backtesting for purely personal non-production research". Binance-derived models may not be used live (§2.4, §4.2); they stay out of paper and live use (DEC-037) | §8 "only for your own benefit"; permission is needed only for "non-personal commercial use" of market data. No concrete restriction was found for DEC-030 use | As SA-02 |
| Allowed retention | Not restricted by the dataset terms (CC §2(a)(1); §1.4). Ambiguous under the general terms' copy and store clauses (F-5b′) | Not addressed in the terms read (F-4a) | As SA-02 |
| Allowed redistribution | None intended. Any derivative shared would need attribution and CC BY-NC-SA 4.0 (§4.5); no hosting (§4.3) | None intended; §8 limits use to "your own benefit" | As SA-02 |
| Coverage | Spot `klines`, `trades` and `aggTrades`, daily and monthly files. Mostly USDT-quoted (DEC-039). Microsecond timestamps from 2025-01-01 (L-025) | Candles at 1 to 1,440 minutes, "from its first trade on Kraken"; no-trade intervals omitted. USD pairs (DEC-039) | `book` depth 10 and `trade` (W-4); `SystemStatus` and WebSocket `status` |
| **Accepted limitations** (DEC-038), for the reviewer to confirm | F-5b′ (whether the archive is a Binance Service; the copy and store clauses against the licence; the governing version for a UK user). Derived-model restriction. No venue status (F-7b; rule DEC-040). Delisted symbols unverified (F-5c) | F-4a: §9 bans "bots … scripts" in general terms that the API page applies to API use; retention is not addressed. No venue-status history (F-7; rule DEC-040) | F-4a as SA-02. History starts only at the first capture |
| Open semantics (P02, DEC-045) | F-5c | F-4d, F-4f, F-4g, F-4h, F-4i | Q-5 and T-3 measured only in authorised capture |
| Operating conditions | DEC-044: reasonable load; respect robot exclusion; verify each `.CHECKSUM` | DEC-044; verify the published SHA-256; REST only on explicit invocation | DEC-044 |

## Context sources (W-7)

| Field | SA-04 FOMC calendar and minutes | SA-05 BLS CPI schedule | SA-06 CFTC COT | SA-07 GDELT | SA-08 FRED/ALFRED (SR-13) | SA-09 Coin Metrics Community |
| --- | --- | --- | --- | --- | --- | --- |
| Licence reviewed | US government publication; no restriction found ([round 1](source-followups.md#f-3--context-sources)) | US government publication | US government publication | GDELT about page: "unlimited and unrestricted use", with citation | FRED API terms of use | "Creative Commons license" (CC BY-NC 4.0) |
| Date reviewed | 2026-10-24 | 2026-10-24 | 2026-10-24 | 2026-10-24 | 2026-10-24 | 2026-10-24 |
| Use permitted | Yes | Yes | Yes | Yes; any use "must include a citation to the GDELT Project" | Personal use; third-party series need permission "beyond personal use" (DEC-030 is personal) | Non-commercial (DEC-030) |
| Allowed retention | Not established (S-2) | Not established (S-2) | Not established (S-2) | Not established (S-2); the use grant is unrestricted | Not established (S-2) | Not established (S-2) |
| Allowed redistribution | None intended | None intended | None intended | None intended; citation if ever shared | None intended | None intended; CC BY-NC terms if ever shared |
| Coverage | Meeting dates; minutes three weeks after the decision. No statement time | Release dates at 08:30 | Friday 3:30 p.m. ET release of Tuesday data | Updates every 15 minutes ([round 2](source-followups-2.md#context-sources--s-7-publication-timing)) | Vintages at date granularity; `available_at` per the approved FRED rule (DEC-042) | Limited assets and 30 days of history; forward-only (DEC-041) |
| **Accepted limitations** (DEC-038), for the reviewer to confirm | S-2 retention not established for US government publications; statement time captured at publication | S-2 as SA-04 | S-2 as SA-04; holiday delays | S-2 not stated | S-2 not stated; a data key is a user action (DEC-028); bandwidth may be limited | S-2 not stated; S-7 Unresolved, hence forward-only; exchange-flow coverage unverified |
| Operating conditions | DEC-044 | DEC-044 | DEC-044 | DEC-044 | DEC-044; key registration by the user | DEC-044; 10 requests per 6 s |

## Not in the baseline (no record)

These are not in the baseline, so they have no record:
- **SR-01:** Coinbase (DEC-031).
- **SR-03:** Binance live (Unresolved).
- **SR-06 to SR-11:** the ETF sources, deferred under DEC-043.
- **The NYSE calendar:** ETF-deferred.
- **CME, Deribit, iShares and blockchain RPC:** out of scope or Unresolved.

A source added later needs its own record before use.

## For the G01 reviewer

DEC-046 asks for one confirmation:
- the records SA-01 to SA-09, with their accepted limitations;
- the §5 amendment as written in the [register](acceptance-objectives.md#5-source-evaluation-criteria-for-the-p01-task-7-source-baseline).

On confirmation, the records are frozen with that date and G01 is recorded as passed.
