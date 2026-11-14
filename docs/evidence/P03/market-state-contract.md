# P03 market-state contract (draft): Kraken top-10 book state and replay checkpoints

[Task](../../tasks/TASK-P03-007.md) · [P03 phase](../../phases/03-market-state-and-ledger/README.md) · [Source map](source-map.md) · [P02 event contract](../P02/event-contract.md)

**Status: draft for review, 2026-11-14; revised after review the same day.** This is preparation only.
- It is accepted only with G03, after G02, and it implements nothing.
- Every value marked **Proposed** needs approval before anything is measured against it (G03).
- `B` and `Q` numbers refer to the [source map](source-map.md).

**Precondition.** The validity, venue-status and maintenance records this contract consumes are specified in [TASK-P02-014](https://github.com/akibrahimug/gladiators/blob/5a8ddbe/docs/tasks/TASK-P02-014.md). They are in the event contract §4.4 only on that task's branch, at `5a8ddbe`. Until that task is merged and Verified, this contract cites the branch.

**Scope.** This contract covers the state that CMP-03 rebuilds from Kraken WebSocket v2 `book` records, for BTC/USD and ETH/USD at depth 10, as captured under DEC-057. It also covers the replay checkpoints, and what CMP-03 hands to CMP-04, CMP-06, CMP-10 and CMP-11.
- It is a view of one venue's displayed top 10 levels. It is not the market's money ledger, and it is not a consolidated book. A displayed order is revocable intent (`c/27:7`; B9, B17; REQ-002, REQ-020).
- Trades are not modelled here: they become features later. Trade records pass through, and they advance `as_of` (§2).

## 1. Inputs and order

| Input | Record | Use |
| --- | --- | --- |
| Book messages | `NativeMarketEvent` `book`, `message_type` `snapshot` or `update` (event contract §4.4). Decimal strings, exactly as received | Levels and checksum |
| Trades | `NativeMarketEvent` `trade` | Advance `as_of` only |
| Validity | Book-validity `GapInterval`s per pair (DEC-075). **Each is known only at its `available_at`, the receive time of the frame that ends it** | The retrospective view (§3.2); a correction marker in the as-known stream (§3.1) |
| Venue status | `VenueStatus` (DEC-075), one per `status` frame | A new `connection_id` invalidates at once in the as-known stream. `system` is carried on the state |
| Maintenance windows | `MaintenanceWindow` (DEC-074, DEC-075) | Carried for R-4 accounting only, from its `available_at`. It **does not invalidate the book** |
| Clock | `quality_flags` and `timestamp_uncertainty_ms` on each record (T-5, T-6, DEC-067) | Carried on the state. These come from the capture's SNTP offsets in `events.jsonl` (`normalize()`'s `offsets`), so they are a dependency outside DEC-075's "raw frames alone" |
| Precision | Price and quantity decimals per pair (BTC/USD 1 and 8; ETH/USD 2 and 8) | The checksum. Today these are constants in `cli.py`, set from the `AssetPairs` snapshot of 2026-10-27, not records (source map G-9) |
| Quarantined records | `quality_state = quarantined`, or an unknown schema | Never applied. They are counted on the state (`quarantined_count`) and kept for audit (B10, L-008) |

**Order (DEC-054).** Records are replayed by the full DEC-054 key:
1. `available_at`;
2. `source_id`;
3. `instrument_id`;
4. `source_event_time`;
5. native sequence or row index;
6. `version`.

For live records the native sequence is the live key, `recv_ns × 100 + index`. That key is **Proposed** for recording as a decision (G-4, Q17).

**Derived records** fill the key as follows. **Proposed**, and part of the same decision request:

| Record | `available_at` | `source_id` | `instrument_id` | `source_event_time` | Sequence |
| --- | --- | --- | --- | --- | --- |
| Validity `GapInterval` | receive time of its ending frame | `SR-02` | the pair | `interval_start` | `recv_ns × 100 + 99`, so it sorts **after** the frame that ends it |
| `VenueStatus` | receive time | `SR-02` | `kraken:status` | receive time | `recv_ns × 100 + index` |
| `MaintenanceWindow` | `first_listed`, revised at `unlisted_at` (a new version) | `SR-02` | `kraken:status` | announced start | `event_id` |

**Intervals are half-open, `[start, end)`.** The snapshot that ends an interval lies at `end`, so it is outside the interval and can restore `VALID`.

## 2. State

There is one `BookState` per instrument (`kraken:BTC/USD:1`, `kraken:ETH/USD:1`) after each applied input. It has the following fields, adapted from B1.

| Field | Meaning |
| --- | --- |
| `instrument_id`, `venue` | As the input records |
| `as_of` | The `available_at` of the last input applied, on any channel for this venue: book, trade or `VenueStatus`. This is the state's watermark (B16) |
| `last_record_id`, `last_sort_key` | The last input applied, and its full DEC-054 key |
| `last_book_received_at`, `last_book_source_event_time` | Taken from the last `book` record (B3) |
| `snapshot_record_id` | The `record_id` of the snapshot the current book was built from. It **replaces** v10's `snapshot_update_id`, because Kraken books carry no update IDs (G-6) |
| `latest_applied_update_id` | Always **null**. It is kept, null, so that v10's field list stays visible (Q1) |
| `bids`, `asks` | Up to 10 levels per side. **Levels are keyed by decimal value**, so "100.0" and "100.00" are the same level, as in `Book.apply`. They are stored as `[price, qty]` with the received strings of the update that last set them. Bids are descending, asks ascending |
| `depth_by_level` | Ten slots per side; an empty slot is `null` |
| `best_bid`, `best_ask` | Level 1 of each side, or `null` |
| `book_health` | `UNINITIALISED`, `VALID` or `INVALID` (§3). There is no separate `SYNCING` state: an invalid book waiting for a snapshot is `INVALID` with its reason |
| `invalid_reason` | When not `VALID`: `initial`, `reconnect`, `checksum`, `bad_level`, `crossed`, `stale`, `venue_maintenance`. For a merged validity interval, the reason is the interval's first rule (`start`, `silence`, `reconnect`, `resync`, `open_at_end`); the full `evidence` is kept on the state |
| `sequence_integrity` | `checksum_verified` if the last message's CRC32 matched; `checksum_failed`; `unverified` before the first snapshot. Kraken has no sequence numbers, so integrity means the checksum (Q1) |
| `connection_id` | From the latest `VenueStatus` |
| `gap_count`, `resync_count`, `dropped_updates`, `quarantined_count` | Counts since the replay start. `dropped_updates` counts the updates not applied while `INVALID`: they are counted, never silently discarded (B11) |
| `timestamp_uncertainty_ms`, `clock_flags` | From the last record |
| `venue_status`, `in_maintenance_window` | From the latest `VenueStatus`, and whether `as_of` lies inside a `MaintenanceWindow` known by `as_of` |

**Staleness is checked by query, not by an input.** No record arrives during a silence. The as-known stream therefore exposes `state_at(t)`, which is the last emitted state with:
- `observed_age_ms = (t − last_book_received_at) / 10⁶`;
- `book_health = INVALID(stale)` if `observed_age_ms > STALE_MS`.

**`STALE_MS` = 15,000 ms (Proposed).** This is DEC-071's silence threshold, applied to book records only.
- Kraken's heartbeats are not records, and they show that the connection is alive, not that the book is current.
- On a quiet market a book can legitimately see no update for 15 s, so this value is especially in need of approval (Q6).

**Not inferred (Q2):**
- depth below level 10: the capture subscribes at depth 10 and truncates updates to 10 (`live.py`);
- queue position, order IDs and hidden or iceberg size: Kraken v2 `book` is aggregated by price level;
- other venues' books;
- book history before the first capture (B17);
- continuity across a missing segment. A segment that was never stored (no `raw_id`) is a gap, not continuous observation (B13). The P02-014 silence rule covers it when frames are missing.

## 3. Two outputs

### 3.1 As-known stream (for features, CMP-06 and CMP-10)

Each record is applied at its own `available_at`, so nothing is backfilled (B3, B11, event contract §6).

| From | Event | To |
| --- | --- | --- |
| `UNINITIALISED` or `INVALID` | Snapshot, checksum match, not crossed, no bad level | `VALID` |
| `UNINITIALISED` or `INVALID` | Snapshot, checksum mismatch | `INVALID(checksum)` |
| `VALID` | Snapshot (a resync or reconnect snapshot while still valid) | The book is replaced, as the capture does. `VALID` if the checksum matches; `INVALID(checksum)` if not |
| `VALID` | Update, checksum match, not crossed | `VALID` |
| `VALID` | Update, checksum mismatch | `INVALID(checksum)` |
| `VALID` | Update with a non-positive price, or a negative quantity | `INVALID(bad_level)`. **Proposed.** The update is not applied, and the record is flagged (B4) |
| `VALID` | Update leaving `best_bid ≥ best_ask` | `INVALID(crossed)`. **Proposed** (B4) |
| `VALID` | `VenueStatus` with a new `connection_id` | `INVALID(reconnect)` **at once**. A new connection means the previous one ended, and its book is not reused |
| `VALID` | `VenueStatus` `system = maintenance` | `INVALID(venue_maintenance)`. **Proposed.** This is CMP-03's own rule: the capture only measures maintenance time and does not invalidate on it |
| `VALID` | `state_at(t)` with `observed_age_ms > STALE_MS` | `INVALID(stale)` at `t` (query only) |
| `INVALID(checksum)`, `INVALID(reconnect)`, `INVALID(initial)` | Update | Not applied; `dropped_updates` + 1 (B2, Q-5) |
| `INVALID(stale)`, `INVALID(crossed)` | Update | **Applied** to the held book. The state becomes `VALID` again if the checksum matches and the book is not crossed. **Proposed.** The capture never resyncs for staleness or a crossed book, so snapshot-only recovery could leave the book invalid for hours. The CRC32 still verifies the whole top 10, so B2's "no silent reuse" holds |
| `INVALID(venue_maintenance)` | `VenueStatus` `system = online`, then a matching snapshot or update | `VALID` |
| Any | Validity `GapInterval` arrives, at its `available_at` | A **correction marker** naming the interval `[start, end)`. Earlier emitted states are not rewritten. If the book is still `VALID` at the marker, it stays `VALID` only if a snapshot has arrived at or after the interval's end. Otherwise it becomes `INVALID` with the interval's reason |

**Applying a message (as the capture does, `live.py` `_apply_book`):**
- **Snapshot:** both sides are cleared, then the bids and asks are applied. A snapshot is **not truncated**.
- **Update:** bids are applied, then asks. Quantity `0` removes the level, and anything else sets it. Each side is then truncated to 10.
- **Check:** after either kind, the CRC32 of the top 10 asks, ascending, then the top 10 bids, descending, is compared with the message's `checksum`. The comparison uses the pair's precision, with the decimal point and leading zeros removed (`book_checksum`).

While a book is `INVALID`, the derived primitives are `null`, never zero. Gaps are not zero activity (B4).

### 3.2 Retrospective validity view (for R-4, audit and case P3-12)

This view is computed after the fact, and is labelled as such. Never use it for a decision at time `t`.

A book is invalid over the union of:
- every validity `GapInterval` `[start, end)` from P02-014. These records are the **single source of interval validity** (DEC-075);
- CMP-03's own content checks: `checksum`, `bad_level`, `crossed`, `stale` and `venue_maintenance`, each from its detection until recovery.

CMP-03's invalid time is therefore **at least** P02-014's. Every difference has a named CMP-03 reason. Only content checks are added here: the rules for silence, reconnect and resync are not restated.

## 4. Derived primitives (B8)

These are computed only when `book_health = VALID`, and are `null` otherwise. Each carries `as_of`.
- `mid = (best_bid + best_ask) / 2`.
- `relative_spread = (best_ask − best_bid) / mid`.
- `top_imbalance = (bid_qty₁ − ask_qty₁) / (bid_qty₁ + ask_qty₁)`. It is `null` if the denominator is 0 (B4).
- **Exit marks** for CMP-04 (DEC-079): `mark_long = best_bid` and `mark_short = best_ask`. They are `null` when the book is not `VALID`, and CMP-04 then reports equity as `stale`.

**Arithmetic (Proposed):**
- **Precision:** Python `decimal` with 28 significant digits and `ROUND_HALF_EVEN`.
- **Serialisation:** results are serialised as plain decimal strings (`format(x, 'f')`). Sums and differences are exact; divisions are rounded by these rules.
- **Currency:** notional is in the quote currency, USD (DEC-039, DEC-080), with no FX.

**Exits.** Fallback exit prices that do not depend on this book belong to CMP-10 and CMP-12, not to CMP-03 (B6).

## 5. Replay checkpoints (Q4)

**Proposed.** A checkpoint is the **full replay state**, not only the `BookState`s. It holds:
- per instrument: `BookState`, `last_book_received_at`, any validity interval known to be open, and the counters;
- for the venue: the last `connection_id`, the latest `VenueStatus`, and all `MaintenanceWindow`s known so far, including their versions;
- **the cursor:** the full DEC-054 sort key of the last record applied. Records share an `available_at`, since one frame can carry both pairs, so a watermark alone is ambiguous (B10);
- **identity:**
  - a content hash of the inputs: SHA-256 over the canonical `to_json(include_clock=False)` of each replayed record in replay order;
  - the set of `raw_id`s;
  - the normaliser version and the contract version;
  - the config hash (`STALE_MS`, depth, precision, arithmetic);
- **coverage:** first and last `available_at`, records applied, quarantined and dropped counts, and the invalid time so far per pair (B16).

**Rules:**
- **When:** a checkpoint may be taken when **every** instrument is `VALID` or `UNINITIALISED`, so no recovery is in progress.
- **Resume:** resuming from a checkpoint and replaying the records after its cursor gives exactly the same states as replaying from the start (B10, B12). Case P3-09 tests this.
- **After a resume:** CMP-06 stays `DATA_BLIND` until it reconciles (B15). Checkpoints go to CMP-11 for audit, and to CMP-06 and CMP-10 as their resume points (B20).

## 6. Determinism rule (Q5, VAL-003)

**Proposed.** Two replays agree when they produce the same sequence of states, serialised as canonical JSON (sorted keys, decimal strings, no floats). Two conditions apply:
- the inputs have the same content hash (§5);
- the config is the same.

No `BookState` field comes from the replay's own clock, so no field is excluded from the comparison.

**Mutations.** A mutation is a change to a record's **order key or content**. Such a change must change the output, either as a different state sequence or as an `INVALID(checksum)` at the first affected update (B5, Q-6). Swapping two records' positions in a file, with their keys unchanged, is undone by the sort and must change nothing, as in event contract F-08.

## 7. Cases and expected outcomes (for G03)

| Case | Input | As-known expectation | Retrospective expectation |
| --- | --- | --- | --- |
| P3-01 | A snapshot, then updates with matching checksums | `VALID` throughout; the levels equal the capture's | No invalid time after the snapshot |
| P3-02 | One update dropped (v10 experiment 3), chosen so that its loss changes the next message's top 10 | The next checksum mismatches: `INVALID(checksum)`, no primitives, `dropped_updates` counts until the next snapshot | Invalid from the mismatch to the snapshot |
| P3-03 | A displayed bid wall at level 1, then cancelled (v10 experiment 1) | The level disappears; no inflow or outflow is inferred (B7, `c/27:7`) | — |
| P3-04 | A silence of more than 15 s | `state_at(t)` is `INVALID(stale)` once 15 s have passed. The `GapInterval` marker arrives at the end; the state is `VALID` only after a matching snapshot or update | Invalid over the interval `[start, end)` |
| P3-05 | A reconnect (a new `connection_id`) | `INVALID(reconnect)` at the `VenueStatus`; `VALID` at the pair's next matching snapshot | Invalid from the last frame before the reconnect to that snapshot (P02-014 rule c) |
| P3-06 | A resync snapshot within one connection | The book is replaced at the snapshot; the interval marker follows it | Invalid from the pair's last book frame before the snapshot (P02-014 rule d) |
| P3-07 | An update making `best_bid ≥ best_ask`, then one that uncrosses it with a matching checksum | `INVALID(crossed)`, then `VALID` (Proposed) | Invalid between the two |
| P3-08 | `VenueStatus` `maintenance`; separately, an announced `MaintenanceWindow` with data flowing | `INVALID(venue_maintenance)` (Proposed); inside the announced window the state stays `VALID` and `in_maintenance_window` is set | The window is excluded from R-4 (DEC-074), not counted as invalid |
| P3-09 | Checkpoint, then resume | Identical to a replay from the start | Identical |
| P3-10 | The same inputs twice; then two updates' `native_seq` swapped; then two rows swapped in a file with keys unchanged | Identical; then detected (as §6); then unchanged | Same |
| P3-11 | As-of replay at a decision time `t` inside a silence (v10 experiment 9) | Only records with `available_at ≤ t` are used. The state is the last emitted one, and `state_at(t)` gives `stale` once 15 s have passed. The later `GapInterval` is not visible at `t` | — |
| P3-12 | Run 3, replayed from its start, or from a checkpoint taken at the end of the preceding segment; one hour compared | — | CMP-03's invalid time for that hour is at least P02-014's, and each difference is attributed to a named CMP-03 reason (§3.2) |
| P3-13 | Updates that add a level, change it, then remove it (VAL-005) | Levels as expected after each; checksums match | — |
| P3-14 | An update with a negative quantity | `INVALID(bad_level)`; the update is not applied (Proposed) | Invalid until recovery |
| P3-15 | A quarantined book record | Not applied; `quarantined_count` + 1 | — |

## 8. Outputs to other components

- **CMP-06 (market regime) and CMP-10 (simulator):** the as-known `BookState`s, the primitives, and checkpoints as resume points. `DATA_BLIND` is CMP-06's state, derived from `book_health` (B14). `NO_EVENT` and `SOURCE_UNAVAILABLE` stay distinct: every CMP-03 invalidity is `SOURCE_UNAVAILABLE` (B9).
- **CMP-04 (ledger):** exit marks only (DEC-079). This adds CMP-03 as an input to CMP-04, which the [component register](../../traceability/components.md) does not yet list. It is recorded as open.
- **CMP-11 (audit):** the retrospective view and the checkpoints, with their identity.

## 9. Still open

| Item | Status |
| --- | --- |
| TASK-P02-014 merged and Verified | Precondition. Until then this contract cites its branch |
| The live ordering key, and how derived records fill the DEC-054 key (§1) | Proposed; needs a decision (G-4) |
| The instrument join: live `BTC/USD` against REST and archive `XBTUSD`. The stored `AssetPairs` gives `wsname` `XBT/USD` for `XXBTZUSD` (snapshot `9b33e378…195f`, 2026-11-14, read for [#41](https://github.com/akibrahimug/gladiators/pull/41)), so an alias table needs all three names | Open; needs a decision before any cross-source join (G-5) |
| Precision as a record, not a constant (G-9) | Open |
| `STALE_MS`; the crossed, `bad_level` and `venue_maintenance` rules; recovery from `stale` and `crossed` by update | Proposed; need approval before measurement (G03) |
| Decimal precision and rounding for the primitives | Proposed |
| Checkpoint contents, cursor and resume rule | Proposed |
| CMP-03 as an input to CMP-04 in the component register | Open; a register update when the contract is accepted |
| Trade corrections (B19, G-8) | None is known in Kraken v2 `trade`. Any that appears is quarantined (B10) |

**Relation to TASK-P03-001.** The board candidate TASK-P03-001 ("Book-state/replay contract, fixtures and invariants") is the acceptance-stage task for this subject. This draft is its preparation. After G02 it carries the contract forward and adds the fixtures.
