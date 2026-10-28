# P02 network capture: transport and live capture

[Task](../../tasks/TASK-P02-005.md) · [Capture and recovery](capture-and-recovery.md) · [Validation plan](capture-validation-plan.md) · [Results on held files](capture-validation-results.md)

**Status: in progress, 2026-10-28.**

## Decisions asked, 2026-10-28

The user's answers. Each question and the chosen option are quoted verbatim.

| Decision | Question (verbatim) | Chosen option: label — description (verbatim) |
| --- | --- | --- |
| DEC-059 | "Kraken archive vs REST: the contract's current rule (round archive volume to 8 decimals, then require equality) gives 4 mismatches, 3 of which are float rounding on ETHUSD. Which comparison rule should the event contract use?" | "Relative 1e-9 tolerance (Recommended)" — "Prices and trade counts must match exactly; volumes may differ by at most 1e-9 relative. This leaves only the real XBTUSD 2026-09-10 difference, and matches the P01 sample." |
| DEC-060 | "Bar identity: key bars on their start time instead of their row position in the file? Row positions shift when a file gains a row, or when the REST window slides each day." | "Key on bar start (Recommended)" — "A bar keeps its identity across revisions and repeated REST pulls; the row number stays in raw_locator for tracing." |
| DEC-061 | "The 30-day Kraken REST pull (DEC-057) needs something to run it once a day. How should it run?" | "Local cron/launchd job (Recommended)" — "I add a small script and you install one launchd job on this Mac; it runs at 00:15 UTC daily, keyless, writing outside the repo. You can remove it any time." |
| DEC-062 | "Next step: build the network side, i.e. a real HTTPS transport for fetch() (for the REST pull, HEAD requests and Q4 archive) and the Kraken WebSocket live capture (W-J), as TASK-P02-005?" | "Yes, build and test it (Recommended)" — "Standard library only (urllib for HTTPS; a minimal WebSocket client). It is tested offline first; the first real calls are the 18 HEAD requests, then a 1-hour live capture, all under DEC-044/057." |

Unchosen options: "Keep the 8-decimal rule"; "Keep row index"; "Claude scheduled routine"; "I run it manually"; "Build it, but no real calls yet"; "Pause P02 here".
