# P05 — Core, Judges, and Managers

Claude Code handoff: [P05 task packets and candidates](../../tasks/README.md#p05) · [delegation and PR workflow](../../working-with-claude.md). Dispatch Ready task cards rather than the whole phase checklist.

**Status: PROPOSED; not started.** The role model follows [DEC-014](../../decisions/README.md) (2026-10-23): Gladiators (CMP-13), Arena (CMP-14), Core decision kernel (CMP-07), Judges (CMP-08), Management (CMP-09) and Gatekeeper (CMP-12). The phase title keeps its original wording.

**Dependencies:** accepted G04 and the input definitions from [P04](../04-features-and-context/README.md).

## Objective

Define research decision contracts for Core, Judges, and Managers and their evidence trail. The source separation, per DEC-014, is: Gladiators forecast; the Core kernel decides, sizes and issues intents; the Gatekeeper alone approves them under deterministic policy; Judges and the Arena evaluate; and Management promotes and budgets. The contracts stay proposals until G05. Reinstated sections L-017 (Core invariants), L-018 (Arena policy) and L-021 (Gatekeeper market policy) apply ([baseline record](../../evidence/P00/baseline-decision.md#reinstated-sections)). Any decision pathway must have a deterministic means to abstain when its required evidence is missing or invalid.

## Documentation deliverables

- [This phase planning specification](README.md), defining the decision-design work.
- Component contracts describing inputs, outputs, authority, versions, state, and failure behavior for Core, Judges, and Managers; future evidence: `../../evidence/P05/decision-contracts.md`.
- A deterministic policy and abstention specification covering data quality, state validity, ledger reconciliation, conflicting assessments, and approved risk constraints; future evidence: `../../evidence/P05/policy-and-abstention.md`.
- A decision trace format and scenario validation matrix mapping each decision to data, features, component versions, rules, and reasons; future evidence: `../../evidence/P05/decision-validation.md`.
- Cited algorithm alternatives, reference baselines, adaptation rationale and bounded fixture comparisons for each research hypothesis, including rejected candidates and limitations; future evidence: `../../evidence/P05/algorithm-research.md`. VAL-009 covers this comparison; held-out end-to-end evaluation follows in P06.

## Traceability

**Requirements:** [REQ-005, REQ-006, REQ-007, REQ-008, REQ-009, REQ-010, REQ-011, REQ-012; Proposed REQ-013, REQ-014, REQ-016, REQ-017, REQ-018, REQ-019](../../requirements.md).

**Components:** [CMP-04 own-account ledger, CMP-06 features/regimes, CMP-07 Core decision kernel, CMP-08 Judges, CMP-09 Management, CMP-12 Gatekeeper, CMP-13 Gladiators, CMP-14 Arena, CMP-11 audit and operations](../../traceability/components.md).

**Architecture:** [architecture index](../../architecture/README.md). **Gate:** G05 in the [milestone register](../../milestones.md).

## Ordered tasks

1. [ ] Reconfirm each component's responsibility and authority against the reconciled v1.0 baseline.
2. [ ] Research the P01 algorithm candidates using primary references; compare alternatives and reference baselines, record adaptation choices, rejected hypotheses and limitations.
3. [ ] Define and later gather bounded comparison evidence for VAL-009 using versioned fixtures; pre-register the separate held-out P06 evaluation before viewing its results.
4. [ ] Specify typed input/output contracts and decision provenance without coupling research output to live execution.
5. [ ] Define rule ordering, conflict resolution, invalid-input behavior, abstention, and deterministic constraint enforcement.
6. [ ] Select and approve policy values, scenario coverage, and acceptance criteria from the agreed research scope; do not invent risk thresholds.
7. [ ] Define audit records and representative valid, invalid, stale, contradictory, and unreconciled scenarios.
8. [ ] Attach later research-comparison, scenario and determinism evidence, then seek G05 acceptance.

## G05 — Exit gate

Pass only when each research hypothesis has cited algorithm alternatives, reference-baseline comparisons, rationale and limitations; every decision pathway has a versioned contract, authority boundary, and trace record; every specified invalid-input or constraint scenario produces its approved outcome; and identical approved inputs and policies reproduce the agreed decisions. Risk values and acceptance criteria require a recorded baseline decision before validation. Bounded fixtures and controlled ledger/simulator stubs can verify contracts here; full simulator integration belongs to G06. The reviewer must accept actual comparison and scenario evidence; the component names or written policies alone do not pass G05.

**Evidence needed:** cited research alternatives and VAL-009 comparison records, reconciled contracts, policy approvals, scenario matrix, reproducible decision traces, constraint and abstention results, fixture/stub scope declarations and dated approval.

**Failure and rework:** keep the affected pathway in abstention, revise its contract or policy, and repeat impacted scenarios. Return to G04 for input-definition defects or G03 for ledger/state defects; reopen downstream evaluations affected by policy changes.

**Exact next step:** after G04 acceptance, draft the responsibility and authority table for Core, Judges, and Managers using the accepted v1.0 terminology.

**Implementation boundary:** these are research and policy documents. No autonomous agent, order-routing connector, or live trading behavior is implemented or authorized.
