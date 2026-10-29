# P02 — Fixes for the Codex reviews of PRs #23 to #32

TASK-P02-008. On 2026-10-29 Codex relayed 11 independent reviews of PRs #23 to #32, each pinned to its exact revision. PRs #23, #24, #26 (both revisions), #27 and #28 had no new findings. This page records each actionable finding and its fix. The PR #32 finding was fixed on that PR's own branch (TASK-P02-007). Reviews are feedback; none of them, and none of these fixes, passes a gate.

## Findings and fixes

| Review (head) | Finding (Codex, P2) | Fix | Test or evidence |
| --- | --- | --- | --- |
| PR #25 (`34f1cda`) | `sample-results.md:55`: `Last-Modified` is server metadata, not proof of when the file became public. Using it as `available_at` risks using data before it could be had | Asked the user; **DEC-069**: `Last-Modified` + 6 h, flagged `available_at_estimated`. Applied in `records.py` and the [event contract §3](event-contract.md) Binance row; the sample-results row is corrected | `test_valid_month_and_available_at`; `test_revision_with_last_modified_takes_retrieval_time` |
| PR #25 (`34f1cda`) | `sample-results.md:79`: the last bar is a lower bound on the delisting date, not an upper bound; an archive cut gives no upper bound | Corrected in the F-4g/F-4j row: after its last bar a pair's status is unknown, not delisted (DEC-040), so W-1 must not drop it there | Documentation |
| PR #29 (`230b1b7`) | `analysis.py:143`: `entry_blocked` blocks only on `status_unknown`, so a current `data_gap` (for example a quarantined price bar) still allows new entries, against 10-DATA:35 and :40 | `entry_blocked` now blocks on `data_gap` or `status_unknown` on the decision day; `no_trade` still does not block | `test_stale_and_entry_blocked` (new `data_gap` and `no_trade` cases) |
| PR #30 (`5b69e7f`) | `live.py:293`: a malformed book update mutates the book, raises, and is logged as a parse error while the book stays valid with unverified levels, counted as valid R-4 time | Book handling is wrapped: any parse or check error invalidates the book (`parse_error`) and resyncs it, under the existing resync cap, before the error is re-raised and counted | `test_malformed_update_invalidates_and_resyncs` |
| PR #31 (`49c20bc`) | `rawstore.py:167`: a short append leaves a fragment; later appends in the same process join it, so a reopen fails with `JSONDecodeError` | `_append` records the file's end before writing and truncates back to it on a short or failed write. If that rollback fails, the store refuses all writes until it is reopened, when `_repair_tail` cuts the fragment | `ShortAppendTests` (Codex's scenario: short index write, two more fetches, reopen; and a failed rollback) |
| PR #32 (`8e8630e`) | `TASK-P02-007.md:5`: the card is Verified without an independent review | Fixed on PR #32: reviewed, 1 Medium and 4 Low fixed, re-reviewed, then Verified | [TASK-P02-007](../../tasks/TASK-P02-007.md) |

## Effect on the running captures

The fixes are not applied to the running jobs. They run from `~/gladiator-capture` at `5b69e7f`, which is left unchanged (Codex: "do not interrupt or modify the running captures").
- **7-day live capture (DEC-064):** the book defect fires only on a parse error. As of 2026-10-29 its `events.jsonl` has no `parse_error` events. The G02 analysis rechecks this over the full window. If any appear, the affected book time is counted as invalid.
- **30-day REST job (DEC-068):** the short-append defect needs a short write to `index.jsonl` or `journal.jsonl`. The analysis checks that the store reopens read-only, and reports any interior malformed line.
- **DEC-069** changes only how the held Binance files are normalized. It changes no capture.

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

- **Tests:** `/usr/bin/python3 -I -B -m unittest discover -s tests` gives 71 OK on Python 3.9 and 3.12. The six new or changed tests fail on the pre-fix code (`b62ec71`): the short-write test reproduces Codex's `JSONDecodeError` on reopen, and the malformed-update test shows the book accepting a later update.
- **Validation runner** (`run_validation.py`, held files): 19 of 19 runnable fixtures and 10 of 10 recovery scenarios pass. The report, SHA-256 `9332ad83…efeb5`, is byte-identical across two runs. It replaces `b21845b5…3ef2`.
- **Change in the report:** only the W-A window's content hash changes. Its 62 records with basis `archive_published` now take `Last-Modified` + 6 h and carry `available_at_estimated`. All other counts are unchanged; Kraken windows are unaffected by DEC-069, and their decision days have no `data_gap`, so `entry_blocked` results are unchanged.
