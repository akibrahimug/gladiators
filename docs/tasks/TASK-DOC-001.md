# TASK-DOC-001 — Check the Claude handoff and repository readiness

| Field | Value |
| --- | --- |
| Work state / type | In progress / Documentation |
| Phase / gates | P00 preparation; contributes REQ-011/012 evidence without passing G00 |
| Components | Cross-project documentation; CMP-11 audit |
| Inputs | This workspace; user working agreement in [Claude workflow](../working-with-claude.md) |
| Dependencies | None for local inspection |
| Coordinator / workers | Claude Code main session, claimed 2026-10-22: coordinator and sole writer of this card, its board row and the report. `gladiator-spec-reader`: read-only source/gate/instruction inspection. `gladiator-reviewer`: read-only review of the report and this card |
| Repository / base / branch | akibrahimug/gladiators (default `master`); base `master` @ `cc357bccd1800348ba5e45b3fd362a3ceef40c13`; branch `task/TASK-DOC-001-handoff-inspection` |
| PR state / URL | Draft requested by the user on 2026-10-22 (one branch and PR per task); URL unset until created. Supersedes the earlier "Not requested" default, which assumed an uncommitted handoff baseline |

## Objective and scope

Verify that a new Claude Code session can follow the task and agent instructions, preserve captured sources and identify what is needed for the first PR. This is a documentation-preparation exception to the G00 dependency; it authorises no application implementation.

Allowed edits: this task card, its own summary row in `docs/tasks/README.md`, and a new `docs/validation/claude-handoff.md` report. Other documents are read-only for this task. Report instruction fixes as findings or separately scoped follow-up tasks. Read-only workers inspect the observed checkout and file hashes; the coordinator owns these limited writes.

## Required reading

[CLAUDE.md](../../CLAUDE.md), [workflow](../working-with-claude.md), [task board](README.md), [source register](../sources/README.md), [milestones](../milestones.md) and the three [agent definitions](../../CLAUDE.md).

## Steps and delegation

1. Give the spec-reader the source/gate/instruction inspection and concrete report criteria.
2. Inspect repository readiness in the current checkout; verify the existing remote/default branch, current baseline and publishing prerequisites. Record the observed destination rather than guessing one. Keep repository mutations outside this inspection task's allowed edits.
3. Verify task states, local Markdown targets and captured-source checksums; record methods and results in the handoff report.
4. Have the reviewer inspect the resulting report and this task's acceptance criteria; resolve factual errors.
5. Record local work state and PR state independently. Leave this inspection's PR state Not requested. Describe the exact inspected file set and readiness findings for the separate Draft publication candidate TASK-DOC-002; branch/commit/push/PR actions belong to that later scoped task.

## Acceptance criteria

- [ ] Report identifies whether Claude discovered the three named agents; unavailable runtime capability is recorded as a blocker rather than a pass.
- [ ] Report confirms original v1.0 remains missing, G00 pending and later code tasks unready.
- [ ] All local Markdown link targets resolve or failures are listed with paths.
- [ ] The three captured files match `docs/sources/captured/SHA256SUMS`; captured files remain unchanged.
- [ ] Repository/remote/base/auth prerequisites are recorded with observed values or precise missing inputs.
- [ ] Independent reviewer findings are recorded and material errors corrected.
- [ ] PR field correctly records local inspection only; report identifies the prerequisites for the separate initial-publication task.

## Verification methods

Use Claude's discovered agent list to check the three names. Resolve relative Markdown targets from their containing files. Compare source files to the recorded SHA-256 digests; on macOS, `shasum -a 256 -c SHA256SUMS` from the captured directory performs that check. Inspect Git state with `git rev-parse --show-toplevel`, `git status --short` and remote/base information only when a repository exists. Check authentication only against the user-selected hosting service.

Current observations and results: not run by Claude. Work remains Ready. The earlier Codex checks are in the [setup report](../validation/setup-report.md).
