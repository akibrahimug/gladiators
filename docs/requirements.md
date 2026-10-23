# Requirements register

[Documentation index](README.md) · [Traceability matrix](traceability/requirements-matrix.md) · [Source register](sources/README.md)

**Status:** requirements extracted or proposed from the accessible brief and user messages. Original v1.0 releases were recovered on 2026-10-23 and every v10 section is mapped ([reconciliation summary](evidence/P00/v1.0-reconciliation.md)); the user decided DR-01–DR-12 on 2026-10-23 (DEC-014–DEC-025), and the wording below applies them ([baseline record](evidence/P00/baseline-decision.md)). These IDs are workspace references, not claimed original identifiers.

| ID | Requirement / planning constraint | Basis and state | Acceptance target |
| --- | --- | --- | --- |
| REQ-001 | Use observable native market events, order flow and volume as primary research inputs where the project is entitled to them, with bars as baseline and fallback; inspection is by reports and CLI output, not a charting UI | Current brief + SRC-002 order-flow message; v10 file 27; DEC-015, DEC-023 | Document input lineage and show decisions trace to events |
| REQ-002 | Describe what each source can and cannot reveal; do not assume visibility of every market-moving action or participant ledger | Proposed clarification of SRC-002; supported by EXT-001/EXT-002 source distinctions | G01 source coverage and blind-spot register |
| REQ-003 | Preserve source identity, usage constraints, version and provenance through capture and research | Proposed design needed for reproducibility | Source register and raw event provenance |
| REQ-004 | Distinguish event time, receive time and knowledge availability; support deterministic replay without future leakage | Proposed design supporting event-first research | Replay and causal-availability acceptance evidence |
| REQ-005 | Detect invalid, stale, duplicate, missing or out-of-order input; propagate uncertainty and explicit invalid state | Proposed reliability design from SRC-002 robustness intent | Recorded integrity/recovery failure cases |
| REQ-006 | Separate market-book state from the system's own cash, position and order ledger. Name the other ledger meanings separately: per-challenger paper ledgers, the cost ledger, the immutable decision ledger and the event ledger (raw journal); public/on-chain observation is REQ-020 | Source B-153, A-013, A-097, FR-05; meanings decided by DEC-018 | Ledger definition and reconciliation evidence |
| REQ-007 | Research algorithms and specify the source roles (Core decision kernel, Gladiators, Arena, Judges, Management, Gatekeeper) with cited evidence | SRC-002 role names; v10 `00-SYSTEM-MAP.md`; role model decided by DEC-014, contracts proposed | Research records, alternatives and role contracts |
| REQ-008 | Investigate regime changes and market-moving context, tracking availability and relevance | SRC-002 context/market-change messages; detailed design proposed | Causal context/replay scenarios and coverage limits |
| REQ-009 | Specify deterministic risk limits, abstention and invalid-data behaviour independent of model confidence | Source Gatekeeper (CMP-12), deny by default; original provisional defaults recorded, not accepted (DEC-017) | Risk scenarios and proposed control policy |
| REQ-010 | Evaluate hypotheses in simulation with explicit execution, fee, latency and uncertainty assumptions | Proposed validation requirement | Reproducible evaluation with held-out data and stated limitations |
| REQ-011 | Trace each research decision and gate to source data, configuration, versions and evidence | Current brief traceability + proposed technical extension | Requirement/component mappings and replayable audit lineage |
| REQ-012 | Preserve specs, organise phased documentation and IDE navigation; implement no live trading | Explicit current task constraint, SRC-001 | Documentation checks; no executable trading system or connections |
| REQ-013 | Bound research LLM and RAG use: textual evidence only, with chunk provenance and availability-time filtering; never a price oracle; no authority to approve or size | Proposed (DEC-019); FR-03; A-034, A-085, B-010, B-019, B-143–B-147 | G04 retrieval causality; G05 role boundary |
| REQ-014 | Treat external, upstream and model-produced content as untrusted: it may propose, never change limits, approve intents or reach credentials | Proposed (DEC-019); A-020, A-077, A-078, B-109, C-035; reinstated L-026 | G05 policy and adversarial cases |
| REQ-015 | Enforce explicit spend budgets and alerts for data, compute and services | Proposed (DEC-019); FR-13; A-069, A-075, B-082, C-002; amounts provisional (DEC-017) | G01 budget; G07 operations |
| REQ-016 | Define the strategy lifecycle and promotion rules, with an immutable record of failed and retired candidates | Proposed (DEC-019); A-046, A-114, B-063, B-080 | G05 lifecycle contract; G06 promotion evidence |
| REQ-017 | Specify position sizing and exits deterministically: size by cash and loss budget, model-independent stops, no averaging down | Proposed (DEC-019); A-053, A-055, A-057–A-059, B-029, B-055 | G05 sizing/exit scenarios |
| REQ-018 | Provide an operator CLI surface for every documented action; no frontend | Proposed (DEC-019); A-117, B-065, B-084, C-008, C-057 | G07 operations; per-phase acceptance commands |
| REQ-019 | Track upstream dependency issues, pins and fork policy as untrusted evidence | Proposed (DEC-019); B-086, C-036, C-039; reinstated L-026 | G05 dependency review; G07 |
| REQ-020 | Observe public/on-chain ledger records as a source with stated coverage; never infer a universal money ledger | Proposed (DEC-018, DEC-019); A-013, C-105, C-108; owner CMP-05 with CMP-01 | G01 source coverage; G04 context |

## Interpretations to resolve

The readable chat expresses an aspiration toward “near zero” error and access to all market-moving information. Neither is treated as an achieved property or testable guarantee. P00/P01 must translate robustness into bounded, measurable acceptance criteria and a documented residual-uncertainty model.

“Ledger” may mean exchange order events, an internal event journal, the system's own account accounting, or an accessible on-chain record. The proposal separates these meanings; DEC-018 confirms the separation (REQ-006, REQ-020). Asset class, venue, licensed feeds, budget, technology stack, algorithm choices and numeric limits remain unselected; the source's provisional defaults are recorded, not accepted ([baseline record](evidence/P00/baseline-decision.md#initial-research-scope-for-p01), DEC-017).

## Change control

When originals are recovered, preserve their IDs. Add explicit aliases to these workspace IDs, record matching sections and conflicts, and update every affected phase, component and gate. Do not silently replace original requirements with this register.

## v1.0 source reconciliation — 2026-10-23

Source status of each requirement against the v10 baseline ([DEC-011](decisions/README.md)), from [TASK-P00-002](tasks/TASK-P00-002.md). "Conflicting" means the source and this register differed at mapping time. Every listed request was decided on 2026-10-23 (DR-01→DEC-014, DR-02→DEC-015, DR-04→DEC-017, DR-05→DEC-018, DR-08→DEC-021, DR-10→DEC-023), and the register above applies them.

| ID | Source status (v10) | Key source rows | Decision request |
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

Candidate requirements found only in the source, now added as REQ-013–REQ-020 with status Proposed (DEC-019): research LLM/RAG boundaries; untrusted-content security; cost and budget controls; strategy lifecycle and promotion; position sizing and exits; operator CLI surface; dependency intelligence; public/on-chain ledger observation. Row references are in the [summary](evidence/P00/v1.0-reconciliation.md).
