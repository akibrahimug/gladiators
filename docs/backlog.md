# Open backlog

> **Source recovery update — 2026-10-23:** Original GLADIATOR releases, including the complete 54-file v1.0 package, are now imported. See the [recovered document index](<sources/originals/RECOVERED.md>). Earlier missing-source statements below are historical. G00 still awaits reconciliation/review.

[Documentation index](README.md) · [Phase 00](phases/00-baseline/README.md) · [Source intake](sources/originals/README.md)

This is the unresolved design/source backlog. Assigned execution work belongs on the [Claude task board](tasks/README.md): OPEN-001/002 feed TASK-P00-001; OPEN-003 feeds TASK-P00-002. Codex supports brainstorming; Claude Code carries accepted tasks into implementation and PRs.

| ID | Priority | Work item | Required input / closure evidence | Affects |
| --- | --- | --- | --- | --- |
| OPEN-001 | First | Recover original Markdown and latest v1.0 architecture from “Day Trading Income Feasibility” | Full chat/spec export or accessible original text; preserve source messages and attachments | G00; all downstream work |
| OPEN-002 | First | Inventory every recovered spec and determine version/supersession | Original filename, checksum, header version, source location, all section mappings | G00; source manifest |
| OPEN-003 | First | Reconcile proposed phases and IDs with actual v1.0 | Conflict/alias map and accepted baseline record; no unmapped original specs | G00; architecture and traceability |
| OPEN-004 | Before G01 | Select bounded asset class, venue/instruments and data access scope | Source rights, capabilities, costs, history, blind spots, outage handling and agreed budget | CMP-01; G01 |
| OPEN-005 | Before G01 | Define robustness and latency objectives | Workload, percentile/time-window definitions, clock uncertainty, stale/recovery limits and evidence method | REQ-002/004/005; G01 |
| OPEN-006 | Before G03 | Resolve meanings of ledger and accounting convention | Original terminology plus separate book/event-journal/account definitions and reconciliation examples | CMP-03/04; G03 |
| OPEN-007 | Before G04 | Bound context/regime hypotheses | Point-in-time source availability, revision rules and relevance tests | CMP-05/06; G04 |
| OPEN-008 | Before G05 | Resolve Core, Judges and Managers roles | Original sections, algorithm research, assessment criteria and independent risk authority | CMP-07/08/09; G05 |
| OPEN-009 | Before G06 | Pre-register evaluation and simulation assumptions | Held-out policy, costs/latency/fill uncertainty, acceptance criteria and failed-hypothesis handling | CMP-10; G06 |
| OPEN-010 | Before G07 | Define paper-only operational readiness | Isolation scope, incident/recovery drills, monitoring, responsibilities and review evidence | CMP-09/10/11; G07 |

## Immediate next action

Recover the specification text from the source chat, then follow the [original intake checklist](sources/originals/README.md). The current conversation reader returns only five recent user turns with assistant reference markers, no attachments and no older-page cursor. The separate browser attempt requires login; it did not provide the original content.

This gap blocks baseline acceptance, not the documentation structure. No owner, budget, schedule or model performance is assumed. Unassigned work remains unassigned until a real owner is recorded.
