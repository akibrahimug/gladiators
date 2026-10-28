# P02 event contract: raw and normalized records

[Task](../../tasks/TASK-P02-001.md) · [P02 phase](../../phases/02-event-capture/README.md) · [Contracts checklist](../../architecture/contracts.md) · [Observability map](../P01/observability-map.md) · [`source_approval` records](../P01/source-approvals.md) · [Sample results](../P01/sample-results.md) · [Acceptance objectives](../P01/acceptance-objectives.md)

**Status: proposed contract, 2026-10-28, for the G02 reviewer.** This document covers P02 tasks 1 to 4. It is not an implementation.
- **What it does not authorise:** capture, storage or code. Live capture (Kraken WebSocket) still needs its own authorisation.
- **What it does not decide:** thresholds. P02 task 5 selects them in the capture validation plan, and they are approved before any measurement.
- **What G02 still needs:** G02 passes only with capture and replay evidence from a later, authorised implementation (P02 exit gate).

**Settled by the user on 2026-10-28:** the time model (DEC-052), revision timing (DEC-053), replay order (DEC-054) and context scope (DEC-055). These are recorded [below](#decisions-asked-2026-10-28). Everything else in this file marked **Proposed** is the coordinator's resolution of a source conflict, for the reviewer to accept or change.

**Sources and IDs used.**
- **Reinstated sections:** L-008 (v4 `08-TRANSPORTERS.md:30`), L-023 (v5 `08-TRANSPORTERS.md:28–30`), L-010 (v4 `10-DATA.md:43–47`), L-024 (v5 `09-CONNECTORS.md:29–30`), L-025 (v5 `10-DATA.md:40–44`).
- **v10 files:** `08-TRANSPORTERS.md`, `09-CONNECTORS.md`, `10-DATA.md`, file 24 (lines 94–118) and file 27.
- **Repository records:** REQ-001, REQ-003, REQ-004, REQ-005 and REQ-011; CMP-01, CMP-02, CMP-03 and CMP-11; VAL-002 and VAL-004.

Short quotes are from the preserved releases; "v10 10:9" means v10 `10-DATA.md` line 9.

## 1. Scope

| Event type | Source and record | Status | Section |
| --- | --- | --- | --- |
| `BarEvent` | Binance Vision `klines` (SA-01); Kraken OHLCVT archive (SA-02); Kraken REST `OHLC` (SA-02) | In the approved baseline | [§4.1](#41-barevent) |
| `TradeEvent` | Binance Vision `trades` (SA-01) | In the approved baseline (H-OF3) | [§4.2](#42-tradeevent) |
| `ObservationEnvelope` | FOMC, CPI, COT, GDELT, FRED/ALFRED and Coin Metrics (SA-04 to SA-09) | In the approved baseline; P02 defines the envelope only (DEC-055) | [§4.3](#43-observationenvelope-context) |
| `NativeMarketEvent` (`book`, `trade`), `VenueStatus` | Kraken WebSocket v2 and REST `SystemStatus` (SA-03) | **Conditional**: capture not authorised | [§4.4](#44-live-types-conditional) |
| `OnChainEvent` | None (F-3; DEC-043) | Out of scope | — |

## 2. Raw preservation and versioning

Every retrieved object is preserved before any parsing. Sources: "Preserve raw bytes and receipt with SHA-256; never silently overwrite" (v10 10:13); "Persist append-only event journal" (L-023, v5 08:30).

**`RawObject` record**, one per retrieved object:

| Field | Meaning | Basis |
| --- | --- | --- |
| `raw_id` | SHA-256 of the exact bytes | v10 10:13 |
| `source_id` | The source registry ID (SR-04, SR-05, …) | REQ-003; L-024 "Record feed identity in every observation" |
| `source_approval_id` | The record that permits it (SA-01 …) | L-025; S-1 |
| `request` | URL or file path, and the query parameters | L-010 manifest "provider URL … access method" |
| `retrieved_at` | Our clock at the end of a successful retrieval (UTC, ns) | DEC-053 |
| `server_last_modified`, `server_etag` | As sent; null if absent | DEC-048 |
| `published_checksum`, `checksum_status` | The checksum the source publishes and the result: `verified`, `mismatch` or `none_published` | DEC-044; SA-02 (quarterly ZIP: `none_published`) |
| `byte_length`, `media_type` | As received | — |
| `supersedes_raw_id` | The earlier version of the same `request`, if the bytes differ | DEC-048 |

**Rules.**
1. **Append-only.** Raw objects are never overwritten or deleted while their record is in use. A changed object at the same `request` is stored as a new `RawObject` with `supersedes_raw_id` set (DEC-048).
2. **Versioning (Proposed; resolves C7).** The layout is v10's "`data/raw/{provider}/{ingest_date}/`" (v10 10:6), keyed by `raw_id`. Two versions never share a path.
3. **Checksum failure.** A `mismatch` quarantines the object. Nothing is parsed from it, and the retrieval is retried under DEC-044's load condition. Repeated mismatch makes the source `SOURCE_UNAVAILABLE` for that object.
4. **Archive containers.** For a ZIP, each member file gets its own `raw_id` and refers back to its container. Kraken's full-history parts are verified per part and then joined. The joined ZIP gets its own `raw_id`.
5. **Change detection.** Re-retrieval compares `raw_id`. A different hash at the same `request` is a revision (§5, S-09).

## 3. Common envelope and time model

Every normalized record carries the common fields below. The four times and the basis are fixed by DEC-052. Sources: L-008 envelope fields (v4 08:30); L-023's "Distinguish event-time, ingestion-time, available-at and processing-time" (v5 08:29); T-1.

| Field | Meaning | Rule |
| --- | --- | --- |
| `record_id` | A deterministic hash of (`source_id`, `instrument_id`, `source_event_time`, native key, `version`) | Stable across replays (L-023 idempotency) |
| `schema_version` | Contract version of this record type | An unknown version is quarantined (v10 08:18) |
| `source_id`, `feed_id` | The registry source and the specific feed or file series | Q-7: "Every record carries its venue and feed identity" |
| `venue` | `binance`, `kraken`, or null for context | Venue-local only (S-6) |
| `instrument_id`, `native_symbol` | See [§3.2](#32-instrument-identity) | F-5e; DEC-039 |
| `source_event_time` | The time the source says the event occurred, in its **native precision and unit** | T-1 ("no padding") |
| `source_time_unit` | `s`, `ms`, `us` or `ns`, as declared for the source era | L-025 ("never heuristic length alone") |
| `received_at` | Our clock when the bytes arrived; for archives, the `RawObject.retrieved_at` | T-1 |
| `ingested_at` | Our clock when this record was normalized | T-1. This is L-023's "processing-time" (Proposed; resolves C1) |
| `available_at` | The earliest time a decision may use this record | T-2, T-2a, DEC-052 |
| `available_at_basis` | One of `archive_published`, `retrieved`, `stated_release`, `scheduled_release`, `live_receive` | DEC-052 |
| `raw_id`, `raw_locator` | The raw object, and the row or byte offset inside it | REQ-003; VAL-002 |
| `version`, `supersedes_record_id` | Increments when a revision replaces a record | DEC-048, DEC-053 |
| `quality_state` | `valid`, `quarantined` or `status_unknown` | §5 |
| `rights_id` | The `source_approval` ID in force at retrieval | L-025. The records are frozen, so the observability map's "Unresolved until F-4" is superseded (Proposed; resolves C13) |

### 3.1 Time rules

- **Precision (Proposed; resolves C3).** Times are stored as integers in their native unit, with `source_time_unit` beside them. Our own clocks (`received_at`, `ingested_at`) are stored in nanoseconds. File 27's `_ns` names are aliases for these, so no source time is padded to nanoseconds.
- **Units (Proposed; resolves C4).** The unit comes from a declared era table per source, never from digit count:
  - Binance spot: `ms` for files covering dates before 2025-01-01, and `us` from 2025-01-01 (L-025; dataset README).
  - Kraken: `s` (README).

  A file whose observed digit count contradicts its era is **quarantined** as a schema mismatch. The sample check by digit count (sample results, step 0) was a verification, not the rule.
- **`available_at` per source:**

  | Source | `available_at` | Basis | Authority |
  | --- | --- | --- | --- |
  | Binance daily file | The daily file's `Last-Modified`, if the file has not been rewritten since; otherwise our `retrieved_at` | `archive_published` / `retrieved` | T-2a; sample results (about 2 to 3 h after day end) |
  | Binance monthly file | As daily, but monthly files are used only for history already past their publication | `archive_published` | T-2a |
  | Kraken quarterly or full archive | The archive's MANIFEST `generated` date (2026-10-01 for both the Q3 and the full archive); if absent, `retrieved_at` | `archive_published` | T-2a; F-4i (bar end is only the earliest possible time). **Consequence:** every historical Kraken bar is available only from 2026-10-01, so it cannot be used in a backtest at its own date. See [§8](#8-for-the-g02-reviewer) |
  | Kraken REST `OHLC` | `received_at`, and only for completed bars. The current incomplete bar is dropped | `live_receive` | v10 10:18 "completed bars only" (Proposed; resolves C16) |
  | Any revised record | Our `retrieved_at` of the revised object | `retrieved` | DEC-053 |
  | FOMC statement | The release time stated on the page ("For release at …") | `stated_release` | DEC-049 |
  | FOMC minutes, COT | The published schedule time, where a schedule exists | `scheduled_release` | W-7 |
  | CPI | **Open:** a P02 dependency (DEC-050, DEC-051) | — | — |
  | GDELT, FRED, Coin Metrics | As W-7, DEC-042 and DEC-041 (Coin Metrics: `retrieved_at`) | various | W-7 |

- **Bar end (Proposed; resolves C16).** `bar_start` is stored as given. `bar_end` is derived as `bar_start` plus one interval, exclusive. Binance `close_time` (the bar's last tick) is kept as `native_close_time` and is never used as `bar_end`.

### 3.2 Instrument identity

*Proposed; resolves C10 and F-5e.*
- `native_symbol` is the venue's string (`LUNAUSDT`, `XBTUSD`).
- `instrument_id` is `{venue}:{native_symbol}:{epoch}`, where `epoch` starts at 1. A new epoch starts when **either**:
  - the series has a gap longer than 7 days and its first price after the gap differs from the last price before it by more than a factor of 10; or
  - a listing record says the asset changed.
- Each epoch break is written to an `InstrumentEpoch` record with its evidence, and it needs the reviewer's confirmation before research use.
- LUNAUSDT is the reference fixture (F-10). These thresholds are placeholders for P02 task 5 to confirm, not approved values.
- The quote currency is part of the instrument and is never converted (DEC-039).

## 4. Event types and field maps

### 4.1 `BarEvent`

Base schema: v10 10:9, "`…bar_start_utc,bar_end_utc,available_at_utc,…provider,source_revision…`". Common fields per §3, plus:

| Field | Binance `klines` (12 columns, no header) | Kraken OHLCVT CSV (7 columns, no header) | Kraken REST `OHLC` (8 fields + `last`) |
| --- | --- | --- | --- |
| `bar_start` (`source_event_time`) | col 1 `open_time` (ms or µs, by era) | col 1 `timestamp` (s, "start of the bar") | field 1 `time` (s) |
| `interval` | From the file path (`1d`, …) | From the file name `PAIR_INTERVAL` (minutes) | Request parameter |
| `open`, `high`, `low`, `close` | cols 2 to 5 | cols 2 to 5 | fields 2 to 5 |
| `volume` (base) | col 6 | col 6, binary-float text | field 7, 8 decimals |
| `trade_count` | col 9 | col 7 | field 8 |
| `quote_volume` | col 8 | — (null) | — (null) |
| `taker_buy_base_volume`, `taker_buy_quote_volume` | cols 10, 11 | — | — |
| `vwap` | — | — | field 6 |
| `native_close_time` | col 7 | — | — |
| ignored | col 12 (`ignore`) | — | `last` (pagination cursor; kept in raw only) |

- **Numbers (Proposed; resolves C15).** Prices and volumes are stored as **decimal strings exactly as received**, with no float conversion (27:50, "Preserve integer/decimal precision"). For comparison between sources only, Kraken archive volumes are rounded to 8 decimals (F-4h). The stored value is never rounded.
- **Nulls:** a field the source does not provide is null, never zero ("nullable fields reflect nonapplicability rather than guesses", 27:50).
- **Sparse series:** Kraken omits no-trade bars ("the series is sparse, not padded"). A missing bar produces no `BarEvent`. It produces an interval classification (§5, S-04).

### 4.2 `TradeEvent`

Binance `trades` (7 columns, no header). Common fields per §3, plus:

| Field | Column | Note |
| --- | --- | --- |
| `native_trade_id` | 1 `id` | Contiguous on the sampled day. A gap is S-05 |
| `price`, `qty`, `quote_qty` | 2, 3, 4 | Decimal strings |
| `source_event_time` | 5 `time` (ms or µs, by era) | — |
| `side_semantics`, `is_buyer_maker` | 6 | Stored as stated: "buyer-is-maker", never converted to a taker side silently (observability map) |
| `is_best_match` | 7 | Stored; not interpreted |

`available_at` is the daily file's publication, per §3.1. Trades are history only; they never stand in for live events.

### 4.3 `ObservationEnvelope` (context)

Envelope only (DEC-055). The meaning of the values is P04's (CMP-05). Base: v10 file 24, lines 94–116. Common fields per §3, plus:

| Field | Meaning | Basis |
| --- | --- | --- |
| `observation_id` | Alias of `record_id` | 24:98 |
| `reference_period` | The period the value describes (e.g. CPI September 2026) | 24:118 |
| `published_at` | The source's stated publication time, if any | DEC-052; 24:104 |
| `source_revision` | The vintage or revision label (ALFRED vintage date, etc.) | 24:110 |
| `value_raw`, `value_unit` | As published; decimal string | 27:50 |
| `verification_status` | `VERIFIED`, `UNVERIFIED` or `QUARANTINED` | 24:112 |
| `coverage_scope` | What the observation covers | 24:113 |
| `availability_state` | `OBSERVED`, `NO_EVENT` or `SOURCE_UNAVAILABLE` | v10 09:29 "Persist `NO_EVENT` versus `SOURCE_UNAVAILABLE` distinctly" |

### 4.4 Live types (Conditional)

These are specified so the contract is complete; **no capture is authorised**. Field names follow file 27 (27:50) and the Kraken WebSocket v2 documentation as read in P01 (SR-02). The documentation is to be re-verified when capture is authorised.

| Type | Native fields kept | Integrity mechanism | Open |
| --- | --- | --- | --- |
| `NativeMarketEvent` `book` | Snapshot and update levels (`price`, `qty`), `checksum`, `timestamp` (RFC3339, µs) | CRC32 over the top 10 levels; a mismatch invalidates the book (27:60) | No documented sequence (observability map), so the order is receive order plus checksum |
| `NativeMarketEvent` `trade` | `trade_id`, `price`, `qty`, `side` (taker), `ord_type`, `timestamp` | `trade_id` continuity | F-4a |
| `VenueStatus` | The `status` channel and REST `SystemStatus` | — | History begins only at capture (SA-03) |

## 5. Integrity scenarios and dispositions

**Dispositions (Proposed; resolves C8).**
- **Quarantine:** the record is kept, with `quality_state = quarantined` and a reason. It is never used for features, and it can be replayed for audit. This is v10's dead-letter ("Dead-letter invalid events; never silently discard", L-008), and Q-1's "reject" means quarantine ("Rejected records go to quarantine", Q-1).
- **Status-unknown:** an interval with no usable data, where the cause is not known (DEC-040, Q-2 as amended). No new entries are opened during it.
- **Valid:** usable from `available_at`.

**Gap classes (Proposed; resolves C9).**
- `no_trade` maps to `NO_EVENT`.
- `data_gap` and `status_unknown` map to `SOURCE_UNAVAILABLE` (R-1).
- A zero-volume archived bar is `status_unknown` (DEC-040) even though it is present.

| ID | Scenario | Detection | Expected result | Fixture |
| --- | --- | --- | --- | --- |
| S-01 | Published checksum mismatch | `checksum_status = mismatch` | Object quarantined; no records parsed; retried; repeated failure makes it `SOURCE_UNAVAILABLE` | F-01 |
| S-02 | Duplicate record (same `record_id`) | Key collision at ingest | Idempotent: one record kept, the duplicate counted (L-023) | F-02 |
| S-03 | Conflicting duplicate (same key, different values) | Same key, different content | Both quarantined, with the conflict recorded ("duplicate conflicting keys", v10 10:14) | F-03 |
| S-04 | Missing interval in a sparse archive | Expected grid minus present bars | Classified `no_trade`, `data_gap` or `status_unknown`, so 100 % are classified (Q-2 amended). With the archive alone, every missing interval is `status_unknown` | F-04 (XBTUSD 2014 gaps; ETHUSD 2018-01-12) |
| S-05 | Trade ID gap | Non-contiguous `native_trade_id` | The interval is marked `data_gap`; no imputation | F-05 |
| S-06 | Invalid OHLC, non-finite value, or timezone-naive time | Q-1 checks | Quarantined (Q-1; v10 ACCEPTANCE:5) | F-06 (constructed) |
| S-07 | Unit contradicts era | Digit count vs the era table | File quarantined (§3.1) | F-07 (a ms row in a 2025 file) |
| S-08 | Out-of-order rows inside a file | Non-monotone `source_event_time` | Reordered for replay by DEC-054's key. The raw row index is kept. No feature uses a bar before its `available_at` (v10 08:18) | F-08 |
| S-09 | Revision found on re-download | New `raw_id` at the same `request` | New version; `available_at` = `retrieved_at` (DEC-053); the earlier version kept; replay at a past decision time sees the old version (27:89, experiment 9) | F-09 (1INCHUSDT-1d-2022-03-08: old and new checksums) |
| S-10 | Symbol reuse | §3.2 epoch rule | New `instrument_id` epoch, recorded for review | F-10 (LUNAUSDT 2022-05) |
| S-11 | Delisting | Last bar and listing status | The series ends; the last bar is an **upper bound** on the delisting date (F-4j). Q-4: "A delisting ends the pair's series" | F-11 (ANKRGBP 2022-12-31) |
| S-12 | Incomplete current bar (REST) | `bar_start` + interval > `received_at` | Dropped (§3.1) | F-12 |
| S-13 | Unknown schema or column count | Column count or MANIFEST mismatch | Quarantined (v10 08:18). Manifest count differences are logged, as the Kraken full archive shows 1,759 pairs against the MANIFEST's 1,760 | F-13 |
| S-14 | Source unavailable (HTTP error, 403, timeout) | Retrieval failure | `SOURCE_UNAVAILABLE` for the interval. A 403 is not retried by other means (DEC-050, DEC-051) | F-14 |
| S-15 | Live book checksum mismatch (Conditional) | CRC32 | The book is invalidated and resynchronised from a fresh snapshot, and no feature is published while it is uncertain (27:83, experiment 3) | F-15 (when capture is authorised) |

**Fixture specifications.** Each fixture is a small, documented input with its expected output:
- **F-04, F-09, F-10, F-11:** taken from files already retrieved in the P01 sample, identified there by SHA-256.
- **F-01 to F-03, F-05 to F-08 and F-12 to F-14:** constructed from those files by a stated edit, for example flipping one byte for F-01 or duplicating one row for F-02.

Fixture data stays outside the repository (DEC-030 redistribution), and each fixture is recorded by the hash of its input and its expected output. The Q-1, Q-3/Q-4 and Q-7 VAL gaps (DEC-042) are covered as follows:
- **Q-1:** by F-06;
- **Q-7:** by the `source_id`/`feed_id` fields on every record (§3);
- **Q-3/Q-4 coverage:** in the capture validation plan (P02 task 5).

## 6. Replay

- **Inputs:** `RawObject`s and the era tables, plus this contract's `schema_version`.
- **Order:** by `available_at`, then `source_id`, `instrument_id`, `source_event_time`, native sequence or row index, and `version` (DEC-054). This is v4 08:30's "sorts by *availability* and sequence, not vendor bar close alone".
- **As-of rule:** a replay at decision time *t* sees only records with `available_at <= t`, and for each key only the highest version with `available_at <= t`. This is v10 10:18's "enforce `available_at <= decision_time`".
- **Determinism:** the same raw objects and contract version give byte-identical normalized output (27:63; VAL-003 at G03).
- **Checks:** record counts per state (raw, accepted, quarantined, duplicates, missing intervals by class, as in L-010, v4 10:47); hash of the output.

## 7. P01 dependencies

| Item | Contract rule or status |
| --- | --- |
| F-4d (Kraken REST trade paging) | Not used. Kraken history comes from the archive; REST is for bars only |
| F-4f (intervals) | Only the 7 standard intervals are in the field map. 30-minute files are ignored |
| F-4g (delisted pairs) | Included. The series end follows S-11 |
| F-4h (archive vs REST values) | Comparison rule in §4.1; availability at bar close stays **Unresolved**, so REST bars use `live_receive` |
| F-4i (bar-start stamps) | §3.1 and §4.1 |
| F-4j (delisting dates) | **Open.** The last bar is an upper bound. A forward `AssetPairs` snapshot per retrieval is proposed, to date future delistings (capture validation plan) |
| F-5c (Binance delisted symbols) | Included |
| F-5e (symbol reuse) | §3.2 (Proposed) |
| CPI timing | **Open** (DEC-050, DEC-051) |
| Q-2 as amended | S-04 |
| DEC-048 keep every version | §2 rules 1 and 5; S-09 |

C12 note: F-4j, F-5e and CPI timing came out of TASK-P01-013 and P01-014, after DEC-045's list was written. This contract adopts them as P02 inputs.

## 8. For the G02 reviewer

Proposed resolutions to confirm:
- C1: `ingested_at` stands for "processing-time".
- C3: native-precision storage.
- C4: the era table for units.
- C7: raw versioning.
- C8: quarantine as the single invalid disposition.
- C9: gap-class mapping.
- C10: the instrument epoch rule. Its thresholds are placeholders.
- C13: `rights_id`.
- C15: decimal strings.
- C16: bar end, and dropping incomplete bars.

None changes an approved P01 value.

**Consequence to note (not a proposal).** T-2a's default, archive publication time, makes Kraken archive history unusable at its own dates. The Q3 and full archives were both generated on 2026-10-01. Binance is not affected: its daily files publish about 2 to 3 hours after the day ends. T-2a allows bar-close timing only "if the venue documents availability at bar close" and the archive matches what was served. That is F-4h, still Unresolved. Kraken history is what DEC-037 uses for paper-simulation models, so F-4h becomes the deciding item for Kraken backtests. The capture validation plan (P02 task 5) should propose how to close it, for example by comparing forward REST bars received at bar close with the next archive release.

## Decisions asked, 2026-10-28

The user's answers to four questions. Each question and the chosen option are quoted verbatim.

| Decision | Question (verbatim) | Chosen option: label — description (verbatim) |
| --- | --- | --- |
| DEC-052 | "The sources name event timestamps four different ways (L-008, L-023, file 27 and the context envelope in file 24), and file 27's event record has no available_at. Which time model should every P02 record use?" | "Four times + basis (Recommended)" — "source_event_time, received_at, ingested_at and available_at on every record, each in native precision, with an available_at_basis field (e.g. archive_published, stated_release, retrieved). Context records add published_at. Matches T-1 and L-023 and fixes C2." |
| DEC-053 | "When a re-download finds that an archive file has changed (e.g. Binance's unlogged monthly rewrites), what available_at should the corrected version get?" | "Our retrieval time (Recommended)" — "We can only prove we knew the new values when we fetched them. Last-Modified is kept as provenance, since it can predate our knowledge and would create lookahead." |
| DEC-054 | "What should be the deterministic replay order for archived events?" | "available_at, then key (Recommended)" — "Sort by available_at, then source_id, instrument, source_event_time, native sequence or row index, and version. Follows L-008: 'sorts by availability and sequence, not vendor bar close alone.'" |
| DEC-055 | "Should the P02 contract also cover the context sources (FOMC, CPI, COT, GDELT, FRED, Coin Metrics), which contracts.md places at P04 / CMP-05?" | "Envelope now, semantics at P04 (Recommended)" — "P02 defines the shared ObservationEnvelope for capture and raw preservation (times, revision, rights, unavailability); P04 defines what the context values mean. Capture stays in one contract." |

Unchosen options: "File 27 fields only"; "Server Last-Modified"; "Event time, then key"; "Market events only".
