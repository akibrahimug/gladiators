# TASK-P00-002a — Map v10 README and docs 01–14

| Field | Value |
| --- | --- |
| Work state | Verified |
| Type | Documentation |
| Phase / gate contribution | P00 / G00 reconciliation contribution; passes no gate |
| Requirement / component IDs | REQ-001 through REQ-012; CMP-01 through CMP-11 as provisional aliases |
| Source baseline | v10 release `docs/sources/originals/releases/gladiator-order-flow-ledger-v10 (1)/trading-ai-spec/` as primary ([DEC-011](../decisions/README.md)); per-file SHA-256 in the [inventory](../sources/originals/recovery-inventory.json); preservation verified by [TASK-P00-001](TASK-P00-001.md) |
| Dependencies | TASK-P00-001 Verified (PR #4) |
| Coordinator / workers | Claude Code main session (coordinator, sole writer). One read-only `gladiator-spec-reader` mapping worker for this section set; `gladiator-reviewer` for coverage review |
| Repository / base branch / base SHA | akibrahimug/gladiators; base `task/TASK-P00-001-preservation-review` @ `2f6b7c54a0a7dce79b303feb5060c593d32be19f` (stacked on PR #4) |
| Task branch / worker worktrees | `task/TASK-P00-002a-docs-mapping`; read-only workers need no worktree |
| PR state / URL | Merged — [#5](https://github.com/akibrahimug/gladiators/pull/5) into `master` at 2026-10-23T19:12:17Z (opened under DEC-009, [PR #1](https://github.com/akibrahimug/gladiators/pull/1)) |
| Tested head revision / evidence | `9d95f9c2839fb115f717890b87d74054acda817e`; the next commit records PR metadata only. Evidence: verification record below |

Part of [TASK-P00-002](TASK-P00-002.md), split by [DEC-012](../decisions/README.md).

## Objective and observable result

Map every `##`/`###` section of the assigned v10 files to workspace REQ/CMP/phase/gate IDs with an explicit relationship (Confirmed, Conflicting, Source-addition, Out-of-scope, Informational, Superseded-in-v10). Result: a mapping table with path:line and file SHA-256 for every section, a reverse check of every REQ and CMP, and concise decision requests for genuine conflicts.

Section set: `README.md` and `docs/01-product-charter.md` … `docs/14-core-engine-build-spec.md` (15 files, 116 sections).

## Scope and ownership

Allowed paths: `docs/evidence/P00/v1.0-reconciliation-a.md` (new); this card and the new TASK-P00-002b/002c cards (created under DEC-012); the TASK-P00-002 umbrella card; the TASK-P00-002/002a–c board rows; DEC-011 and DEC-012 rows in `docs/decisions/README.md`; one catalog row per new file. Preserved originals, archives, checksum files, the inventory and captured sources remain unchanged. Requirement, traceability and phase edits are integrated once, in TASK-P00-002c. Original IDs and terminology take precedence; CMP IDs stay provisional aliases.

## Plan and delegation

1. Spec-reader worker returns the mapping, reverse check and decision requests for this section set.
2. Coordinator checks row coverage against the actual heading list, spot-checks citations, writes the evidence file.
3. `gladiator-reviewer` independently compares coverage with the source files and checks the mappings.
4. Coordinator resolves material findings, records results, opens the draft PR and records its URL.

## Acceptance criteria

- [x] Every `##`/`###` heading in the section set (and each CSV or code file as a file-level row) has exactly one mapping row with path:line; a mechanical heading count matches.
- [x] Each row has a relationship from the vocabulary; Conflicting and Source-addition rows say what differs.
- [x] Every REQ-001..012 and CMP-01..11 has a reverse-check entry for this set.
- [x] Genuine conflicts and architecture choices are decision requests, not silent resolutions.
- [x] Independent reviewer findings are recorded and material ones resolved; preserved files unchanged; links resolve.
- [x] The draft PR's real URL and tested head are recorded here.

## Decision request or blocker

None blocking the mapping. Decisions raised by the mapping are recorded in the evidence file and the decision register; G00 stays Pending for the designated reviewer.

## Verification record — 2026-10-23

| Check | Revision | Result |
| --- | --- | --- |
| Heading coverage (coordinator index script) | `3030dca`, re-run after fixes | 116/116 headings, heading text exact; 2 declared H1 rows |
| Independent review (`gladiator-reviewer`) | `2f6b7c5..3030dca` | No blocker; 3 material, 9 minor findings; recorded in the [evidence file](../evidence/P00/v1.0-reconciliation-a.md#independent-review) |
| Fix verification (same reviewer) | `3030dca..d0996d3` | All material findings resolved; criteria 1–5 sufficient once recorded; residues and N1–N3 fixed next without another round |
| Links / preserved files | final commit | 0 broken links; no change under `docs/sources/` |
| PR #5 review feedback (user) | after `7124aa7` | Tag index REQ-012 row wrongly listed A-017 (index generated before the A-017 REQ fix). Regenerated: A-017 removed, count 28 → 27; no other row changed |

Tested head and PR URL are recorded in the PR field after the draft PR opens.
