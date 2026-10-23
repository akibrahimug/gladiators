# Milestone gate register

[Documentation index](README.md) · [Phase index](phases/README.md) · [Evidence format](evidence/gate-record-template.md)

**This is the gate-state record. No gate has passed.** The detailed phase specifications supply the full exit criteria; summaries here do not weaken them. Owners and reviewers are unassigned.

| Gate | Phase / prerequisite | Required acceptance evidence | Current state | Owner / reviewer / decision |
| --- | --- | --- | --- | --- |
| G00 | [P00](phases/00-baseline/README.md), no predecessor | Preserved original v1.0 specs; complete inventory/checksums; source-section mappings; conflict dispositions; accepted baseline | Pending — reconciliation and decisions done (DEC-014–DEC-025); reviewer decision outstanding | The user / the user (DEC-026) / no decision |
| G01 | [P01](phases/01-research-and-data-access/README.md), G00 | Bounded venue/instrument/source scope; access and coverage limits; algorithm research questions; documented workload, quality/latency/recovery targets and evaluation methods | Not started | Unassigned / unassigned / no decision |
| G02 | [P02](phases/02-event-capture/README.md), G01 | Accepted event contract; source/raw lineage; representative capture and gap/duplicate/order/staleness evidence against agreed thresholds | Not started | Unassigned / unassigned / no decision |
| G03 | [P03](phases/03-market-state-and-ledger/README.md), G02 | Feed-specific book fixtures and reproducible replay; invalidation/recovery; separate simulated account-ledger reconciliation and invariants | Not started | Unassigned / unassigned / no decision |
| G04 | [P04](phases/04-features-and-context/README.md), G03 | Versioned causal feature/context definitions; knowledge-time and revision tests; regime uncertainty and expiry evidence | Not started | Unassigned / unassigned / no decision |
| G05 | [P05](phases/05-core-judges-and-managers/README.md), G04 | Research/role contracts; candidate/Judge lineage; independent deterministic risk, disagreement and abstention evidence | Not started | Unassigned / unassigned / no decision |
| G06 | [P06](phases/06-simulation-and-validation/README.md), G05 | Pre-registered held-out evaluation; documented execution/cost/latency assumptions; sensitivity, replay and risk/ledger evidence; limitations | Not started | Unassigned / unassigned / no decision |
| G07 | [P07](phases/07-paper-readiness/README.md), G06 | Paper-only boundary; operational procedures; recovery/stop/incident drills; monitored data/ledger reconciliation and reviewed handover | Not started | Unassigned / unassigned / no decision |

G00 evidence so far: [preservation review](evidence/P00/preservation-review.md), [reconciliation summary](evidence/P00/v1.0-reconciliation.md), the [baseline decision record](evidence/P00/baseline-decision.md) and the [gate record](evidence/P00/g00-gate-record.md) with decision Pending.

## Closure rule

For every gate, record its exact baseline, predecessor gate revisions, criteria and thresholds agreed in advance, evidence links and versions, observed results, unresolved issues, reviewer, decision and date. Use the [gate record](evidence/gate-record-template.md). All mandatory criteria and phase requirements must be satisfied. A checklist, document count, profitability claim or model confidence score cannot close a gate.

## Change and rework

If source recovery changes a requirement, contract, assumption or component boundary, record the impact and reassess every dependent gate. Mark affected accepted gates **Reopened** when their evidence no longer applies, and return to the phase that owns the failure. Preserve prior evidence with its original baseline.

No gate in this register authorises live order routing, credentials, capital deployment or external account changes. G07 is paper readiness only.

## Setup versus development

The [setup report](validation/setup-report.md) verifies documentation navigation and preservation. It is separate from G00, whose source-recovery criteria remain unsatisfied, and from all future system acceptance gates.
