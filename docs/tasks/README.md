# Claude task board

[Claude entry point](../../CLAUDE.md) · [Execution workflow](../working-with-claude.md) · [Task template](task-template.md) · [Phase specifications](../phases/README.md)

## Start here

Two bootstrap documentation tasks came first: **TASK-DOC-001**, the readiness inspection, and **TASK-DOC-002**, the post-baseline refresh. Original v1.0 releases were recovered on 2026-10-23 (TASK-P00-001) and reconciled (TASK-P00-002); the user decided DR-01–DR-12 on 2026-10-23 (TASK-P00-003). G00 now waits on its reviewer, the user, and still blocks all later implementation. Candidate rows below are a decomposition guide, not dispatchable task packets.

| Task packet | Work state | Prerequisite | PR state |
| --- | --- | --- | --- |
| [TASK-DOC-001 — Check handoff and repository readiness](TASK-DOC-001.md) | Verified | None; no accepted architecture required | Merged — [#1](https://github.com/akibrahimug/gladiators/pull/1) |
| [TASK-DOC-002 — Refresh handoff after the published baseline](TASK-DOC-002.md) | Verified | TASK-DOC-001 Verified | [#2](https://github.com/akibrahimug/gladiators/pull/2) merged into #1's branch after #1 had merged; carried to `master` by [#8](https://github.com/akibrahimug/gladiators/pull/8), merged |
| [TASK-P00-001 — Preserve originals](TASK-P00-001.md) | Verified | Originals recovered; preservation review complete | Import [#3](https://github.com/akibrahimug/gladiators/pull/3) and review [#4](https://github.com/akibrahimug/gladiators/pull/4) merged |
| [TASK-P00-002 — Reconcile plan](TASK-P00-002.md) | Verified (umbrella; G00 Pending) | TASK-P00-001 Verified | Not requested (one draft per packet) |
| [TASK-P00-002a — Map README and docs 01–14](TASK-P00-002a.md) | Verified | TASK-P00-001 Verified | Merged — [#5](https://github.com/akibrahimug/gladiators/pull/5) |
| [TASK-P00-002b — Map core-engine and components 00–13](TASK-P00-002b.md) | Verified | TASK-P00-002a (integrated as base) | [#6](https://github.com/akibrahimug/gladiators/pull/6) merged into packet a's branch after #5 had merged; carried to `master` by [#9](https://github.com/akibrahimug/gladiators/pull/9), merged |
| [TASK-P00-002c — Map components 14–27, lineage annex, integrate](TASK-P00-002c.md) | Verified | TASK-P00-002b (integrated as base) | [#7](https://github.com/akibrahimug/gladiators/pull/7) merged into packet b's branch after #6 had merged; carried to `master` by [#9](https://github.com/akibrahimug/gladiators/pull/9), merged |
| [TASK-P00-003 — Apply DR-01–DR-12 decisions and prepare G00](TASK-P00-003.md) | Verified | TASK-P00-002 Verified; user decisions recorded | Draft — [#11](https://github.com/akibrahimug/gladiators/pull/11) |

A card is the task's authoritative record. The coordinator updates this index when its state changes. Owner, branch, commit, evidence and actual PR URL are kept on the card.

**Bootstrap refresh — TASK-DOC-002:** the board first planned TASK-DOC-002 as the first publication of the inspected handoff. Two things changed that plan:

- the user had already pushed the initial Git documentation baseline to `master` at `cc357bc`;
- [DEC-009](../decisions/README.md) gives every task its own branch and PR, so TASK-DOC-001 opened its own draft PR.

[TASK-DOC-002](TASK-DOC-002.md) was materialised instead as a refresh of the handoff documents that predated that baseline. Neither task authorises application code.

## Readiness and state rules

- **Draft:** a proposed slice still lacks a complete packet or accepted decisions. Expand a candidate into the [template](task-template.md) before scheduling it.
- **Ready:** prerequisites are satisfied and scope, allowed files, source/contract references, acceptance criteria and verification method are concrete. Implementation additionally requires an accepted relevant baseline, the predecessor phase gate, a usable repository/base revision and an assigned implementation scope. The current planning handoff supplies no such implementation assignment.
- **In progress:** one coordinator has claimed the task and recorded worker/path ownership.
- **Verified:** all scoped acceptance results and independent review are complete, with evidence and revision identity. For local documentation inspection without Git, record file hashes and inspection date.
- **Blocked:** record the exact missing input/decision, affected work and unblock condition. Continue independent Ready work.

PR state is separate: **Not requested**, **Blocked**, **Draft**, **Open**, **Merged** or **Closed**. An opened PR needs a real URL; a Verified local task can still have a Blocked PR. Claude can complete a delivery handoff at draft-PR creation while human review/merge remains pending.

Phase gates retain their own [milestone states](../milestones.md). Task verification, PR opening and PR merge each contribute evidence; none automatically passes a gate.

## P00

Use the full [source-intake](TASK-P00-001.md) and [reconciliation](TASK-P00-002.md) packets. Source reading can be divided into independent sections; the coordinator owns original import, shared mappings and source-preservation records. G00 acceptance remains a separate reviewer decision after these outputs exist.

## P01

Candidates are Draft pending G00 and the accepted [P01 scope](../phases/01-research-and-data-access/README.md).

| Candidate ID | Bounded outcome | Type / dependency |
| --- | --- | --- |
| TASK-P01-001 | Selected-source registry and observability/access map for the chosen market scope | Research/documentation; G00 |
| TASK-P01-002 | Cited algorithm-research agenda, reference baselines and required observations | Research/documentation; scope from TASK-P01-001 |
| TASK-P01-003 | Workload, quality/latency/recovery objectives and source evaluation criteria | Documentation/validation; TASK-P01-001/002 outputs |

## P02

Candidates are Draft pending G01 and accepted [P02 contracts](../phases/02-event-capture/README.md).

| Candidate ID | Bounded outcome | Type / dependency |
| --- | --- | --- |
| TASK-P02-001 | Source-specific raw/normalized event contract and integrity fixtures | Documentation; G01 |
| TASK-P02-002 | Capture/raw-journal implementation for one selected source | Implementation; accepted TASK-P02-001 contract and explicit assignment |
| TASK-P02-003 | Capture provenance and integrity/recovery validation evidence | Validation; TASK-P02-002; VAL-002/004 capture stage |

## P03

Candidates are Draft pending G02 and accepted [P03 boundaries](../phases/03-market-state-and-ledger/README.md).

| Candidate ID | Bounded outcome | Type / dependency |
| --- | --- | --- |
| TASK-P03-001 | Book-state/replay contract, fixtures and invariants for selected feed semantics | Documentation; G02 |
| TASK-P03-002 | Separate simulated-account ledger contract, accounting convention and fixtures | Documentation; G02; independent of book editing after shared event IDs settle |
| TASK-P03-003 | One book/replay implementation slice with deterministic fixture results | Implementation/validation; accepted TASK-P03-001 contract; VAL-003/005 |
| TASK-P03-004 | One account-ledger implementation slice with fixture reconciliation | Implementation/validation; accepted TASK-P03-002 contract; VAL-006 ledger stage |

TASK-P03-003 and TASK-P03-004 may run concurrently only with disjoint files and accepted shared event contracts. Split either further when it would exceed a reviewable PR.

## P04

Candidates are Draft pending G03 and accepted [P04 definitions](../phases/04-features-and-context/README.md).

| Candidate ID | Bounded outcome | Type / dependency |
| --- | --- | --- |
| TASK-P04-001 | Versioned feature/context availability, revision and expiry contracts | Documentation; G03 |
| TASK-P04-002 | One selected causal feature or context adapter with fixtures | Implementation; accepted TASK-P04-001 slice |
| TASK-P04-003 | Knowledge-time, uncertainty and regime-shift evidence | Validation; TASK-P04-002; VAL-002 feature stage, VAL-007/008 |

## P05

Candidates are Draft pending G04 and accepted [P05 roles](../phases/05-core-judges-and-managers/README.md).

| Candidate ID | Bounded outcome | Type / dependency |
| --- | --- | --- |
| TASK-P05-001 | Cited algorithm alternatives, bounded baseline comparisons and role/decision contracts | Research/documentation; G04; VAL-009 bounded stage |
| TASK-P05-002 | One accepted Core/Judge research-decision slice and provenance | Implementation; accepted TASK-P05-001 contract |
| TASK-P05-003 | Deterministic Gatekeeper (CMP-12) policy slice with controlled ledger/simulator stubs | Implementation/validation; accepted policy; VAL-010/011 bounded stage |

Policy authority and values must be decided before TASK-P05-003 is Ready. Contract changes remain coordinator-owned.

## P06

Candidates are Draft pending G05 and accepted [P06 assumptions](../phases/06-simulation-and-validation/README.md).

| Candidate ID | Bounded outcome | Type / dependency |
| --- | --- | --- |
| TASK-P06-001 | Pre-registered evaluation, held-out dataset and execution/cost assumptions | Documentation; G05; criteria set before results |
| TASK-P06-002 | One simulator/execution-model integration slice | Implementation; accepted TASK-P06-001 assumptions |
| TASK-P06-003 | Reproducible held-out, sensitivity, risk and ledger evaluation evidence | Validation; TASK-P06-002; VAL-006/009/011 integrated stages, VAL-012/013 |

## P07

Candidates are Draft pending G06 and accepted [P07 paper-only scope](../phases/07-paper-readiness/README.md).

| Candidate ID | Bounded outcome | Type / dependency |
| --- | --- | --- |
| TASK-P07-001 | Paper-readiness plan and operations runbook with responsibilities | Documentation; G06 |
| TASK-P07-002 | One explicitly assigned paper-only monitoring or recovery slice | Implementation; accepted TASK-P07-001 scope |
| TASK-P07-003 | Paper-boundary, recovery/stop/incident rehearsal and handover evidence | Validation; required prior outputs; VAL-014 |

G07 concerns readiness. Starting a paper exercise retains the separate decision in P07. Live trading is outside this task board.

## Create a runnable packet

For each selected candidate, copy the template to its TASK-ID file, fill exact source sections/accepted decisions and permitted file paths, split scope until one coordinator can deliver a reviewable PR, add the card here, then set Ready only when the readiness rule holds. Discover verification commands from the actual codebase; the current documentation workspace contains no application test commands.

A worker result must identify its task, exact inputs/base, paths changed, acceptance evidence, checks and unresolved decisions. For implementation use the workflow's verified worktree and integration rules.
