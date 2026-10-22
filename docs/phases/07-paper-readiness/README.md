# P07 — Paper readiness

Claude Code handoff: [P07 task packets and candidates](../../tasks/README.md#p07) · [delegation and PR workflow](../../working-with-claude.md). Dispatch Ready task cards rather than the whole phase checklist.

**Status: PROPOSED; not started.** Original v1.0 reconciliation is required before this phase can be accepted.

**Dependencies:** accepted G06 and the validated scope from [P06](../06-simulation-and-validation/README.md).

## Objective

Define whether the evaluated system is ready for a bounded paper or simulated observation exercise, with explicit operating ownership, audit evidence, and stop conditions. This phase assesses readiness only; starting a paper exercise remains a separately recorded decision. Neither action authorizes live trading.

## Documentation deliverables

- [This phase planning specification](README.md), defining paper-readiness review.
- A paper exercise plan specifying environment identity, source scope, simulated-account boundaries, planned duration, observation criteria, and responsibilities; future evidence: `../../evidence/P07/paper-exercise-plan.md`.
- An operations runbook covering startup checks, data degradation, ledger discrepancies, policy abstention, alerts, stop/recovery behavior, and incident records; future evidence: `../../evidence/P07/operations-runbook.md`.
- A readiness review and handoff record linking prior gates, rehearsal evidence, known limitations, selected acceptance criteria, and the separate decision about whether to begin; future evidence: `../../evidence/P07/readiness-review.md`.

## Traceability

**Requirements:** [REQ-003, REQ-005, REQ-006, REQ-009, REQ-010, REQ-011, REQ-012](../../requirements.md).

**Components:** [CMP-01 source registry, CMP-02 ingest and raw log, CMP-04 own-account ledger, CMP-09 Managers/risk, CMP-10 simulation/paper, CMP-11 audit and operations](../../traceability/components.md).

**Architecture:** [architecture index](../../architecture/README.md). **Gate:** G07 in the [milestone register](../../milestones.md).

## Ordered tasks

1. [ ] Carry the accepted simulation scope, assumptions, and limitations into the proposed paper exercise plan.
2. [ ] Define a verifiable paper/simulation environment boundary and the checks that establish no live order route is available in the exercise.
3. [ ] Assign an operating owner and specify startup, monitoring, abstention, stopping, recovery, and incident procedures.
4. [ ] Select and approve exercise duration, evidence coverage, operational thresholds, rehearsal scenarios, and readiness criteria.
5. [ ] When separately authorized and implemented, rehearse invalid data, disconnects, unreconciled ledger state, constraint failures, and stop/recovery behavior.
6. [ ] Record the G07 review; if accepted, document the separate decision on whether and when to start the bounded paper exercise.

## G07 — Exit gate

Pass only when G00–G06 evidence remains applicable; the paper/simulation boundary is demonstrated; every approved operational rehearsal satisfies its expected outcome; and an identified reviewer accepts the plan, owner, limitations, and evidence. Duration and operational thresholds require recorded approval before rehearsal or evaluation. A completed documentation folder cannot pass G07, and G07 approval itself does not start an exercise or grant live trading authority.

**Evidence needed:** linked prior gate decisions, approved exercise plan and runbook, environment-boundary evidence, rehearsal results and incident dispositions, and dated readiness approval with a separate start decision if one is later made.

**Failure and rework:** keep paper operation unstarted or stopped, resolve the failed prerequisite, and repeat the affected rehearsal. Reopen upstream gates when their evidence no longer applies; retain the failed review as part of the audit trail.

**Exact next step:** after G06 acceptance, draft the paper exercise plan from the evaluated scope and name its proposed operating owner.

**Implementation boundary:** no paper connector, credentials, environment, order-routing capability, or live trading is set up by this documentation work. Live trading requires a separately scoped and explicitly authorized project.
