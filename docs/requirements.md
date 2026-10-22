# Requirements register

[Documentation index](README.md) · [Traceability matrix](traceability/requirements-matrix.md) · [Source register](sources/README.md)

**Status:** requirements extracted or proposed from the accessible brief and user messages. Original v1.0 requirement IDs and wording remain pending. These IDs are workspace references, not claimed original identifiers.

| ID | Requirement / planning constraint | Basis and state | Acceptance target |
| --- | --- | --- | --- |
| REQ-001 | Use observable market events, order flow and volume as primary research inputs; chart displays may support inspection | Current brief + SRC-002 order-flow message; user intent | Document input lineage and show decisions trace to events |
| REQ-002 | Describe what each source can and cannot reveal; do not assume visibility of every market-moving action or participant ledger | Proposed clarification of SRC-002; supported by EXT-001/EXT-002 source distinctions | G01 source coverage and blind-spot register |
| REQ-003 | Preserve source identity, usage constraints, version and provenance through capture and research | Proposed design needed for reproducibility | Source register and raw event provenance |
| REQ-004 | Distinguish event time, receive time and knowledge availability; support deterministic replay without future leakage | Proposed design supporting event-first research | Replay and causal-availability acceptance evidence |
| REQ-005 | Detect invalid, stale, duplicate, missing or out-of-order input; propagate uncertainty and explicit invalid state | Proposed reliability design from SRC-002 robustness intent | Recorded integrity/recovery failure cases |
| REQ-006 | Separate market-book state from the system's own cash, position and order ledger | Proposed interpretation of “ledger”; original meaning unresolved | Ledger definition and reconciliation evidence |
| REQ-007 | Research algorithms and resolve the roles of Core, Judges and Managers with cited evidence | SRC-002 uses these role names; boundaries proposed | Research records, alternatives and role contracts |
| REQ-008 | Investigate regime changes and market-moving context, tracking availability and relevance | SRC-002 context/market-change messages; detailed design proposed | Causal context/replay scenarios and coverage limits |
| REQ-009 | Specify deterministic risk limits, abstention and invalid-data behaviour independent of model confidence | Proposed reliability design; no limits selected | Risk scenarios and proposed control policy |
| REQ-010 | Evaluate hypotheses in simulation with explicit execution, fee, latency and uncertainty assumptions | Proposed validation requirement | Reproducible evaluation with held-out data and stated limitations |
| REQ-011 | Trace each research decision and gate to source data, configuration, versions and evidence | Current brief traceability + proposed technical extension | Requirement/component mappings and replayable audit lineage |
| REQ-012 | Preserve specs, organise phased documentation and IDE navigation; implement no live trading | Explicit current task constraint, SRC-001 | Documentation checks; no executable trading system or connections |

## Interpretations to resolve

The readable chat expresses an aspiration toward “near zero” error and access to all market-moving information. Neither is treated as an achieved property or testable guarantee. P00/P01 must translate robustness into bounded, measurable acceptance criteria and a documented residual-uncertainty model.

“Ledger” may mean exchange order events, an internal event journal, the system's own account accounting, or an accessible on-chain record. The proposal separates these meanings. Asset class, venue, licensed feeds, budget, technology stack, algorithm choices and numeric limits remain unselected.

## Change control

When originals are recovered, preserve their IDs. Add explicit aliases to these workspace IDs, record matching sections and conflicts, and update every affected phase, component and gate. Do not silently replace original requirements with this register.
