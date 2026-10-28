# P02 recovery results (RC-05 to RC-08)

[Task](../../tasks/TASK-P02-006.md) · [Capture and recovery](capture-and-recovery.md) · [Network capture](network-capture.md)

**Status: in progress, 2026-10-28.**

## Decisions asked, 2026-10-28

The user's answers. Each question and the chosen option are quoted verbatim.

| Decision | Question (verbatim) | Chosen option: label — description (verbatim) |
| --- | --- | --- |
| DEC-064 | "When should the 7-day Kraken live capture (the rest of W-J) run? It's about 13 GB uncompressed (about 1 GB gzipped) and covers Kraken's announced maintenance on 2026-10-29, 08:01–08:16 UTC. It runs from this Mac, so the Mac must stay awake and online." | "Start it now (Recommended)" — "I launch it in the background from the fixed code (head of PR #30); it also exercises the maintenance exclusion and real reconnects." |
| DEC-065 | "While that runs, should I build the remaining recovery tests (RC-05 crash-completion marker, RC-06 disk-full injection, RC-07/RC-08 clock-offset handling on live records) as TASK-P02-006?" | "Yes (Recommended)" — "Offline code and tests only; no new network calls. Closes CV-11." |

Unchosen options: "You start it later"; "Skip the 7-day window"; "Not now".
