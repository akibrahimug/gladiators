# P02 capture integrity and recovery design

[Task](../../tasks/TASK-P02-004.md) · [Event contract](event-contract.md) · [Capture validation plan](capture-validation-plan.md) · [Acceptance objectives](../P01/acceptance-objectives.md) · [P02 phase](../../phases/02-event-capture/README.md)

**Status: proposed design, 2026-10-28, for the G02 reviewer.** This file is the P02 deliverable "a capture integrity and recovery design covering gaps, reconnects, duplicates, persistence, retention, and auditability". It authorises no capture and contains no code.

Thresholds in this file are of two kinds:
- **approved P01 values**, cited by their ID;
- **proposed values**, marked **Proposed**. These are listed in the [capture validation plan](capture-validation-plan.md#3-thresholds), and each must be approved before any measurement.

## 1. Retrieval modes

| Mode | Sources | Authorised? | Trigger |
| --- | --- | --- | --- |
| **A. Archive pull** | Binance Vision files; Kraken OHLCVT ZIPs | Yes, for the sample plan (DEC-035). Further pulls need a task that names them | Explicit invocation only (DEC-044) |
| **B. REST pull** | Kraken `OHLC`, `AssetPairs`, `SystemStatus` | One-off keyless calls on explicit invocation (DEC-044). A **scheduled** pull (for example daily) is not authorised; see the [validation plan](capture-validation-plan.md#4-f-4h-closure-route) | Explicit invocation |
| **C. Live stream** | Kraken WebSocket v2 `book`, `trade` and `status` (W-4) | **No.** Sample step 2 needs its own authorisation | — |
| **D. Context pull** | FOMC, COT, GDELT, FRED/ALFRED, Coin Metrics | As mode A or B. A source that returns HTTP 403 is not read (DEC-050, DEC-051) | Explicit invocation |

## 2. Persistence and auditability

- **Raw first:** every retrieval writes its `RawObject` (event contract §2) before any parsing, and the write is complete only after the SHA-256 is recorded.
- **Journal:** an append-only retrieval journal records each attempt with its time, `request`, `http_status`, `byte_length`, `raw_id` and outcome. A failed attempt is journalled too, as the basis for `GapInterval`s (R-1).
- **Idempotent re-runs:** a re-run of the same retrieval adds a journal line. It adds no new records unless the bytes differ (S-02a, S-09).
- **Audit:**
  - every normalized record traces through `raw_id` and `raw_locator` to its bytes, and through the journal to its retrieval (VAL-002);
  - every quarantine has a reason code;
  - the coverage report (Q-3) is produced per snapshot.

## 3. Failure and recovery scenarios

| ID | Scenario | Mode | Detection | Recovery | Recorded as | Objective |
| --- | --- | --- | --- | --- | --- | --- |
| RC-01 | HTTP 5xx, timeout or connection reset | A, B, D | Journal outcome | Retry with exponential backoff, up to *N_retry* attempts (**Proposed**: 3; delays 30 s, 2 min, 10 min) | A `GapInterval` with `SOURCE_UNAVAILABLE` if all retries fail (R-1) | Reported |
| RC-02 | HTTP 403, 401 or 429 | A, B, D | Status code | **No retry by another route.**<br>- 403 and 401: stop and record (DEC-050).<br>- 429: wait for the `Retry-After` time, then one retry (DEC-044, reasonable load) | `SOURCE_UNAVAILABLE`, with the reason | — |
| RC-03 | Truncated or partial download | A | `byte_length` ≠ `Content-Length`, or ZIP CRC failure | Delete the partial file and resume or retry (as RC-01) | Journal entry; no `RawObject` until complete | — |
| RC-04 | Published checksum mismatch | A | `checksum_status` | Quarantine the object, then retry as RC-01. A repeated mismatch is recorded as a source fault (S-01) | Quarantine and journal | Zero mismatched objects parsed |
| RC-05 | Process crash or restart during ingest | All | A journal entry with no completion marker | Re-run from the raw object. Ingest is idempotent (S-02a) | Journal | Re-run output byte-identical (Q-6) |
| RC-06 | Disk full, or write failure | All | I/O error | Stop retrieval, and journal the error if possible. No partial `RawObject` is kept | `SOURCE_UNAVAILABLE` for the window | — |
| RC-07 | Host clock offset > 100 ms | All | NTP log, at least hourly (T-5) | Continue; each record gets `timestamp_uncertainty_ms` | Field on records | T-5 |
| RC-08 | Host clock offset > 1 s (intraday) or > 60 s (daily) | All | NTP log | Dependent decisions `ABSTAIN` (T-6). Capture continues, with the uncertainty recorded | Field on records | T-6 |
| RC-09 | WebSocket disconnect (mode C, Conditional) | C | Socket close or heartbeat loss | Reconnect, resubscribe with a snapshot, and resume only once the book checksum holds (R-2, Q-5) | `GapInterval` from disconnect to valid book (R-1) | R-3: p95 ≤ 60 s |
| RC-10 | Book checksum mismatch (mode C) | C | CRC32 | Invalidate the book and resubscribe with a snapshot. No feature is published during the uncertain interval (S-15, Q-5) | `GapInterval` `data_gap` | Zero books accepted after an unresolved mismatch (Q-5) |
| RC-11 | Venue maintenance (mode C) | C | `status` channel or `SystemStatus` | Pause; the time is excluded from R-4 | `VenueStatus` and `GapInterval` | R-4 |
| RC-12 | Revised archive file found on re-pull | A | New `raw_id` at the same `request` | New version (S-09, DEC-053) | Version chain | — |

## 4. Retention

- **Raw objects:** kept for as long as any normalized record or experiment refers to them (DEC-048: every version kept).
- **Accepted limitations:** retention runs under the accepted limitations in SA-01 to SA-09. For Kraken, F-4a still applies.
- **Budget:**
  - Live capture: **R-5, ≤ 2 GB compressed per pair per day.** If it is exceeded, reduce depth or pairs, never the integrity checks.
  - Archive sources: no budget is set. For scale, the P01 sample used 10.1 GB for the full Kraken history plus the Q3 file.
  - A disk-use report runs with each retrieval.
- **Redistribution:** none (DEC-030). Raw objects and fixtures stay outside the repository.

## 5. What this design does not cover

- The book-state builder and replay checkpoints. These are P03 (CMP-03).
- Live capture code and its scheduling. Both need an authorised implementation task (TASK-P02-002).
