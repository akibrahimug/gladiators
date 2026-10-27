# P01 — Research and data access

Claude Code handoff: [P01 task packets and candidates](../../tasks/README.md#p01) · [delegation and PR workflow](../../working-with-claude.md). Dispatch Ready task cards rather than the whole phase checklist.

**Status: PROPOSED; in progress since 2026-10-24. G00 passed (DEC-027); P01 works from the [accepted baseline](../../evidence/P00/baseline-decision.md) under the documented research assumptions (DEC-017, DEC-028, DEC-029).**

**Dependencies:** accepted G00 and the documented baseline from [P00](../00-baseline/README.md).

## Objective

Determine which observations are available, what each observation represents, and what remains unobservable. Establish an access and provenance plan before selecting capture or analysis designs. Do not assume that public order-flow data exposes private institutional ledgers, hidden orders, or future money movements.

## Documentation deliverables

- [This phase planning specification](README.md), defining research and access decisions.
- A source registry covering the selected scope, access route, permitted use, update semantics, coverage, timestamps, known delays, limitations, and verification references; future evidence: `../../evidence/P01/source-registry.md`.
- An observability map distinguishing observed events, derived state, inference, unavailable data, and the system's own account records; future evidence: `../../evidence/P01/observability-map.md`.
- An approved data evaluation plan and access decision, including a representative sample plan and source-dependent acceptance criteria; future evidence: `../../evidence/P01/data-access-decision.md`.
- A cited algorithm-research agenda linking candidate algorithm families, reference baselines, required observations and falsifiable hypotheses to Gladiator research (CMP-13; the Core is the decision kernel, DEC-014); future evidence: `../../evidence/P01/research-agenda.md`.
- A workload and acceptance-objective register defining selected instrument/event scope, latency measurement points and percentiles, clock uncertainty, quality/recovery targets and evaluation methods before measurement; future evidence: `../../evidence/P01/acceptance-objectives.md`.

## Traceability

**Requirements:** [REQ-001, REQ-002, REQ-003, REQ-004, REQ-005, REQ-006, REQ-007; Proposed REQ-015, REQ-020](../../requirements.md).

**Components:** [CMP-01 source registry, CMP-02 ingest and raw log, CMP-03 book/replay, CMP-04 own-account ledger, CMP-05 context, CMP-13 Gladiators (research framing)](../../traceability/components.md).

**Baseline inputs (2026-10-23):** P01 evaluates the original provisional defaults in the [baseline record](../../evidence/P00/baseline-decision.md#initial-research-scope-for-p01): events first where entitled (DEC-015), the market universe, the daily-first horizon and the £0 phase-1 budget. None is accepted (DEC-017). Reinstated sections L-010, L-024 and L-025 apply to source and connector scope.

**Progress 2026-10-24:** [TASK-P01-001](../../tasks/TASK-P01-001.md) covers tasks 1–3 for market data and core context: the [source registry](../../evidence/P01/source-registry.md) and [observability map](../../evidence/P01/observability-map.md). [TASK-P01-004](../../tasks/TASK-P01-004.md) followed up items F-1 to F-5 ([record](../../evidence/P01/source-followups.md)). F-1 (licence-clear free daily ETF bars) is narrowed but not closed: Twelve Data and IEX HIST remain open. DEC-029 (crypto first) applies only if F-1 closes negatively. Kraken is the leading crypto candidate (not a selection) and remains Conditional. Coinbase appeared unusable for model research without its written consent (indirect evidence). The user decided the research is personal and non-commercial (DEC-030) and that Coinbase stays out of model research (DEC-031). [TASK-P01-002](../../tasks/TASK-P01-002.md) covers task 5 with the [research agenda](../../evidence/P01/research-agenda.md): baselines B0–B3 and BB, predictive hypotheses H-01 to H-06 and order-flow hypotheses H-OF1 to H-OF9, each with its null, the data it needs and the gate that evaluates it. [TASK-P01-003](../../tasks/TASK-P01-003.md) covers task 6 with the [acceptance-objective register](../../evidence/P01/acceptance-objectives.md). Its invariants are quoted from the sources, and its proposed values await the G01 reviewer before any measurement. [TASK-P01-005](../../tasks/TASK-P01-005.md) drafts tasks 4 and 7 in the [data-access decision](../../evidence/P01/data-access-decision.md), which is pending until Kraken confirms (DEC-032).

**Progress 2026-10-25:** [TASK-P01-006](../../tasks/TASK-P01-006.md) followed up the remaining public-documentation items ([round 2](../../evidence/P01/source-followups-2.md)). F-1 closed negatively for the routes examined, with all four remaining routes set aside with evidence, so DEC-029 is triggered: the daily-first baseline runs on crypto spot first, and ETFs stay in scope as a G01 dependency. Kraken publishes venue status publicly (Conditional on its terms), but no history of it was found, so historical venue-status coverage for archived bars is a new G01 dependency (F-7). F-4d and F-4h are narrowed; F-4f, F-4g and F-4i wait for the sample plan. Under DEC-033 the user chose not to wait for Kraken; [TASK-P01-007](../../tasks/TASK-P01-007.md) found no concrete restriction in Kraken's published terms for personal use, but ambiguity on scripts and retention, and evaluated Binance Vision, whose dataset terms permit personal non-production backtesting ([reassessment](../../evidence/P01/source-reassessment.md)). Binance Vision (now Conditional) is proposed to the G01 reviewer as the primary source for crypto research history. That proposal is subject to F-5b, F-5c, F-5d, F-7b and F-8, and to its terms' bar on live use of derived models. [TASK-P01-008](../../tasks/TASK-P01-008.md) then read Binance's general terms ([evidence](../../evidence/P01/binance-general-terms.md)): no UK restriction was found, but retention is ambiguous under the general terms, and whether the archive is a Binance Service, and which version governs a UK user, are unconfirmed (F-5b′). Binance also has no historical venue status (F-7b, narrowed).

**Progress 2026-10-26:** [TASK-P01-009](../../tasks/TASK-P01-009.md) drafted the [G01 gate record](../../evidence/P01/g01-gate-record.md), with a readiness note and decision requests GR-01 to GR-12. At that point no reviewer was designated and no decision was recorded. The same day, the user, as G01 reviewer (DEC-034), answered GR-01 to GR-12 (DEC-036 to DEC-046) and authorised downloads after the pass (DEC-035). [TASK-P01-010](../../tasks/TASK-P01-010.md) recorded the answers and drafted the [`source_approval` records](../../evidence/P01/source-approvals.md). G01 passes only when the reviewer confirms those records (DEC-046).

**Progress 2026-10-27:** [TASK-P01-011](../../tasks/TASK-P01-011.md) logged the independent Codex reviews of PRs #12 to #22 ([log](../../evidence/P01/codex-review-log.md)) and fixed their open findings. The PR #19 fix applies Binance dataset terms §1.2 to §1.5: F-5b′ narrows to F-5b″, and Binance retention is not restricted for DEC-030 use (previously ambiguous). G01 stays pending.

**Architecture:** [architecture index](../../architecture/README.md). **Gate:** G01 in the [milestone register](../../milestones.md).

## Ordered tasks

1. [ ] Confirm the research universe and required event types from the accepted P00 baseline.
2. [ ] Research candidate sources against current primary documentation and record source-specific evidence.
3. [ ] Classify every required observation as accessible, conditional, unavailable, or unresolved; document the consequence for the architecture.
4. [ ] Define sample selection, access requirements, provenance fields, retention constraints, and capture-quality criteria.
5. [ ] Frame cited algorithm alternatives, reference baselines and research hypotheses; record which source observations each needs and how P05/P06 will evaluate it.
6. [ ] Select and record workload, latency, quality and recovery objectives with definitions and evaluation methods; select thresholds before measurement.
7. [ ] Select the proposed source baseline and record approved criteria for evaluating it.
8. [ ] Review coverage gaps and alternatives, then record the G01 decision and P02 handoff.

## G01 — Exit gate

Pass only when every required event or context input in the selected scope maps to a source and access decision, or to a documented gap with an accepted scope adjustment. Every selected source must have evidence for its semantics and limitations. The research agenda must identify cited alternatives, reference baselines and data needs. The workload and quality/latency/recovery objectives must have recorded definitions, justified thresholds and evaluation methods. The reviewer must approve the source baseline, research agenda, evaluation criteria, and unresolved exceptions before P02 starts. No universal latency or coverage threshold is assumed.

**Evidence needed:** completed source registry, observability map, cited primary documentation, access feasibility evidence, sample plan, algorithm-research agenda, acceptance-objective register and dated approval. Access not yet demonstrated remains a dependency, never an assumed capability.

**Failure and rework:** revise the source choice or research scope; update affected requirements and components. Return to G00 if the needed scope change conflicts with the accepted v1.0 baseline.

**Exact next step:** after G00 acceptance, enumerate the required event and context types for the approved initial scope in the source registry.

**Implementation boundary:** research and design are future work; this document does not create connections, purchase data, or start capture or trading.
