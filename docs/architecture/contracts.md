# Interface and data contract checklist

[Architecture map](README.md) · [Components](../traceability/components.md) · [Acceptance scenarios](../validation/acceptance-scenarios.md)

**Status:** proposed questions and minimum information to resolve; no executable schema or API is implemented. P00 must reconcile these against original v1.0 contracts.

| Contract | Producer → consumer | Information to specify | Failure semantics to settle | Phase / gate |
| --- | --- | --- | --- | --- |
| Source descriptor | CMP-01 → CMP-02, CMP-05 | Source/version, venue, instrument IDs, coverage, access/usage constraints, feed type, timestamp/sequence guarantees | Unavailable source, scope change, expired access | P01 / G01 |
| Event envelope and raw reference | CMP-02 → CMP-03, CMP-05, CMP-11 | Stable identity, source sequence if present, event time if supplied, receive time, availability time, raw payload reference, units, schema and quality state | Duplicate identity, sequence gap, correction, unknown message, clock uncertainty | P02 / G02 |
| Book state and replay checkpoint | CMP-03 → CMP-06, CMP-10 | Snapshot/version, watermark, venue coverage, depth semantics, reconstruction status, contributing events | Gap/stale state invalidation, snapshot recovery, trade corrections | P03 / G03 |
| Account journal and state | CMP-10 → CMP-04 → CMP-07, CMP-12 | Simulated fill/order reference, asset/currency, quantities, fees, entries, balances/positions, reconciliation reference | Duplicate fill, fee adjustment, missing entry, unbalanced state | P03 / G03 |
| Context observation | CMP-05 → CMP-06 | Observation time, publication/first-known time, revision history, source, confidence and expiry | Late arrival, revised publication, conflicting sources | P04 / G04 |
| Feature/regime record | CMP-06 → CMP-13; regime state → CMP-07, CMP-12 | Event window, as-of time, availability, value/units, validity, definition/version, uncertainty | Insufficient history, stale context, out-of-domain state | P04 / G04 |
| Forecast, intent and assessment | CMP-13 → CMP-07 → CMP-12; evidence CMP-10 → CMP-08 → CMP-09 | Hypothesis ID, model/version, input lineage, score meaning, rationale, assessment and abstention reason | Missing evidence, disagreement, unsupported confidence | P05 / G05 |
| Risk disposition | CMP-12 → CMP-10 | Candidate ID, ledger version, policy/version, limits, allow/deny/abstain, reason, expiry | Invalid data, breached limit, emergency stop, unavailable ledger | P05 / G05 |
| Simulation and audit record | CMP-10 + all components → CMP-11 | Scenario/run ID, baseline, input hashes, configuration, seed if applicable, outcome, assumptions, incident linkage | Replay mismatch, incomplete provenance, interrupted run | P06–P07 / G06–G07 |

## Decisions required before contracts become specifications

- Define identity scope, ordering scope, schema versioning and backwards compatibility.
- Choose exact numeric representation and units for each asset and currency; avoid unstated rounding.
- Specify timestamp precision, clock uncertainty and how missing source timestamps are represented.
- Distinguish source event time from first available knowledge time and local processing time.
- Define valid/invalid/recovering/stale transitions and downstream handling.
- State retention, access boundaries and a raw-record integrity strategy.
- Define ledger reconciliation equations for the selected accounting convention.
- Confirm that risk dispositions terminate in a simulation/paper boundary.

Attach original section references, worked examples and acceptance cases to each accepted contract. A filled-out checklist alone does not pass a development gate.
