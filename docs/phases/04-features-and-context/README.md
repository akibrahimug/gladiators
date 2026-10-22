# P04 — Features and context

Claude Code handoff: [P04 task packets and candidates](../../tasks/README.md#p04) · [delegation and PR workflow](../../working-with-claude.md). Dispatch Ready task cards rather than the whole phase checklist.

**Status: PROPOSED; not started.** Original v1.0 reconciliation is required before this phase can be accepted.

**Dependencies:** accepted G03 and the valid state contracts from [P03](../03-market-state-and-ledger/README.md).

## Objective

Specify how event-derived observations and external context become time-consistent research inputs. State what each feature can support, what it cannot reveal, and how unavailable or stale information affects its use. Any interpretation of participant intent remains an inference with a stated limitation.

## Documentation deliverables

- [This phase planning specification](README.md), defining feature and context research scope.
- A feature catalog with input dependencies, calculation definitions, units, windows, availability time, provenance, version, and missing-data behavior; future evidence: `../../evidence/P04/feature-catalog.md`.
- A context contract covering approved event/news/calendar inputs and their actual observation times, revisions, coverage, and fallback behavior; future evidence: `../../evidence/P04/context-contract.md`.
- A regime hypothesis and evaluation plan with labels, data partitions, leakage checks, and criteria selected before evaluation; future evidence: `../../evidence/P04/regime-evaluation-plan.md`.

## Traceability

**Requirements:** [REQ-001, REQ-002, REQ-003, REQ-004, REQ-005, REQ-008, REQ-009, REQ-011](../../requirements.md).

**Components:** [CMP-03 book/replay, CMP-05 context, CMP-06 features/regimes, CMP-07 Core research, CMP-11 audit and operations](../../traceability/components.md).

**Architecture:** [architecture index](../../architecture/README.md). **Gate:** G04 in the [milestone register](../../milestones.md).

## Ordered tasks

1. [ ] Enumerate proposed features and context inputs from the accepted architecture and record each research hypothesis.
2. [ ] Specify dependencies, availability times, units, computation windows, and observable-versus-inferred meaning.
3. [ ] Define missing, stale, revised, contradictory, and incomplete input behavior, including suppression or abstention.
4. [ ] Define regime labels and evaluation procedures without assuming that regime changes can always be identified in advance.
5. [ ] Select evaluation periods, partitions, leakage checks, and acceptance criteria; record approval before examining held-out results.
6. [ ] Attach later reproducibility, timing, and evaluation evidence, then seek G04 acceptance.

## G04 — Exit gate

Pass only when every accepted feature and context input has a complete dependency and availability-time definition; missing-data behavior is specified; and the approved timing, leakage, and reproducibility checks pass with linked evidence. Research hypotheses must be recorded as supported, rejected, or unresolved against preselected criteria. Accept only the evaluated scope; no predictive performance level is assumed by this plan.

**Evidence needed:** feature catalog, context contract, regime plan, approved evaluation criteria and partitions, timing and missing-data results, reproducible research outputs, and dated approval.

**Failure and rework:** remove or revise unsupported features, correct timing or provenance defects, and repeat the affected evaluation. Return to G01 for missing context sources or G03 for invalid market-state dependencies; update downstream component mappings.

**Exact next step:** after G03 acceptance, draft the feature catalog with each feature's source dependencies and earliest legitimate availability time.

**Implementation boundary:** this phase proposes research specifications. No predictive engine, signal service, or trading action is implemented here.
