# Component responsibility and dependency register

[Architecture](../architecture/README.md) · [Contracts](../architecture/contracts.md) · [Requirement matrix](requirements-matrix.md) · [Phases](../phases/README.md)

**Status:** proposed component labels and boundaries pending original v1.0 reconciliation. No component is implemented. Original identifiers must be retained as aliases after recovery.

| ID | Component and responsibility | Inputs / dependencies | Outputs / consumers | Owns phase / gate | Requirements |
| --- | --- | --- | --- | --- | --- |
| CMP-01 | Source registry: bounded coverage, feed/access semantics, provenance | Original baseline, primary feed documentation | Source descriptors → CMP-02, CMP-05; limitations → all research | P01 / G01 | REQ-002, REQ-003 |
| CMP-02 | Capture and raw log: preserve original events and normalized envelopes | CMP-01 selected sources and contract | Raw references, normalized events, integrity state → CMP-03, CMP-05, CMP-11 | P02 / G02 | REQ-001, REQ-003, REQ-004, REQ-005 |
| CMP-03 | Market book and replay: reconstruct supported venue state | CMP-02 events, snapshot/recovery rules | Versioned book/checkpoints/validity → CMP-06, CMP-10 | P03 / G03 | REQ-001, REQ-004, REQ-005 |
| CMP-04 | Own-account ledger: simulated journal, cash, positions, fees and reconciliation | CMP-10 simulated fills/adjustments; accepted accounting convention | Ledger version and reconciliation state → CMP-09, CMP-11 | P03 / G03; integration P06 / G06 | REQ-005, REQ-006, REQ-011 |
| CMP-05 | Context availability: source observations, first-known time and revisions | CMP-01 source scope, CMP-02 observations | Causal context with expiry/quality → CMP-06 | P01 discovery; P04 / G04 | REQ-002, REQ-003, REQ-004, REQ-008 |
| CMP-06 | Features and regimes: definitions, as-of windows, validity and uncertainty | CMP-03 book, CMP-05 context | Versioned causal features/regime state → CMP-07; evaluation → CMP-10 | P04 / G04 | REQ-001, REQ-004, REQ-005, REQ-008 |
| CMP-07 | Core research: evidence-backed algorithm hypotheses and candidates | CMP-06 inputs, CMP-01 coverage, documented algorithm research | Candidate/hypothesis with rationale → CMP-08; versioned research → CMP-11 | P01 research framing; P05 / G05 | REQ-007, REQ-008, REQ-010, REQ-011 |
| CMP-08 | Judges: assess evidence, unsupported scores and disagreement | CMP-07 candidate and lineage | Assessment or abstention → CMP-09 | P05 / G05 | REQ-007, REQ-009, REQ-011 |
| CMP-09 | Managers and risk: deterministic policy, limits and stop/abstain decisions | CMP-08 assessment, CMP-04 ledger, input validity, versioned policy | Simulation/paper disposition only → CMP-10; reasons → CMP-11 | P05 / G05; operations P07 / G07 | REQ-005, REQ-006, REQ-009, REQ-012 |
| CMP-10 | Simulation/paper: hypothetical fills, costs and evaluation with stated assumptions | CMP-09 disposition, CMP-03 replay, agreed execution model | Simulated fills → CMP-04; evaluation → CMP-07/08 and CMP-11 | P06 / G06; paper scope P07 / G07 | REQ-006, REQ-010, REQ-011, REQ-012 |
| CMP-11 | Audit and operations: versions, lineage, evidence, configuration and incidents | Every component and gate record | Reproducible run records, monitoring/recovery evidence and traceability | Cross-phase; consolidated P07 / G07 | REQ-003, REQ-004, REQ-005, REQ-011, REQ-012 |

## Handoff rules to specify

The [contract checklist](../architecture/contracts.md) records the fields and failure semantics for every major handoff. Before acceptance, each handoff needs a producer/consumer owner, contract revision, units/identity/time conventions, valid/invalid state transitions and linked acceptance scenarios.

CMP-04 and CMP-10 form a simulated accounting feedback relationship. P03 can specify and verify the ledger with fixtures; full simulator integration is assessed in P06. This does not imply a live broker or account connection.

CMP-11 is a cross-cutting responsibility rather than an extra decision-making authority. Core, Judges and Managers are names recovered from the user messages; their assigned responsibilities here are proposals that may change when the original architecture is recovered.
