# GLADIATOR

> **Source recovery update — 2026-10-23:** Original GLADIATOR releases, including the complete 54-file v1.0 package, are now imported. See the [recovered document index](<docs/sources/originals/RECOVERED.md>). Earlier missing-source statements below are historical. G00 passed on 2026-10-24 ([gate record](docs/evidence/P00/g00-gate-record.md)).

Order-flow and ledger research system — documentation workspace.

**Workspace edition:** 0.3, updated 22 October 2026 (Europe/London).  
**Requested architecture baseline:** v1.0 — original specifications not yet recovered.  
**Current activity:** documentation setup only. No trading software or connections are implemented.

## Start here

1. Read the [documentation index](docs/README.md).
2. Review the [source register](docs/sources/README.md) to see exactly what was recovered.
3. Follow the [phased roadmap](docs/roadmap.md) and [Phase 00](docs/phases/00-baseline/README.md).
4. Use the [requirements matrix](docs/traceability/requirements-matrix.md) to trace a requirement to its component, phase, gate and future evidence.
5. Check the [milestone register](docs/milestones.md) before treating any phase as complete.

Open **GLADIATOR.code-workspace** in Cursor or another compatible IDE. Relative Markdown links work from this folder without a server or extension. The [IDE guide](docs/ide-guide.md) explains navigation.

## Claude Code handoff

Use Codex for brainstorming and design discussion. Use Claude Code for assigned implementation, wiring, checks and PRs. Start Claude Code in this GLADIATOR folder; [CLAUDE.md](CLAUDE.md) points to the [task board](docs/tasks/README.md), [execution workflow](docs/working-with-claude.md), three project agents and PR template.

The handoff is committed and pushed to the [GitHub repository](https://github.com/akibrahimug/gladiators) on `master`. Claude Code's readiness inspection, [TASK-DOC-001](docs/tasks/TASK-DOC-001.md), recorded agent discovery and verified publishing access ([report](docs/validation/claude-handoff.md)). Each task gets its own branch and draft PR ([DEC-009](docs/decisions/README.md)). G00 passed on 2026-10-24; implementation candidates remain Draft until the user explicitly accepts one as Ready and its phase's predecessor gate has passed.

## What is established

The current brief requests preservation of existing specifications, a coherent phase plan, indexes, milestone gates and component traceability. The readable prior chat asks for market-event and volume analysis, investigation of market-moving context, and rigorous research around a Core, Judges and Managers.

The retrieved chat contains five user turns; its assistant messages contain reference markers instead of specification text. No local GLADIATOR project or specification files were located. The [captured record](docs/sources/captured/conversation-reader.json) is preserved. **This workspace is a proposed organisational scaffold, not an imported or approved v1.0 architecture.**

## Working boundaries

- Prioritise observable market events over chart-derived signals; distinguish market order books from the system's own account ledger.
- Keep source facts, user requirements, proposed design and unresolved questions visibly separate.
- Add original specifications intact when recovered; map them rather than rewriting them.
- Complete this documentation task without executable trading code, broker connections, credentials, live orders or deployment.
- Planned later work ends at simulation and paper readiness. Any live-trading phase requires a separate future scope decision.

## Current state

| Item | State |
| --- | --- |
| Documentation structure and navigation | Created; see [setup verification](docs/validation/setup-report.md) |
| Original v1.0 specification import | Done 2026-10-23 — [SRC-003](docs/sources/README.md), [preservation review](docs/evidence/P00/preservation-review.md) |
| G00 baseline gate | Passed 2026-10-24 ([gate record](docs/evidence/P00/g00-gate-record.md)) |
| G01–G07 development gates | Not started |
| Implementation and trading | Not started |

See the [open backlog](docs/backlog.md), [decisions](docs/decisions/README.md) and [change log](CHANGELOG.md).
