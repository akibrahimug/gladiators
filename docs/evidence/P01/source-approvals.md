# P01 `source_approval` records

[Task](../../tasks/TASK-P01-010.md) · [G01 gate record](g01-gate-record.md) · [Data-access decision](data-access-decision.md) · [Source registry](source-registry.md) · [Acceptance objectives](acceptance-objectives.md#5-source-evaluation-criteria-for-the-p01-task-7-source-baseline)

**Status: confirmed by the G01 reviewer and frozen, 2026-10-27 (DEC-047).** Drafted 2026-10-26; SA-01 revised 2026-10-27 (TASK-P01-011: dataset terms §1.2 to §1.5), before the confirmation.
- **Basis:** prepared under DEC-038; approved for planning and sampling (DEC-046). Any later change reopens the record and needs a new date.
- **Authorisation:** these records authorise no account, key registration, download, capture, spending or trading.
- **Downloads:** they follow DEC-035 and DEC-044, effective from the G01 pass on 2026-10-27.

**Basis.** Reinstated L-025 (v5 `10-DATA.md:39`, the section; the rule at :44) says: "Freeze a `source_approval` record (licence reviewed, intended use, date, allowed retention/redistribution, coverage, sample verification). A free endpoint is not automatically an approved dataset." Each record below has those six fields, plus:
- its accepted limitations;
- its standing against the other S-criteria.

The amended §5 rule (DEC-038, effective from the G01 pass on 2026-10-27) relaxes **S-1 and S-2 only**: a limitation recorded here and accepted by the reviewer satisfies them for personal, non-commercial research (DEC-030). Every other criterion still applies as written, so each record shows how S-3 to S-7 stand. Any change of use reopens the record.

**Common to every record:**
- **Intended use:** DEC-030. This means personal, non-commercial research and paper simulation, with no product, clients or redistribution.
- **Sample verification:** pending. Each record is approved for planning and sampling (DEC-046, DEC-047), with its open data-semantics items carried to P02 as dependencies (DEC-045). When the sample plan completes, the coordinator updates this field and the record is re-frozen with a new date. That update needs the reviewer's confirmation only if a result changes an accepted limitation or an S-criterion standing.
- **Terms readings:** these are the coordinator's, not legal advice.

## Crypto market data

| Field | SA-01 Binance Vision archive (SR-04) | SA-02 Kraken OHLCVT archive and public REST (SR-05) | SA-03 Kraken WebSocket v2 public and REST status (SR-02) |
| --- | --- | --- | --- |
| Role | Primary daily-bar and historical-trade source for research (DEC-036) | Cross-check for research; history for any model used in paper simulation (DEC-036, DEC-037) | Live depth, trades and venue status, **only under a later capture authorisation** (not yet given) |
| Licence reviewed | Dataset terms v1.0 ("Last Updated: August 26, 2026"; re-read 2026-10-27 for §1.2 to §1.5 and §7), CC BY-NC-SA 4.0; Binance general terms BT-1 to BT-4 ([reassessment](source-reassessment.md), [general terms](binance-general-terms.md)) | Kraken global terms ("Last Updated: 19 October, 2026") §8 and §9; the legacy API page ([round 1](source-followups.md#f-4--crypto-venue-terms), [reassessment](source-reassessment.md)) | As SA-02 |
| Date reviewed | 2026-10-25; 2026-10-27 (§1.2 to §1.5, §7) | 2026-10-24 (terms); 2026-10-25 (reassessment, data details) | 2026-10-24 (terms); 2026-10-25 (venue status) |
| Use permitted | §4.1 permits "algorithmic historical backtesting for purely personal non-production research". §2.4 extends the terms to derived models, and §4.2 bars their live use; §3.4 excludes commercial licensing | §8 permits use "only for your own benefit"; permission is needed for "non-personal commercial use" of market data. No concrete restriction was found for DEC-030 use | As SA-02 |
| Allowed retention | Not restricted for DEC-030 use. The licence grants reproduction (CC §2(a)(1)). The general terms apply (§1.2), but the dataset terms prevail in any conflict (§1.5) and do not limit CC rights in downloaded Datasets (§3.3; §1.4) | Not addressed in the terms read (F-4a) | As SA-02 |
| Allowed redistribution | None intended. Any derivative shared would need attribution and CC BY-NC-SA 4.0 (§4.5); no hosting (§4.3) | None intended. §8 limits use to "your own benefit"; whether "Our Content" covers API data is open (F-4a) | As SA-02 |
| Coverage | Spot `klines`, `trades` and `aggTrades`, as daily and monthly files. Mostly USDT-quoted (DEC-039). Microsecond timestamps from 2025-01-01 (L-025). Archived files may be revised, and revisions are announced (two listed); each revision is a correction with its own `available_at` (T-2a) | Candles at 1 to 1,440 minutes, "from its first trade on Kraken through 30 June 2026", plus quarterly incremental ZIPs (2026 Q1 to Q3 listed). `available_at` lags the bar end by up to a quarter. No-trade intervals are omitted. USD pairs (DEC-039) | `book` at depth 10 and `trade` (W-4); `SystemStatus` and the WebSocket `status` channel |
| **Accepted limitations** (DEC-038), confirmed 2026-10-27 | F-5b″: the Terms of Use linked in dataset terms §1.2 was not rendered; BT-1 is inferred to be it, because §1.3 names Nest Exchange Limited, the BT-1 party; any UK Local Terms are unknown ([correction](binance-general-terms.md#correction-2026-10-27-the-dataset-terms-own-incorporation-and-priority-clauses-f-5b)). The derived-model restriction: Binance-derived models stay out of paper and live use (DEC-037); whether feature or model choices made on Binance count as "derived" is not addressed. Findings must be revalidated on Kraken before paper use (F-8, DEC-037). The USDT/USD basis (F-5d, DEC-039). No venue status (F-7b); the DEC-040 rule applies | F-4a: §9 bans "bots … scripts" in general terms that the API page applies to API use; retention is not addressed; "Our Content" scope is unclear. No venue-status history (F-7); the DEC-040 rule applies. The USDT/USD basis when compared with SA-01 (DEC-039) | F-4a as SA-02. History starts only at the first capture. Round 2: the WebSocket `status` page "does not say whether authentication is required" |
| Other S-criteria | S-3 passes (free; no key). S-4b passes: open and close times explicit; `.CHECKSUM` per file. S-5 is likely met, but delisted symbols are open (F-5c; P02 dependency, DEC-045). S-6: venue-local, Binance only | S-3 passes. S-4b: integrity passes (published SHA-256), but timestamp semantics are open (F-4i, F-4f; P02 dependencies, DEC-045). S-5 is likely met ("from its first trade"), but delisted pairs are open (F-4g; DEC-045). S-6: venue-local, Kraken only | S-3, S-4 and S-6 pass (RFC3339 timestamps; CRC32 checksum on the top 10 levels; venue-local) |
| Operating conditions | DEC-044: reasonable load; respect robot exclusion; verify each `.CHECKSUM`. Also the dataset terms §7.1 and §7.2: posted rate limits, script guidelines and download protocols (coordinator's application) | DEC-044: verify the published SHA-256; REST pulls only on explicit invocation | DEC-044 |

## Context sources (W-7)

| Field | SA-04 FOMC calendar and minutes | SA-05 BLS CPI schedule | SA-06 CFTC COT | SA-07 GDELT | SA-08 FRED/ALFRED (SR-13) | SA-09 Coin Metrics Community |
| --- | --- | --- | --- | --- | --- | --- |
| Licence reviewed | No terms page read; a US government publication with no restriction found ([round 1](source-followups.md#f-3--context-sources)) | No terms page read; US government publication | No terms page read; US government publication | GDELT about page | FRED API terms of use | Docs: "Creative Commons license" (CC BY-NC 4.0) |
| Date reviewed | 2026-10-24 | 2026-10-24 | 2026-10-24 | 2026-10-24 (terms); 2026-10-25 (timing) | 2026-10-24 (terms); 2026-10-25 (timing) | 2026-10-24 (terms); 2026-10-25 (timing) |
| Use permitted | No restriction found | No restriction found | No restriction found | "unlimited and unrestricted use", with "a citation to the GDELT Project" | Personal use. Third-party series need permission "beyond personal use", and DEC-030 use is personal | Non-commercial (DEC-030) |
| Allowed retention | Not established (S-2) | Not established (S-2) | Not established (S-2) | Not stated (S-2); the use grant is unrestricted | Not stated (S-2) | Not stated (S-2) |
| Allowed redistribution | None intended | None intended | None intended | None intended; citation if ever shared | None intended | None intended; CC BY-NC terms if ever shared |
| Coverage | Meeting dates; minutes released three weeks after the decision. No statement time | Release dates at 08:30 | Tuesday data, released Friday at 3:30 p.m. ET | Updates every 15 minutes; history from 2015-02-19, with "not currently a historical backfile" ([round 2](source-followups-2.md#context-sources--s-7-publication-timing)) | Vintages at date granularity | "limited assets and 30 days of history"; exchange-flow coverage unverified |
| **Accepted limitations** (DEC-038), confirmed 2026-10-27 | S-2 retention not established | S-2 as SA-04 | S-2 as SA-04 | S-2 not stated | S-2 not stated. A data key is a user action (DEC-028); bandwidth may be limited | S-2 not stated; the asset and 30-day limits; exchange-flow coverage unverified |
| Other S-criteria (S-3 passes for all) | **S-7:** minutes timing documented. **Statement release time is not documented**, so statement events are forward-only, with `available_at` = the observed publication time, as DEC-041 does for Coin Metrics. **Confirmed with the records, 2026-10-27.** The calendar lists 2026–27 meetings only; historical meeting and minutes dates are to be confirmed by sample step 3, or as a P02 dependency. This amends W-7's first-publication rule for statements | S-7: 08:30 documented. The page lists only Oct–Dec 2026; historical release dates are to be confirmed by sample step 3, or as a P02 dependency | S-7: Friday 3:30 p.m. ET documented; holidays may delay release. Historical release dates are to be confirmed by sample step 3, or as a P02 dependency | S-7: 15-minute cadence documented | S-7: date granularity; met by the FRED `available_at` rule (DEC-042, effective at the pass) | **S-7 is not met for history.** Forward use meets it through DEC-041's rule (`available_at` = `retrieved_at`); historical use stays barred until completion times are documented |
| Operating conditions | DEC-044 | DEC-044 | DEC-044 | DEC-044 | DEC-044; key registration by the user | DEC-044; 10 requests per 6 s |

## Not in the baseline (no record)

None of these is in the baseline, so none has a record:
- **SR-01 Coinbase:** excluded (DEC-031).
- **SR-03 Binance live:** Unresolved.
- **SR-06 to SR-11, the ETF sources:** deferred (DEC-043).
- **The NYSE calendar:** deferred with ETFs.
- **CME, Deribit, iShares and blockchain RPC:** out of scope or Unresolved.

A source added later needs its own record before use.

## For the G01 reviewer

DEC-046 asks for one confirmation, covering:
- records SA-01 to SA-09, with their accepted limitations;
- the S-criteria standings in each record, including the forward-only treatment of FOMC statement times (SA-04);
- the §5 amendment as written in the [register](acceptance-objectives.md#5-source-evaluation-criteria-for-the-p01-task-7-source-baseline).

**Confirmed on 2026-10-27 (DEC-047).** The records are frozen with that date, and G01 is recorded as passed with these conditions ([gate record](g01-gate-record.md#reviewer-confirmation-2026-10-27)).
