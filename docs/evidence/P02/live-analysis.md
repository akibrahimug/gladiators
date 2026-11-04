# P02 — Read-only analysis of the live runs and the 30-day pull

TASK-P02-003. This page records the analysis method, the user's decisions of 2026-11-04 and the results of each run. The tool is `analyse.py` (`src/gladiator_capture/live_analysis.py`). It only reads the captured data: files are opened read-only and the raw store is opened with `read_only=True`. Reports go outside the runs and the repository (DEC-030). **Nothing on this page passes G02.**

## Method

The rules and their tests are listed on the [task card](../../tasks/TASK-P02-003.md#method-dec-071-and-the-review-fixes). In short:

- **R-4 (DEC-071):** a pair's book is invalid during the union of the capture's own invalid intervals, a `parse_error` on one of its book frames (the PR #30 defect in the run-1 code; an upper bound there), and every frame silence over 15 s, from the last frame before it to the first one after it. Venue maintenance is excluded. The capture's built-in `invalid_book_ns` is shown beside it for comparison and is not used.
- **R-3** runs from each `disconnect` to the pair's next `book_valid`. **Q-5:** every `book_valid` needs a fresh book snapshot for that pair since the pair was last invalidated.
- **T-3** uses 1 ms bins per channel, pair and UTC day, raw and SNTP-corrected. **T-5/T-6** report time under each flag. Before the first sample counts only for T-6 intraday (DEC-067), and the intraday figure is split by cause.
- **R-3** starts at the `disconnect` event, which for a receive timeout is up to 15 s after the last frame.
- **Limit:** times are wall-clock. A clock step just after a wake can shorten or lengthen a silence near it; this is not corrected.
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

Command: `python3.12 -I -B analyse.py live --run ~/gladiator-data/live-7d --out <scratchpad>/live-7d-prov.json`, 11:16–11:49 UTC, code `d6bc907`. Report SHA-256 `72c43357…6faf`; 1,961 s, 258 MB peak memory. Scratchpad only: the run was still writing. **Provisional:** it covers 164 closed segments, 2026-10-28 10:35:31 to 2026-11-04 10:57:10 UTC (168.4 h), and skips the open segment. The run has 0 parse errors and 0 unreadable lines, so `bca6079`'s attribution change cannot alter it.

| Check | BTC/USD | ETH/USD | Against |
| --- | --- | --- | --- |
| **R-4** valid share, DEC-071 | **91.99 %** | **91.99 %** | ≥ 99 %: **fails** (expected; [interruption](live-run-interruption.md)) |
| Invalid time: DEC-071 / capture events only | 48,546 s / 121 s | 48,546 s / 121 s | the capture's own count misses the sleep |
| Longest valid stretch | 30.65 h (10-31 18:28 to 11-02 01:07) | same | each reconnect of about 2 s ends a stretch |
| **R-3** recovery after a disconnect | n = 71; p50 1.62 s, p95 2.44 s, max 3.93 s | same | p95 ≤ 60 s: **passes**, 0 breaches |

| Check | Result |
| --- | --- |
| Frames | 53,438,905 in 164 segments; 0 unreadable lines; 0 unreadable `events.jsonl` lines |
| Silences over 15 s (DEC-071) | 25, totalling 48,462 s (13.46 h), all but one in the 10-29 19:03 to 10-30 08:57 sleep. This matches the 2026-10-31 scan |
| Clock steps | Some silences overlap. For example, a frame at 10-29 19:07:23 is followed by one at 19:06:56, so the wall clock stepped back about 27 s after a wake. The union of intervals absorbs the overlap, so the totals are unaffected. This is the clock-step limit stated above, now observed |
| Events | 71 `disconnect`, 72 `connected`, 142 `book_invalid`, 144 `book_valid`, **0 `parse_error`**, 662 `venue_status`, 9,274 `ntp` |
| Maintenance | 126 s, 10-29 08:01:08 to 08:03:14 UTC; excluded from R-4 |
| **Q-5** | Every `book_valid` follows a fresh snapshot for its pair: **passes** |
| **T-3** (offset-corrected p50 / p95 / p99, per day) | Book updates: 14–45 / 86–186 / 138–289 ms. Trades: 15–50 / 93–248 / 140–439 ms. 2026-11-04 has the highest figures. Raw p50 is −38 to −79 ms, because the local clock is behind. Reported, not required |
| Items older than 15 s on receipt | 3,471 (book 1,662 BTC and 1,716 ETH; trades 67 and 26), all on 10-29/30, delivered after a wake (up to 2.0 h old). The silence before each is already invalid under DEC-071. The few seconds of valid book that follow each wake are not separately excluded |
| **T-5** | 9,274 samples, 305 failed; 4,305 over 100 ms; maximum 1,908 ms; 297,650 s (82.7 h) with `timestamp_uncertainty_ms` set. Four gaps between good samples exceed 1 h, all in the sleep; the longest is 13,817 s |
| **T-6** | Two samples over 1 s (1,908 ms at 10-30 07:56:37 and 1,892 ms at 08:24:37); none over 60 s. Intraday abstention 68,132 s: 0.1 s before the first sample, 3,663 s with an offset over 1 s, and 64,469 s with a sample over 60 s old. The last is mostly the sleep, plus the slack of run 1's 60 s query interval (before DEC-066). Daily abstention: 0 s |
| **R-5** | 1.34 GB gzip for 14.3 GB of frames: **95 MB per pair per day**, against a 2 GB limit: **passes** |
| Integrity and provenance | 164 of 164 segment hashes equal their index entries, all SR-02/SA-03; index and journal 164 lines each, all parse; 164 objects present with matching length and hash; 164 `stored` outcomes; opens read-only |

### Still to do

- Run 1's final report once it has ended (about 2026-11-04 23:57 UTC). It replaces the provisional figures above.
- The rerun (DEC-070) after about 2026-11-12. R-4 is judged on the rerun (DEC-070).
- The 30-day pull after its last day, 2026-11-27, together with the archive/REST bar comparison over the window (a later slice).
