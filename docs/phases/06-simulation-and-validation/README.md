# P06 — Simulation and validation

Claude Code handoff: [P06 task packets and candidates](../../tasks/README.md#p06) · [delegation and PR workflow](../../working-with-claude.md). Dispatch Ready task cards rather than the whole phase checklist.

**Status: PROPOSED; not started.** Original v1.0 reconciliation is required before this phase can be accepted.

**Dependencies:** accepted G05 and the decision contracts from [P05](../05-core-judges-and-managers/README.md).

## Objective

Specify a reproducible simulation study that evaluates the accepted research system under documented market and execution assumptions. Separate measured outcomes from modeled fills and unsupported claims. Approve the evaluation design before inspecting the results used for acceptance.

## Documentation deliverables

- [This phase planning specification](README.md), defining simulation and evaluation work.
- A simulator contract covering event replay, order/fill modeling, fees, delays, partial fills, rejected actions, ledger effects, and model limitations; future evidence: `../../evidence/P06/simulator-contract.md`.
- An evaluation protocol with dataset identities, chronological partitions, development/evaluation separation, baseline comparators, scenario coverage, and preselected acceptance criteria; future evidence: `../../evidence/P06/evaluation-protocol.md`.
- A report template for results, uncertainty, sensitivity, failure cases, and reproduction instructions; future evidence: `../../evidence/P06/validation-report.md`.

## Traceability

**Requirements:** [REQ-003, REQ-004, REQ-005, REQ-006, REQ-009, REQ-010, REQ-011, REQ-012](../../requirements.md).

**Components:** [CMP-03 book/replay, CMP-04 own-account ledger, CMP-07 Core research, CMP-08 Judges, CMP-09 Managers/risk, CMP-10 simulation/paper, CMP-11 audit and operations](../../traceability/components.md).

**Architecture:** [architecture index](../../architecture/README.md). **Gate:** G06 in the [milestone register](../../milestones.md).

## Ordered tasks

1. [ ] Define the simulator's modeled behaviors and identify inputs that cannot support reliable fill or queue assumptions.
2. [ ] Specify costs, timing, liquidity, accounting, and execution assumptions with provenance and sensitivity ranges chosen for the approved scope.
3. [ ] Select chronological data partitions, comparison baselines, stress scenarios, metrics, and reproduction artifacts.
4. [ ] Record reviewer approval of the evaluation protocol and acceptance thresholds before using held-out results for acceptance.
5. [ ] When separately authorized and implemented, run the approved study and record all results, limitations, and failed scenarios.
6. [ ] Review reproducibility and sensitivity evidence, then record the G06 decision and remaining limitations.

## G06 — Exit gate

Pass only when the approved simulation and evaluation criteria are met with reproducible, revision-specific evidence; accounting and risk invariants pass across the selected scenarios; and the reviewer records the accepted limitations and model sensitivity. Thresholds, windows, assumptions, and benchmark choices must be selected and approved before acceptance evaluation. A favorable result under one modeled assumption does not establish readiness beyond the evaluated scope.

**Evidence needed:** simulator contract, approved protocol, data/configuration/version identities, complete result report including failures, sensitivity results, reproduction evidence, and dated approval. No study has been run by this documentation setup.

**Failure and rework:** report the failure against its preselected criterion, revise the hypothesis or design, and evaluate on an appropriately controlled protocol. Return to the phase owning the defect and reopen G06 after any material upstream change.

**Exact next step:** after G05 acceptance, draft the simulator contract and explicitly enumerate unsupported execution assumptions.

**Implementation boundary:** simulation code and experiments are future work. G06 does not authorize connection to a live trading account.
