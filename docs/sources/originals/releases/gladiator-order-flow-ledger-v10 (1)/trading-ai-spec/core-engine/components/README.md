# GLADIATOR — component specifications

This directory is the canonical **separated** component design for the core-engine-first build. Existing `../KERNEL.md`, `../CORE.md` and prototype remain intact; these documents refine them. No dashboard. Phase 1 uses free/local services and has live trading disabled.

## Read order

- [System map and build order](00-SYSTEM-MAP.md)
- [Core decision kernel](01-CORE-KERNEL.md)
- [The Arena: rules and maintenance](02-ARENA.md)
- [Judges: statistical evidence and promotion](03-JUDGES.md)
- [Management: orchestration and governance](04-MANAGEMENT.md)
- [Gatekeeper: independent risk and permissions](05-GATEKEEPER.md)
- [Gladiators: model contracts and roster](06-GLADIATORS.md)
- [Code of conduct and constitutional rules](07-CODE-OF-CONDUCT.md)
- [Transporters: event delivery and replay](08-TRANSPORTERS.md)
- [Connectors: external and internal adapters](09-CONNECTORS.md)
- [Data acquisition, verification, cleaning and usage](10-DATA.md)
- [Qlib and the training pipeline](11-QLIB-AND-TRAINING.md)
- [RAG and institutional memory](12-RAG-MEMORY.md)
- [Execution simulator and reconciled ledger](13-EXECUTION-AND-LEDGER.md)
- [Costs, reliability and terminal operations](14-COSTS-AND-OPERATIONS.md)
- [Terminal CLI and acceptance gates](15-CLI-AND-ACCEPTANCE.md)
- [Thinking in Systems: causal governance](16-SYSTEMS-THINKING.md)
- [Upstream issue intelligence and fork policy](19-UPSTREAM-ISSUES-AND-FORK-POLICY.md)

## Critical distinction

The **core** (`01-CORE-KERNEL.md`) makes decisions. Qlib/training produces forecasts. Gladiators are interchangeable model contestants. The arena evaluates; judges assess; management schedules; gatekeeper vetoes; transport moves events; connectors talk to sources; data controls truth. No single LLM is presumed to be profitable.

## Implementation status

These are build specifications. The earlier `runtime/core.py` remains a limited CSV/SQLite/logistic-regression prototype; it does not implement these modules. Proposed `gladiator` commands are future CLI contracts until coded and tested.

- [20 — Competitive Intelligence](20-COMPETITIVE-INTELLIGENCE.md): public quantitative-firm research, permitted acquisition, benchmarks, evidence grading, and governance.

- [Algorithm research and independent reconstruction](21-ALGORITHM-RESEARCH-AND-REVERSE-ENGINEERING.md)
- [Core assurance and external peer review](23-CORE-ASSURANCE-AND-PEER-REVIEW.md)
- [Machine-readable algorithm register](22-ALGORITHM-REGISTER.csv)

- [24 — Market awareness and regime detection](24-MARKET-AWARENESS-AND-REGIME-DETECTION.md): sources, independently detected market shifts, event-time schema, fail-closed risk states and acceptance tests.
- [25 — Market intelligence source register](25-MARKET-INTELLIGENCE-SOURCE-REGISTER.csv): verified official URLs, free vs paid coverage, as-of issues, rights reviews, priorities.
- [26 — Market awareness adversarial review](26-MARKET-AWARENESS-ADVERSARIAL-REVIEW.md): failure modes, unresolved decisions, falsifiable experiments and residual market risks.

- [27 — Order flow and ledger intelligence](27-ORDER-FLOW-AND-LEDGER-INTELLIGENCE.md): direct trades/depth, crypto chain data, ETF venue limitations, defensible leading signals and replay tests.
