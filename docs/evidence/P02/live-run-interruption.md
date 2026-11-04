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

- **Gap rule (proposed for the G02 analysis; open item):** RC-09 records a `GapInterval` from the disconnect to the next valid book. For a frozen process that undercounts, so the analysis proposes that a gap starts at the last frame received when the next frame is more than 15 s later. That is RC-09's "heartbeat loss" with the capture's own receive timeout (`live.py`, `ws.settimeout(15)`); Kraken sends a heartbeat every second. The run's built-in summary (`invalid_book_ns`) counts invalid time only from the detected disconnect, so it counts the sleep as valid and **must not be used for R-4**. The rule goes to the user with the G02 results, and RC-09 is updated only if it is accepted.
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

The user chose to have the rerun started automatically ([TASK-P02-010](../../tasks/TASK-P02-010.md)). At 2026-11-04 10:10:47 UTC the coordinator armed [`ops/rerun/run2-watcher.sh`](../../../ops/rerun/run2-watcher.sh) against the first run's pid 76475, under `caffeinate -i -s`, from `~/gladiator-data/run2-watcher/`. The watcher does steps 1 to 4 above:

- It waits for the first run to exit and requires that run's `live-summary.jsonl`.
- It copies `origin/master` as it is at that moment into `~/gladiator-capture-run2`, recording the revision and whether #33 is included.
- It runs the offline tests, then starts the rerun.

If any check fails, it logs the reason and does not start the rerun. The start is recorded here once it is observed.

Disk on 2026-11-04 10:10 UTC: 265 GB free. The first run held 27 GB after about 6.6 days awake, which agrees with the estimate of about 31 GB for a full run.
