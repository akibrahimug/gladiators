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

Asked with the interactive question tool, in the same round as DEC-073 (the fresh run after the kernel panic, recorded on the live run interruption page by TASK-P02-010, [#35](https://github.com/akibrahimug/gladiators/pull/35)). Run 2 had just stopped. Its only announced window had left the `upcoming_maintenance` list 80 s after its start, and no run used for R-4 contained an announced window. The question and options, verbatim:

| Decision | Question (verbatim) | Chosen option: label — description (verbatim) |
| --- | --- | --- |
| DEC-074 | "Kraken announced, then withdrew at 07:01 UTC, a 7-hour WebSocket/FIX/REST maintenance for today, 07:00–14:00 UTC. If it is rescheduled inside the next run, R-4 (≥ 99 % valid, excluding 'venue-declared maintenance') currently excludes only time when the status channel reports 'maintenance'. If Kraken drops the connection without sending that status first, up to 7 h would count as invalid, about 4 %, and R-4 would fail. Which rule should apply? I'm asking before it happens, so the rule is fixed before the outcome is known." | "Status + announced window (Recommended)" — "Exclude status-reported maintenance plus the window the venue last announced in its status frames, if it was not withdrawn before it started. A small analysis change with tests, in PR #36." |


The question's "withdrew at 07:01 UTC" was the coordinator's reading at the time. The item left the list 80 s after its start, which Kraken does for every item at about its start (below).

Unchosen options:
- "Status channel only" — "Keep the current rule. Time dropped without a 'maintenance' status counts as invalid."
- "Report both, decide at G02" — "Compute both; you choose at the G02 review. Not fixed in advance."

**How it is applied.** Only items whose `affected_services` include `spot_ws`, or that name no services, count; the book and trade feeds arrive over the WebSocket. Each item is tracked by its `event_id`, or by its times if it has no usable id. It keeps the times of its latest announcement, and its window is clipped to the run. As the option reads, the whole announced window is excluded unless a status frame stopped listing the item before its start. Listing it again cancels that. Kraken removes items from the list at about their start (below), so leaving the list later is not a withdrawal. A window counts from its announced start even if it was first listed later. Frames without an `upcoming_maintenance` list change nothing. Items with unreadable times are skipped and counted in the report. A first implementation (`b7d6753`) cut a window at the first frame that no longer listed it. Review M1 showed that this undoes the rule when the connection drops after Kraken has unlisted the item, so `cf03f00` follows the option as written.

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

Command: `python3.12 -I -B analyse.py live --run ~/gladiator-data/live-7d --out ~/gladiator-data/analysis/live-7d.json`, 10:12–10:50 UTC, code `cf03f00` (DEC-074 as the option reads). Report SHA-256 `2343a77208955bb2f5bfa81bd78f7f3cb37be2117254c484d47735e23d109b9e`; 2,273 s, 246 MB peak memory. Not provisional: the run wrote `live-summary.jsonl` at 2026-11-05 00:01 UTC. Window: `ran_at_utc` 2026-10-28 10:35:30.616 plus `duration_s` 653,057.5 s, so 181.40 h of wall clock to 2026-11-04 23:59:48 UTC. 178 segments, 62,332,037 frames. The report replaces three earlier ones:
- the provisional report `72c43357…6faf` (164 segments, code `d6bc907`);
- a first final report, `46e8d52c…ffdea`, made at 00:05–00:39 UTC on `bca6079`, before DEC-074. It gave R-4 92.56 %, with 126 s of maintenance;
- `65ae7724…7b27e3b`, on `b7d6753`. It cut announced windows when they left the list, and gave R-4 92.69 % with 1,113 s of maintenance (review M1).

Apart from maintenance and R-4, all three give the same results.

| Check | BTC/USD | ETH/USD | Against |
| --- | --- | --- | --- |
| **R-4** valid share, DEC-071 and DEC-074 | **92.43 %** | **92.43 %** | ≥ 99 %: **fails** (the sleep; [interruption](live-run-interruption.md)) |
| Invalid time: DEC-071 / capture events only | 47,651 s / 125 s | 47,651 s / 125 s | the capture's own summary gives 99.98 %, which misses the sleep |
| Excluding the 1.25 s initial sync | 92.43 % | 92.43 % | |
| Longest valid stretch | 30.65 h (10-31 18:28 to 11-02 01:07) | same | each reconnect of about 2 s ends a stretch |
| **R-3** recovery after a disconnect | n = 76; p50 1.62 s, p95 2.44 s, max 3.93 s | same | p95 ≤ 60 s: **passes**, 0 breaches |

| Check | Result |
| --- | --- |
| Frames and events | 0 unreadable frame lines; 0 unreadable `events.jsonl` lines. Events: 76 `disconnect`, 77 `connected`, 152 `book_invalid`, 154 `book_valid`, **0 `parse_error`**, 744 `venue_status`, 10,055 `ntp`. The summary agrees: 0 checksum failures, 0 resyncs |
| Silences over 15 s (DEC-071) | 25, totalling 48,462 s (13.46 h), all but one in the 10-29 19:03 to 10-30 08:57 sleep. Unchanged since the provisional report. Some overlap because the clock stepped back about 27 s after a wake; the union absorbs it |
| Maintenance (DEC-074) | 23,400 s (6.5 h) in all. Status channel: 126 s, 10-29 08:01:08 to 08:03:14, inside event 47's window. Announced `spot_ws` windows, each counted in full: event 47, 10-29 08:01 to 08:16 (left the list at 08:01:19); event 50, 10-30 08:00 to 08:15, inside the sleep (first frame without it at 08:24:11); event 53, "WebSocket API Maintenance", **11-04 11:45 to 17:45 (21,600 s)**, which left the list at 11:46:19 while data kept flowing. Event 54 (11-05 07:00) lies after the window. Event 53's 6 h of normal data leave the window. That lowers R-4 a little, because valid time leaves the share; it does not raise it. Event 50's 900 s and 4.5 s of reconnect time on 10-29 leave the invalid time. Without DEC-074 the figure is 92.56 % |
| **Q-5** | Every `book_valid` follows a fresh snapshot for its pair: **passes** |
| **T-3** (offset-corrected p50 / p95 / p99, per day) | Book updates: 14–42 / 86–184 / 138–312 ms. Trades: 15–48 / 93–236 / 140–426 ms. The highest figures are on 2026-11-04. Raw p50 is −32 to −79 ms, because the local clock is behind. Reported, not required |
| Items older than 15 s on receipt | 3,471 (book 1,662 BTC and 1,716 ETH; trades 67 and 26), all on 10-29/30, delivered after a wake (up to 2.0 h old). The silence before each is already invalid |
| **T-5** | 10,055 samples, 331 failed; 4,576 over 100 ms; maximum 1,908 ms; 314,552 s (87.4 h) with `timestamp_uncertainty_ms` set. Four gaps between good samples exceed 1 h, all in the sleep; the longest is 13,817 s |
| **T-6** | Two samples over 1 s (1,908 ms at 10-30 07:56:37 and 1,892 ms at 08:24:37); none over 60 s. Intraday abstention 69,738 s: 1.3 s before the first sample, 3,663 s with an offset over 1 s, 66,074 s with a sample over 60 s old (mostly the sleep, plus the slack of run 1's 60 s query interval). Daily abstention: 0 s |
| **R-5** | 1.55 GB gzip for 16.7 GB of frames: **103 MB per pair per day**, against 2 GB: **passes** |
| Integrity and provenance | 178 of 178 segment hashes equal their index entries, all SR-02/SA-03; index and journal 178 lines each, all parse, no incomplete tail; 178 objects present with matching length and hash; 178 `stored` outcomes; opens read-only. Summary consistent with the frames |

**Kraken's `upcoming_maintenance` list.** Three times, the item left the list within 80 s of its announced start (events 47, 53 and 54). For event 47 the venue really was in maintenance; for 53 and 54 the status stayed `online` and data kept flowing. Leaving the list after the start is therefore not a withdrawal, and DEC-074 counts the whole announced window, as the option reads. A cut at that point (`b7d6753`) would have undone the rule whenever Kraken drops the socket after unlisting the item (review M1).

### Run 2 (DEC-070), stopped by a kernel panic, 2026-11-05

Command as above with `--run ~/gladiator-data/live-7d-run2 --out ~/gladiator-data/analysis/live-7d-run2.json`, 10:10–10:12 UTC, code `cf03f00`. Report SHA-256 `e8ce0c603655caeb13a2deae204734f784abfc0830bd329db8fa0ac43399afdd`. It replaces `8c6fcf87…421a857` (`b7d6753`: 99.93 %, 80.8 s of maintenance). A kernel panic stopped the run at 08:12 UTC (recorded by TASK-P02-010, [#35](https://github.com/akibrahimug/gladiators/pull/35)). It wrote no `live-summary.jsonl`, so the report is **provisional by construction**: the 9th segment (08:02 to 08:11 UTC, never ingested) is skipped. It covers 8.00 h, 00:02:01 to 08:02:01 UTC, 8 segments and 4,600,048 frames. Run 2 is not used for R-4; run 3 (DEC-073) takes its place.

| Check | Result |
| --- | --- |
| R-4 | 99.92 % both pairs (20.4 s invalid: 5.4 s from the capture's events, plus one 16.2 s silence) |
| R-3 | 3 disconnects; max 1.82 s |
| Maintenance | 3,721 s: event 54 from 07:00:00 to the end of the analysed frames at 08:02:01. It left the list at 07:01:20.8. The status stayed `online` throughout |
| Q-5, parse errors | Passes; 0 |
| T-5 / T-6 | 957 samples, 23 failed, 492 over 100 ms, max 225 ms; the longest interval between good samples is 94 s. T-6 intraday abstention 108 s, all from samples over 60 s old; none over 1 s |
| R-5 | 157 MB per pair per day |
| Integrity | 8 of 8 segment hashes match, SR-02/SA-03; store clean (8 `started`, 8 `stored`) |

### Run 3 (DEC-073), final, 2026-11-13

Command: `python3.12 -I -B analyse.py live --run ~/gladiator-data/live-7d-run3 --out ~/gladiator-data/analysis/live-7d-run3.json`, 16:23–17:16 UTC on 2026-11-13, code `master` `3a76174` (analysis code byte-identical to `cf03f00`). Report SHA-256 `c713a85de4268c9a91e3993a972a6e8091f5265fc57300896e38564a6edf74ff`; 3,187 s, 288 MB peak memory. Not provisional: the run wrote `live-summary.jsonl` at 2026-11-12 09:18 UTC. Window: `ran_at_utc` 2026-11-05 09:15:59.797 plus `duration_s` 604,819.9 s, so 168.01 h to 2026-11-12 09:16:19.704 UTC. 169 segments, 87,754,675 frames. The run directory's file list, sizes and mtimes (344 files) were identical before and after the analysis.

| Check | BTC/USD | ETH/USD | Against |
| --- | --- | --- | --- |
| **R-4** valid share, DEC-071 and DEC-074 | **99.960 %** | **99.960 %** | ≥ 99 %: **passes** |
| Invalid time: DEC-071 / capture events only | 203.1 s / 83.1 s | 203.1 s / 83.1 s | the capture's own summary gives 99.981 % |
| Excluding the 1.36 s initial sync | 99.960 % | 99.960 % | |
| Longest valid stretch | 21.38 h (11-07 07:32 to 11-08 04:55) | same | |
| **R-3** recovery after a disconnect | n = 56; p50 1.61 s, p95 4.86 s, max 14.00 s | same | p95 ≤ 60 s: **passes**, 0 breaches |

| Check | Result |
| --- | --- |
| Frames and events | 0 unreadable frame or `events.jsonl` lines. Events: 59 `disconnect` (48 `WebSocketClosed`, 8 receive timeouts, 2 `gaierror`, 1 `ConnectionError`), 57 `connected`, 118 `book_invalid`, 114 `book_valid`, **0 `parse_error`**, 4,947 `venue_status` (all `online`), 20,057 `ntp`. The summary agrees: 0 checksum failures, 0 resyncs. R-3 has 56 recoveries for 59 disconnects because consecutive disconnects before a valid book count once (from the first) |
| Silences over 15 s (DEC-071) | 8, totalling 145.3 s; none over 60 s. Each ended in a receive timeout and a reconnect. The longest, 29.0 s from 11-08 04:55:10, was a local DNS failure (`gaierror`) and gives R-3's maximum of 14.0 s |
| Maintenance (DEC-074) | **97,200 s (27 h, 16.1 % of the window)**, all from announced `spot_ws` windows; the status channel never reported `maintenance` (0 s). Counted in full: event 55, 11-06 07:00–14:00; event 57, 11-09 08:00–14:00; event 58, 11-10 07:00–14:00, with event 56 (10:00–11:00) inside it; event 62, 11-11 07:00–14:00, with event 59 (09:00–10:00) inside it. Each left the list 18–79 s after its start. **Event 61** ("Kraken Website and API Maintenance", 11-12 08:01–08:16) was unlisted on 11-11 at 16:57:47, before its start, so it is a withdrawal and is not excluded: the first in any run. Events 60 (`spot_trading` only) and 63–65 (futures) list no `spot_ws` and do not count. 0 items skipped |
| **Q-5** | Every `book_valid` follows a fresh snapshot for its pair: **passes** |
| **T-3** (offset-corrected p50 / p95 / p99, per day) | Book updates: 19–36 / 105–184 / 173–435 ms. Trades: 20–45 / 117–315 / 186–891 ms. Raw p50 is −35 to −73 ms (local clock behind). Reported, not required |
| Items older than 15 s on receipt | 9 trades (7 BTC, 2 ETH); the largest are 17.0 s (BTC, 11-06) and 21.1 s (ETH, 11-11) old, raw |
| **T-5** | 20,057 samples, 692 failed; 9,446 over 100 ms; maximum 1,552 ms; 295,080 s (82.0 h) with `timestamp_uncertainty_ms` set. Longest interval between good samples 222 s; none over 1 h |
| **T-6** | One sample over 1 s (1,552 ms at 11-06 09:41:05); none over 60 s. Intraday abstention 4,384 s: 1.1 s before the first sample, 30.0 s with an offset over 1 s, 4,352.7 s with a sample over 60 s old. Daily abstention: 0 s |
| **R-5** | 2.11 GB gzip for 23.6 GB of frames: **151 MB per pair per day**, against 2 GB: **passes**. The feed was busier than in run 1 (103 MB) |
| Integrity and provenance | 169 of 169 segment hashes equal their index entries, all SR-02/SA-03; index 169 and journal 338 lines, all parse, no incomplete tail; 169 objects present with matching length and hash; 169 `started` and 169 `stored`; opens read-only. Summary consistent with the frames |

**Effect of DEC-074 on run 3.** Inside the four excluded windows, the capture's events show 14 disconnects and about 33 s of invalid book per pair (longest 10.0 s; coordinator's count from `events.jsonl`, not the tool's interval logic). That is a lower invalid rate than the rest of the run, so excluding the windows lowers R-4 slightly: counting them in, the estimate is 99.961 % instead of 99.960 %. R-4 passes by a wide margin either way.

### Still to do

- Run 3: done (above, TASK-P02-012).
- The 30-day pull after its last day, 2026-11-27 (TASK-P02-012), together with the archive/REST bar comparison over the window (a later slice).
