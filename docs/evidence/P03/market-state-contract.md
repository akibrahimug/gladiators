# P03 market-state contract (draft): Kraken top-10 book state and replay checkpoints

[Task](../../tasks/TASK-P03-007.md) · [P03 phase](../../phases/03-market-state-and-ledger/README.md) · [Source map](source-map.md) · [P02 event contract](../P02/event-contract.md)

**Status: draft for review, 2026-11-14. This is preparation only.**
- **Acceptance:** it is accepted only with G03, after G02. It implements nothing.
- **Values:** every value marked **Proposed** needs approval before anything is measured against it (G03).
- **References:** `B` and `Q` numbers refer to the [source map](source-map.md).

**Scope.** This contract covers the state CMP-03 rebuilds from Kraken WebSocket v2 `book` records, for BTC/USD and ETH/USD at depth 10, as captured under DEC-057. It also covers the replay checkpoints, and what CMP-03 hands to CMP-04, CMP-06 and CMP-10.
- **A venue view, not the market:** this is a view of one venue's displayed top 10 levels. It is not the market's money ledger, and it is not a consolidated book (B9, B17; REQ-002, REQ-020).
- **Not covered:** trades become features later. Trades are consumed here only as a pass-through of `NativeMarketEvent` `trade` records, with no state.

## 1. Inputs

| Input | Record | Use |
| --- | --- | --- |
| Book messages | `NativeMarketEvent` `book`, `message_type` `snapshot` or `update` (event contract §4.4). Decimal strings, exactly as received | Levels and checksum |
| Validity | Book-validity `GapInterval`s per pair (DEC-075; event contract §4.4, TASK-P02-014) | Forces `INVALID` over each interval |
| Venue status | `VenueStatus` (DEC-075) | Carried on the state; `maintenance` forces `INVALID` with reason `venue_maintenance` |
| Maintenance windows | `MaintenanceWindow` (DEC-074, DEC-075) | Carried on the state for R-4 accounting only. **Does not invalidate the book** |
| Clock | `quality_flags` and `timestamp_uncertainty_ms` on each record (T-5, T-6, DEC-067) | Carried on the state |
| Precision | Price and quantity decimals per pair, from the `AssetPairs` snapshot in force at the message's `available_at` (BTC/USD 1 and 8; ETH/USD 2 and 8 throughout the 30-day pull) | The checksum and `depth_by_level` formatting |

**Order.** Records are replayed in DEC-054's order: `available_at`, then `native_seq` (the live key `recv_ns × 100 + index`). This key is **Proposed** for recording as a decision (source map G-4, Q17).

## 2. State

One `BookState` per instrument (`instrument_id` `kraken:BTC/USD:1`, `kraken:ETH/USD:1`), after each applied input. It has these fields (B1, adapted):

| Field | Meaning |
| --- | --- |
| `instrument_id`, `venue` | As the input records |
| `as_of` | The `available_at` of the last input applied: the state's watermark (B16) |
| `last_record_id`, `last_native_seq` | The last input applied |
| `snapshot_record_id` | The `record_id` of the snapshot the current book was built from. It **replaces** v10's `snapshot_update_id`: Kraken books carry no update IDs (source map G-6) |
| `latest_applied_update_id` | Always **null**. It is kept, null, so v10's field list stays visible (Q1) |
| `bids`, `asks` | Up to 10 levels per side, as `[price, qty]` decimal strings exactly as received; bids descending, asks ascending |
| `depth_by_level` | Ten slots per side; an empty slot is `null` |
| `best_bid`, `best_ask` | Level 1 of each side, or `null` |
| `book_health` | `UNINITIALISED`, `SYNCING`, `VALID`, `INVALID` (§3) |
| `invalid_reason` | When not `VALID`: `initial`, `silence`, `reconnect`, `resync`, `checksum`, `crossed`, `venue_maintenance`, `stale`, `open_at_end` |
| `sequence_integrity` | `checksum_verified` if the last message's CRC32 matched; `checksum_failed`; `unverified` before the first snapshot. Kraken has no sequence numbers, so integrity means the checksum (Q1) |
| `observed_age_ms` | The time from the last book record's `received_at` to `as_of`, in ms |
| `gap_count`, `resync_count` | The number of validity `GapInterval`s, and of resync snapshots, since the replay start |
| `timestamp_uncertainty_ms`, `clock_flags` | From the last record |
| `venue_status`, `in_maintenance_window` | From the latest `VenueStatus`, and whether `as_of` lies inside an excluded `MaintenanceWindow` |

**Not inferred (Q2):**
- **Depth beyond 10 levels.** The capture subscribes at depth 10 and truncates to 10 (`live.py`). Nothing is said about level 11 or below.
- **Queue position, order IDs and hidden or iceberg size.** Kraken v2 `book` is aggregated by price level.
- **Other venues' books.**
- **Book history before the first capture** (B17).

## 3. State machine

```
UNINITIALISED --snapshot--> VALID?   (checksum match -> VALID; mismatch -> INVALID(checksum))
VALID --update, checksum match, not crossed--> VALID
VALID --update, checksum mismatch--> INVALID(checksum)
VALID --best_bid >= best_ask--> INVALID(crossed)
VALID --validity GapInterval starts--> INVALID(<interval evidence>)
VALID --VenueStatus system = maintenance--> INVALID(venue_maintenance)
VALID --observed_age_ms > STALE_MS--> INVALID(stale)
INVALID --snapshot after the interval ends, checksum match--> VALID
INVALID --update--> INVALID   (updates are not applied while invalid; B2, Q-5)
```

**Rules:**
- **Applying an update:** for each level, quantity `0` removes the price and anything else sets it. Then each side is truncated to 10, and the CRC32 of the top 10 asks and bids is compared with the message's `checksum`. This matches the capture exactly (`live.py` `Book.apply`, `truncate`, `book_checksum`).
- **No silent reuse (B2):** after `INVALID`, only a fresh snapshot can return the book to `VALID`, and only once every validity `GapInterval` covering it has ended.
- **Crossed book (B4):** `best_bid >= best_ask` makes the state `INVALID(crossed)` until the next snapshot. **Proposed.**
- **Staleness:** `STALE_MS` = **15,000 ms (Proposed)**, the same as DEC-071's silence. Kraken sends heartbeats every second, so a book with no record for 15 s is not current. The value needs approval (Q6).
- **Gaps are not zero activity (B4):** while `INVALID`, the derived primitives are `null`, never zero.

## 4. Derived primitives (B8)

These are computed only when `book_health = VALID`, in exact decimal arithmetic, and otherwise `null`. Each carries the state's `as_of`.

- `mid = (best_bid + best_ask) / 2`.
- `relative_spread = (best_ask − best_bid) / mid`.
- `top_imbalance = (bid_qty₁ − ask_qty₁) / (bid_qty₁ + ask_qty₁)`. It is `null` if the denominator is 0 (B4).
- **Exit marks** for CMP-04 (DEC-079): `mark_long = best_bid` and `mark_short = best_ask`. They are `unknown` when the book is not `VALID`.

Notional is in the quote currency, USD (DEC-039, DEC-080). There is no FX.

## 5. Replay checkpoints (Q4)

**Proposed.** A checkpoint is the full `BookState` per instrument at a watermark, plus the replay's identity:
- the input set (a hash over the sorted `record_id`s replayed);
- the contract version and config hash (`STALE_MS`, depth);
- the `AssetPairs` precision snapshot used.

A checkpoint may be taken only while the book is `VALID`.

**Resume rule:** resuming from a checkpoint and replaying the records after its watermark must give exactly the same `BookState` sequence as replaying from the start (B10, B12). This is tested (§7, case P3-09).

## 6. Determinism rule (Q5, VAL-003)

**Proposed.** Two replays agree when, with the same input records (by `record_id`) and the same config:
- they produce the same sequence of `BookState`s;
- serialised as canonical JSON (sorted keys, decimal strings unchanged, no floats);
- excluding only the fields that come from our own clocks at replay time. Today that is none. `ingested_at` is not part of `BookState`.

A mutation of the input order must be detected: the state sequence differs, or an `INVALID(checksum)` appears (B5, Q-6).

## 7. Cases and expected outcomes (for G03)

| Case | Input | Expected |
| --- | --- | --- |
| P3-01 | Snapshot, then updates with matching checksums | `VALID` throughout; levels equal those the capture held |
| P3-02 | One update dropped (v10 experiment 3) | The next checksum mismatches; `INVALID(checksum)`; no primitives until the next snapshot |
| P3-03 | A displayed bid wall at level 1, then cancelled (v10 experiment 1) | The level disappears; no inflow or outflow is inferred (B7, c/27:7) |
| P3-04 | A validity `GapInterval` (silence or reconnect) | `INVALID` from its start; `VALID` only at a matching snapshot after its end |
| P3-05 | A resync snapshot within a connection | `INVALID(resync)` over the derived interval, then `VALID` |
| P3-06 | An update making `best_bid >= best_ask` | `INVALID(crossed)` (Proposed) |
| P3-07 | No book record for longer than `STALE_MS` with the connection up | `INVALID(stale)` (Proposed) |
| P3-08 | `VenueStatus` `maintenance` | `INVALID(venue_maintenance)`. An announced `MaintenanceWindow` with data flowing stays `VALID` and is only flagged |
| P3-09 | Checkpoint, then resume | Identical to a replay from the start |
| P3-10 | The same inputs twice; then a swap of two updates | Identical outputs the first time; the swap is detected the second time |
| P3-11 | As-of replay at a decision time inside an interval (v10 experiment 9) | Only records with `available_at` at or before the decision time are used; the state at that time is the one reported |
| P3-12 | A real hour of run 3 (one segment, by `raw_id`) | `VALID` share and `INVALID` intervals agree with TASK-P02-014's records for that hour |

## 8. Outputs to other components

- **CMP-06 (market regime) and CMP-10 (simulator):** `BookState` and the primitives. `DATA_BLIND` is CMP-06's state, derived from `book_health` (B14).
- **CMP-04 (ledger):** exit marks only (DEC-079). This adds CMP-03 as an input of CMP-04, which the [component register](../../traceability/components.md) does not list yet. It is recorded as open.
- **CMP-11 (audit):** checkpoints, with their replay identity.

## 9. Still open

| Item | Status |
| --- | --- |
| Live ordering key `recv_ns × 100 + index` (G-4) | Proposed here; needs a decision |
| Instrument join: live `BTC/USD` against REST and archive `XBTUSD` (G-5). Note that `AssetPairs` gives `wsname` `XBT/USD`, while WebSocket v2 uses `BTC/USD`, so the alias table needs both names | Open; needs a decision before any cross-source join |
| `STALE_MS`, and the crossed-book rule | Proposed; need approval before measurement (G03) |
| Checkpoint format and resume rule | Proposed |
| The component register's CMP-03 → CMP-04 input | Open; a register update when accepted |
| Trade corrections (B19, G-8) | Not seen in Kraken v2 `trade`; none is modelled. If one appears it is quarantined (B10) |
