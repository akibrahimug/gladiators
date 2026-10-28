# P02 recovery results (RC-05 to RC-08)

[Task](../../tasks/TASK-P02-006.md) · [Capture and recovery](capture-and-recovery.md) · [Network capture](network-capture.md)

**Status: results, 2026-10-28**, at code `537e8d3`. Offline only: no network calls (DEC-065). Not a G02 decision.

## 1. What was added

| Scenario | Implementation | Test evidence |
| --- | --- | --- |
| **RC-05** crash or restart during ingest | `RawStore` is opened either **read-only**, with no lock and no changes (for analysis), or as the **single writer**: it takes an exclusive lock on `.writer.lock` and holds it until `close()`. Each ingest journals `started` before copying, and `stored` after indexing. On opening, `recover()` runs. It is safe because no other writer can be mid-ingest. It: closes each `started` that has no completion entry, journalling `recovered_incomplete` (or `recovered_complete` when the object was already indexed); removes `.part` files; and tolerates a truncated last journal or index line. Re-running the ingest is idempotent | **Crash part-way through a copy:**<br>- journal `started`, `recovered_incomplete`, `started`, `stored`;<br>- 1 partial file removed;<br>- the re-ingested object is **byte-identical** to the source and to an uncrashed ingest of the same file (Q-6) |
| **RC-06** disk full or write failure | One failure path covers the copy, the hash check and the rename. It removes the `.part` file, journals `failed` with its `raw_id` (`write_failed:<error>` or `copy_hash_mismatch`), and re-raises. Journal and index lines are each written in one checked `os.write`. When a writer opens the store, a cut-off final line is cut back to the last newline and kept beside the file, so it cannot merge with the next line. `fetch()` writes its temp file inside the same `try`, stops without retrying into a full disk, and records a `GapInterval` with `SOURCE_UNAVAILABLE` | **Injected ENOSPC:**<br>- no partial file;<br>- `fetch()` makes **1 call**, with `write_failed:OSError` and `SOURCE_UNAVAILABLE`;<br>- the earlier mislabelling of a failed hash check is fixed |
| **RC-07** clock offset over 100 ms (T-5) | `live_records.normalize()` sets `timestamp_uncertainty_ms` = the latest SNTP offset when it exceeds 100 ms. A sample applies from its own time. A latest sample older than 60 min adds `clock_offset_stale` | Offsets of 50 and 150 ms; a sample that arrives after the frame; a sample 2 h old |
| **RC-08** clock offset over 1 s or 60 s (T-6) | Records are flagged `clock_abstain_intraday` above 1 s (absolute), and also `clock_abstain_daily` above 60 s. A latest sample older than 1 min also adds `clock_abstain_intraday`, because T-6 requires at most 1-minute logging for intraday decisions | −1,500 ms; 70,000 ms; a sample 2 min old |

**Also fixed in the live normalizer:**
- **Exact strings:** values are kept exactly as received (C15). JSON numbers are read as their text, so `0.00000010` stays `0.00000010`.
- **Snapshots:** book snapshots are emitted, with `message_type` `snapshot` or `update`.
- **Fields:** `quote_currency` and `source_version` are added.
- **Book sequence:** `native_sequence` is null for the book. The key `native_seq` = `recv_ns` × 100 + index, which is stable however the frames are segmented.
- **Timestamps:** RFC 3339 is parsed for any fraction length, so it works on Python 3.9.

**Proposed, for the user:** a live record that arrives before the first SNTP sample is flagged `clock_offset_unknown` and `clock_abstain_intraday`. This is conservative, but it is the coordinator's rule.

**Tests:** `/usr/bin/python3 -I -B -m unittest discover -s tests` gives 68 OK on Python 3.9 and 3.12. The tests cover lock refusal, cut-off-line repair, read-only opening, `recovered_complete`, copy-hash-mismatch labelling, rename failure and `fetch` temp-file failure.

**Validation runner** (`run_validation.py`, held files; runner code as committed in `b4182f0`):
- 19 of 19 runnable fixtures pass;
- **10 of 10 recovery scenarios pass**;
- the report, SHA-256 `b21845b5…3ef2`, is byte-identical across two separate runs.

The hash differs from `c920d603…` (TASK-P02-002) for two reasons:
- F-02a's journal now includes the `started` marker;
- the recovery section gained RC-05, RC-06 and RC-07/RC-08 and lost its "not exercised" list.

## 2. Applied to the one-hour live capture

The command was `/usr/bin/python3 -I -B tools/apply_clock_1h.py src <scratchpad>/net-live-1h` (the script is committed in `tools/`), run over `frames.jsonl` (`99f1c638…85b7`) with its 55 successful SNTP samples:

- **297,450** live records: 4 book snapshots, 292,861 book updates and 4,585 trades. The earlier count of 297,446 left out the snapshots.
- **215,982 (72.6 %)** carry `timestamp_uncertainty_ms`, because the offset was above 100 ms (T-5).
- **0** values are in exponent form. **292,865 of 292,865** book checksums recomputed from the stored strings match the venue's.
- **22,995 (7.7 %)** are flagged `clock_abstain_intraday`, because the latest sample was **more than 1 minute old** (T-6). The capture queried once a minute (DEC-063), and:
  - 49 of 54 intervals came out at 60–61 s, after processing overhead;
  - 5 queries failed, giving gaps of about 125 s.
- **The user's decision (DEC-066):** query every 30 s from the next capture. No record exceeded the 1 s or 60 s offset limits.

**Do not open the running 7-day store with this code.** The 7-day capture (DEC-064) runs code `5b69e7f`, which takes no writer lock. Until it ends, about 2026-11-04 10:35 UTC, open `~/gladiator-data/live-7d/store` only with `RawStore(..., read_only=True)`. A writer open would remove the capture's in-progress `.part` copy and write into its journal.

## 3. CV-11 status

All of RC-01 to RC-12 are now exercised:
- RC-01 to RC-08 offline, in the runner;
- RC-09 to RC-11 live, in TASK-P02-005;
- RC-12 through F-09.

RC-05's Q-6 metric (byte-identical output) is checked. **CV-11: Pass.** Real-disk ENOSPC and two-process contention are simulated or locked, not reproduced.

## Decisions asked, 2026-10-28

The user's answers. Each question and the chosen option are quoted verbatim.

| Decision | Question (verbatim) | Chosen option: label — description (verbatim) |
| --- | --- | --- |
| DEC-064 | "When should the 7-day Kraken live capture (the rest of W-J) run? It's about 13 GB uncompressed (about 1 GB gzipped) and covers Kraken's announced maintenance on 2026-10-29, 08:01–08:16 UTC. It runs from this Mac, so the Mac must stay awake and online." | "Start it now (Recommended)" — "I launch it in the background from the fixed code (head of PR #30); it also exercises the maintenance exclusion and real reconnects." |
| DEC-065 | "While that runs, should I build the remaining recovery tests (RC-05 crash-completion marker, RC-06 disk-full injection, RC-07/RC-08 clock-offset handling on live records) as TASK-P02-006?" | "Yes (Recommended)" — "Offline code and tests only; no new network calls. Closes CV-11." |
| DEC-066 | "T-6 requires a clock reading at most 1 minute old for intraday decisions, but DEC-063 allows one SNTP query per minute. The real gaps come out at 60–61 s, plus about 125 s whenever a query fails (5 of 60 did). As a result, 7.7% of the 1-hour capture's records are flagged to abstain for intraday use. Daily decisions are unaffected. How should this be resolved?" | "Query every 30 s (Recommended)" — "Two small UDP queries a minute to time.apple.com. One failed query no longer breaks the 1-minute rule. Amends DEC-063; applies from the next capture (the running 7-day run keeps 60 s)." |

Unchosen options:
- DEC-064: "You start it later"; "Skip the 7-day window".
- DEC-065: "Not now".
- DEC-066: "Keep 60 s, allow 5 s slack"; "Keep as is".
