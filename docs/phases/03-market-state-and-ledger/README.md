# P03 — Market state and ledger

Claude Code handoff: [P03 task packets and candidates](../../tasks/README.md#p03) · [delegation and PR workflow](../../working-with-claude.md). Dispatch Ready task cards rather than the whole phase checklist.

**Status: PROPOSED; not started.** Original v1.0 reconciliation is required before this phase can be accepted.

**Dependencies:** accepted G02 and the event contract from [P02](../02-event-capture/README.md).

## Objective

Specify reproducible market state from the observations actually available and keep the system's own account ledger separate. A reconstructed order book or trade history is a market-data view; it must not be described as access to the market's complete money ledger.

## Documentation deliverables

- [This phase planning specification](README.md), defining state and ledger boundaries.
- A market-state contract describing supported depth, state transitions, snapshot alignment, sequence recovery, invalid states, and replay checkpoints; future evidence: `../../evidence/P03/market-state-contract.md`.
- A separate own-account ledger contract for simulated or later paper balances, positions, orders, fills, fees, adjustments, and reconciliation; future evidence: `../../evidence/P03/own-account-ledger-contract.md`.
- State and ledger invariants with a validation matrix, including stale, incomplete, and unreconciled states; future evidence: `../../evidence/P03/state-and-ledger-validation.md`.

## Traceability

**Requirements:** [REQ-001, REQ-002, REQ-004, REQ-005, REQ-006, REQ-009, REQ-011](../../requirements.md).

**Components:** [CMP-02 ingest and raw log, CMP-03 book/replay, CMP-04 own-account ledger, CMP-07 Core and CMP-12 Gatekeeper as ledger consumers, CMP-11 audit and operations](../../traceability/components.md).

**Architecture:** [architecture index](../../architecture/README.md). **Gate:** G03 in the [milestone register](../../milestones.md).

## Ordered tasks

1. [ ] Describe the market-state transitions supported by each approved event type and the state that cannot be inferred.
2. [ ] Specify snapshot/delta alignment, checkpointing, recovery, stale-state signaling, and invalidation rules.
3. [ ] Define the separate own-account ledger and its units, identifiers, event lifecycle, and accounting invariants.
4. [ ] Specify reconciliation and discrepancy handling, including when derived outputs must be withheld.
5. [ ] Approve invariant checks, reconciliation tolerances where justified, and representative replay cases before measurement.
6. [ ] Review later implementation evidence for deterministic state reconstruction and ledger reconciliation, then seek G03 acceptance.

## G03 — Exit gate

Pass only when the market-state and own-account contracts remain explicitly separate; every transition and reconciliation invariant has an expected outcome; and approved replay and discrepancy cases satisfy the selected criteria. Identical approved inputs and configuration must produce identical agreed state outputs. Reviewer approval must reference actual evidence; documentation alone cannot pass G03. Any tolerance must have a recorded rationale and baseline approval.

**Evidence needed:** both contracts, invariant matrix, input and configuration identities, deterministic replay comparisons, reconciliation results, invalid-state handling results, and dated approval.

**Failure and rework:** mark affected state invalid or unreconciled, revise the relevant contract, and repeat its cases. Return to G02 for capture or ordering defects and reopen impacted downstream gates.

**Exact next step:** after G02 acceptance, draft the market-state contract from the approved event semantics and enumerate unavailable state explicitly.

**Implementation boundary:** state engines and account ledgers are not implemented by this documentation setup. Real accounts and live orders remain outside scope.
