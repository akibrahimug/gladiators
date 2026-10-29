# P02 — Event capture

Claude Code handoff: [P02 task packets and candidates](../../tasks/README.md#p02) · [delegation and PR workflow](../../working-with-claude.md). Dispatch Ready task cards rather than the whole phase checklist.

**Status: PROPOSED; in progress since 2026-10-28.** G01 passed on 2026-10-27 (DEC-047). Tasks 1 to 4 are drafted in the [event contract](../../evidence/P02/event-contract.md) (TASK-P02-001). The inputs are the G01 conditions: the [`source_approval` records](../../evidence/P01/source-approvals.md) as amended (DEC-048 to DEC-051); the P02 dependencies F-4d, F-4f, F-4g, F-4h, F-4i and F-5c (DEC-045), plus F-4j, F-5e, CPI timing and historical FOMC and COT dates (sample results); and the three VAL gaps as test obligations (DEC-042).

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

**Reinstated sources (DEC-020):** L-008 and L-023 (transport invariants and correctness), L-010, L-024 and L-025 (data and connectors) apply to this phase; see the [baseline record](../../evidence/P00/baseline-decision.md#reinstated-sections).

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

**Progress 2026-10-28:** [TASK-P02-001](../../tasks/TASK-P02-001.md) drafted the [event contract](../../evidence/P02/event-contract.md), covering tasks 1 to 4. It applies the user's decisions DEC-052 to DEC-055 and proposes resolutions for the reviewer. It adds F-4j, F-5e and CPI timing to the P02 inputs.

[TASK-P02-004](../../tasks/TASK-P02-004.md) drafted task 5: the [capture and recovery design](../../evidence/P02/capture-and-recovery.md) and the [capture validation plan](../../evidence/P02/capture-validation-plan.md). Its new thresholds (TH-1 to TH-6) and the F-4h closure route await the reviewer.

On 2026-10-28 the user approved the thresholds (DEC-056), authorised the retrievals (DEC-057) and assigned the implementation on held files (DEC-058). [TASK-P02-002](../../tasks/TASK-P02-002.md) built it and ran the plan on held files ([results](../../evidence/P02/capture-validation-results.md)). All 19 runnable fixtures and all 7 recovery scenarios pass. One archive/REST difference was found (F-4h).

[TASK-P02-005](../../tasks/TASK-P02-005.md) built the network side and ran the authorised calls ([results](../../evidence/P02/network-capture.md)): 18 HEAD requests, one daily REST test, and a 1-hour live capture. In the live capture, Q-5, R-1 to R-5 passed, T-5 was flagged (the clock is 34–258 ms off), and T-6 was not triggered.

On the same day, the 7-day live window started at 10:35 UTC (DEC-064). [TASK-P02-006](../../tasks/TASK-P02-006.md) added RC-05 to RC-08 ([results](../../evidence/P02/recovery-results.md)), so CV-11 now passes.

On 2026-10-29 the coordinator installed the 30-day job (DEC-068; first pull 10:16 UTC, last pull 2026-11-27), and the user accepted the pre-first-sample clock rule (DEC-067) ([TASK-P02-007](../../tasks/TASK-P02-007.md)).

On 2026-10-29 [TASK-P02-008](../../tasks/TASK-P02-008.md) fixed five Codex review findings ([review fixes](../../evidence/P02/review-fixes.md)) and recorded DEC-069 (Binance `available_at` = `Last-Modified` + 6 h, flagged).

**Exact next step:** the 7-day window ends about 2026-11-04 10:35 UTC. Its results then go to the user for the G02 review. The 30-day pull runs until 2026-11-27.

**Implementation boundary:** capture code for held files exists (`src/gladiator_capture/`, DEC-058). Network transports, live capture and the DEC-057 retrievals are later tasks. Trading is out of scope.
