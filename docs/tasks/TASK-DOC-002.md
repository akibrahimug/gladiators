# TASK-DOC-002 — Refresh handoff documents after the published baseline

| Field | Value |
| --- | --- |
| Work state | In progress |
| Type | Documentation |
| Phase / gate contribution | P00 preparation; contributes REQ-011/012 evidence without passing G00 |
| Requirement / component IDs | REQ-011, REQ-012; CMP-11 audit |
| Source baseline | No original v1.0 content is involved (SRC-003 missing). Inputs: [TASK-DOC-001 report](../validation/claude-handoff.md) findings F3 and F7–F13, and [DEC-009](../decisions/README.md) |
| Dependencies | [TASK-DOC-001](TASK-DOC-001.md) Verified; its report, card and DEC-009 row are this task's base |
| Coordinator / workers | Claude Code main session, claimed 2026-10-22: coordinator and sole writer of every allowed path below. `gladiator-reviewer`: read-only review |
| Repository / base branch / base SHA | akibrahimug/gladiators; base `task/TASK-DOC-001-handoff-inspection` @ `17f7d320d94fdf698aded1ba45a97ac23c82621f`. This branch is stacked on [PR #1](https://github.com/akibrahimug/gladiators/pull/1); retarget to `master` once that merges |
| Task branch / worker worktrees | `task/TASK-DOC-002-baseline-refresh`; single writer in the main checkout, so no worker worktrees |
| PR state / URL | Not yet opened; a draft PR is due under DEC-009. Becomes Draft with its real URL once created, or Blocked if creation fails |
| Tested head revision / evidence | Unset until observed |

## Objective and observable result

The board originally scoped TASK-DOC-002 as the first publication of the handoff. The user met that purpose before this packet was materialised, by committing and pushing the handoff to `master` at `cc357bc`. That commit is the initial Git documentation baseline, not G00's accepted baseline ([report](../validation/claude-handoff.md#repository-and-publishing-readiness)). The remaining work is a refresh: handoff documents still describe the repository as it was before that commit, and TASK-DOC-001 as local-only.

Result:

- No handoff document says the baseline is uncommitted, that publishing access is unverified, or that no Claude session has run.
- The workflow describes the TASK-DOC-001 → TASK-DOC-002 sequence as it actually happened under DEC-009.
- The TASK-DOC-001 report and this card are catalogued and indexed.

## Scope and ownership

Allowed paths, all written by the coordinator:

| Path | Allowed change | Findings |
| --- | --- | --- |
| `docs/working-with-claude.md` | Worker handoff: the snapshot-exception paragraph. Repository and PR readiness: the opening status paragraph and the TASK-DOC-001/TASK-DOC-002 paragraph. Claude Code format references: the runtime-verification sentence. First-session prompt | F3, F10, F13 |
| `README.md` | Edition line; the second Claude Code handoff paragraph; the trailing `# gladiators` line | F7, F8 |
| `docs/ide-guide.md` | The verification sentence in the handoff paragraph | F10 |
| `docs/tasks/README.md` | Start-here paragraph; a TASK-DOC-002 row; the TASK-DOC-002 candidate paragraph; the TASK-P00-001 row's PR reason | F9, F13 |
| `docs/tasks/TASK-P00-001.md`, `docs/tasks/TASK-P00-002.md` | The PR state field only | F9 |
| `docs/tasks/TASK-DOC-002.md` | This card | — |
| `docs/catalog.md`, `docs/README.md`, `docs/evidence/README.md` | Catalogue and index the TASK-DOC-001 report and this card | F12 |
| `CHANGELOG.md` | A new 0.3 entry | F11 |

Unchanged:

- `docs/sources/**` (captured and originals), `docs/milestones.md` and `docs/validation/setup-report.md`, which is a dated record.
- `CLAUDE.md`, `.claude/agents/**`, phase READMEs, requirements, traceability and architecture.
- The TASK-DOC-001 card, its report and the decision register.

Excluded scope:

- Application code and gate decisions.
- Any change to the P00 blockers beyond removing the stale publishing reason.
- Finding F14 (agent tool declarations), which awaits a user decision.

## Required reading

[TASK-DOC-001 report](../validation/claude-handoff.md), [DEC-009](../decisions/README.md), [Claude workflow](../working-with-claude.md), [task board](README.md) and [template](task-template.md).

## Plan and delegation

1. Coordinator: edit the allowed paths, keeping each change to the stale statement or index entry it corrects.
2. Coordinator: re-run the read-only link check, the captured-source checksums, the catalog-versus-tracked-files comparison and an allowed-path diff check.
3. `gladiator-reviewer`: review the diff against this card's criteria and return findings with file:line, per-criterion evidence and the checks it ran.
4. Coordinator: resolve material findings, record the review, push and open the draft PR, then record its URL and the Verified state.

## Acceptance criteria

- [ ] No allowed-path document still claims the baseline is uncommitted, publishing access is unverified, Claude has not run, or agent discovery is unverified. Each corrected statement is consistent with the TASK-DOC-001 report. (F3, F7, F9, F10)
- [ ] The workflow's TASK-DOC-001/TASK-DOC-002 paragraph, its first-session prompt and the board's TASK-DOC-002 text agree with DEC-009 and the actual task sequence. (F13)
- [ ] TASK-P00-001 and TASK-P00-002 remain Blocked, with the missing source as the only stated reason.
- [ ] CHANGELOG has a 0.3 entry; the 0.2 entry and the setup report are unchanged. (F11)
- [ ] The catalog lists exactly the tracked files, including the TASK-DOC-001 report and this card. The documentation and evidence indexes link the report. (F12)
- [ ] The README's stray second H1 is removed. (F8)
- [ ] All local Markdown links resolve; captured checksums match; the diff touches only allowed paths.
- [ ] Independent reviewer findings are recorded and material ones resolved.
- [ ] The draft PR's real URL and tested head are recorded on this card.

## Verification and independent review

| Criterion / check | Exact method | Observed result / evidence | Run revision |
| --- | --- | --- | --- |
| Stale statements removed | Search allowed paths for "uncommitted", "not yet verified", "remain to be verified", "still need verification", "launched no Claude", "local inspection only" | Not run | Unset |
| Links | Read-only link checker (method in the [TASK-DOC-001 report](../validation/claude-handoff.md#local-markdown-links)) | Not run | Unset |
| Checksums | `shasum -a 256 -c SHA256SUMS` in `docs/sources/captured/` | Not run | Unset |
| Catalog completeness | Compare `git ls-files` with catalog rows | Not run | Unset |
| Scope | `git diff --name-status 17f7d32..HEAD` against allowed paths | Not run | Unset |
| Independent review | `gladiator-reviewer` on `17f7d32..HEAD` | Not run | Unset |

## Decision request or blocker

None blocking. The README's trailing `# gladiators` line came from the repository's first commit (`21e82ce`). This task removes it as a stray second H1; the PR calls this out so the user can keep it.

## PR and completion record

Unset until the draft PR exists.
