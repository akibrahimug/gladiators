# TASK-P00-002c — Map v10 components 14–27, lineage annex and integrate the reconciliation

| Field | Value |
| --- | --- |
| Work state | Verified |
| Type | Documentation |
| Phase / gate contribution | P00 / G00 reconciliation contribution; passes no gate |
| Requirement / component IDs | REQ-001 through REQ-012; CMP-01 through CMP-11 as provisional aliases |
| Source baseline | v10 release `docs/sources/originals/releases/gladiator-order-flow-ledger-v10 (1)/trading-ai-spec/` as primary ([DEC-011](../decisions/README.md)); per-file SHA-256 in the [inventory](../sources/originals/recovery-inventory.json); preservation verified by [TASK-P00-001](TASK-P00-001.md) |
| Dependencies | TASK-P00-001 Verified (PR #4); TASK-P00-002b integrated as base |
| Coordinator / workers | Claude Code main session (coordinator, sole writer). One read-only `gladiator-spec-reader` mapping worker for this section set; `gladiator-reviewer` for coverage review |
| Repository / base branch / base SHA | akibrahimug/gladiators; base `task/TASK-P00-002b-core-mapping` @ `fcf1775f4cbc16794027fcf4ac1a281f13fd8ab5` (packet b final head, merged in `a60fda2`; originally branched from `d959bfd`) |
| Task branch / worker worktrees | `task/TASK-P00-002c-components-integration`; read-only workers need no worktree |
| PR state / URL | [#7](https://github.com/akibrahimug/gladiators/pull/7) was merged at 2026-10-23T19:12:47Z into its stacked base `task/TASK-P00-002b-core-mapping`, so its changes did not reach `master`. Follow-up [#9](https://github.com/akibrahimug/gladiators/pull/9) carried them (head 897f1cc included); merged into `master` at 2026-10-23T19:17:53Z |
| Tested head revision / evidence | `95a57eaa92f70d9b5398019a88b7b038c86f08a2`; the next commit records PR metadata only |

Part of [TASK-P00-002](TASK-P00-002.md), split by [DEC-012](../decisions/README.md).

## Objective and observable result

Map every `##`/`###` section of the assigned v10 files to workspace REQ/CMP/phase/gate IDs with an explicit relationship (Confirmed, Conflicting, Source-addition, Out-of-scope, Informational, Superseded-in-v10). Result: a mapping table with path:line and file SHA-256 for every section, a reverse check of every REQ and CMP, and concise decision requests for genuine conflicts.

Section set: `core-engine/components/14-COSTS-AND-OPERATIONS.md` … `27-ORDER-FLOW-AND-LEDGER-INTELLIGENCE.md` and the two CSV registers (14 files, 97 sections); lineage annex for content only in earlier releases (PF-05).

## Scope and ownership

Allowed paths: `docs/evidence/P00/v1.0-reconciliation-c.md` (new, with the lineage annex); integration edits allowed by the TASK-P00-002 umbrella card, plus a pointer paragraph in `docs/phases/README.md` (recorded at review, 2026-10-23) (`docs/requirements.md`, `docs/architecture/*.md`, `docs/traceability/*.md`, `docs/phases/*/README.md`, `docs/roadmap.md`, `docs/backlog.md`, `docs/decisions/README.md`, `docs/sources/source-map.md`, the task board and these cards); a draft G00 gate record under `docs/evidence/P00/` with decision Pending; milestone-register edits limited to linking evidence; catalog rows. Preserved originals, archives, checksum files, the inventory and captured sources remain unchanged. This packet integrates packets a–c into the shared planning documents. Original IDs and terminology take precedence; CMP IDs stay provisional aliases.

## Plan and delegation

1. Spec-reader worker returns the mapping, reverse check and decision requests for this section set.
2. Coordinator checks row coverage against the actual heading list, spot-checks citations, writes the evidence file, integrates all three packets into the planning documents and drafts the G00 gate record.
3. `gladiator-reviewer` independently compares coverage with the source files and checks the mappings.
4. Coordinator resolves material findings, records results, opens the draft PR and records its URL.

## Acceptance criteria

- [x] Every `##`/`###` heading in the section set (and each CSV or code file as a file-level row) has exactly one mapping row with path:line; a mechanical heading count matches.
- [x] Each row has a relationship from the vocabulary; Conflicting and Source-addition rows say what differs.
- [x] Every REQ-001..012 and CMP-01..11 has a reverse-check entry for this set.
- [x] Genuine conflicts and architecture choices are decision requests, not silent resolutions.
- [x] Lineage annex lists content absent from v10 with a proposed disposition; shared planning documents reflect packets a–c; a draft G00 record exists with decision Pending.
- [x] Independent reviewer findings are recorded and material ones resolved; preserved files unchanged; links resolve.
- [x] The draft PR's real URL and tested head are recorded here.

## Decision request or blocker

None blocking the mapping. Decisions raised by the mapping are recorded in the evidence file and the decision register; G00 stays Pending for the designated reviewer.

## Verification record — 2026-10-23

| Check | Revision | Result |
| --- | --- | --- |
| Heading coverage (coordinator index script) | final | 97/97 headings, text exact; 12 H1 rows; 2 CSV rows |
| Independent review (`gladiator-reviewer`) | `fcf1775..8ef75bc` | No blocker; 4 medium (lineage gaps, DR-01 divergence, backlog overclaim, no-CMP lists), 6 low, 4 nits; recorded in the [evidence file](../evidence/P00/v1.0-reconciliation-c.md#independent-review) |
| Fix verification (same reviewer) | `8ef75bc..d5d76e1` | All resolved; completeness re-run clean; N1, N2 fixed next without another round |
| Links / preserved files | final | 0 broken links; 415/415 checksums; no change under `docs/sources/` |
