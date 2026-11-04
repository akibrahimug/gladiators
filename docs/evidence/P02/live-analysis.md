# P02 — Read-only analysis of the live runs and the 30-day pull

TASK-P02-003. This page records the analysis method, the user's decisions of 2026-11-04 and the results of each run. The tool is `analyse.py` (`src/gladiator_capture/live_analysis.py`). It only reads the captured data: files are opened read-only and the raw store is opened with `read_only=True`. Reports go outside the runs and the repository (DEC-030). **Nothing on this page passes G02.**

## Method

The rules and their tests are listed on the [task card](../../tasks/TASK-P02-003.md#method-dec-071-and-the-review-fixes). In short:

- **R-4 (DEC-071):** a pair's book is invalid during the union of the capture's own invalid intervals, a `parse_error` (the PR #30 defect in the run-1 code), and every frame silence over 15 s, from the last frame before it to the first one after it. Venue maintenance is excluded. The capture's built-in `invalid_book_ns` is shown beside it for comparison and is not used.
- **R-3** runs from each `disconnect` to the pair's next `book_valid`. **Q-5:** every `book_valid` needs a fresh book snapshot for that pair since the pair was last invalidated.
- **T-3** uses 1 ms bins per channel, pair and UTC day, raw and SNTP-corrected. **T-5/T-6** report time under each flag; before the first sample counts as unknown (DEC-067).
- **R-5** gzips each closed segment at level 6. **Integrity:** every frame line parses, each segment's SHA-256 matches its store index entry, and every store line and object checks out.
- A run with no `live-summary.jsonl` has not finished. Its newest segment is still open, so it is skipped and the report is **provisional**.

## Decisions asked 2026-11-04

Asked with the interactive question tool before any run was measured with these rules. The questions and options, verbatim:

| Decision | Question (verbatim) | Chosen option: label — description (verbatim) |
| --- | --- | --- |
| DEC-072 | "TASK-P02-003 (the G02 capture analysis) is still only a candidate row. It would add a read-only offline analysis tool (new code in src/gladiator_capture/ plus tests). The tool computes R-1 to R-5, Q-5 and T-3/T-5/T-6 for both 7-day runs and the 30-day pull, and runs the store checks from the review fixes. Should I write the packet and build it now, so that run 1 can be analysed once it ends tonight?" | "Build it now (Recommended)" — "Packet, tool and tests on their own branch with a draft PR. Uses the hours before run 1 ends; the captured data is only read." |
| DEC-071 | "How should a gap be counted for R-4 (≥ 99 % of time with a valid book)? The capture's built-in count starts a gap only at a detected disconnect, so the 13.5 h Mac sleep on 29–30 Oct counted as 'valid'." | "Last frame + 15 s (Recommended)" — "A gap starts at the last frame received when the next frame comes more than 15 s later. That is the capture's own receive timeout, and Kraken sends a heartbeat every 1 s. Catches sleeps and freezes." |
| (DEC-059, confirmed again) | "Archive vs REST bar comparison (event contract §4.1): the current rule (volume rounded to 8 decimals must match exactly) flags 4 mismatches, 3 of which are float rounding of 1–2 × 10⁻⁸. Which rule should be official?" | "Relative 10⁻⁹ (Recommended)" — "Same tolerance as the P01 sample. Flags only the one real difference (XBTUSD 2026-09-10)." |
| (DEC-060, confirmed again) | "Bar record keys: the contract allows 'native ID or row index'. A row index shifts when a revision inserts a row or the 30-day REST window slides. Should bars key on bar_start instead?" | "Key on bar_start (Recommended)" — "Already implemented this way; this would accept it into the event contract §3." |

Unchosen options:
- DEC-072: "Packet only, no code" — "Write the card and the analysis method now. Implementation waits for your later acceptance."; "Wait until both runs end" — "Do nothing on P02-003 until about 12 Nov."
- DEC-071: "Report both, decide at G02" — "Compute both the disconnect-based and the last-frame count; you choose at the G02 review. This is not pre-registered."; "Disconnect-based (RC-09 as is)" — "Keep the current rule. It undercounts frozen or sleeping periods."
- Volume rule: "Keep 8-decimal exact" — "Stays as the official rule; the 3 rounding cases stay flagged as mismatches."
- Bar keys: "Allow row index too" — "Leave the contract wording as is."

**Correction (coordinator, 2026-11-04):** the last two questions had already been decided. The user chose the 10⁻⁹ tolerance as DEC-059 and `bar_start` keys as DEC-060 on 2026-10-28; the event contract and `validate.py` already apply both. The coordinator asked again because [capture-validation-results §4](capture-validation-results.md#4-findings-for-the-user) still read "Proposed". The answers match the earlier decisions, so they create no new decision, and that page is corrected.

## Results

### 30-day REST pull (DEC-068), provisional, 2026-11-04

Command: `/usr/bin/python3 -I -B analyse.py rest --run ~/gladiator-data/rest-daily --out <scratchpad>/rest.json` at 10:58 UTC, on the working tree for this task (base `d0b6b86`). Report SHA-256 `677baad0…2588`. Scratchpad only: the pull is still running.

| Check | Result |
| --- | --- |
| Days | 7 (2026-10-29 to 2026-11-04), no duplicate day; started 2026-10-29 |
| Calls | 21 of 21 stored, every one on the first attempt; no `gap`, no API error |
| Store | Index 21 lines and journal 49 lines, all parse, no incomplete tail; opens read-only; 21 objects, each present with the indexed length and hash. Journal outcomes: 21 `attempt`, 21 `stored`, 7 `robots` |
| Run times | 00:15:00–00:15:04 UTC on 6 days. **2026-10-30 ran at 02:04:46 UTC**: the Mac was in maintenance sleep from 00:09:04 to 02:04:45 (`pmset -g log`), and launchd ran the missed job at the next wake. The OHLC call returns the last 720 daily bars, so a late run within the day loses no bar |

### Run 1 (DEC-064), provisional, 2026-11-04

RESULTS_RUN1

### Still to do

- Run 1's final report once it has ended (about 2026-11-04 23:57 UTC). It replaces the provisional figures above.
- The rerun (DEC-070) after about 2026-11-12. R-4 is judged on the rerun (DEC-070).
- The 30-day pull after its last day, 2026-11-27, together with the archive/REST bar comparison over the window (a later slice).
