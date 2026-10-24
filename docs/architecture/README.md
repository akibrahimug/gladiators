# Architecture map

> **Source recovery update — 2026-10-23:** Original GLADIATOR releases, including the 54-file v10 release identified as v1.0, are now imported; v10 is not a complete superset of earlier releases (PF-05). See the [recovered document index](<../sources/originals/RECOVERED.md>). Earlier missing-source statements below are historical. Reconciliation and decisions are done (DEC-014–DEC-025), and G00 passed on 2026-10-24 (DEC-027).

[Documentation index](../README.md) · [Component register](../traceability/components.md) · [Contract checklist](contracts.md)

**Status:** proposed navigation and responsibility map, first created from the accessible brief and now aligned with the v10 role model (DEC-014). Component IDs are workspace aliases for original names.

> **Reconciliation, 2026-10-23:** this map is now compared section by section with the v10 release ([summary](../evidence/P00/v1.0-reconciliation.md)). The user decided the component model on 2026-10-23 ([DEC-014](../decisions/README.md)), and the flow below follows it. Boundaries remain proposals until their gates.

## Meaning of order flow and ledger

A market feed can expose specified orders, book levels, trades and venue events. It is not evidence of access to all participants' balances, intentions or transfers. Nasdaq's ITCH specification describes exchange order and trade messages within that feed's scope ([EXT-001](https://www.nasdaqtrader.com/content/technicalsupport/specifications/dataproducts/NQTVITCHSpecification_5.0.pdf)). Coinbase documents separate market channels and an authenticated user channel ([EXT-002](https://help.coinbase.com/en/developer-platform/websocket-feeds/exchange)).

The design implication is to document visibility per source, rather than infer a universal money ledger. Order-book events, executed volume, a raw event journal and the system's own account ledger serve different purposes. Lower rendering delay alone does not establish an informational advantage; any latency claim must be measured for selected sources.

## Proposed flow

```mermaid
flowchart TD
  S["CMP-01 Source registry"] --> I["CMP-02 Capture / raw log"]
  I --> B["CMP-03 Market book / replay"]
  I --> X["CMP-05 Context / availability"]
  B --> F["CMP-06 Features / regimes"]
  X --> F
  F --> G["CMP-13 Gladiators"]
  G --> C["CMP-07 Core decision kernel"]
  X --> C
  C --> K["CMP-12 Gatekeeper"]
  X --> K
  L["CMP-04 Own-account ledger"] --> C
  L --> K
  K --> T["CMP-10 Simulation / paper"]
  T --> L
  T --> J["CMP-08 Judges"]
  T --> R["CMP-14 Arena"]
  G --> R
  R --> J
  J --> M["CMP-09 Management"]
  M -. "promotion and budgets" .-> G
  F -- "regime state" --> C
  F -- "regime state" --> K
  X -- "textual evidence" --> G
  L --> J
  J --> R
  R --> M
  A["CMP-11 Audit / configuration"] -. "lineage across all stages" .-> I
  A -.-> K
  A -.-> T
```

The diagram is a proposed logical relationship, not an implemented service topology. The ledger feedback is simulated state for this roadmap. External account credentials, order routes and live execution are absent.

## Component boundaries

| Group | Responsibility | Boundary question for baseline |
| --- | --- | --- |
| CMP-01 / CMP-02 | Source catalog, capture, raw provenance and normalized events | Which asset/venue, rights and feed semantics? |
| CMP-03 | Reconstruct only the market state supported by each feed; replay it | Price-level or order-level data? Recovery guarantees? |
| CMP-04 | Account for simulated cash, positions, fills and fees separately | What did “ledger” mean in original v1.0? Which accounting convention? |
| CMP-05 / CMP-06 | Track context knowledge time, features and regime uncertainty | Which contexts and hypotheses have measurable relevance? |
| CMP-13 / CMP-14 | Gladiators forecast; the Arena compares them fairly | Which baselines, pools and leakage controls (reinstated L-018)? |
| CMP-07 / CMP-12 | Core decides and sizes; the Gatekeeper alone approves | Which decision maths and which policy values (DEC-017 defaults, not accepted)? |
| CMP-08 / CMP-09 | Judges evaluate; Management promotes and budgets | Which promotion criteria and evidence thresholds? |
| CMP-10 | Simulate and later assess paper-only behaviour | Which fill, queue, latency and cost assumptions are defensible? |
| CMP-11 | Record lineage, policy/config versions, incidents and evidence | Which records are required for reproducibility and recovery? |

## Proposed invariants

- Every derived value identifies its source events, schema and transformation version.
- Unknown, stale and invalid states remain explicit; no consumer silently treats them as valid.
- Knowledge available after a decision cannot enter that decision's replay inputs.
- Book state and own-account accounting have distinct contracts and reconciliation rules.
- Model output cannot bypass deterministic risk rules or create an external order.
- An abstention has a reason and lineage, just as a research candidate does.

These are proposed acceptance requirements to reconcile at G00 and specify at G01–G05. They are not verified system properties. Storage engines, programming languages, infrastructure and model families are intentionally unresolved until originals and research justify selections.
