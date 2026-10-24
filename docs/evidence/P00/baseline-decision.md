# P00 baseline decision record

[Task](../../tasks/TASK-P00-003.md) · [Decision register](../../decisions/README.md) · [Reconciliation summary](v1.0-reconciliation.md) · [Lineage annex](v1.0-reconciliation-c.md#lineage-annex) · [G00 gate record](g00-gate-record.md) · [P00 phase](../../phases/00-baseline/README.md)

This is the P00 deliverable planned as `baseline-decision.md`: the scope and terminology baseline that follows the user's decisions on DR-01–DR-12, which were recorded on 2026-10-23 as [DEC-014–DEC-025](../../decisions/README.md). **Accepted baseline since 2026-10-24:** the G00 reviewer passed G00 ([DEC-027](../../decisions/README.md), [gate record](g00-gate-record.md)). The provisional defaults below stay unaccepted until their gates.

## Source baseline

| Part | Content | Basis |
| --- | --- | --- |
| Primary | v10 release `docs/sources/originals/releases/gladiator-order-flow-ledger-v10 (1)/trading-ai-spec/`, every section as mapped in packets [a](v1.0-reconciliation-a.md), [b](v1.0-reconciliation-b.md) and [c](v1.0-reconciliation-c.md) | DEC-011 |
| Reinstated earlier-release sections | The 10 sections in the next table, cited in place from their release folders, plus the T19–T30 test-ID alias (L-034, alias only) | DEC-020 |
| Not in the baseline | Every other lineage-annex row (L-001–L-007, L-009, L-011–L-016, L-019, L-020, L-022, L-027, L-029–L-033, L-039, L-040). They stay preserved and can be proposed again by a later decision | DEC-020 |
| Precedence inside v10 | Component files refine `KERNEL.md`/`CORE.md` (an interpretation, not a statement in the source) | DEC-024 |
| Historical only | v5 `audit/spec_audit.py`: preserved and never executed | DEC-025 |
| Out of scope beyond P07 | Live-trading and capital content, kept as original text in a deferred annex: the OOS rows in packets a–c and FR-10 | DEC-021 |

Every row here points at a preserved file. No original text is copied, moved or edited.

### Reinstated sections

| Lineage row | Release folder | path:line | Section | Planning use |
| --- | --- | --- | --- | --- |
| L-008 | `gladiator-core-research-update-v4` | `core-engine/components/08-TRANSPORTERS.md:29` | v0.4 transport invariants | P02 event contract (REQ-003/004/005; CMP-02) |
| L-010 | `gladiator-core-research-update-v4` | `core-engine/components/10-DATA.md:41` | v0.4 data sourcing plan and audit gates | P01–P02 source and data scope (CMP-01/02) |
| L-017 | `gladiator-core-reviewed-v5` | `core-engine/components/01-CORE-KERNEL.md:31` | v0.5 decision invariants (22 October 2026) | P05 Core kernel contract (CMP-07) |
| L-018 | `gladiator-core-reviewed-v5` | `core-engine/components/02-ARENA.md:32` | v0.5 anti-overfitting tournament policy | P05–P06 Arena and evaluation (CMP-14, CMP-10) |
| L-021 | `gladiator-core-reviewed-v5` | `core-engine/components/05-GATEKEEPER.md:27` | v0.5 market-specific policy | P05 Gatekeeper policy (CMP-12) |
| L-023 | `gladiator-core-reviewed-v5` | `core-engine/components/08-TRANSPORTERS.md:27` | v0.5 transport correctness | P02 (CMP-02) |
| L-024 | `gladiator-core-reviewed-v5` | `core-engine/components/09-CONNECTORS.md:28` | v0.5 connector capabilities | P01–P02 (CMP-01/02) |
| L-025 | `gladiator-core-reviewed-v5` | `core-engine/components/10-DATA.md:39` | v0.5 ETF and crypto source-specific controls | P01–P02 (CMP-01/02) |
| L-026 | `gladiator-core-reviewed-v5` | `core-engine/components/11-QLIB-AND-TRAINING.md:27` | v0.5 dependency security and versioning | P05 (CMP-13); REQ-014, REQ-019 |
| L-028 | `gladiator-core-reviewed-v5` | `core-engine/components/13-EXECUTION-AND-LEDGER.md:27` | v0.5 execution accounting invariants | P03, P06 (CMP-04, CMP-10) |
| L-034 (alias only) | `gladiator-market-awareness-v9` | `core-engine/components/23-CORE-ASSURANCE-AND-PEER-REVIEW.md:45` | Market-awareness adversarial extension (v0.9 amendment) | Test IDs T19–T30, kept as aliases of the v10 `24-MARKET-AWARENESS-AND-REGIME-DETECTION.md:189` acceptance cases (P04, P06) |

The section text of L-034 is not reinstated; only its test IDs are kept, as aliases. The coordinator checked each heading at the cited line on 2026-10-23. The four v10 rows that refer to dropped content resolve as follows. L-037 is resolved by L-017, L-018, L-021, L-025 and L-028, and L-038 by L-026. L-035 and L-036 remain stale v10 claims: the v0.4 amendments are mostly not reinstated, and `audit/spec_audit.py` is historical only (DEC-025).

## Terminology

| Term | Baseline meaning | Workspace ID | Decision |
| --- | --- | --- | --- |
| Core | The deterministic decision kernel. It observes, reconciles, evaluates, sizes and issues intents. It is not the arena, an LLM or the broker (v10 `00-SYSTEM-MAP.md:6`, `:15`) | CMP-07 | DEC-014 |
| Gladiators | Research candidates that produce versioned, calibrated forecasts | CMP-13 | DEC-014 |
| Arena | Fair tournament comparison of gladiators | CMP-14 | DEC-014 |
| Judges | Evaluate evidence and set promotion outcomes | CMP-08 | DEC-014 |
| Management | Schedules, budgets and promotes; governance, not risk approval | CMP-09 | DEC-014 |
| Gatekeeper | The only approver of intents; deterministic risk policy, deny by default | CMP-12 | DEC-014 |
| Market Intelligence | v10 component 24, an observation and fusion layer that feeds both Core and the Gatekeeper (`00-SYSTEM-MAP.md:34`) | Alias over CMP-05 and CMP-06 | DEC-014 |
| Own-account ledger | The system's simulated cash, position, order and fee journal | REQ-006, CMP-04 | DEC-018 |
| Other "ledger" meanings | Per-challenger paper ledgers, the cost ledger, the immutable decision ledger and the event ledger are named separately in REQ-006; public/on-chain ledger observation is REQ-020 | REQ-006, REQ-020 | DEC-018 |
| Phase and gate IDs | Workspace P00–P07 and G00–G07. Source labels (Phase 0–9, Stages A–I, P0–P8, G0–G6) are cited file-qualified through the [crosswalk](v1.0-reconciliation.md#source-identifier-crosswalk) | — | DEC-016 |

The source components that still have no CMP (Code of Conduct, dependency intelligence, market state machine, OnChainEvent and the CLI surface) are covered by the alias table and by the Proposed requirements REQ-013–REQ-020. No new CMP is created for them.

## Initial research scope for P01

These are the inputs P01 must evaluate. **None of them is a selection.** Each is an original provisional default and is not accepted (DEC-017). P01 confirms or replaces each one with evidence at G01, or at G05 for the risk values.

| Item | Original provisional default | Source inconsistency to resolve | Decide at |
| --- | --- | --- | --- |
| Primary input | Native market events first where the project is entitled to them; bars as baseline and fallback (DEC-015) | Docs 01–14 and components 00–13 are bar-based; file 27 puts events first | G01 entitlement evidence |
| Market universe | US ETFs plus crypto spot (README:9, 27:3) | docs/03:4 US equities and ETFs; docs/13:4 and docs/12:37 US equities | G01 |
| Horizon | Daily bars first (17:33) | 20:21 and CORE:8 "15-minute/1-hour" | G01 |
| Budget | £0 paid services in phase 1 (14:6, 17:11; KERNEL:60; KERNEL:6 cited earlier in error, corrected 2026-10-24 by TASK-P01-001) | CORE:71 £20/month | G01 |
| Risk defaults | GBP 500 simulated equity; risk per trade ≤1% with a 0.5% research default; 1 position and ≤2 entries per session for eventual live operation (05:9, ACCEPTANCE:11); long-only cash (CORE:56, KERNEL:30, 05:8) | 0.5–1% vs ≤1%; £2.50–£5 planned loss (18:18) | G05 |
| Stack | Python CLI with conditional Qlib use (17:6, 19:20–27) | — | An implementation phase (DEC-022) |

## Ownership and review

| Item | Value | Basis |
| --- | --- | --- |
| Decision owner for architecture and source choices | The user (repository owner) | DEC-008, DEC-014–DEC-025 |
| G00 reviewer | The user | DEC-026 |
| Gate evidence format | [Gate-record template](../gate-record-template.md), one record per gate under `docs/evidence/Pxx/` | P00 task 5 |
| Review criteria | The [milestone register](../../milestones.md) row and the phase exit gate, applied as written; a PR or merge passes no gate | CLAUDE.md, milestones closure rule |

## Remaining limitations

- PF-01: the archives were not compared with the browser downloads. PF-02 and PF-04: the v1.0 conversation evidence and message IDs are not preserved. The reviewer weighs these at G00.
- Lineage completeness is checked at heading level only.
- Mapping relationships are interpretations against workspace IDs.
