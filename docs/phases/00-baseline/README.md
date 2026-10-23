# P00 — Baseline and source reconciliation

Claude Code handoff: [P00 task packets and candidates](../../tasks/README.md#p00) · [delegation and PR workflow](../../working-with-claude.md). Dispatch Ready task cards rather than the whole phase checklist.

**Status: PROPOSED; documentation preparation in progress. G00 is pending reconciliation/review of the recovered v1.0 specifications.**

**Dependencies:** none. This phase establishes the prerequisite for every later phase.

## Objective

Establish which documents are authoritative, preserve their original contents, and reconcile this proposed plan with the user's latest v1.0 order-flow/ledger architecture. Do not reconstruct missing architecture text from assistant placeholders or inferred terminology.

## Documentation deliverables

- [This phase planning specification](README.md), covering baseline capture and acceptance.
- A source inventory and unchanged copies of the original specifications, with provenance, retrieval date, version, and checksum where applicable; future evidence: `../../evidence/P00/source-inventory.md`.
- A section-by-section reconciliation describing retained, superseded, conflicting, and missing requirements; future evidence: `../../evidence/P00/v1.0-reconciliation.md`.
- An accepted scope and terminology baseline, linked to the [requirements register](../../requirements.md), [architecture index](../../architecture/README.md), and [component map](../../traceability/components.md); future evidence: `../../evidence/P00/baseline-decision.md`.

## Traceability

**Requirements:** [REQ-003, REQ-011, REQ-012](../../requirements.md), plus the baseline for all other requirements.

**Components:** [CMP-01 through CMP-11](../../traceability/components.md); no component definition is accepted until reconciled.

**Gate:** G00 in the [milestone register](../../milestones.md).

## Ordered tasks

1. [x] Retrieve the complete original v1.0 specifications and relevant attachments; record any unavailable items explicitly.
2. [x] Inventory and preserve the source documents without editing their contents; give each source a stable identity.
3. [x] Compare each proposed requirement and component with an exact source location, or mark it as a proposal with no source match.
4. [ ] Resolve architectural vocabulary, boundaries, conflicts, and intended revision precedence with the baseline reviewer.
5. [ ] Select and document the initial research scope, decision owner, gate evidence format, and review criteria.
6. [ ] Update the plan and traceability to match the accepted baseline, then record the G00 decision.

Progress 2026-10-23: tasks 1–2 by [TASK-P00-001](../../tasks/TASK-P00-001.md) ([preservation review](../../evidence/P00/preservation-review.md)); task 3 by [TASK-P00-002](../../tasks/TASK-P00-002.md) ([reconciliation summary](../../evidence/P00/v1.0-reconciliation.md)). Tasks 4–6 need the user decisions DR-01–DR-12 and the G00 reviewer; the [draft G00 record](../../evidence/P00/g00-gate-record.md) is Pending.

## G00 — Exit gate

Pass only when every supplied source is inventoried and preserved; every requirement and component is linked to a source location or an explicitly accepted proposal; and all baseline conflicts have a recorded disposition. Missing original v1.0 specifications keep G00 pending. The baseline reviewer must record approval of scope, provenance, and the reconciliation before P01 starts.

**Evidence needed:** source inventory, preservation evidence, reconciliation, exception dispositions, and a dated approval linked from the milestone register. File existence alone is insufficient.

**Failure and rework:** preserve unresolved sources and questions, keep G00 pending, and revise only the proposed documents. Re-run the mapping when additional originals arrive; do not silently overwrite or replace the source baseline.

**Exact next step:** obtain the original v1.0 Markdown specifications and attachments, then create the source inventory with their actual identities and provenance.

**Implementation boundary:** this phase organizes and reconciles documents. It does not authorize implementation or live trading.
