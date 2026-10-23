# Documentation index

> **Source recovery update — 2026-10-23:** Original GLADIATOR releases, including the complete 54-file v1.0 package, are now imported. See the [recovered document index](<sources/originals/RECOVERED.md>). Earlier missing-source statements below are historical. G00 still awaits reconciliation/review.

[Project home](../README.md) · [Full file catalog](catalog.md) · [Roadmap](roadmap.md)

**Status:** provisional planning documents pending recovery of the original v1.0 specifications.

## Read in this order

| Document | Purpose |
| --- | --- |
| [Source register](sources/README.md) | Establish what is available, missing and externally referenced |
| [Requirements](requirements.md) | Stable requirement IDs and provenance |
| [Architecture map](architecture/README.md) | Proposed component boundaries and order-flow/ledger distinctions |
| [Interface questions](architecture/contracts.md) | Event, state, ledger and decision contract checklist |
| [Roadmap](roadmap.md) | Phase order and dependency rationale |
| [Phase index](phases/README.md) | Detailed tasks and gate criteria for P00–P07 |
| [Claude Code entry point](../CLAUDE.md) | Short project instructions for the implementation agent |
| [Claude execution workflow](working-with-claude.md) | Delegation, worktree ownership, verification and PR handoff |
| [Task board and packets](tasks/README.md) | Readiness, concrete starter tasks and phase task candidates |
| [Task template](tasks/task-template.md) | Required scope, acceptance, evidence and PR fields |
| [PR template](../.github/pull_request_template.md) | Source/task/revision traceability and reviewer context |
| [Milestone register](milestones.md) | Gate state and evidence required for closure |
| [Requirement traceability](traceability/requirements-matrix.md) | Requirement → component → phase → gate → evidence |
| [Component traceability](traceability/components.md) | Component responsibilities, dependencies and handoffs |
| [Acceptance scenarios](validation/acceptance-scenarios.md) | Proposed future verification cases |
| [Backlog](backlog.md) | Immediate source-recovery work and unresolved design questions |
| [Decision register](decisions/README.md) | Confirmed task boundaries and proposed decisions |
| [Evidence index](evidence/README.md) | Gate record format and evidence handling |
| [Setup verification](validation/setup-report.md) | Checks of this documentation workspace only |
| [Claude handoff readiness](validation/claude-handoff.md) | TASK-DOC-001 agent, link, checksum and repository/publishing checks |
| [IDE guide](ide-guide.md) | Opening, searching and navigating the project |
| [Change log](../CHANGELOG.md) | Documentation changes |

## Documentation conventions

Stable identifiers: `REQ-001` requirements; `CMP-01` components; `P00` phases; `G00` gates; `DEC-001` decisions; `VAL-001` acceptance scenarios; `SRC-001` user/source records; `EXT-001` external references.

Execution uses `TASK-P00-001` task IDs, and `TASK-DOC-001`/`TASK-DOC-002` for the handoff preparation tasks. Task cards own work state, branch/commit, evidence and PR references. The [task board](tasks/README.md) defines those states separately from gates.

Document states are **Captured source**, **Confirmed task constraint**, **Proposed**, **Pending source**, or **Accepted baseline**. An organised document is not evidence that its proposed system exists.

Gates are **Pending**, **Not started**, **Under review**, **Passed**, or **Reopened**. A gate passes only when its evidence, owner, reviewer, date and baseline are recorded. No gate is passed by this setup.

Preserve originals under [source intake](sources/originals/README.md). Place new analysis outside originals, cite source paths/sections, and log conflicts in the [backlog](backlog.md). Dates use ISO format; technical event-time conventions remain a baseline decision.
