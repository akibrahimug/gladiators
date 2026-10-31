# P02 — The 7-day live capture was interrupted by system sleep

TASK-P02-009. A read-only check of the running 7-day capture (DEC-064) on 2026-10-31 found that the Mac slept for most of one night. The capture was not touched. Its data were read only: `events.jsonl` and the closed hourly frame segments, read as plain files. The raw store was not opened.

## What happened

| Item | Observed | Evidence |
| --- | --- | --- |
| Sleep | The system entered sleep at **2026-10-29 19:03:48 UTC**, requested by `loginwindow` (pid 239). That is a user-initiated sleep: the Apple menu, the lid, or the power button. Until the next full wake at **2026-10-30 08:57 UTC**, the Mac only woke briefly for maintenance (DarkWake, about 45 s each) | `pmset -g log` |
| Why `caffeinate` didn't stop it | The run is wrapped in `caffeinate -i`, which only prevents *idle* sleep. A user-initiated sleep is not blocked by any `caffeinate` flag | `pmset -g assertions`: `PreventUserIdleSystemSleep` held for pid 76475 |
| Frame silence | 24,125,063 frames in the closed segments (10-28 10:35:31 to 10-31 15:57:02 UTC). There were 25 silences longer than 15 s, totalling **48,462 s (13.46 h)**. Twenty-four of them fall between 10-29 19:03:51 and 10-30 08:57:00; the other is a 16 s silence on 10-31 at 04:41. Every closed segment parsed with no malformed line | Scan of `frames-*.jsonl` by `recv_ns` |
| Connections | 44 disconnects so far; all reconnected within 3.4 s of being detected. 20 of them came during the sleep window, one at each brief wake. There were no `parse_error` events | `events.jsonl` |
| Book state during sleep | On each brief wake the capture reconnected, and both books passed their checksums and went `book_valid`. The Mac then slept again **before** any `book_invalid` event was written, so for each silence the event log shows the books as valid. Any invalid time comes only from the next `disconnect` | `events.jsonl` (for example `book_valid` at 10-30 08:24:11, then no event until `disconnect` at 08:57:00) |
| Clock | Two SNTP samples exceeded the T-6 intraday limit of 1 s: **1908 ms** at 10-30 07:56:37 and **1892 ms** at 08:24:37. Both came seconds after a wake, before the system clock had been corrected. Outside the sleep window the largest offset is 265 ms | `ntp` events |
| Run end | The capture's deadline uses `time.monotonic_ns`, which on this Mac is `mach_absolute_time()` and stops during sleep. The hourly segment boundaries moved from :35:31 to :57:02 past the hour. So the run captures 7 days of *awake* time and ends about **2026-11-04 23:57 UTC**, not 10:35 | `time.get_clock_info("monotonic")`; segment file names |

## Consequences for the G02 analysis

- **Gap rule (RC-09, heartbeat loss):** a gap starts at the last frame received, not at the next `disconnect` event. The threshold is the capture's own 15 s receive timeout (`live.py`, `ws.settimeout(15)`); Kraken sends a heartbeat every second. Without this rule, R-4 would count the sleep as valid book time.
- **R-4 for this run fails.** The run spans about 181 h of wall-clock time and has at least 13.46 h without data, so a valid book covers at most about 92.6 % of the time. That is well under 99 %. The longest unbroken stretch runs from 10-30 08:57 to the end of the run, about 5 days 15 h.
- **T-5/T-6:** the two samples over 1 s count as clock skew for intraday decisions while they are the latest sample (RC-07, DEC-067). They are reported, not filtered out.
- **The run stays as evidence.** It is analysed in full when it ends, including the checks recorded in the [review fixes](review-fixes.md#effect-on-the-running-captures).

## Decision asked 2026-10-31

| ID | Question (verbatim) | Option chosen (verbatim) |
| --- | --- | --- |
| DEC-070 | "The Mac was put to sleep (by loginwindow, so through the Apple menu, the lid or the power button) from 29 Oct 19:03 to 30 Oct 08:57 UTC. The 7-day capture paused for about 13.5 h. Its timer counts awake time only, so it now ends around 4 Nov 23:57 UTC. That still gives 7 days of capture, but the longest unbroken stretch is about 5 days 15 h, which fails R-4 (book valid ≥ 99 % of the time). G02 also waits for the 30-day pull, which ends 27 Nov, so a second run would not delay G02. What should I do?" | "Rerun after it ends (Recommended)": "Let the current run finish untouched and keep it as evidence. Then start a fresh 7-day run (about 13 GB; 98 GB is free) ending around 12 Nov. Use the fixed code if #32/#33 are merged by then, otherwise 5b69e7f. You keep the Mac awake for those 7 days." |

Options not chosen:
- "Accept it with the gap": "No rerun. Record the 13.5 h as a gap, report R-4 as failed over the whole window, and use the 5 d 15 h unbroken stretch as the evaluation window."
- "Decide at G02": "Record the gap now and leave the choice to the G02 review. A rerun started then would end around 4 Dec, after the 30-day pull."

## Rerun plan (DEC-070)

1. Let the first run end by itself, about 2026-11-04 23:57 UTC. Check that it has exited before starting anything.
2. Put the rerun's code in a **separate** copy, `~/gladiator-capture-run2`. Leave `~/gladiator-capture` unchanged, because the 30-day REST job (DEC-068) runs from it until 2026-11-27. The copy is taken from `master` if #32 and #33 are merged by then, and otherwise from `5b69e7f`. Its revision is recorded.
3. Write to a new directory, `~/gladiator-data/live-7d-run2`, outside the repository (DEC-030). Use the same pairs, depth, duration and SNTP interval as DEC-064 and DEC-066.
4. Run under `caffeinate -i -s`, which also blocks system sleep while on AC power. **That still does not block a user-initiated sleep, so the Mac must not be put to sleep, and its lid must not be closed, for the 7 days.**
5. Check its `events.jsonl` and `pmset -g log` for sleep once a day, read-only.
6. The G02 analysis uses the rerun for R-4 and reports both runs.

Disk: 98 GB free on 2026-10-31. The first run is at 12 GB and will be about 26 GB; the rerun adds about 13 GB.
