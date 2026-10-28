# P02 recovery results (RC-05 to RC-08)

[Task](../../tasks/TASK-P02-006.md) · [Capture and recovery](capture-and-recovery.md) · [Network capture](network-capture.md)

**Status: results, 2026-10-28**, at code `0c75c0b`. Offline only: no network calls (DEC-065). Not a G02 decision.

## 1. What was added

| Scenario | Implementation | Test evidence |
| --- | --- | --- |
| **RC-05** crash or restart during ingest | `RawStore` journals `started` before copying and `stored` after indexing. On restart, `recover()` finds `started` entries with no completion entry, removes `.part` files, and journals `recovered_incomplete`. Re-running the same ingest is idempotent (S-02a) | A crash part-way through a copy gives exactly the journal sequence `started`, `recovered_incomplete`, `started`, `stored`, and leaves one partial file, which is removed |
| **RC-06** disk full or write failure | A failed copy removes its `.part` file, journals `failed` with `write_failed:<error>`, and re-raises. `fetch()` stops without retrying into a full disk, giving a `GapInterval` with `SOURCE_UNAVAILABLE`. A failed live-segment ingest is recorded and the segment kept on disk (TASK-P02-005) | An injected ENOSPC leaves no partial file; `fetch()` makes 1 call and records `write_failed:OSError` |
| **RC-07** clock offset over 100 ms (T-5) | `live_records.normalize()` gives each live record `timestamp_uncertainty_ms` = the latest SNTP offset when it exceeds 100 ms. A record before the first sample is marked `clock_offset_unknown` | Offsets of 50 and 150 ms, and a record before its sample |
| **RC-08** clock offset over 1 s or 60 s (T-6) | Records are flagged `clock_abstain_intraday` above 1 s, and also `clock_abstain_daily` above 60 s. Dependent decisions must ABSTAIN | 1,500 ms and −70,000 ms |

**Tests:** `/usr/bin/python3 -I -B -m unittest discover -s tests` gives 61 OK on Python 3.9 and 3.12.

**Validation runner** (`run_validation.py`, held files): 19 of 19 runnable fixtures pass, and **10 of 10 recovery scenarios** pass (RC-01 to RC-08 with their variants). Report SHA-256 `e927a0bc…ad04`. It changed from `c920d603…` because F-02a's journal now includes the `started` marker.

## 2. Applied to the one-hour live capture

`live_records.normalize()` was run over the hour's `frames.jsonl` (`99f1c638…85b7`) using its SNTP samples:

- **297,446** live records (trade and book updates);
- **215,978 (72.6 %)** carry `timestamp_uncertainty_ms`, because the offset was above 100 ms (T-5);
- **0** records flagged for abstention: the maximum offset was 258 ms, below T-6's 1 s.

## 3. CV-11 status

All of RC-01 to RC-12 are now exercised. RC-09 to RC-11 were exercised live in TASK-P02-005, and RC-12 through F-09. **CV-11: Pass.**


## Decisions asked, 2026-10-28

The user's answers. Each question and the chosen option are quoted verbatim.

| Decision | Question (verbatim) | Chosen option: label — description (verbatim) |
| --- | --- | --- |
| DEC-064 | "When should the 7-day Kraken live capture (the rest of W-J) run? It's about 13 GB uncompressed (about 1 GB gzipped) and covers Kraken's announced maintenance on 2026-10-29, 08:01–08:16 UTC. It runs from this Mac, so the Mac must stay awake and online." | "Start it now (Recommended)" — "I launch it in the background from the fixed code (head of PR #30); it also exercises the maintenance exclusion and real reconnects." |
| DEC-065 | "While that runs, should I build the remaining recovery tests (RC-05 crash-completion marker, RC-06 disk-full injection, RC-07/RC-08 clock-offset handling on live records) as TASK-P02-006?" | "Yes (Recommended)" — "Offline code and tests only; no new network calls. Closes CV-11." |

Unchosen options: "You start it later"; "Skip the 7-day window"; "Not now".
