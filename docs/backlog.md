# Open backlog

> **Source recovery update — 2026-10-23:** Original GLADIATOR releases, including the complete 54-file v1.0 package, are now imported. See the [recovered document index](<sources/originals/RECOVERED.md>). Earlier missing-source statements below are historical. G00 passed on 2026-10-24 (DEC-027).

[Documentation index](README.md) · [Phase 00](phases/00-baseline/README.md) · [Source intake](sources/originals/README.md)

This is the unresolved design/source backlog. Assigned execution work belongs on the [Claude task board](tasks/README.md): OPEN-001/002 feed TASK-P00-001; OPEN-003 feeds TASK-P00-002. Codex supports brainstorming; Claude Code carries accepted tasks into implementation and PRs.

| ID | Priority | Work item | Required input / closure evidence | Affects |
| --- | --- | --- | --- | --- |
| OPEN-001 | First — Partly done 2026-10-23: release archives recovered and preserved (TASK-P00-001, PR #3 import, PR #4 review); the v1.0 conversation evidence and source-message IDs are not preserved (PF-02, PF-04) | Recover original Markdown and latest v1.0 architecture from “Day Trading Income Feasibility” | Full chat/spec export or accessible original text; preserve source messages and attachments | G00; all downstream work |
| OPEN-002 | First — Partly done 2026-10-23: inventory, checksums and version evidence in the [preservation review](evidence/P00/preservation-review.md); section mappings in the [reconciliation summary](evidence/P00/v1.0-reconciliation.md). Supersession is not established: no release states it (PF-03), and precedence was decided on 2026-10-23 (DEC-020, DEC-024) | Inventory every recovered spec and determine version/supersession | Original filename, checksum, header version, source location, all section mappings | G00; source manifest |
| OPEN-003 | First — Done; G00 passed 2026-10-24 (DEC-027): mapping ([summary](evidence/P00/v1.0-reconciliation.md)), decisions DEC-014–DEC-025 and the [baseline record](evidence/P00/baseline-decision.md) | Reconcile proposed phases and IDs with actual v1.0 | Conflict/alias map and accepted baseline record; no unmapped original specs | G00; architecture and traceability |
| OPEN-004 | Before G01 — Done; G01 passed 2026-10-27 (DEC-047): scope and defaults confirmed (DEC-036 to DEC-045), sources in the [`source_approval` records](evidence/P01/source-approvals.md) | Select bounded asset class, venue/instruments and data access scope | Source rights, capabilities, costs, history, blind spots, outage handling and agreed budget | CMP-01; G01 |
| OPEN-005 | Before G01 — Done; G01 passed 2026-10-27: objectives approved with amendments (DEC-042) in the [register](evidence/P01/acceptance-objectives.md); measurement follows in P02 to P05 | Define robustness and latency objectives | Workload, percentile/time-window definitions, clock uncertainty, stale/recovery limits and evidence method | REQ-002/004/005; G01 |
| OPEN-006 | Before G03 — meanings decided 2026-10-23 (DEC-018); accounting convention open | Resolve meanings of ledger and accounting convention | Original terminology plus separate book/event-journal/account definitions and reconciliation examples | CMP-03/04; G03 |
| OPEN-007 | Before G04 | Bound context/regime hypotheses | Point-in-time source availability, revision rules and relevance tests | CMP-05/06; G04 |
| OPEN-008 | Before G05 — role model decided 2026-10-23 (DEC-014); contracts open | Specify Core, Gladiators, Arena, Judges, Management and Gatekeeper contracts | Original sections, algorithm research, assessment criteria and independent risk authority | CMP-07/08/09/12/13/14; G05 |
| OPEN-009 | Before G06 | Pre-register evaluation and simulation assumptions | Held-out policy, costs/latency/fill uncertainty, acceptance criteria and failed-hypothesis handling | CMP-10; G06 |
| OPEN-010 | Before G07 | Define paper-only operational readiness | Isolation scope, incident/recovery drills, monitoring, responsibilities and review evidence | CMP-09/10/11/12; G07 |
| OPEN-011 | First — Done 2026-10-23: DEC-014–DEC-025 ([TASK-P00-003](tasks/TASK-P00-003.md)) | Decide reconciliation requests DR-01–DR-12 (roles, primary input, phase crosswalk, provisional selections, ledger meanings, proposed requirements, lineage, live annex, stack, REQ-001 wording, precedence, audit tool) | User decisions recorded in the decision register; [list](evidence/P00/v1.0-reconciliation.md#consolidated-decision-requests) | G00; all downstream |

## Immediate next action

Updated 2026-10-23: originals are recovered and reconciled, and DR-01–DR-12 are decided. G00 passed on 2026-10-24 ([gate record](evidence/P00/g00-gate-record.md)); the next action is the P01 task packets. *Updated 2026-10-27: G01 passed (DEC-047); the next actions are the P01 sample plan and the P02 packets.* Earlier text: recover the specification text from the source chat, then follow the [original intake checklist](sources/originals/README.md); the conversation reader returned only five recent user turns, and the browser attempt required login.

Implementation still waits on its own phase gates. No owner, budget, schedule or model performance is assumed. Unassigned work remains unassigned until a real owner is recorded.
