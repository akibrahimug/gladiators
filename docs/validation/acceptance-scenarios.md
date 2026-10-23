# Proposed acceptance scenarios

[Requirements](../requirements.md) · [Traceability](../traceability/requirements-matrix.md) · [Gates](../milestones.md)

**Status:** future validation specifications, not executed tests. Reconcile with original v1.0 at G00. Fixture sizes, instruments, thresholds and tools remain to be selected.

| ID | Scenario and required observation | Requirements | Components | Gate |
| --- | --- | --- | --- | --- |
| VAL-001 | Inventory originals; each spec/section maps to a phase and component or an explicit deferred/conflict record; byte hashes match | REQ-003/011/012 | All | G00 |
| VAL-002 | At G02 trace normalized event envelopes to raw payloads, source identity and access scope; at G04 trace features to those events; at G05 extend lineage to candidates. Missing required lineage invalidates that stage's record | REQ-001/002/003/011 | CMP-01/02 at G02; CMP-06 at G04; CMP-13/07 at G05; CMP-11 throughout | G02, G04, G05 |
| VAL-003 | Replay the same versioned event corpus twice and compare declared state outputs/checkpoints under the agreed determinism rule | REQ-004/005 | CMP-02/03/11 | G03 |
| VAL-004 | Inject gaps, duplicates, reordering, clock anomalies and stale intervals; verify capture status/recovery at G02 with downstream contract fixtures, then integrated state/risk abstention at G05 | REQ-004/005/009 | CMP-02 at G02; CMP-03/09 at G05 | G02, then G05 |
| VAL-005 | Apply add/change/remove/trade/correction events supported by the selected feed; reconcile with authoritative fixture snapshots | REQ-001/005 | CMP-03 | G03 |
| VAL-006 | Apply duplicate fills, fees, adjustments and missing entries: verify ledger reconciliation with fixture events at G03, risk invalidation with controlled inputs at G05, and full simulator integration at G06 | REQ-005/006/009 | CMP-04 at G03; CMP-12 at G05; CMP-10 at G06 | G03, G05, G06 |
| VAL-007 | Deliver a context revision late; verify an earlier decision sees only information known then | REQ-004/008 | CMP-05/06 | G04 |
| VAL-008 | Replay regime shift, missing context and unsupported feature state; verify feature uncertainty/expiry with downstream contract fixtures at G04, then integrated research/risk response at G05 | REQ-005/008/009 | CMP-05/06 at G04; CMP-07/12/13 at G05 | G04, then G05 |
| VAL-009 | Compare cited algorithm candidates and a declared reference baseline on bounded fixtures at G05; record failed hypotheses/limitations, then perform held-out end-to-end comparison at G06 | REQ-007/010 | CMP-13/14/08 at G05; CMP-10 at G06 | G05, then G06 |
| VAL-010 | Supply missing evidence, conflicting Judges and invalid scores; record assessment/abstention with source and version lineage | REQ-007/009/011 | CMP-07/08/09/11/12/13 | G05 |
| VAL-011 | Breach each selected risk limit and activate the stop condition; verify policy outcomes with ledger fixtures and a simulator-output stub at G05, then no bypass in full simulation at G06 | REQ-005/006/009 | CMP-04/09 at G05; CMP-10 integration at G06 | G05, then G06 |
| VAL-012 | Evaluate on declared held-out periods with fees, latency, spread and fill/queue uncertainty; report sensitivity and selection limits | REQ-007/010/011 | CMP-13/10/11 | G06 |
| VAL-013 | Reproduce a simulation from input/configuration hashes and inspect a full decision and ledger trail | REQ-004/006/010/011 | CMP-04/10/11 | G06 |
| VAL-014 | Rehearse paper-only outage, restart and incident procedures; show agreed recovery and reconciliation outcomes | REQ-005/009/011/012 | CMP-09/10/11/12 | G07 |
| VAL-015 | Inspect the delivered workspace: links resolve, source hashes match, phases/gates/IDs are consistent, no executable trading code or credentials created | REQ-011/012 | All documentation | Setup report; G00 source portion still pending |

Early-stage fixture/stub evidence verifies only the declared contract and must be labelled with its scope. It does not establish that a later component exists or that end-to-end behaviour passes. Each later listed gate requires fresh integrated evidence under its accepted baseline.

A positive simulation result is an observation under recorded assumptions, not evidence of guaranteed future profit or negligible loss. Thresholds and acceptance methods must be written before results are used to accept a gate.
