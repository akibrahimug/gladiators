# Phase documentation

**Status: PROPOSED. P00 is complete and G00 passed on 2026-10-24. G01 passed on 2026-10-27, and P01's sample steps 0, 1 and 3 ran the same day. P02–P07 are not started.**

These folders make the documentation navigable. Their presence does not establish that a phase, component, experiment, or gate has been completed. The original architecture was recovered and reconciled, and G00 passed on 2026-10-24 ([gate record](../evidence/P00/g00-gate-record.md)).

| Phase | Planning document | Required predecessor | Exit gate | Current state |
| --- | --- | --- | --- | --- |
| P00 | [Baseline and source reconciliation](00-baseline/README.md) | None | G00 | Complete; G00 passed on 2026-10-24 |
| P01 | [Research and data access](01-research-and-data-access/README.md) | Accepted G00 | G01 | G01 passed on 2026-10-27; sample steps 0, 1 and 3 run |
| P02 | [Event capture](02-event-capture/README.md) | Accepted G01 | G02 | Not started |
| P03 | [Market state and ledger](03-market-state-and-ledger/README.md) | Accepted G02 | G03 | Not started |
| P04 | [Features and context](04-features-and-context/README.md) | Accepted G03 | G04 | Not started |
| P05 | [Core, Judges, and Managers](05-core-judges-and-managers/README.md) | Accepted G04 | G05 | Not started |
| P06 | [Simulation and validation](06-simulation-and-validation/README.md) | Accepted G05 | G06 | Not started |
| P07 | [Paper readiness](07-paper-readiness/README.md) | Accepted G06 | G07 | Not started |

Each phase README is its current planning specification. Future evidence paths are shown as inline code until those files exist. Unchecked tasks are outstanding work, including work that may require a later implementation request.

For Claude Code, turn phase work into bounded task packets using the [task board](../tasks/README.md) and [execution workflow](../working-with-claude.md). Phase checklists describe outcomes; individual Ready task cards define worker scope, files, acceptance and PR delivery. Source/gate dependencies still apply.

Follow the [roadmap](../roadmap.md) for sequencing, the [milestone register](../milestones.md) for gate decisions, the [requirements register](../requirements.md) for requirement IDs, and [component traceability](../traceability/components.md) for component IDs. The [architecture index](../architecture/README.md) records the proposed architecture and its reconciliation boundary.

## Gate rules

- G00–G07 are sequential acceptance decisions. Writing a document or creating a folder never passes a gate automatically.
- Gate evidence must name its source baseline, document or implementation revision, reviewer, decision date, and unresolved exceptions. Record decisions in the milestone register and link the supporting evidence.
- Select measurable acceptance criteria before evaluating results. Thresholds, test windows, supported sources, instruments, and environments require a recorded baseline decision; no numeric performance threshold is assumed here.
- A changed upstream contract triggers an impact review of affected requirements, components, downstream phases, and previously accepted gates. Reopen the affected gate when its evidence no longer supports the decision.
- This setup is documentation only. Later implementation tasks remain unstarted. P07 concerns readiness for paper or simulated operation only; no gate in this plan authorizes live trading.

**Source phase schemes:** the recovered sources use their own phase, stage and gate labels (Phase 0–9, Stages A–I, P0–P8, G0–G6 and others). They are crosswalked, provisionally, in the [reconciliation summary](../evidence/P00/v1.0-reconciliation.md#source-identifier-crosswalk), kept by DEC-016; cite them file-qualified, not as P/G IDs.

**Immediate next step (superseded 2026-10-23 for recovery):** originals are recovered and mapped; DR-01–DR-12 were decided on 2026-10-23 (DEC-014–DEC-025), and G00 passed on 2026-10-24 (DEC-027); the next step is P01. Earlier text: obtain the original v1.0 Markdown specifications and source attachments, then complete P00 reconciliation before approving any downstream scope.
