# Requirements register

[Documentation index](README.md) · [Traceability matrix](traceability/requirements-matrix.md) · [Source register](sources/README.md)

**Status:** requirements extracted or proposed from the accessible brief and user messages. Original v1.0 releases were recovered on 2026-10-23 and every v10 section is mapped ([reconciliation summary](evidence/P00/v1.0-reconciliation.md)); requirement wording below is unchanged until decisions DR-01–DR-12 are made. These IDs are workspace references, not claimed original identifiers.

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

## v1.0 source reconciliation — 2026-10-23

Source status of each requirement against the v10 baseline ([DEC-011](decisions/README.md)), from [TASK-P00-002](tasks/TASK-P00-002.md). "Conflicting" means the source and this register differ; nothing here changes a requirement until the linked decision is made.

| ID | Source status (v10) | Key source rows | Open decision |
| --- | --- | --- | --- |
| REQ-001 | Conflicting within the source: docs 01–14 and components 00–13 are bar-based; file 27 (v1.0 header) puts native market events first | A-026, B-130, C-104, C-108 | DR-02, DR-10 |
| REQ-002 | Confirmed | B-110, C-077, C-093 | — |
| REQ-003 | Confirmed | A-027, B-128, C-081 | — |
| REQ-004 | Confirmed | A-027, B-113, C-109 | — |
| REQ-005 | Confirmed | B-094, C-083, C-109 | — |
| REQ-006 | Own-account ledger confirmed; source also uses "ledger" for public/on-chain records | B-153, C-105 | DR-05 |
| REQ-007 | Conflicting role model (Core kernel, Gladiators, Arena, Judges, Management, Gatekeeper) | B-025, B-042, C-110 | DR-01 |
| REQ-008 | Confirmed | B-051, C-076 | — |
| REQ-009 | Confirmed; the source sets provisional numeric defaults | A-054, B-091 | DR-04 |
| REQ-010 | Confirmed | A-030, B-151, C-066 | — |
| REQ-011 | Confirmed | A-098, B-050, C-006 | — |
| REQ-012 | Confirmed as current boundary; the source designs an eventual live path, off by default | B-003, C-074 | DR-08 |

Candidate requirements found only in the source (Proposed, pending DR-06 and DR-01): research LLM/RAG boundaries; untrusted-content security; cost and budget controls; strategy lifecycle and promotion; position sizing and exits; operator CLI surface; dependency intelligence; public/on-chain ledger observation. Row references are in the [summary](evidence/P00/v1.0-reconciliation.md).
