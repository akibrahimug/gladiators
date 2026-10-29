# P02 event contract: raw and normalized records

[Task](../../tasks/TASK-P02-001.md) · [P02 phase](../../phases/02-event-capture/README.md) · [Contracts checklist](../../architecture/contracts.md) · [Observability map](../P01/observability-map.md) · [`source_approval` records](../P01/source-approvals.md) · [Sample results](../P01/sample-results.md) · [Acceptance objectives](../P01/acceptance-objectives.md)

**Status: proposed contract, 2026-10-28, for the G02 reviewer.**
- **Covers:** P02 tasks 1 to 4.
- **Not an implementation:** it authorises no capture, storage or code. Live capture (the Kraken WebSocket) still needs its own authorisation.
- **No thresholds:** P02 task 5 selects them in the capture validation plan, and they are approved before any measurement. Capture-and-recovery behaviour (R-1 to R-4: disconnects, reconnects, restarts) belongs to `capture-and-recovery.md`.
- **G02:** passes only with capture and replay evidence from a later, authorised implementation (P02 exit gate).

**Decided by the user on 2026-10-28:** DEC-052 (time model), DEC-053 (revision timing), DEC-054 (replay order) and DEC-055 (context scope). They are quoted [below](#decisions-asked-2026-10-28).

**Proposed:** everything else marked **Proposed** is the coordinator's resolution of a source conflict. [§0](#0-source-conflicts) lists each conflict. The reviewer accepts or changes each one.

**Citation form.** Short quotes are from the preserved releases. "v10 10:9" means v10 `10-DATA.md` line 9. The reinstated sections are:
- L-008 (v4 `08-TRANSPORTERS.md:30`);
- L-023 (v5 `08-TRANSPORTERS.md:28–30`);
- L-010 (v4 `10-DATA.md:43–47`);
- L-024 (v5 `09-CONNECTORS.md:29–30`);
- L-025 (v5 `10-DATA.md:40–44`).

The other source files are v10 `08-TRANSPORTERS.md`, `09-CONNECTORS.md`, `10-DATA.md` and `ACCEPTANCE.md`; file 24, lines 94–118; and file 27.

## 0. Source conflicts

These were identified by `gladiator-spec-reader` on 2026-10-28.

| ID | Conflict | Sources | Resolution | Status |
| --- | --- | --- | --- | --- |
| C1 | The timestamp sets differ:<br>- `occurred/available/ingested` (L-008);<br>- `created/effective/available` (v10 08:9);<br>- four times including "processing-time" (L-023);<br>- `exchange_event/local_receive/ingest` (27:50);<br>- `published`/`first_available` (24:105–106) | v4 08:30; v10 08:9; v5 08:29; 27:50; 24:105–106 | Four times plus a basis (§3). `ingested_at` stands for "processing-time" | DEC-052; the alias is Proposed |
| C2 | `NativeMarketEvent` has no `available_at`; it appears only on `FlowFeature` | 27:50 vs 27:54; T-1 | `available_at` on every record | DEC-052 |
| C3 | The `_ns` integer fields conflict with "native precision … no padding" | 27:50; T-1 | Native unit plus a `source_time_unit` field (§3.1) | Proposed |
| C4 | "never heuristic length alone" vs the sample's check by digit count | v5 10:41; sample results | A declared era table (§3.1) | Proposed |
| C5 | The replay order key is not chosen | v4 08:30; v10 08:9; v5 08:28; 27:63 | `available_at`, then a fixed key (§6) | DEC-054 |
| C6 | Which `available_at` a detected revision gets | T-2a; DEC-048; 27:89 | Our retrieval time | DEC-053 |
| C7 | The raw layout has no rule for several versions of one file | v10 10:6, 10:13 | `supersedes_raw_id`; keyed by `raw_id` (§2) | Proposed |
| C8 | Dead-letter, quarantine and reject are all used | v4 08:30; v10 08:12, 08:18; Q-1 | Quarantine is the single invalid disposition (§5) | Proposed |
| C9 | The Q-2 classes are not mapped to R-1's `NO_EVENT`/`SOURCE_UNAVAILABLE` | Q-2; R-1; DEC-040; v10 09:29 | A `GapInterval` record that keeps all three classes (§4.5) | Proposed |
| C10 | Identity terms differ (`instrument` vs `native_symbol`; `event_id` vs `observation_id`), and symbols are reused | 27:50; 24:98; F-5e | `instrument_id` epochs and `record_key` (§3.2) | Proposed |
| C11 | The W-1 delisting rule needs a date that Kraken does not give | W-1; F-4j | The last bar is a lower bound on the delisting date, and there is no upper bound; after it the pair is `status_unknown` (corrected 2026-10-29, TASK-P02-008); the date stays open (§7) | Open |
| C12 | F-4j, F-5e and CPI timing are missing from DEC-045's P02 list | DEC-045; sample results | Adopted as P02 inputs (§7) | Proposed |
| C13 | `rights_id` (27) vs `rights_profile_id` (24); the map says "Unresolved until F-4" | 27:50; 24:111 | `rights_id` = the frozen `source_approval` ID | Proposed |
| C14 | Where context capture belongs | contracts.md; P02 README | Envelope in P02, meaning in P04 | DEC-055 |
| C15 | "Preserve integer/decimal precision" vs the float volumes in the Kraken archive | 27:50; F-4h | Store decimal strings as received; round only to compare (§4.1) | Proposed |
| C16 | Bar end: Kraken gives start only, Binance `close_time` is the last tick, and REST returns an incomplete bar | v10 10:9, 10:18; F-4i | Derived `bar_end`; incomplete bars dropped (§3.1) | Proposed |
| C17 | Envelope field names differ (`payload_hash` vs `raw_payload_hash`; `dataset_version`) | v4 08:30; v10 08:9; 27:50; 24:109 | Crosswalk (§3.3) | Proposed |

## 1. Scope

| Event type | Source and record | Status | Section |
| --- | --- | --- | --- |
| `BarEvent` | Binance Vision `klines` (SA-01); Kraken OHLCVT archive and REST `OHLC` (SA-02) | In the approved baseline | [§4.1](#41-barevent) |
| `TradeEvent` | Binance Vision `trades` (SA-01) | In the approved baseline (H-OF3) | [§4.2](#42-tradeevent) |
| `ObservationEnvelope` | FOMC, CPI, COT, GDELT, FRED/ALFRED and Coin Metrics (SA-04 to SA-09) | In the approved baseline; envelope only (DEC-055) | [§4.3](#43-observationenvelope-context) |
| `GapInterval`, `InstrumentEpoch` | Derived from all of the above | Proposed | [§4.5](#45-derived-records) |
| `NativeMarketEvent` (`book`, `trade`), `VenueStatus` | Kraken WebSocket v2 and REST `SystemStatus` (SA-03) | **Conditional**: capture not authorised | [§4.4](#44-live-types-conditional) |
| `OnChainEvent` | None (F-3; DEC-043) | Out of scope | — |

## 2. Raw preservation and versioning

Every retrieved object is preserved before any parsing. Sources:
- "Preserve raw bytes and receipt with SHA-256; never silently overwrite" (v10 10:13);
- "Persist append-only event journal" (L-023, v5 08:30);
- "record disputes and corrections as new dataset versions" (v10 10:17).

**`RawObject` record**, one per retrieved object:

| Field | Meaning | Basis |
| --- | --- | --- |
| `raw_id` | SHA-256 of the exact bytes | v10 10:13 |
| `source_id` | Source registry ID (SR-04, SR-05, …) | REQ-003; "Record feed identity in every observation" (L-024) |
| `source_approval_id` | The record that permits the retrieval (SA-01 …) | L-025; S-1 |
| `request` | URL or file path, and its query parameters | The L-010 manifest's "provider URL … access method" |
| `retrieved_at` | Our clock at the end of a successful retrieval (UTC, ns) | DEC-053 |
| `server_last_modified`, `server_etag` | As sent; null if absent | DEC-048 |
| `published_checksum`, `checksum_status` | The checksum the source publishes, and the result: `verified`, `mismatch` or `none_published` | DEC-044. SA-02's quarterly ZIP is `none_published` |
| `byte_length`, `media_type`, `http_status` | As received | — |
| `container_raw_id`, `member_path` | For a file extracted from a ZIP | Proposed |
| `supersedes_raw_id` | The earlier version at the same `request`, if the bytes differ | DEC-048 |

**Rules (Proposed; they resolve C7).**
1. **Append-only.** A raw object is never overwritten or deleted while any record refers to it. A changed object at the same `request` is stored as a new `RawObject`, with `supersedes_raw_id` set.
2. **Layout.** The layout is "`data/raw/{provider}/{ingest_date}/`" (v10 10:6), keyed by `raw_id`. Two versions never share a path.
3. **Checksum mismatch.** The object is quarantined, and nothing is parsed from it. How many retries are allowed, and when to declare the source `SOURCE_UNAVAILABLE`, are thresholds for P02 task 5.
4. **Archives.** Each ZIP member gets its own `raw_id`, linked to its container. Kraken's full-history parts are verified one by one and then joined, and the joined ZIP gets its own `raw_id`.
5. **Change detection.** On re-retrieval, `raw_id` is compared. A different hash at the same `request` is a revision (S-09). The `last_modified_after_period` flag is set only for evidence of a rewrite: the file is listed in the README changelog, or a re-retrieval found new bytes. A `Last-Modified` lag alone does not set it: in the retained S3 listings, 98 of 271 monthly files have lags over 14 days, 81 of them from a 2021-06-22 bulk backfill (TASK-P02-004).

## 3. Common envelope and time model

Every normalized record carries the fields below. The four times and the basis are fixed by DEC-052. Sources: L-008's envelope (v4 08:30); "Distinguish event-time, ingestion-time, available-at and processing-time" (L-023, v5 08:29); T-1.

| Field | Meaning | Rule |
| --- | --- | --- |
| `record_key` | Natural key: (`source_id`, `feed_id`, `native_symbol`, `source_event_time`, native ID or row index). **For bars, the bar start, not the row index (DEC-060)** | Proposed. It does **not** include the epoch or the version, so it stays stable when either changes (L-023 idempotency) |
| `record_id` | Hash of (`record_key`, `version`) | Proposed. One per version |
| `schema_version` | Contract version of this record type | An unknown version is quarantined (v10 08:18) |
| `source_id`, `feed_id` | The registry source, and the specific feed or file series (for example `binance:spot:klines:1d:monthly`) | Q-7: "Every record carries its venue and feed identity" |
| `producer` | The capture component and its version | L-008 `producer` |
| `venue` | `binance` or `kraken`; `official` for context | Venue-local only (S-6) |
| `market` | `CRYPTO_SPOT` or `CROSS_ASSET` | 24:100 |
| `native_symbol`, `instrument_id` | See [§3.2](#32-instrument-identity) | F-5e; DEC-039 |
| `source_event_time` | When the source says the event occurred, in its **native precision and unit** | T-1 ("no padding"). L-008's `occurred_at_utc`; 24's `source_event_time_utc` |
| `source_time_unit` | `s`, `ms`, `us` or `ns`, as declared for the source era | L-025, "never heuristic length alone" |
| `received_at` | Our clock when the bytes arrived. For an archive, that is `RawObject.retrieved_at` | T-1 |
| `ingested_at` | Our clock when this record was normalized | T-1; this stands for L-023's "processing-time" (Proposed) |
| `available_at` | The earliest time a decision may use this record | T-2, T-2a, DEC-052. It replaces 24's `first_available_at_utc` |
| `available_at_basis` | `archive_published`, `retrieved`, `stated_release`, `first_published`, `scheduled_release` or `live_receive` | DEC-052 |
| `raw_id`, `raw_locator` | The raw object, and the row or byte offset inside it | REQ-003; VAL-002 |
| `version`, `supersedes_record_id` | `version` increments when a revision replaces a record | DEC-048, DEC-053 |
| `quality_state` | `valid` or `quarantined` | §5 |
| `quality_flags` | Non-blocking notes, for example `zero_volume`, `last_modified_after_period` (§2 rule 5) | 24:113 |
| `rights_id` | The `source_approval` ID in force at retrieval | L-025 (Proposed; resolves C13) |

### 3.1 Time rules

**Precision (Proposed; C3).** Source times are stored as integers in their native unit, alongside `source_time_unit`. Our own clocks (`received_at`, `ingested_at`) use nanoseconds. File 27's `_ns` names alias these fields; a source time is never padded.

**Units (Proposed; C4).** Each source has a declared era table, and digit count is never the rule:
- **Binance spot:** `ms` for files covering dates before 2025-01-01, and `us` from 2025-01-01 (L-025; the dataset README).
- **Kraken:** `s` (the archive README).

A file whose digit count contradicts its era is quarantined as a schema mismatch (S-07). The sample's digit count was a verification, not the rule.

**`available_at` per source:**

| Source | `available_at` | Basis | Authority |
| --- | --- | --- | --- |
| Binance daily or monthly file | The file's `Last-Modified` + 6 h, flagged `available_at_estimated` (DEC-069: `Last-Modified` is only the earliest possible publication time); if `Last-Modified` is not recorded, `retrieved_at`. A later re-retrieval with different bytes gives the new version `retrieved_at` | `archive_published`, else `retrieved` | T-2a; DEC-053; DEC-069. **Consequence:** files backfilled on 2021-06-22 (every pre-launch month in the retained listings) make those older bars available only from 2021-06-22. See [§8](#8-for-the-g02-reviewer) |
| Kraken quarterly or full archive | The MANIFEST `generated` date (2026-10-01 for both Q3 and the full archive); `retrieved_at` if it is absent. **Consequence:** historical Kraken bars become available only from 2026-10-01 ([§8](#8-for-the-g02-reviewer)) | `archive_published` | T-2a; F-4i |
| Kraken REST `OHLC` | `received_at`, for completed bars only; the current incomplete bar is dropped (Proposed; C16) | `live_receive` | "completed bars only" (v10 10:18) |
| Any revised record | Our `retrieved_at` for the revised object | `retrieved` | DEC-053 |
| FOMC statement | The release time stated on the page ("For release at …") | `stated_release` | DEC-049 |
| FOMC minutes | First publication: the release time stated on the minutes page, else the observed time | `first_published` (or `stated_release`) | W-7; SA-04 ("Minutes keep the first-publication rule") |
| CFTC COT | First publication. The scheduled Friday 3:30 p.m. ET applies only when the observed release date matches the schedule. Otherwise the record takes the observed time, because "holidays may delay release" (SA-06) | `first_published`, or `scheduled_release` when matched | W-7. "`scheduled_at_utc` is separate from `published_at_utc`" (24:118) |
| CPI | **Open:** a P02 dependency (DEC-050, DEC-051) | — | — |
| GDELT, FRED/ALFRED, Coin Metrics | GDELT and FRED as W-7 and DEC-042; Coin Metrics uses `retrieved_at` (DEC-041) | various | W-7 |

**Bar end (Proposed; C16).**
- `bar_start` is stored as given.
- `bar_end` = `bar_start` + one interval, exclusive.
- Binance `close_time`, the bar's last tick, is kept as `native_close_time` and never used as `bar_end`.

### 3.2 Instrument identity

*Proposed; it resolves C10 and F-5e.*
- **`native_symbol`** is the venue's name for the instrument, as used in the request: `LUNAUSDT`, or `XBTUSD` for Kraken.
- **Kraken REST** returns its own key (`XXBTZUSD` for the `XBTUSD` request). It is kept as `native_response_key`. An alias table built from `AssetPairs` (`altname` ↔ key ↔ `wsname`), retrieved with each REST pull, joins REST and archive records on `native_symbol`.
- **`instrument_id`** is `{venue}:{native_symbol}:{epoch}`, with the epoch starting at 1.
- **New epoch.** A new epoch starts when the series has a gap of more than *G* days and its first price after the gap differs from the last price before it by more than a factor *K*, or when a listing record states an asset change.
- *G* and *K* are **placeholders**. Example values of 7 days and 10× are for P02 task 5 to set.
- **Review of breaks.** Each break is an `InstrumentEpoch` record (§4.5) and needs the reviewer's confirmation before research use.
- **Stability.** A later epoch change re-labels `instrument_id` and leaves `record_key` untouched.
- **Quote currency** is part of the instrument and is never converted (DEC-039).

### 3.3 Crosswalk from source fields

*Proposed; it resolves C17 and completes the field map.*

| Source field | Origin | Contract field or disposition |
| --- | --- | --- |
| `event_id` | L-008 | `record_id` |
| `causation_id`, `correlation_id` | L-008 | **Not used in P02.** Archived market data has no cause; reserved for internal events from P05 onward |
| `schema_version`, `producer` | L-008 | Same names |
| `occurred_at_utc`, `available_at_utc`, `ingested_at_utc` | L-008 | `source_event_time`, `available_at`, `ingested_at` |
| `dataset_version` | L-008 | `RawObject.raw_id`, plus `version` |
| `payload_hash`, `raw_payload_hash` | L-008; 27:50; 24:109 | `raw_id` (file level) and `raw_locator` (row level) |
| `type` | v10 08:9 | The record type (`BarEvent`, `TradeEvent`, …), versioned by `schema_version` |
| `created_at_utc`, `effective_at_utc` | v10 08:9 | `ingested_at`; `source_event_time` |
| `payload` | v10 08:9 | Kept in the raw object, not copied into the record |
| `bar_start_utc`, `bar_end_utc` | v10 10:9 | `bar_start`, `bar_end` (§3.1) |
| `provider` | v10 10:9 | `source_id` |
| `source_revision` | v10 10:9; 24:110 | `version` for archives; `source_revision` for context vintages |
| `currency` | v10 10:9 | `quote_currency` (§4.1) |
| `corporate_action_basis` | v10 10:9 | **Not applicable** to crypto spot; reserved for ETFs (deferred, DEC-043) |
| `observation_id`, `domain`, `market`, `symbol` | 24:98–102 | `record_id`; `domain` (§4.3); `market`; `native_symbol` |
| `published_at_utc`, `first_available_at_utc` | 24:105–106 | `published_at`; `available_at` |
| `original_event_timezone` | 24:108 | `original_event_timezone` (§4.3) |
| `rights_profile_id` | 24:111 | `rights_id` |
| `quality_flags` | 24:113 | `quality_flags` |
| `scheduled_at_utc` | 24:118 | `scheduled_at` (§4.3), kept separate from `published_at` |

## 4. Event types and field maps

### 4.1 `BarEvent`

The base is v10 10:9. Each `BarEvent` has the common fields (§3) plus:

| Field | Binance `klines` (12 columns, no header) | Kraken OHLCVT CSV (7 columns, no header) | Kraken REST `OHLC` (8 fields, plus `last`) |
| --- | --- | --- | --- |
| `bar_start` (`source_event_time`) | col 1 `open_time` (ms or µs, by era) | col 1 `timestamp` (s; "start of the bar") | field 1 `time` (s) |
| `interval` | From the file path (`1d`, …) | From the file name `PAIR_INTERVAL` (minutes) | The request parameter |
| `open`, `high`, `low`, `close` | cols 2–5 | cols 2–5 | fields 2–5 |
| `volume` (base) | col 6 | col 6, binary-float text | field 7, 8 decimals |
| `trade_count` | col 9 | col 7 | field 8 |
| `quote_volume` | col 8 | null | null |
| `taker_buy_base_volume`, `taker_buy_quote_volume` | cols 10, 11 | null | null |
| `vwap` | null | null | field 6 |
| `native_close_time` | col 7 | null | null |
| `quote_currency` | From the symbol (USDT) | From the pair (USD) | From the pair (USD) |
| Kept in the raw object only | col 12 `ignore` | — | `last` (pagination cursor) |

- **Numbers (Proposed; C15).** Prices and volumes are stored as **decimal strings exactly as received**. There is no float conversion ("Preserve integer/decimal precision", 27:50). The stored value is never rounded. **Comparison (F-4h), DEC-059, 2026-10-28:** prices and trade counts must match exactly, and volumes may differ by at most 10⁻⁹ relative. This supersedes the earlier rule, which rounded volumes to 8 decimals.
- **Nulls.** A field the source lacks is null, never zero ("nullable fields reflect nonapplicability rather than guesses", 27:50).
- **Sparse series.** Kraken omits no-trade bars: "the series is sparse, not padded". A missing bar produces a `GapInterval` (§4.5), never a `BarEvent`.
- **Zero-volume bar.** It is kept, with `quality_flags` containing `zero_volume`. It also produces a `GapInterval` of class `status_unknown` (DEC-040).

### 4.2 `TradeEvent`

Binance `trades`: 7 columns, no header. Each `TradeEvent` has the common fields (§3) plus:

| Field | Column | Note |
| --- | --- | --- |
| `native_trade_id` | 1 `id` | Contiguous on the sampled day; a break is S-05 |
| `price`, `qty`, `quote_qty` | 2, 3, 4 | Decimal strings |
| `source_event_time` | 5 `time` (ms or µs, by era) | — |
| `is_buyer_maker`, `side_semantics` | 6 | Stored as stated (`buyer_is_maker`). Never silently converted to a taker side (observability map) |
| `is_best_match` | 7 | Stored, not interpreted |
| `quote_currency` | From the symbol | — |

`available_at` follows the daily file's publication (§3.1). Trades are history only and never stand in for live events.

### 4.3 `ObservationEnvelope` (context)

This is the envelope only (DEC-055); the meaning of the values belongs to P04 (CMP-05). It is based on v10 file 24, lines 94–118. Each `ObservationEnvelope` has the common fields (§3) plus:

| Field | Meaning | Basis |
| --- | --- | --- |
| `domain` | `macro_release`, `news`, `event_calendar`, … | 24:99 |
| `reference_period` | The period the value describes, for example CPI for September 2026 | 24:118 ("reference period") |
| `scheduled_at` | The scheduled release time, if any; kept separate from `published_at` | 24:118 |
| `published_at` | The source's stated or observed publication time | DEC-052; 24:105 |
| `original_event_timezone` | As stated by the source, for example `America/New_York` | 24:108 |
| `source_revision` | The vintage or revision label, for example an ALFRED vintage date | 24:110 |
| `value_raw`, `value_unit` | As published, as decimal strings | 27:50 |
| `verification_status` | `VERIFIED`, `UNVERIFIED` or `QUARANTINED` | 24:112 |
| `coverage_scope` | What the observation covers | 24:114 |
| `availability_state` | `OBSERVED`, `NO_EVENT` or `SOURCE_UNAVAILABLE` | v10 09:29 ("Persist `NO_EVENT` versus `SOURCE_UNAVAILABLE` distinctly") |

### 4.4 Live types (Conditional)

These are specified so the contract is complete. **No capture is authorised.**
- Field names follow 27:50 and the Kraken WebSocket v2 documentation read in P01 (SR-02).
- The integrity details below come from that documentation, not from file 27. They must be checked again when capture is authorised.
- F-4a (Kraken's §9 and its retention ambiguity) applies, under SA-02 and SA-03.

| Type | Fields (27:50 and the Kraken documentation) | Integrity | Open |
| --- | --- | --- | --- |
| `NativeMarketEvent` `book` | `message_type` (snapshot/update). **Snapshots carry no venue timestamp**, so `source_event_time` = the receive time, flagged `source_time_is_receive_time` (an exception to §3; TASK-P02-006); `native_symbol`, price levels (`price`, `qty`), `size_unit` (venue-declared), `quote_currency`, `checksum`, `timestamp` (RFC3339 µs, kept native), `native_sequence` = null, `source_version` = the API version | The documented CRC32 over the top 10 levels. On a mismatch the book is invalidated and rebuilt. "invalidate and rebuild on gaps", 27:60 | There is no documented sequence (observability map), so events are ordered by receive order, with the checksum as the check |
| `NativeMarketEvent` `trade` | `message_type`, `trade_id` (as `native_sequence`), `price`, `qty`, `size_unit`, `side` (taker), `ord_type`, `timestamp`, `quote_currency`, `source_version` | `trade_id` continuity | F-4a |
| `VenueStatus` | `system` (`online`, `maintenance`, `cancel_only`, `post_only`, …), `api_version`, `connection_id`, `version`; REST `SystemStatus` `status` and `timestamp` | — | History begins only at capture (SA-03) |

### 4.5 Derived records

*Proposed; resolves C9.*

| Record | Fields | Notes |
| --- | --- | --- |
| `GapInterval` | `source_id`, `feed_id`, `instrument_id`, `interval_start`, `interval_end`, `gap_class` (`no_trade`, `data_gap`, `status_unknown`), `availability_state` (`NO_EVENT` for `no_trade`; `SOURCE_UNAVAILABLE` otherwise), `evidence`, `available_at` | Keeps all three DEC-040/Q-2 classes. R-1's two states are kept alongside, so nothing is lost |
| `InstrumentEpoch` | `venue`, `native_symbol`, `epoch`, `start`, `end`, `trigger` (gap/price rule, or a listing record), `evidence`, `review_status` (`proposed`, `confirmed`) | §3.2 |

## 5. Integrity scenarios and dispositions

**Dispositions (Proposed; resolves C8).**
- **Quarantine.** The record or file is kept with `quality_state = quarantined` and a reason. It is never used for features, and it can be replayed for audit. This is v4's dead-letter rule ("Dead-letter invalid events; never silently discard", L-008, v4 08:30). Q-1's "reject" is the same disposition ("Rejected records go to quarantine", Q-1).
- **Gap.** A `GapInterval` (§4.5). No entry opens during a `status_unknown` interval (DEC-040).
- **Valid.** The record is usable from its `available_at`.

| ID | Scenario | Detection | Expected result |
| --- | --- | --- | --- |
| S-01 | Published checksum mismatch | `checksum_status = mismatch` | The object is quarantined and no records are parsed. Retry limits are set by task 5 |
| S-02a | Same object re-ingested | Same `raw_id` | Idempotent: no new records (L-023) |
| S-02b | Duplicate timestamp in one file, same values | Two rows with the same `record_key` | **Both quarantined** (Q-1: "Reject duplicate timestamps"; ACCEPTANCE:5) |
| S-03 | Duplicate timestamp, different values | Same `record_key`, different content | Both quarantined, and the conflict is recorded ("duplicate conflicting keys", v10 10:14) |
| S-04 | Missing interval in a sparse archive | The expected grid minus the bars present | A `GapInterval`; 100 % of intervals are classified (Q-2 amended). Using the archive alone, every one is `status_unknown` |
| S-05 | Trade ID break | Non-contiguous `native_trade_id` | `GapInterval` `data_gap`; nothing is imputed |
| S-06 | Invalid OHLC, non-finite value, or timezone-naive time | Q-1 checks | Quarantined (Q-1; ACCEPTANCE:5) |
| S-07 | Unit contradicts the era table | Digit count against the era table | The file is quarantined (§3.1) |
| S-08 | Out-of-order rows in a file | `source_event_time` not monotone | Replayed in DEC-054's order, with the raw row index kept. No feature uses a bar before its `available_at` (v10 08:18) |
| S-09 | Revision found on re-download | A new `raw_id` at the same `request` | A new `version` with `available_at` = `retrieved_at` (DEC-053). The earlier version is kept. A replay at an earlier decision time sees the old version (27:89, experiment 9) |
| S-10 | Symbol reuse | §3.2 epoch rule | A proposed `InstrumentEpoch`, held for review |
| S-11 | Delisting | Last bar and listing status | Archived bars stop. The last bar is a **lower bound** on the delisting date, with no upper bound (F-4j; corrected 2026-10-29, TASK-P02-008). Until a delisting date is known, the pair is `status_unknown` after its last bar, not ended. "A delisting ends the pair's series" (Q-4) applies from the dated delisting |
| S-12 | Incomplete current bar (REST) | `bar_start` + interval > `received_at` | Dropped (§3.1) |
| S-13 | Unknown schema or column count | Column count, or a MANIFEST mismatch | Quarantined (v10 08:18). Manifest count differences are logged; the full archive has 1,759 pairs against the MANIFEST's 1,760 |
| S-14 | Source unavailable (HTTP error, 403, timeout) | Retrieval failure | A `GapInterval` with `SOURCE_UNAVAILABLE`. A 403 is not retried by other means (DEC-050, DEC-051) |
| S-15 | Live book checksum mismatch (Conditional) | CRC32 | The book is invalidated and resynchronised from a fresh snapshot; no feature is published during the uncertain interval (27:83, experiment 3) |
| S-16 | Future-available record | `available_at` > decision time | Invisible under the as-of rule (§6). "Out-of-order bars cannot create future features" (v10 08:18) |
| S-17 | Late or stale observation | `available_at` − `source_event_time` exceeds the lag limit (set by task 5), or a value repeats beyond its expected update | Flagged `stale` in `quality_flags` and never treated as current: "delayed market events must not be silently treated as current" (L-023, v5 08:29). Q-1 "stale … observations" |

**Fixtures.** Each fixture has an input, its hash or the location of its hash, the edit applied, and the expected counts. The data stays outside the repository (DEC-030); each fixture is recorded by its input hash and its expected output.

| Fixture | Scenario | Input (hash) | Edit | Expected |
| --- | --- | --- | --- | --- |
| F-01 | S-01 | `BTCUSDT-1d-2024-12.zip` (`82ec9021…`) | Flip one byte | 1 file quarantined; 0 records |
| F-02a | S-02a | The same file, ingested twice | None | 31 records, unchanged |
| F-02b | S-02b | `BTCUSDT-1d-2024-12.csv` | Duplicate row 5 | 2 rows quarantined; 30 valid |
| F-03 | S-03 | The same CSV | Duplicate row 5 with `close` changed | 2 rows quarantined; conflict recorded; 30 valid |
| F-04 | S-04 | `XBTUSD_1440.csv`, a member of `Kraken_OHLCVT_Full.zip` (`bc273e90…`) | None | 12 `GapInterval`s, all `status_unknown` (2013-10-11 … 2014-12-25) |
| F-05 | S-05 | `ETHUSDT-trades-2025-01-15.csv` (ZIP `0fc1d699…`) | Delete row 1,000 | 1 `data_gap`; 2,689,487 valid |
| F-06 | S-06 | `BTCUSDT-1d-2024-12.csv` | Two edits: set `high` < `low` in row 1; `close` = `NaN` in row 2. The parser checks values per row, so a bad value quarantines only its row | 2 rows quarantined; 29 valid |
| F-06b | S-06 (naive time) | A constructed context observation whose source time is an ISO string with no zone, for example a `published_at` of `2026-10-14T08:30:00` | Constructed. Binance's integer epoch column cannot hold a naive time; a non-integer there is a type error, which falls under S-13 | The record is quarantined |
| F-07 | S-07 | `BTCUSDT-1d-2025-01.csv` | Divide row 1's `open_time` by 1,000, giving ms in a µs-era file | The file is quarantined |
| F-08 | S-08 | `BTCUSDT-1d-2024-12.csv` | Swap rows 3 and 4 | 31 valid; the replay order is unchanged from the unedited file |
| F-09 | S-09 | `1INCHUSDT-1d-2022-03-08.zip`, the new version (`f7398aba…`). The old version is not served, so it is **constructed**: the new file with one value changed, standing in for the changelog's old checksum `4b9e5c51…` | Ingest the constructed old version, then the real new one | 2 versions. A replay before the second `retrieved_at` sees version 1 |
| F-10 | S-10 | LUNAUSDT 2022-04 to 2022-06 (`dc79e0d8…`, `bb63b3c8…`, `7d36dcce…`) | None | With the example placeholders *G* = 7 days and *K* = 10×: 1 proposed epoch break on 2022-05-31 (a 17-day gap, then 0.00005 → 1.00) |
| F-11 | S-11 | `ANKRGBP_1440.csv`, a member of the full ZIP | None | The series ends 2022-12-31. The delisting date is recorded as ≤ 2022-12-31 |
| F-12 | S-12 | `ohlc_XBTUSD_1440.json` (`6144e5f8…`) | None | The last bar (2026-10-27) is dropped; 57 bars kept |
| F-13 | S-13 | `BTCUSDT-1d-2024-12.csv` | Remove column 12 from every row | The file is quarantined |
| F-14 | S-14 | A recorded retrieval with `http_status` 403. The BLS header capture `bls_cpi.nr0.htm.hdr` serves as the example | Simulated: the failure is injected at the retrieval layer, not by editing a file | 1 `GapInterval` with `SOURCE_UNAVAILABLE`, and no retry by another route |
| F-15 | S-15 | Defined when capture is authorised | — | — |
| F-16 | S-16 | `BTCUSDT-1d-2024-12.zip` (`82ec9021…`); `Last-Modified` 2025-01-08 00:50:27 UTC | None. Replay at the decision time 2025-01-07 00:00 UTC | All 31 rows are invisible, since their `available_at` is after the decision time |
| F-17 | S-17 | `cftc_deacmesf.htm` (`0078b0e7…`), positions as of 2026-10-20 | Constructed: replay the same report as the latest COT observation at a decision time more than 14 days after its `available_at` (TH-5) | Flagged `stale` |

**VAL gaps (DEC-042).**
- **Q-1:** covered by F-02b, F-03, F-06 and F-06b.
- **Q-7:** covered by `source_id` and `feed_id` on every record (§3).
- **Q-3 and Q-4 (coverage):** in the capture validation plan (P02 task 5).

## 6. Replay

- **Inputs:** the `RawObject`s, the era tables, the alias table, the `InstrumentEpoch` records, and this contract's `schema_version`.
- **Order:** by `available_at`, then `source_id`, `instrument_id`, `source_event_time`, native sequence or row index, and `version` (DEC-054). This follows "sorts by *availability* and sequence, not vendor bar close alone" (v4 08:30).
- **As-of rule:** a replay at decision time *t* sees only records with `available_at` ≤ *t*. For each `record_key`, it sees only the highest `version` whose `available_at` ≤ *t* ("enforce `available_at <= decision_time`", v10 10:18).
- **Determinism:** the same raw objects and contract version produce byte-identical normalized output (27:63; VAL-003 at G03).
- **Checks:**
  - record counts by state: raw, accepted, quarantined, duplicates, and `GapInterval`s by class (L-010, v4 10:47);
  - a hash of the output.

## 7. P01 dependencies

| Item | Contract rule or status |
| --- | --- |
| F-4a (Kraken §9 and retention) | **Open, accepted limitation** (SA-02, SA-03). Raw REST and archive bytes are retained under it |
| F-4d (Kraken REST trade paging) | Not used: Kraken history comes from the archive, and REST is used for bars only |
| F-4f (intervals) | Only the 7 standard intervals are mapped; 30-minute files are ignored |
| F-4g (delisted pairs) | Included; the end of each series follows S-11 |
| F-4h (archive vs REST) | The comparison rule is in §4.1. Availability at bar close stays **Unresolved**, so REST bars use `live_receive` (see §8) |
| F-4i (bar-start stamps) | §3.1, §4.1 |
| F-4j (delisting dates) | **Open.** The last bar gives only a lower bound (corrected 2026-10-29). Proposed: a forward `AssetPairs` snapshot with each retrieval, to date future delistings (capture validation plan) |
| F-5c (Binance delisted symbols) | Included |
| F-5e (symbol reuse) | §3.2 (Proposed) |
| CPI release timing, current and historical | **Open** (DEC-050, DEC-051) |
| Historical FOMC meeting and minutes dates | **Open:** P02 dependency (sample results, step 3) |
| Historical COT release dates | **Open:** P02 dependency (sample results, step 3). Holiday delays matter (§3.1) |
| Q-2 as amended | S-04; `GapInterval` |
| DEC-048 (keep every version) | §2 rules 1 and 5; S-09 |

C12: F-4j, F-5e and CPI timing came out of TASK-P01-013 and P01-014, after DEC-045's list. This contract adopts them as P02 inputs.

## 8. For the G02 reviewer

**Proposed resolutions to confirm:** C1's alias, C3, C4, C7, C8, C9, C10 (the *G* and *K* placeholders), C12, C13, C15, C16 and C17, plus the coordinator rules in §2 (rules 3 to 5), §3.1 (COT schedule matching) and §3.2 (the alias table). The FOMC minutes and COT rules in §3.1 apply W-7's first-publication rule rather than changing it. **None changes an approved P01 value.**

**A consequence to note (not a proposal).**
- T-2a's default, the archive publication time, makes Kraken archive history unusable at its own dates, because the Q3 and full archives were both generated on 2026-10-01.
- T-2a allows bar-close timing only "if the venue documents availability at bar close" and the archive matches what was served at the time. That is F-4h, which is still Unresolved.
- Kraken history is what DEC-037 uses for the paper-simulation models, so F-4h decides whether Kraken backtests are possible.
- **Binance has a similar, smaller effect.** In the retained listings, every monthly file for months before the archive's launch was written on 2021-06-22. Under T-2a those bars are available only from 2021-06-22 (plus DEC-069's 6 h), so Binance research history before mid-2021 cannot be used at its own dates either. Most later files publish within days, though the listings show some late ones (for example LUNCUSDT 2024-07, 281 days after its month).
- The capture validation plan (P02 task 5) should propose how to close F-4h, for example by comparing forward REST bars received at bar close with the next archive release.

## Decisions asked, 2026-10-28

The user's answers to four questions. Each question and the chosen option are quoted verbatim.

| Decision | Question (verbatim) | Chosen option: label — description (verbatim) |
| --- | --- | --- |
| DEC-052 | "The sources name event timestamps four different ways (L-008, L-023, file 27 and the context envelope in file 24), and file 27's event record has no available_at. Which time model should every P02 record use?" | "Four times + basis (Recommended)" — "source_event_time, received_at, ingested_at and available_at on every record, each in native precision, with an available_at_basis field (e.g. archive_published, stated_release, retrieved). Context records add published_at. Matches T-1 and L-023 and fixes C2." |
| DEC-053 | "When a re-download finds that an archive file has changed (e.g. Binance's unlogged monthly rewrites), what available_at should the corrected version get?" | "Our retrieval time (Recommended)" — "We can only prove we knew the new values when we fetched them. Last-Modified is kept as provenance, since it can predate our knowledge and would create lookahead." |
| DEC-054 | "What should be the deterministic replay order for archived events?" | "available_at, then key (Recommended)" — "Sort by available_at, then source_id, instrument, source_event_time, native sequence or row index, and version. Follows L-008: 'sorts by availability and sequence, not vendor bar close alone.'" |
| DEC-055 | "Should the P02 contract also cover the context sources (FOMC, CPI, COT, GDELT, FRED, Coin Metrics), which contracts.md places at P04 / CMP-05?" | "Envelope now, semantics at P04 (Recommended)" — "P02 defines the shared ObservationEnvelope for capture and raw preservation (times, revision, rights, unavailability); P04 defines what the context values mean. Capture stays in one contract." |

Unchosen options: "File 27 fields only"; "Server Last-Modified"; "Event time, then key"; "Market events only".
