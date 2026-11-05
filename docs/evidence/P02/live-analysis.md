# P02 — Read-only analysis of the live runs and the 30-day pull

TASK-P02-003. This page records the analysis method, the user's decisions of 2026-11-04 and the results of each run. The tool is `analyse.py` (`src/gladiator_capture/live_analysis.py`). It only reads the captured data: files are opened read-only and the raw store is opened with `read_only=True`. Reports go outside the runs and the repository (DEC-030). **Nothing on this page passes G02.**

## Method

The rules and their tests are listed on the [task card](../../tasks/TASK-P02-003.md#method-dec-071-and-the-review-fixes). In short:

- **R-4 (DEC-071):** a pair's book is invalid during the union of the capture's own invalid intervals, a `parse_error` on one of its book frames (the PR #30 defect in the run-1 code; an upper bound there), and every frame silence over 15 s, from the last frame before it to the first one after it. Venue maintenance is excluded: time while the `status` channel reports `maintenance`, plus announced WebSocket windows (DEC-074, below). The capture's built-in `invalid_book_ns` is shown beside it for comparison and is not used.
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

## Decision asked 2026-11-05

Asked with the interactive question tool, in the same round as DEC-073 (the fresh run after the kernel panic, recorded on the live run interruption page by TASK-P02-010, [#35](https://github.com/akibrahimug/gladiators/pull/35)). Run 2 had just stopped. Its only announced window had been withdrawn 80 s after its start, and no run used for R-4 contained an announced window. The question and options, verbatim:

| Decision | Question (verbatim) | Chosen option: label — description (verbatim) |
| --- | --- | --- |
| DEC-074 | "Kraken announced, then withdrew at 07:01 UTC, a 7-hour WebSocket/FIX/REST maintenance for today, 07:00–14:00 UTC. If it is rescheduled inside the next run, R-4 (≥ 99 % valid, excluding 'venue-declared maintenance') currently excludes only time when the status channel reports 'maintenance'. If Kraken drops the connection without sending that status first, up to 7 h would count as invalid, about 4 %, and R-4 would fail. Which rule should apply? I'm asking before it happens, so the rule is fixed before the outcome is known." | "Status + announced window (Recommended)" — "Exclude status-reported maintenance plus the window the venue last announced in its status frames, if it was not withdrawn before it started. A small analysis change with tests, in PR #36." |

Unchosen options:
- "Status channel only" — "Keep the current rule. Time dropped without a 'maintenance' status counts as invalid."
- "Report both, decide at G02" — "Compute both; you choose at the G02 review. Not fixed in advance."

**How it is applied.** Only items whose `affected_services` include `spot_ws` count; the book and trade feeds arrive over the WebSocket. Each item keeps the times of its latest announcement. The option does not cover a window withdrawn after it started, as happened on 2026-11-05. The analysis then counts it only up to the first `status` frame that no longer lists it. That is the stricter reading, because it excludes less time. During a real outage no frames arrive, so the window runs to its announced end or to the first frame after reconnecting.

## Results

### 30-day REST pull (DEC-068), provisional, 2026-11-04

Command: `/usr/bin/python3 -I -B analyse.py rest --run ~/gladiator-data/rest-daily --out <scratchpad>/rest.json` at 10:58 UTC, on the working tree for this task (base `d0b6b86`). Report SHA-256 `677baad0…2588`. Scratchpad only: the pull is still running.

| Check | Result |
| --- | --- |
| Days | 7 (2026-10-29 to 2026-11-04), no duplicate day; started 2026-10-29 |
| Calls | 21 of 21 stored, every one on the first attempt; no `gap`, no API error |
| Store | Index 21 lines and journal 49 lines, all parse, no incomplete tail; opens read-only; 21 objects, each present with the indexed length and hash. Journal outcomes: 21 `attempt`, 21 `stored`, 7 `robots` |
| Run times | 00:15:00–00:15:04 UTC on 6 days. **2026-10-30 ran at 02:04:46 UTC**: the Mac was in maintenance sleep from 00:09:04 to 02:04:45 (`pmset -g log`), and launchd ran the missed job at the next wake. The OHLC call returns the last 720 daily bars, so a late run within the day loses no bar |

### Run 1 (DEC-064), final, 2026-11-05

Command: `python3.12 -I -B analyse.py live --run ~/gladiator-data/live-7d --out ~/gladiator-data/analysis/live-7d.json`, 09:23–10:01 UTC, code `b7d6753` (DEC-074 included). Report SHA-256 `65ae7724a501fc4c977c492e09930bf227ffe667ae4784a0681f158f17b27e3b`; 2,290 s, 244 MB peak memory. Not provisional: the run wrote `live-summary.jsonl` at 2026-11-05 00:01 UTC. Window: `ran_at_utc` 2026-10-28 10:35:30.616 plus `duration_s` 653,057.5 s, so 181.40 h of wall clock to 2026-11-04 23:59:48 UTC. 178 segments, 62,332,037 frames. The report replaces two earlier ones:
- the provisional report `72c43357…6faf` (164 segments, code `d6bc907`);
- a first final report, `46e8d52c…ffdea`, made at 00:05–00:39 UTC on `bca6079`, before DEC-074. It gave R-4 92.56 %, with 126 s of maintenance, and is otherwise identical.

| Check | BTC/USD | ETH/USD | Against |
| --- | --- | --- | --- |
| **R-4** valid share, DEC-071 and DEC-074 | **92.69 %** | **92.69 %** | ≥ 99 %: **fails** (the sleep; [interruption](live-run-interruption.md)) |
| Invalid time: DEC-071 / capture events only | 47,655 s / 130 s | 47,655 s / 130 s | the capture's own summary gives 99.98 %, which misses the sleep |
| Excluding the 1.25 s initial sync | 92.69 % | 92.69 % | |
| Longest valid stretch | 30.65 h (10-31 18:28 to 11-02 01:07) | same | each reconnect of about 2 s ends a stretch |
| **R-3** recovery after a disconnect | n = 76; p50 1.62 s, p95 2.44 s, max 3.93 s | same | p95 ≤ 60 s: **passes**, 0 breaches |

| Check | Result |
| --- | --- |
| Frames and events | 0 unreadable frame lines; 0 unreadable `events.jsonl` lines. Events: 76 `disconnect`, 77 `connected`, 152 `book_invalid`, 154 `book_valid`, **0 `parse_error`**, 744 `venue_status`, 10,055 `ntp`. The summary agrees: 0 checksum failures, 0 resyncs |
| Silences over 15 s (DEC-071) | 25, totalling 48,462 s (13.46 h), all but one in the 10-29 19:03 to 10-30 08:57 sleep. Unchanged since the provisional report. Some overlap because the clock stepped back about 27 s after a wake; the union absorbs it |
| Maintenance (DEC-074) | 1,113 s in all. Status channel: 126 s, 10-29 08:01:08 to 08:03:14. Announced windows (`spot_ws`): event 47, 10-29 08:01:00 to 08:01:19, overlapping the status interval; event 50, **10-30 08:00 to 08:15 in full (900 s)**: the Mac was asleep, and the first status frame without it came at 08:24:11, after its end; event 53, 11-04 11:45:00 to 11:46:19. Event 54 (11-05 07:00) lies after the window. Event 50 fell inside the sleep, so its 900 s would otherwise count as invalid; that adds 0.13 points to R-4. Without DEC-074 the figure is 92.56 % |
| **Q-5** | Every `book_valid` follows a fresh snapshot for its pair: **passes** |
| **T-3** (offset-corrected p50 / p95 / p99, per day) | Book updates: 14–42 / 86–184 / 138–312 ms. Trades: 15–48 / 93–236 / 140–426 ms. The highest figures are on 2026-11-04. Raw p50 is −32 to −79 ms, because the local clock is behind. Reported, not required |
| Items older than 15 s on receipt | 3,471 (book 1,662 BTC and 1,716 ETH; trades 67 and 26), all on 10-29/30, delivered after a wake (up to 2.0 h old). The silence before each is already invalid |
| **T-5** | 10,055 samples, 331 failed; 4,576 over 100 ms; maximum 1,908 ms; 314,552 s (87.4 h) with `timestamp_uncertainty_ms` set. Four gaps between good samples exceed 1 h, all in the sleep; the longest is 13,817 s |
| **T-6** | Two samples over 1 s (1,908 ms at 10-30 07:56:37 and 1,892 ms at 08:24:37); none over 60 s. Intraday abstention 69,738 s: 1.3 s before the first sample, 3,663 s with an offset over 1 s, 66,074 s with a sample over 60 s old (mostly the sleep, plus the slack of run 1's 60 s query interval). Daily abstention: 0 s |
| **R-5** | 1.55 GB gzip for 16.7 GB of frames: **103 MB per pair per day**, against 2 GB: **passes** |
| Integrity and provenance | 178 of 178 segment hashes equal their index entries, all SR-02/SA-03; index and journal 178 lines each, all parse, no incomplete tail; 178 objects present with matching length and hash; 178 `stored` outcomes; opens read-only. Summary consistent with the frames |

**Kraken's `upcoming_maintenance` list.** Three times, the item left the list within 80 s of its announced start (events 47, 53 and 54). For event 47 the venue really was in maintenance; for 53 and 54 the status stayed `online` and data kept flowing. So "withdrawn" in DEC-074 means "no longer listed". The cut still behaves as intended. While the socket is up, a real maintenance shows as a `maintenance` status, which is always excluded. During an outage, the drop is only seen in the first frame after reconnecting, so the window covers the outage.

### Run 2 (DEC-070), stopped by a kernel panic, 2026-11-05

Command as above with `--run ~/gladiator-data/live-7d-run2 --out ~/gladiator-data/analysis/live-7d-run2.json`, 09:21–09:23 UTC, code `b7d6753`. Report SHA-256 `8c6fcf87c23a0d192e465d825c8fd970c78a06a48555943a252fbd2a6421a857`. A kernel panic stopped the run at 08:12 UTC (recorded by TASK-P02-010, [#35](https://github.com/akibrahimug/gladiators/pull/35)). It wrote no `live-summary.jsonl`, so the report is **provisional by construction**: the 9th segment (08:02 to 08:11 UTC, never ingested) is skipped. It covers 8.00 h, 00:02:01 to 08:02:01 UTC, 8 segments and 4,600,048 frames. Run 2 is not used for R-4; run 3 (DEC-073) takes its place.

| Check | Result |
| --- | --- |
| R-4 | 99.93 % both pairs (20.4 s invalid: 5.4 s from the capture's events, plus one 16.2 s silence) |
| R-3 | 3 disconnects; max 1.82 s |
| Maintenance | 80.8 s: event 54, 07:00:00 to 07:01:20.8, when it left the list. The status stayed `online` throughout |
| Q-5, parse errors | Passes; 0 |
| T-5 / T-6 | 957 samples, 23 failed, 492 over 100 ms, max 225 ms; the longest interval between good samples is 94 s. T-6 intraday abstention 108 s, all from samples over 60 s old; none over 1 s |
| R-5 | 157 MB per pair per day |
| Integrity | 8 of 8 segment hashes match, SR-02/SA-03; store clean (8 `started`, 8 `stored`) |

### Still to do

- Run 3 (DEC-070, DEC-073), after about 2026-11-12 09:16 UTC. R-4 is judged on it.
- The 30-day pull after its last day, 2026-11-27, together with the archive/REST bar comparison over the window (a later slice).
