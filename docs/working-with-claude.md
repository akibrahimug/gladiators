# Working with Claude Code

[Project home](../README.md) · [Claude entry point](../CLAUDE.md) · [Task board](tasks/README.md)

## Working agreement

The user and Codex develop ideas, question assumptions and document design decisions. Claude Code handles implementation, integration, meaningful verification and PR preparation for assigned work. This handoff records the user's preference on 2026-10-22.

Claude can choose routine implementation details within the accepted task. For an unresolved architecture choice, source conflict, changed contract, threshold or wider scope, return a short decision request: problem; source/REQ/CMP/P/G IDs; viable options and tradeoffs; recommendation; effect of waiting. Record the result in the [decision register](decisions/README.md) and update the task before dependent work continues. Continue independent work that does not depend on that choice.

## Execution sequence

1. **Establish readiness.** Read the assigned task card and its linked source/phase/contracts. Check dependencies and gate records. Ready requires resolved scope, allowed files, acceptance criteria and a verification method. A phase checklist or a candidate row is insufficient to dispatch.
2. **Claim the task.** The main Claude session is coordinator. Record owner, branch, exact base commit, worker assignments and file ownership in the task card. Shared contracts, task-board state, milestone records and traceability edits belong to the coordinator.
3. **Delegate bounded work.** Use the [spec reader](../.claude/agents/spec-reader.md) for source and dependency checks, the [implementer](../.claude/agents/implementer.md) for a Ready implementation slice, and the [reviewer](../.claude/agents/reviewer.md) for an independent review. Give each worker the explicit handoff described below.
4. **Integrate.** Inspect each worker's diff and evidence. Apply accepted changes to the task branch, resolve overlaps and update related task/source/requirement/component links. Re-run checks affected by integration against the combined revision.
5. **Verify and review.** Record observed acceptance results, actual checks and limitations. Give an independent reviewer the task card, base/head revision and changed files. Resolve material findings and repeat affected checks. A reviewer with no findings does not substitute for acceptance evidence.
6. **Open the PR.** When repository access is available, push the task branch and create a draft PR using the [PR template](../.github/pull_request_template.md). Use the actual base branch. Record the URL and tested head commit in the task card. Keep unfinished acceptance work visible in the draft.
7. **Handoff.** Report what changed, checks and findings, unresolved decisions, task state, PR state/URL and gate impact. PR publication failure leaves a precise blocker and a prepared description; it is never reported as an opened PR.

## Worker handoff and isolation

Every assignment includes task ID/card; objective; source and accepted decision links; REQ/CMP/P/G IDs; allowed paths and reserved shared files; inputs from other workers; expected outputs/checks; and stop conditions. Implementation writers also require the exact committed base SHA. Workers receive the task context explicitly rather than relying on the coordinator's chat history.

A read-only inspection that must run before its instructions are committed may use the observed checkout path, file manifest/hashes and inspection date instead of a base SHA. The coordinator alone writes the permitted report and task metadata, and the reviewer assesses those concrete file snapshots against the task criteria. This exception does not authorise concurrent writers or implementation on an uncommitted baseline. TASK-DOC-001 did not need it: it ran against the committed baseline `cc357bc` ([report](validation/claude-handoff.md)).

Use disjoint file ownership and isolated Git worktrees for concurrent writers. Ensure the task card and instructions are committed in the supplied base: uncommitted parent changes are not a worker baseline. Verify each writer's actual checkout path and starting SHA. Claude's worktree default may differ from the parent branch, so a mismatch must be corrected by the coordinator before edits begin. Recheck isolation if a delegation becomes an agent-team teammate.

When Git/worktree support is unavailable, run one writer at a time in a clearly assigned checkout. Read-only research and review can still run independently. Coordinate overlapping contracts sequentially. Workers return changed paths, commit or worktree reference, acceptance results, checks, limitations and unresolved decisions. The coordinator owns publishing and integration.

## Repository and PR readiness

At the first inspection this folder was not a Git repository. During documentation editing an existing repository appeared, with origin [akibrahimug/gladiators](https://github.com/akibrahimug/gladiators) and remote default `origin/master`. These settings were observed, not created or changed by this handoff. The user then committed and pushed the handoff documents to `master` at `cc357bc`. On 2026-10-22, TASK-DOC-001 verified that committed baseline and authenticated `gh` access to the repository ([report](validation/claude-handoff.md#repository-and-publishing-readiness)).

Before the first PR, Claude must establish:

- The user-selected repository destination, visibility, permitted remote and base branch.
- A valid repository and committed baseline containing these instructions and the task card.
- The existing working-tree state, preserving unrelated changes.
- Available Git/hosting client and authenticated access to the selected repository.

Use the existing selected repository after verifying the remote and actual base; choose no new hosting destination or visibility on the user's behalf. Once the task assignment and repository access are established, routine branching, commits, pushes and draft-PR creation belong to Claude's delivery workflow; they need no additional design sign-off. Honour the user's tool permissions.

Use one bounded task per PR, with branch name `task/<TASK-ID>-<short-scope>`. Related tightly coupled subtasks may share a PR if the task card records the reason and ownership. Use the PR body field or a body file so descriptions retain their intended formatting. Before creating a duplicate, check for an existing PR for the task branch. After changes to an open PR, re-run affected checks and update the tested head revision.

Human review and merge remain separate from Claude's PR preparation. Gates retain the review requirements in the [milestone register](milestones.md).

The handoff originally planned TASK-DOC-001 as a local-only inspection, with the first publication under a separate TASK-DOC-002. Two things changed that plan:

- the user pushed the initial Git documentation baseline directly to `master` at `cc357bc`;
- [DEC-009](decisions/README.md) gives every task its own branch and PR.

TASK-DOC-001 therefore opened its own draft PR. [TASK-DOC-002](tasks/TASK-DOC-002.md) became a refresh of the handoff documents that predated that baseline.

## State and traceability

The [task board](tasks/README.md) defines work and PR states independently. Link **source/decision → REQ → CMP → P/G → TASK → branch/commit → PR → evidence**. The task card is the task record; the board is its index. A task can be locally Verified while its PR is Blocked, and neither state makes a phase complete.

Original v1.0 recovery remains a G00 prerequisite. This workflow does not convert the provisional component map into an accepted implementation brief.

## Claude Code format references

A root `CLAUDE.md` supplies project instructions ([official memory documentation](https://code.claude.com/docs/en/memory)). The three project agent definitions use Markdown with YAML frontmatter under `.claude/agents/`, and the implementer requests worktree isolation ([official subagent documentation](https://code.claude.com/docs/en/sub-agents)). Start a fresh Claude Code session after this project's first agents directory is created.

On 2026-10-22 the runtime discovered all three agents ([report](validation/claude-handoff.md#agent-discovery)):

- the spec-reader ran with its declared tools;
- the reviewer received Read and Bash but not its declared Glob and Grep (open finding F14);
- the implementer has not yet run.

Claude documents PR creation as a supported workflow ([official common workflows](https://code.claude.com/docs/en/common-workflows)). These references confirm file formats and capabilities; task ownership and delivery rules above are this project's working agreement.

## First-session prompt

The bootstrap tasks TASK-DOC-001 and TASK-DOC-002 have run. For a later session:

> Read CLAUDE.md and the task board. Work only on Ready tasks. Give each one its own `task/<TASK-ID>-<short-scope>` branch and draft PR (DEC-009), and use gladiator-spec-reader and gladiator-reviewer as its card requires. Keep application implementation unstarted while G00 is pending. Record real task/PR states and precise blockers.
