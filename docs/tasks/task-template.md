# TASK template — replace with a unique TASK-ID and outcome

Template only. A task with unresolved mandatory fields remains Draft or Blocked.

| Field | Required value |
| --- | --- |
| Work state | Draft / Ready / In progress / Verified / Blocked |
| Type | Documentation / Research / Implementation / Validation |
| Phase / gate contribution | Pxx / Gxx; prerequisite gate record |
| Requirement / component IDs | Exact REQ and CMP IDs |
| Source baseline | Original source path/section/version/hash, accepted decision links |
| Dependencies | Task IDs and required outputs; external inputs |
| Coordinator / workers | Assigned owner and delegated roles |
| Repository / base branch / base SHA | Actual selected repository and committed revision |
| Task branch / worker worktrees | Actual names, paths and starting revisions |
| PR state / URL | Not requested / Blocked / Draft / Open / Merged / Closed; actual URL |
| Tested head revision / evidence | Actual commit and evidence links; unset until observed |

## Objective and observable result

Describe one bounded change and its expected behaviour or document output. Give an input/output example for implementation where useful.

## Scope and ownership

List exact allowed paths; reserved shared paths; source files that remain intact; interfaces this task may change; and excluded scope. A worker may edit only its assigned subset. Resolve missing file ownership before marking Ready.

## Required reading

Link the phase specification, exact source sections, accepted contracts/decisions and related acceptance scenarios. Label proposed material explicitly.

## Plan and delegation

List ordered subtasks with owner, inputs, outputs and dependency. Identify which can run independently and which wait for shared contracts. Include the exact worker return criteria.

## Acceptance criteria

- [ ] Concrete observable outcome for every scoped requirement.
- [ ] Required failure cases and boundary behaviour match the accepted contract.
- [ ] Evidence identifies the source baseline, configuration and actual tested revision.
- [ ] Task and affected traceability documents reflect the final change.

Replace these generic lines with task-specific criteria before Ready.

## Verification and independent review

| Criterion / check | Exact method or repository command | Observed result / evidence | Run revision |
| --- | --- | --- | --- |
| Replace with concrete checks | Resolve before Ready | Not run | Unset |

Use the repository's actual commands after discovery; document-only work may use explicit inspection methods. Record skipped checks and why. Add independent reviewer findings and their disposition; unresolved material findings keep the task short of Verified.

## Decision request or blocker

State the missing input or choice, affected IDs, options, recommendation, unaffected work that can continue and the exact condition that unblocks this task.

## PR and completion record

Use the project PR template. Record branch/base/head, actual URL, checks, review, remaining limitations and gate evidence contributed. Mark work Verified only after acceptance evidence and independent review are complete. Track PR publication and merge separately. Leave milestone decisions to the recorded gate reviewer.
