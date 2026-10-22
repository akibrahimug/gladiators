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
| PR state / URL | Draft under [DEC-009](../decisions/README.md) (user instruction, 2026-10-22: a branch and PR per task); URL recorded after creation. Replaces the earlier "Not requested" default |

## Objective and scope

Verify that a new Claude Code session can follow the task and agent instructions, preserve captured sources and identify what is needed for the first PR. This is a documentation-preparation exception to the G00 dependency; it authorises no application implementation.

Allowed edits: this task card, its own summary row in `docs/tasks/README.md`, and a new `docs/validation/claude-handoff.md` report. Other documents are read-only for this task. Report instruction fixes as findings or separately scoped follow-up tasks. Read-only workers inspect the observed checkout and file hashes; the coordinator owns these limited writes.

Scope amendment, 2026-10-22 ([DEC-009](../decisions/README.md)): the user asked Claude to create a branch and open a PR for each task. This task therefore also adds the DEC-009 row to `docs/decisions/README.md`. It commits its allowed files on its task branch, pushes, and opens a draft PR. It still makes no other repository change.

## Required reading

[CLAUDE.md](../../CLAUDE.md), [workflow](../working-with-claude.md), [task board](README.md), [source register](../sources/README.md), [milestones](../milestones.md) and the three agent definitions: [spec reader](../../.claude/agents/spec-reader.md), [implementer](../../.claude/agents/implementer.md) and [reviewer](../../.claude/agents/reviewer.md).

## Steps and delegation

1. Give the spec-reader the source/gate/instruction inspection and concrete report criteria.
2. Inspect repository readiness in the current checkout; verify the existing remote/default branch, current baseline and publishing prerequisites. Record the observed destination rather than guessing one. Limit repository mutations to this task's branch, commits, push and draft PR under DEC-009.
3. Verify task states, local Markdown targets and captured-source checksums; record methods and results in the handoff report.
4. Have the reviewer inspect the resulting report and this task's acceptance criteria; resolve factual errors.
5. Record local work state and PR state independently. Under DEC-009, open this task's draft PR and record its real URL and tested head. Describe the exact inspected file set and readiness findings for the separate candidate TASK-DOC-002, including which of its original publication scope remains.

## Acceptance criteria

- [ ] Report identifies whether Claude discovered the three named agents; unavailable runtime capability is recorded as a blocker rather than a pass.
- [ ] Report confirms original v1.0 remains missing, G00 pending and later code tasks unready.
- [ ] All local Markdown link targets resolve or failures are listed with paths.
- [ ] The three captured files match `docs/sources/captured/SHA256SUMS`; captured files remain unchanged.
- [ ] Repository/remote/base/auth prerequisites are recorded with observed values or precise missing inputs.
- [ ] Independent reviewer findings are recorded and material errors corrected.
- [ ] PR field records the DEC-009 draft PR with its real URL and tested head. The report identifies the prerequisites and remaining scope for TASK-DOC-002. (Amended under DEC-009; the original criterion was "PR field correctly records local inspection only".)

## Verification methods

Use Claude's discovered agent list to check the three names. Resolve relative Markdown targets from their containing files. Compare source files to the recorded SHA-256 digests; on macOS, `shasum -a 256 -c SHA256SUMS` from the captured directory performs that check. Inspect Git state with `git rev-parse --show-toplevel`, `git status --short` and remote/base information only when a repository exists. Check authentication only against the user-selected hosting service.

Current observations and results: run by Claude on 2026-10-22 against base `cc357bc`, with methods and evidence in the [handoff report](../validation/claude-handoff.md). Independent review is pending. The earlier Codex checks are in the [setup report](../validation/setup-report.md).
