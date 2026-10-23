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

## Critical distinction

The **core** (`01-CORE-KERNEL.md`) makes decisions. Qlib/training produces forecasts. Gladiators are interchangeable model contestants. The arena evaluates; judges assess; management schedules; gatekeeper vetoes; transport moves events; connectors talk to sources; data controls truth. No single LLM is presumed to be profitable.

## Implementation status

These are build specifications. The earlier `runtime/core.py` remains a limited CSV/SQLite/logistic-regression prototype; it does not implement these modules. Proposed `gladiator` commands are future CLI contracts until coded and tested.

- [18 — Adversarial design review (2026-10-22)](18-ADVERSARIAL-REVIEW-2026-10-22.md): critical gaps, evidence, critique protocol and release gates.
