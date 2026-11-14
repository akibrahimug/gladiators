# P02 — The 7-day live capture was interrupted by system sleep

TASK-P02-009. A read-only check of the running 7-day capture (DEC-064) on 2026-10-31 found that the Mac slept for most of one night. The capture was not touched. Its data were read only: `events.jsonl` and the closed hourly frame segments, read as plain files. The raw store was not opened.

## What happened

| Item | Observed | Evidence |
| --- | --- | --- |
| Sleep | The system entered sleep at **2026-10-29 19:03:48 UTC**, requested by `loginwindow` (pid 239). That is a user-initiated sleep: the Apple menu, the lid, or the power button. Until the next full wake at **2026-10-30 08:57 UTC**, the Mac only woke briefly for maintenance (DarkWake, about 45 s each) | `pmset -g log` |
| Why `caffeinate` didn't stop it | The run is wrapped in `caffeinate -i`, which only prevents *idle* sleep. A user-initiated sleep is not blocked by any `caffeinate` flag | `pmset -g assertions`: `PreventUserIdleSystemSleep` held for pid 76475 |
| Frame silence | 24,125,063 frames in the closed segments (10-28 10:35:31 to 10-31 15:57:02 UTC). There were 25 silences longer than 15 s, totalling **48,462 s (13.46 h)**. Twenty-four of them fall between 10-29 19:03:51 and 10-30 08:57:00. The other is a 16 s silence on 10-31 at 04:41: the 15 s receive timeout fired, a `timeout` disconnect was logged at 04:41:29, and the books were valid again at 04:41:31. `pmset` shows no sleep then. Every closed segment parsed with no malformed line | Scan of `frames-*.jsonl` by `recv_ns` |
| Connections | 44 disconnects so far; all reconnected within 3.4 s of being detected. There were no `parse_error` events. 20 of the disconnects came during the sleep window. Silences and disconnects don't pair one to one there: sometimes the old socket carried frames for a few seconds after a wake, then went quiet and hit the 15 s timeout (the four 16 s silences). Event times just after a wake are also uncertain, because the system clock had not yet been corrected (`pmset` logs DarkWake adjustments such as −31 s) | `events.jsonl`; `pmset -g log` |
| Book state during sleep | On each brief wake the capture reconnected, and both books passed their checksums and went `book_valid`. The Mac then slept again **before** any `book_invalid` event was written, so for each silence the event log shows the books as valid. Any invalid time comes only from the next `disconnect` | `events.jsonl` (for example `book_valid` at 10-30 08:24:11, then no event until `disconnect` at 08:57:00) |
| Clock | Two SNTP samples exceeded the T-6 intraday limit of 1 s: **1908 ms** at 10-30 07:56:37 and **1892 ms** at 08:24:37. Both came seconds after a wake, before the system clock had been corrected. Outside the sleep window the largest offset is 265 ms | `ntp` events |
| Run end | The capture's deadline uses `time.monotonic_ns`, which on this Mac is `mach_absolute_time()` and stops during sleep. The hourly segment boundaries moved from :35:31 to :57:02 past the hour. So the run captures 7 days of *awake* time and ends about **2026-11-04 23:57 UTC**, not 10:35 | `time.get_clock_info("monotonic")`; segment file names |

## Consequences for the G02 analysis

- **Gap rule (accepted as DEC-071 on 2026-11-04, before any measurement with it; RC-09 updated):** RC-09 records a `GapInterval` from the disconnect to the next valid book. For a frozen process that undercounts, so DEC-071 has a gap start at the last frame received when the next frame is more than 15 s later. That is RC-09's "heartbeat loss" with the capture's own receive timeout (`live.py`, `ws.settimeout(15)`); Kraken sends a heartbeat every second. The run's built-in summary (`invalid_book_ns`) counts invalid time only from the detected disconnect, so it counts the sleep as valid and **must not be used for R-4**. The [live analysis](live-analysis.md) applies DEC-071 instead. The user accepted the rule on 2026-11-04 ([live analysis](live-analysis.md#decisions-asked-2026-11-04)).
- **R-4 for this run fails.** The run spans about 181 h of wall-clock time and has at least 13.46 h without data, so a valid book covers at most about 92.6 % of the time. That is well under 99 %. The stretch after the sleep runs from 10-30 08:57 to the projected end, about 5 days 15 h, but it contains short reconnects. The longest projected stretch with no silence over 15 s runs from 10-31 04:41 to the end, about 4 days 19 h; time with a valid book is shorter still, because each reconnect takes up to about 3.4 s.
- **T-5/T-6:** the two samples over 1 s trigger T-6 intraday abstention (`clock_abstain_intraday`) while they are the latest sample; both also exceed T-5's 100 ms (RC-07). They are reported, not filtered out.
- **The run stays as evidence.** It is analysed in full when it ends, including the checks recorded in the [review fixes](review-fixes.md#effect-on-the-running-captures).

## Decision asked 2026-10-31

| ID | Question (verbatim) | Option chosen (verbatim) |
| --- | --- | --- |
| DEC-070 | "The Mac was put to sleep (by loginwindow, so through the Apple menu, the lid or the power button) from 29 Oct 19:03 to 30 Oct 08:57 UTC. The 7-day capture paused for about 13.5 h. Its timer counts awake time only, so it now ends around 4 Nov 23:57 UTC. That still gives 7 days of capture, but the longest unbroken stretch is about 5 days 15 h, which fails R-4 (book valid ≥ 99 % of the time). G02 also waits for the 30-day pull, which ends 27 Nov, so a second run would not delay G02. What should I do?" | "Rerun after it ends (Recommended)": "Let the current run finish untouched and keep it as evidence. Then start a fresh 7-day run (about 13 GB; 98 GB is free) ending around 12 Nov. Use the fixed code if #32/#33 are merged by then, otherwise 5b69e7f. You keep the Mac awake for those 7 days." |

Options not chosen:
- "Accept it with the gap": "No rerun. Record the 13.5 h as a gap, report R-4 as failed over the whole window, and use the 5 d 15 h unbroken stretch as the evaluation window."
- "Decide at G02": "Record the gap now and leave the choice to the G02 review. A rerun started then would end around 4 Dec, after the 30-day pull."

Corrections to the question, found in review after the answer:
- "About 5 days 15 h" is the stretch after the sleep. It contains short reconnects; see the R-4 bullet above.
- The disk figures were low. See the disk note below.
- The `5b69e7f` fallback in the option text would break DEC-066: that code queries SNTP every 60 s, and DEC-066 sets 30 s from the next capture. `master` (`44867bb`) already has the 30 s interval and the writer lock, so the rerun uses `master` at the least. This keeps the chosen option's intent (the newest fixed code) and follows DEC-066.

## Rerun plan (DEC-070)

1. Let the first run end by itself, about 2026-11-04 23:57 UTC. Check that it has exited before starting anything.
2. Put the rerun's code in a **separate** copy, `~/gladiator-capture-run2`. Leave `~/gladiator-capture` unchanged, because the 30-day REST job (DEC-068) runs from it until 2026-11-27. The copy is taken from `master`: after #32 and #33 if they are merged by then, otherwise `44867bb` (see the corrections above). Its revision is recorded.
3. Write to a new directory, `~/gladiator-data/live-7d-run2`, outside the repository (DEC-030). Use the same pairs, depth and duration as DEC-064, with DEC-066's 30 s SNTP interval.
4. Run under `caffeinate -i -s`, which also blocks system sleep while on AC power. **That still does not block a user-initiated sleep, so the Mac must not be put to sleep, and its lid must not be closed, for the 7 days.**
5. Check its `events.jsonl` and `pmset -g log` for sleep once a day, read-only.
6. The G02 analysis uses the rerun for R-4 and reports both runs.

Disk: 98 GB free on 2026-10-31. The first run holds 12 GB after about 63.9 h awake: 6.1 GB of hourly frame segments plus 6.0 GB in the raw store, which keeps an ingested copy of each closed segment. A full run is therefore about 31 GB, and the rerun adds about the same. The first run's remaining 19 GB plus the rerun's 31 GB leave about 48 GB free once both have finished. The frames alone come to about 1.15 GB per pair per day, within R-5's 2 GB.

### Watcher (TASK-P02-010, 2026-11-04)

The user chose to have the rerun started automatically ([TASK-P02-010](../../tasks/TASK-P02-010.md)). At 2026-11-04 10:10:47 UTC the coordinator armed [`ops/rerun/run2-watcher.sh`](../../../ops/rerun/run2-watcher.sh) against the first run's pid 76475, under `caffeinate -i -s`, from `~/gladiator-data/run2-watcher/`. It re-armed the watcher at 10:20:35 UTC after review fixes, as pid 1192. The watcher does steps 1 to 4 above:

- It waits for the first run to exit and requires that run's `live-summary.jsonl`.
- It copies `origin/master` as it is at that moment into `~/gladiator-capture-run2`, recording the revision and whether #33 is included.
- It runs the offline tests, then starts the rerun.

If any check fails, it logs the reason and does not start the rerun.

### Rerun start (observed 2026-11-05)

| Step | Observed |
| --- | --- |
| 1. First run ended | `live-summary.jsonl` written at 2026-11-05 00:01 UTC; `duration_s` 653,057.5 (181.4 h of wall clock, including the 13.5 h sleep), 62,332,037 frames, 76 disconnects, 0 parse errors. The capture's own R-4 count (99.98 %) misses the sleep; the read-only analysis (TASK-P02-003, [#36](https://github.com/akibrahimug/gladiators/pull/36)) applies DEC-071. Its `caffeinate` released its sleep assertion at 00:01:16 UTC (`pmset -g log`) |
| 2. Code | 00:01:59 UTC: copied from `origin/master` `d0b6b868a1ec2b84745ee21400daf470bbf1a992` into `~/gladiator-capture-run2`; `REVISION` holds the same SHA. Watcher log: "PR #33 fixes included: yes" |
| Offline tests | 74 tests OK on `d0b6b86`, 00:02:00 UTC |
| 3. Started | 00:02:00 UTC: `caffeinate -i -s /usr/bin/python3 -I -B ~/gladiator-capture-run2/capture.py live --out ~/gladiator-data/live-7d-run2 --seconds 604800`. Python pid 1192 (the watcher's, after `exec`), `caffeinate` pid 50517, which holds `PreventSystemSleep` from 00:02:00 UTC. First event `connected` at 00:02:01.255 UTC, first frame segment `frames-1793836921284145000.jsonl` at 00:02:01.284 UTC. The first SNTP offsets are 20 to 26 ms |
| Expected end | About 2026-11-12 00:02 UTC if the Mac stays awake; the timer counts awake time only |

**Announced maintenance.** The rerun's first `status` frame announces Kraken maintenance of the WebSocket, FIX and REST APIs from 2026-11-05 07:00 to 14:00 UTC (event 54, "WebSocket, FIX + REST API Maintenance", phase `reminder_24h`). The rerun's code reconnects indefinitely, at most 60 s apart (`RECONNECT_DELAYS_S`). A refused handshake raises `ConnectionError`, and a DNS or TLS failure raises an `OSError` subclass. The reconnect loop catches both, so an outage does not end the capture. R-4 excludes venue-declared maintenance (RC-11); how much of the 7 h is excluded depends on whether the venue reports `maintenance` on the `status` channel before it drops the connection.

**Outcome.** The item left the `upcoming_maintenance` list at 07:01:20 UTC, 80 s after its announced start. The status stayed `online` and data kept flowing, so the feed saw no maintenance. Kraken removes items from that list at about their start (seen for three announcements), so leaving the list is not a withdrawal (the read-only analysis, TASK-P02-003, [#36](https://github.com/akibrahimug/gladiators/pull/36)).

### Rerun stopped by a kernel panic (2026-11-05)

| Item | Observed |
| --- | --- |
| Last frame | 2026-11-05 08:11:50.047 UTC (last `events.jsonl` line 08:11:20). The capture had run 8.16 h: 3 disconnects (00:52, 03:54, 04:09 UTC), each recovered in under 2 s; 0 parse errors; status always `online` |
| Cause | Kernel panic at 08:12:50 UTC: "x86 CPU CATERR detected" (`/Library/Logs/DiagnosticReports/ProxiedDevice-Bridge/panic-full-2026-11-05-081250.0003.ips`, summarised in `.contents.panic`). This is a hardware-level CPU error reported by the iMac's T2 bridge, not a sleep. The unified log has no entries between 08:10 and 09:05 UTC |
| Restart | The Mac booted at 09:05:08 UTC (`kern.boottime`; `last`: "reboot time Thu Nov 5 09:05"). `pmset -g log`: "SMC shutdown cause: 5: Software initiated shutdown" |
| Data left | `~/gladiator-data/live-7d-run2`: 2.3 GB in 9 frame segments, 8 of them ingested into the store; the 9th (08:02 to 08:11 UTC) was still open. No `live-summary.jsonl`, and `run.log` is empty. Kept unchanged as evidence |
| Side effect | The reboot cleared `/private/tmp`, which held the coordinator's worktrees and its link and preservation check scripts. Every branch had been pushed, so nothing was lost; the worktrees and scripts were recreated |

### Decision asked 2026-11-05

Asked with the interactive question tool. The question and options, verbatim:

| Decision | Question (verbatim) | Chosen option: label — description (verbatim) |
| --- | --- | --- |
| DEC-073 | "The DEC-070 rerun stopped after 8.2 h. At 08:12:50 UTC today the iMac kernel-panicked with 'x86 CPU CATERR detected' (a hardware-level CPU error), and it was down until it booted at 09:05. The capture can't resume after a reboot. Its partial data (9 segments, 3 short disconnects, all checks clean) is kept. A fresh 7-day run started now would end about 12 Nov 09:30 UTC, still before the 30-day pull ends (27 Nov), so G02 isn't delayed. What should happen?" | "Start a fresh run now (Recommended)" — "New 7-day run from master d0b6b86 into ~/gladiator-data/live-7d-run3; keep run 2's partial data as evidence. If the panic recurs, we learn that early." |

Unchosen options:
- "Check hardware first" — "You run Apple Diagnostics (hold D at startup) or check the panic yourself; I start the run once you say so. Delays the end date by however long that takes."
- "Stop live reruns" — "No further 7-day run. Judge R-4 at G02 on run 1 (fails, 92.56 %) plus run 2's 8.2 h."

The same round asked how R-4 should treat announced maintenance (DEC-074). That rule belongs to the analysis and is recorded with TASK-P02-003 (PR [#36](https://github.com/akibrahimug/gladiators/pull/36)).

"All checks clean" in the question meant the rerun's own events: no parse error, and every disconnect recovered within 2 s. The read-only analysis's provisional report on run 2 is recorded by TASK-P02-003 ([#36](https://github.com/akibrahimug/gladiators/pull/36)).

### Run 3 start (DEC-073, 2026-11-05)

| Step | Observed |
| --- | --- |
| Code | `master` was still `d0b6b868a1ec2b84745ee21400daf470bbf1a992` after `git fetch`. That revision was extracted with `git archive` into a new copy, `~/gladiator-capture-run3`, with `REVISION`. `diff -r -q` against `~/gladiator-capture-run2` finds no difference. 74 offline tests OK with `/usr/bin/python3 -I -B -m unittest discover -s tests` |
| Started | 09:15:59 UTC by the coordinator: `nohup caffeinate -i -s /usr/bin/python3 -I -B ~/gladiator-capture-run3/capture.py live --out ~/gladiator-data/live-7d-run3 --seconds 604800`, output to `run.log` in that directory. Python pid 6634, `caffeinate` pid 6636 |
| First events | `connected` at 09:16:00.836 UTC; both books valid at 09:16:01.157; first SNTP offset 82 ms; `status` `online` with no upcoming maintenance |
| Expected end | About 2026-11-12 09:16 UTC if the Mac stays up; still before the 30-day pull's last day (2026-11-27) |

Run 3 takes run 2's place for R-4 under DEC-070. The G02 analysis reports all three runs. Steps 4 to 6 of the rerun plan apply unchanged. To stop it, `kill 6634`.

Disk on 2026-11-04 10:10 UTC: 265 GB free. The first run held 27 GB after about 6.42 days awake. Scaled to 7 days that is about 29.4 GB, close to the estimate of about 31 GB for a full run.

### Run 3 day-1 check (2026-11-06)

Rerun plan step 5, read-only, at 2026-11-06 17:21–17:35 UTC (32.1 h into run 3). Nothing in the run directory was written to; the analysis tool was not run against the open store.

| Check | Method | Observed |
| --- | --- | --- |
| Process | `ps` | Python pid 6634 and `caffeinate` pid 6636 alive |
| Sleep | `pmset -g log`, Sleep, Wake and DarkWake entries since 2026-11-05 | None |
| Restart | `uptime`; `last reboot` | Up 1 day 8 h 16 m; last boot 2026-11-05 09:05 UTC (the panic recovery, before run 3 started) |
| Frame gaps | Scan of every `recv_ns` in the 33 frame segments | 27,017,159 frames; longest gap 3.03 s; none over DEC-071's 15 s; last frame 2026-11-06 17:22:23 UTC |
| Disconnects | `events.jsonl` | 11, all `WebSocketClosed` ("socket closed"); both books valid again 1.28–1.90 s later; 12 `connected` events in total including the start |
| Parse errors | `events.jsonl` | 0 |
| Venue status | `events.jsonl`, 201 `venue_status` events | `system` was `online` in all of them |
| Announced maintenance | `upcoming_maintenance` items | One item, event 55, "WebSocket, FIX + REST API Maintenance.", services `spot_fix`, `spot_rest`, `spot_ws`, 2026-11-06 07:00–14:00 UTC. First seen 2026-11-05 14:31:21; last listed 07:00:09; first frame without it 07:00:18, 18 s after its start, so not withdrawn before its start. Frames kept flowing through the window |
| Clock | `ntp` events | 3,834 samples, 3,699 with an offset; largest offset 1,552 ms; 1,707 over 100 ms. T-5 is judged in the analysis |
| Disk | `du -sh`; `df -h` | Run 3 holds 14 GiB (frames 6.9 GiB, store 6.8 GiB), as `du -h` prints them; 265 GiB free |
| 30-day job | `launchctl list`; `launchd.out.log` | `com.gladiator.rest-daily` loaded; last pull ran at 2026-11-06 00:15:00 UTC |

Two observations for the G02 analysis, neither a failure:

- **Event 55 is the second 07:00–14:00 window in two days** (event 54 on 2026-11-05 in run 2). Under DEC-074 each such window is excluded from R-4 in full, 7 h here, because the item left the list after its start. Frames continued through it; two disconnects (09:00:49 and 10:05:38 UTC) left each book invalid for about 3 s in total. So the excluded 7 h were mostly valid time, and on run 3 so far excluding them lowers R-4 slightly (reviewer's estimate from the events: 99.9849 % → 99.9840 % per pair) rather than raising it. A window holding a longer outage than the run's average would raise it. If Kraken announces one every day, 07:00–14:00 on 2026-11-06 to -11 and 07:00–09:16 on -12 come to about 44 h, so R-4 is computed over about three quarters (about 74 %) of run 3's 168 h.
- **The feed is busier than in run 1.** Run 3's frame segments average 222 MB per hour against run 1's 94 MB. At that rate run 3 ends at about 75 GB, frames plus store, well within the free space.

The daily read-only check (rerun plan step 5) continues until run 3 ends; its results are recorded with run 3's analysis by TASK-P02-012.

### Run 3 later checks and end (2026-11-07 to 2026-11-13)

Read-only, like the day-1 check. The coordinator's notes are in `~/gladiator-data/analysis/run3-daily-checks.md` (DEC-030).

| When (UTC) | Observed |
| --- | --- |
| Day 2, 11-07 12:39 (51.4 h) | Alive; no sleep or reboot (`pmset -g log` from 11-06 17:23; the day-1 check covers the time before). 12 disconnects since day 1, recovered in 1.30–1.82 s. Two silences just over the 15 s receive timeout (16.30 s from 04:00:27 and 16.32 s from 04:03:43), each ending in a `timeout` disconnect, valid again within 1.8 s. No network log entries 03:59–04:05; cause unknown. Item 56 announced (11-10 10:00–11:00) |
| Interim, 11-07 18:39 (57.4 h) | Alive; no disconnects since 12:39 |
| Day 3, 11-08 10:22 (73.1 h) | Alive; no sleep or reboot. A local outage at about 04:55: SNTP failed at 04:54:52, the last frame was at 04:55:10, then a `timeout` disconnect and two `gaierror` disconnects ("nodename nor servname provided", a DNS failure on this side); connected 04:55:39.0 and valid 04:55:39.5. A 16.23 s silence at 05:07:01 recovered in 1.65 s. All four silences over 15 s so far fell between 04:00 and 05:10 UTC |
| Days 4 to 7 (11-09 to 11-12) | **Not checked daily**, a deviation from rerun plan step 5: no coordinator session ran on those days. Only early detection was lost. The checks below, made after the end, cover the same items for the whole run |
| End, 11-12 09:16:19 | Last frame 09:16:19.705; `live-summary.jsonl` written 09:18 (`duration_s` 604,819.9; 59 disconnects; 0 parse errors; 0 checksum failures); the process exited |
| After the end, 11-13 16:21 | `uptime` 8 d 7 h; last boot 2026-11-05 09:05, so no restart during the run. No sleep, wake or dark-wake entry from 2026-11-05 until **2026-11-12 09:20:55**: from the daily power logs `/var/log/powermanagement/2026.11.05.asl` to `2026.11.12.asl` (read with `syslog -f`; reviewer), because `pmset -g log` now starts at 2026-11-06 17:23, and from `pmset -g log` after that. The 09:20:55 entry is an idle sleep 2.4 min after the capture and `caffeinate` exited at 09:18:29 (4.6 min after the last frame). The frames agree: 8 silences over 15 s in the whole run, the longest 29 s. The 30-day job pulled every day through 11-13 00:15 on the first attempt |

The whole run ran without a sleep or a restart. Its analysis is in the [live analysis](live-analysis.md#run-3-dec-073-final-2026-11-13).
