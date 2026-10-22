# Phased development roadmap

[Documentation index](README.md) · [Detailed phases](phases/README.md) · [Gates](milestones.md)

**Status:** proposed work breakdown; reconcile against the original v1.0 architecture at G00. The current task creates documentation only. No development phase has been executed.

| Phase | Objective | Prerequisite | Exit gate | Main components |
| --- | --- | --- | --- | --- |
| [P00 Baseline](phases/00-baseline/README.md) | Recover, preserve and map every original spec | None for source recovery | G00 | All |
| [P01 Research and data access](phases/01-research-and-data-access/README.md) | Bound the market, sources, access and research questions | G00 | G01 | CMP-01, CMP-05, CMP-07 |
| [P02 Event capture](phases/02-event-capture/README.md) | Specify and later verify event capture, provenance and integrity | G01 | G02 | CMP-02, CMP-11 |
| [P03 Market state and ledger](phases/03-market-state-and-ledger/README.md) | Specify deterministic book reconstruction and separate account accounting | G02 | G03 | CMP-03, CMP-04 |
| [P04 Features and context](phases/04-features-and-context/README.md) | Define causal features and regime/context validity | G03 | G04 | CMP-05, CMP-06 |
| [P05 Core, Judges and Managers](phases/05-core-judges-and-managers/README.md) | Resolve roles, decision evidence and deterministic risk controls | G04 | G05 | CMP-07, CMP-08, CMP-09 |
| [P06 Simulation and validation](phases/06-simulation-and-validation/README.md) | Evaluate hypotheses with realistic costs and failure cases | G05 | G06 | CMP-10 and all decision inputs |
| [P07 Paper readiness](phases/07-paper-readiness/README.md) | Define operational and paper-only readiness | G06 | G07 | CMP-09, CMP-10, CMP-11 |

Dependency chain: **G00 → G01 → G02 → G03 → G04 → G05 → G06 → G07**.

Source recovery, reading and drafting can overlap. Dependent implementation and gate closure follow the chain. CMP-11 audit/configuration work spans every phase. New discoveries reopen affected gates; they do not silently change the accepted baseline.

## Why this order

Event validity precedes inference: capture and reconstruction must be demonstrably reproducible before features or decision models rely on them. The account ledger is specified separately so balances and positions are never inferred from public market volume. Decision evaluation follows causal dataset and feature definitions. Paper readiness follows simulation evidence and operational controls.

## Completion levels

1. **Workspace setup:** files, indexes and proposed relationships exist. This is the current deliverable.
2. **Baseline accepted:** original specs are preserved, conflicts resolved and G00 reviewed.
3. **Phase complete:** the phase's acceptance evidence and gate record are reviewed.
4. **Paper readiness:** G07 is reviewed against an agreed paper-only scope.

There is no calendar promise or profitability target in this plan. G01 must record workload, data, latency, recovery and evaluation thresholds with a justification before development estimates are treated as commitments. Any later live-trading proposal is outside this roadmap.
