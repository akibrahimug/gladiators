# Decision register

[Documentation index](../README.md) · [Backlog](../backlog.md) · [Sources](../sources/README.md)

No original architecture decision records were recovered. The entries below describe current task constraints or proposals only.

| ID | Decision / question | State | Basis | Impact and review |
| --- | --- | --- | --- | --- |
| DEC-001 | Create documentation only; no live trading implementation or connection | Confirmed task constraint | SRC-001 | Applies to every phase; any future live scope requires a separate request |
| DEC-002 | Preserve source files intact; map them through new navigation documents | Confirmed task constraint | SRC-001 | Originals retained with identity/version/checksum and explicit supersession |
| DEC-003 | Use P00–P07 and G00–G07 as the proposed planning sequence | Proposed | This workspace organisation | Reconcile at G00; retain aliases if original numbering differs |
| DEC-004 | Separate market events/book state from internal account ledger | Proposed | SRC-002 “ledger” ambiguity; EXT-001/EXT-002 | Resolve terminology at G00; contracts at G03 |
| DEC-005 | Make data validity, causal replay and deterministic risk explicit requirements | Proposed | Robustness intent in SRC-002 | Resolve acceptance criteria G01; evidence G02–G06 |
| DEC-006 | Do not select venue, stack, models or numerical targets without original specs and research | Pending baseline decisions | Original v1.0 unavailable | Record choices and alternatives in P00/P01 rather than guessing |
| DEC-007 | End this roadmap at paper readiness | Confirmed current scope boundary; future roadmap proposal | SRC-001 no live trading yet | G07 cannot authorise capital deployment |
| DEC-008 | Use Codex for brainstorming/design and Claude Code for implementation, wiring and PRs | Confirmed user preference, 2026-10-22 | User's follow-up instruction; [working agreement](../working-with-claude.md) | Claude follows bounded task packets and brings unresolved architecture decisions back to the user |
| DEC-011 | Reconciliation baseline: map the v10 release (`gladiator-order-flow-ledger-v10 (1)`) section by section as primary; list content present only in earlier releases in a lineage annex with proposed dispositions, without line-by-line mapping | Confirmed user decision, 2026-10-23 | User's answer to the TASK-P00-002 baseline question, choosing "v10 primary + lineage annex" over a cumulative baseline or mapping all 10 releases; context: [PF-05](../evidence/P00/preservation-review.md#findings-and-dispositions) | Bounds TASK-P00-002 to 349 v10 sections + 2 CSV registers; precedence for dropped earlier content stays a later decision. Does not accept G00. (DEC-009 and DEC-010 are recorded in [PR #1](https://github.com/akibrahimug/gladiators/pull/1), not yet merged into this branch's base.) |
| DEC-012 | Deliver TASK-P00-002 as three packets with one draft PR each: a (README + docs 01–14), b (core-engine + components 00–13), c (components 14–27 + CSVs + lineage annex + integration into shared planning documents) | Confirmed user decision, 2026-10-23 | User's answer to the TASK-P00-002 delivery question | Shared requirement/traceability/phase edits happen once, in packet c. Packets are stacked on PR #4 |

## Record format for a future accepted decision

Copy into a new Markdown document when there is a concrete decision: stable ID/title; status/date; source and requirement links; problem/context; options and evidence; chosen option; consequences; affected components/phases/contracts; validation evidence; owner/reviewer; supersedes/superseded-by.

An accepted change must update the traceability matrix and identify whether previous gate evidence remains applicable. A proposed entry does not imply user approval.
