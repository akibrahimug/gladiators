# GLADIATOR — Claude Code entry point

The user uses Codex for brainstorming and design discussions, and Claude Code for implementation, wiring, tests and PRs. Work autonomously within an assigned, accepted task; take unresolved architecture choices back to the user with options and affected IDs.

This project currently contains documentation only. The original v1.0 specs have been recovered; see [the recovered source index](docs/sources/originals/RECOVERED.md). G00 passed on 2026-10-24: the [accepted baseline](docs/evidence/P00/baseline-decision.md) is the v10 release with recorded decisions. Use the recorded task and gate states; component boundaries and provisional defaults stay proposals until their gates.

1. **Select work:** read [the task board](docs/tasks/README.md) and the assigned task packet. Begin only a Ready task; document the exact blocker for other states. Documentation and research tasks may proceed once their predecessor gate has passed (P01 since G00, 2026-10-24); documentation preparation for a later phase may be drafted earlier when a Ready card scopes it.
2. **Execute or delegate:** read [the Claude workflow](docs/working-with-claude.md), then the task's source, phase, contracts and acceptance criteria. Give workers explicit task context, file scope and return criteria. Implementation writers require a committed base revision; read-only bootstrap inspection uses the observed checkout and file hashes.
3. **Review and publish:** follow the workflow's integration and PR steps. One coordinator owns shared documents and the PR. Report actual checks, review findings, task state and the real PR URL or publication blocker.

Preserve [original sources](docs/sources/originals/README.md) and captured files unchanged. The [milestone register](docs/milestones.md) owns gate decisions. A PR supplies evidence; its opening or merge never passes a gate automatically.

Current scope ends at documentation and future simulation/paper readiness. Live order routing, trading credentials and capital deployment remain outside scope.

Project agents: [spec reader](.claude/agents/spec-reader.md), [implementer](.claude/agents/implementer.md), [reviewer](.claude/agents/reviewer.md). Agent instructions guide behaviour; they are not an enforced security boundary.
