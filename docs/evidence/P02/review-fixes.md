# P02 — Fixes for the Codex reviews of PRs #23 to #32

TASK-P02-008. On 2026-10-29 Codex relayed 11 independent reviews of PRs #23 to #32, each pinned to its exact revision. PRs #23, #24, #26 (both revisions), #27 and #28 had no new findings.

Delivery IDs, all acknowledged on 2026-10-29. Each is PR : base : head, with the hashes shortened here:
- `pr23:8177337…:61a0cfe`; `pr24:8177337…:f7a0482`; `pr25:8177337…:34f1cda`;
- `pr26:8177337…:e92dcd4`; `pr26:8177337…:03fc85c`; `pr27:8177337…:2a27020`; `pr28:8177337…:192df96`;
- `pr29:8177337…:230b1b7`; `pr30:8177337…:5b69e7f`; `pr32:44867bb…:8e8630e`;
- `pr31:81773371246b825c…:49c20bc`. This one is relayed with a truncated base hash. It is the PR #31 review against the same base, `8177337`.

This page records each actionable finding and its fix. The PR #32 finding was fixed on that PR's own branch (TASK-P02-007). Reviews are feedback; none of them, and none of these fixes, passes a gate.

## Findings and fixes

| Review (head) | Finding (Codex, P2) | Fix | Test or evidence |
| --- | --- | --- | --- |
| PR #25 (`34f1cda`) | `sample-results.md:55`: `Last-Modified` is server metadata, not proof of when the file became public. Using it as `available_at` risks using data before it could be had | Asked the user; **DEC-069**: `Last-Modified` + 6 h, flagged `available_at_estimated`. Applied in `records.py` and the [event contract §3](event-contract.md) Binance row; the sample-results row is corrected | `test_valid_month_and_available_at`; `test_revision_with_last_modified_takes_retrieval_time` |
| PR #25 (`34f1cda`) | `sample-results.md:79`: the last bar is a lower bound on the delisting date, not an upper bound; an archive cut gives no upper bound | Corrected in the F-4g/F-4j row, in the event contract (C11, S-11, F-4j), in the capture validation plan and results, and in the W-F report string (now `>= last bar (lower bound); status_unknown after`). After its last bar a pair's status is unknown, not delisted (DEC-040), so W-1 must not drop it there | Validation report W-F |
| PR #29 (`230b1b7`) | `analysis.py:143`: `entry_blocked` blocks only on `status_unknown`, so a current `data_gap` (for example a quarantined price bar) still allows new entries, against 10-DATA:35 and :40 | `entry_blocked` now blocks on a `data_gap` or `status_unknown` that overlaps the **last completed interval** [D − step, D). Before, it checked [D, D + step), the bar still forming at D (10-DATA:18, completed bars only). `no_trade` still does not block. Only gaps known by D (`available_at` <= D) count, so a replay cannot block on a gap found later (10-DATA:18); a bar missing at D is itself a gap known at D. For a late-publishing feed (DEC-069), a last completed bar not yet visible at D blocks entries until it is | `test_stale_and_entry_blocked` (`data_gap` and `status_unknown` on D − 1 block, as does a multi-interval gap overlapping D − 1; `no_trade`, a gap on the forming bar and a gap recorded after D do not) |
| PR #30 (`5b69e7f`) | `live.py:293`: a malformed book update mutates the book, raises, and is logged as a parse error while the book stays valid with unverified levels, counted as valid R-4 time | Book handling is wrapped: any parse or check error invalidates the book (`parse_error`) and resyncs it, under the existing resync cap, before the error is re-raised and counted. Recovery from a parse error has its own bucket, `recovery_parse_error_s`; `resyncs` counts only resubscribes actually sent | `test_malformed_update_invalidates_and_resyncs`; `test_malformed_snapshot_and_resync_cap` |
| PR #31 (`49c20bc`) | `rawstore.py:167`: a short append leaves a fragment; later appends in the same process join it, so a reopen fails with `JSONDecodeError` | `_append` records the file's end before writing and truncates back to it on a short or failed write. If that rollback fails, the store refuses all writes until it is reopened, when `_repair_tail` cuts the fragment. Because a rolled-back store keeps going, objects are now indexed before they are registered in memory, so a retried `member()` or ingest writes its index line | `ShortAppendTests`: Codex's scenario (short index write, two more fetches, reopen); a raising journal write; a retried `member()`; a failed rollback |
| PR #32 (`8e8630e`) | `TASK-P02-007.md:5`: the card is Verified without an independent review | Fixed on PR #32: reviewed, 1 Medium and 4 Low fixed, re-reviewed, then Verified | [TASK-P02-007](../../tasks/TASK-P02-007.md) |

## Effect on the running captures

The fixes are not applied to the running jobs. They run from `~/gladiator-capture` at `5b69e7f`, which is left unchanged (Codex: "do not interrupt or modify the running captures").
- **7-day live capture (DEC-064):** the book defect fires only on a parse error. As of 2026-10-29 its `events.jsonl` has no `parse_error` events. The G02 analysis rechecks this over the full window. If any appear, the affected book time is counted as invalid.
- **30-day REST job (DEC-068):** the short-append defect needs a short write to `index.jsonl` or `journal.jsonl`. The analysis checks that the store reopens read-only, and reports any interior malformed line.
- **DEC-069** changes only how the held Binance files are normalized. It changes no capture.

## Consequences of DEC-069

- **Scope:** all Binance records with basis `archive_published` move by 6 h and carry `available_at_estimated`. That covers klines and trades, including W-A, W-B and W-D's 2,689,488 trades. Revisions keep our retrieval time without the flag (DEC-053). Kraken archives keep the MANIFEST `generated` date.
- **TH-6:** `late` is measured from `available_at`, so a daily Binance file is now flagged late when its `Last-Modified` is more than 42 h after the period end, not 48 h. This is the conservative reading of TH-6 under DEC-069. No held Binance file is flagged late before or after the change: W-A and W-D both have 0. W-H's 55 `late` flags are on Kraken REST bars, which DEC-069 does not touch.
- **Not adopted:** the review suggested `min(Last-Modified + 6 h, retrieved_at)`. Our own download proves the file was available, so this would be a little less conservative for files we fetch within 6 h of publication. It is not part of DEC-069 as answered, so it is left for the user. It affects no held file: every one was fetched long after its `Last-Modified`.

## Decision asked, 2026-10-29

Asked with the interactive question tool. The question and options, verbatim:

| Decision | Question (verbatim) | Chosen option: label — description (verbatim) |
| --- | --- | --- |
| DEC-069 | "Codex flagged (PR #25) that a Binance file's Last-Modified is only the earliest time it could have been public. The event contract (T-2a, DEC-052) currently uses it as the record's available_at, so the earliest-possible time stands in for when the data was actually available. Daily files show Last-Modified about 2–3 h after the day ends. What should historical Binance archive bars use for available_at?" | "Last-Modified + 6 h, flagged (Recommended)" — "Adds a fixed safety margin for publication delays and marks the time as an estimate. For the 00:00 UTC daily decision this costs nothing: bar D still arrives before the D+2 decision." |

Unchosen options:
- "Last-Modified + 24 h, flagged" — "Larger margin. Every daily bar is used one day later than now in backtests."
- "Keep it, add a flag only" — "Keep Last-Modified and mark it as a lower bound. Values unchanged; the lookahead risk Codex raised stays."
- "Our first retrieval time" — "Provable, but no Binance history before our download is usable for backtests."

## Validation

- **Tests:** `/usr/bin/python3 -I -B -m unittest discover -s tests` gives 74 OK on Python 3.9 and 3.12 at `8228135` and `8ce10f2`.
  - Against the pre-fix code (`b62ec71`), 9 of them fail or error. The short-write test reproduces Codex's `JSONDecodeError` on reopen.
  - Against the first fix (`fa8ef7b`), 3 still fail or error: the last-completed-interval, member-retry and parse-error-bucket cases.
- **Validation runner** (`run_validation.py`, held files, code at `8228135`; re-run at `8ce10f2` with the same hash): 19 of 19 runnable fixtures and 10 of 10 recovery scenarios pass. The report, SHA-256 `71ef844b…2201`, is byte-identical across two runs. It replaces `b21845b5…3ef2`.
- **Changes in the report:**
  - DEC-069 changes the W-A content hash from `d29b8f86…8599` to `e5c6aaf0…b84a`. W-A is the only window with a content hash. W-B and W-D records also move, but the report gives no hash for them.
  - The delisting strings (four in W-F, one in F-11) now read `>= last bar (lower bound); status_unknown after`.
  - The F-16 key is renamed to `visible_from_available_at`.
  - All counts are unchanged. Neither W-E pair is blocked at 2026-09-30.
