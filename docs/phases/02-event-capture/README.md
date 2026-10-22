# P02 — Event capture

Claude Code handoff: [P02 task packets and candidates](../../tasks/README.md#p02) · [delegation and PR workflow](../../working-with-claude.md). Dispatch Ready task cards rather than the whole phase checklist.

**Status: PROPOSED; not started.** Original v1.0 reconciliation is required before this phase can be accepted.

**Dependencies:** accepted G01 and the source contracts from [P01](../01-research-and-data-access/README.md).

## Objective

Specify how source observations become a provenance-preserving event record that can be inspected and replayed. Preserve the distinction between source event time, receipt time, and processing time. Define behavior for missing, duplicate, late, reordered, or revised observations before any downstream component depends on them.

## Documentation deliverables

- [This phase planning specification](README.md), defining capture design and validation scope.
- A raw and normalized event contract with source identifiers, schema versions, timestamp meaning, sequence handling, and correction semantics; future evidence: `../../evidence/P02/event-contract.md`.
- A capture integrity and recovery design covering gaps, reconnects, duplicates, persistence, retention, and auditability; future evidence: `../../evidence/P02/capture-and-recovery.md`.
- A replay fixture and validation plan tied to the approved source baseline; future evidence: `../../evidence/P02/capture-validation-plan.md`.

## Traceability

**Requirements:** [REQ-001, REQ-003, REQ-004, REQ-005, REQ-011](../../requirements.md).

**Components:** [CMP-01 source registry, CMP-02 ingest and raw log, CMP-03 book/replay, CMP-11 audit and operations](../../traceability/components.md).

**Architecture:** [architecture index](../../architecture/README.md). **Gate:** G02 in the [milestone register](../../milestones.md).

## Ordered tasks

1. [ ] Map each approved source field and timestamp to its documented meaning and provenance.
2. [ ] Define raw preservation, normalized event schemas, versioning, and ordering rules without concealing source limitations.
3. [ ] Specify detection and disposition of gaps, duplicates, late events, disconnects, corrections, and invalid records.
4. [ ] Define replay inputs, outputs, deterministic ordering, fixture selection, and expected integrity checks.
5. [ ] Select quantitative capture criteria and recovery scenarios from source behavior; obtain approval before evaluating results.
6. [ ] Review the contract and validation plan; where later implementation is authorized, attach actual verification evidence before seeking G02 acceptance.

## G02 — Exit gate

Pass only when all selected event types have versioned contracts and provenance mappings; each identified integrity and recovery scenario has a specified expected result; and the agreed capture/replay criteria have approved, revision-specific evidence. Select thresholds and representative windows in the validation plan before measurement. If capture is not implemented and verified, G02 remains pending regardless of documentation completeness.

**Evidence needed:** event contract, recovery scenario matrix, approved criteria, representative fixture provenance, capture-quality and replay results from a later authorized implementation, and dated reviewer approval.

**Failure and rework:** quarantine or mark incomplete inputs, revise the capture design, and repeat affected validation. Return to G01 when the source cannot satisfy the approved contract; notify downstream phases of contract changes.

**Exact next step:** after G01 acceptance, draft the raw and normalized event contract for the approved source baseline.

**Implementation boundary:** connectors, storage, and replay code are future work. This setup does not start data capture or implement trading.
