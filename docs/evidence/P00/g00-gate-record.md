# G00 gate record — draft

[Milestones](../../milestones.md) · [Gate-record template](../gate-record-template.md) · [P00 phase](../../phases/00-baseline/README.md) · [Reconciliation summary](v1.0-reconciliation.md)

**G00 decision: Passed on 2026-10-24 by the reviewer, the user ([DEC-026](../../decisions/README.md), [DEC-027](../../decisions/README.md)).** The coordinator prepared the evidence fields; only the decision fields record the reviewer's decision, transcribed by [TASK-P00-004](../../tasks/TASK-P00-004.md). Drafted 2026-10-23 under [TASK-P00-002c](../../tasks/TASK-P00-002c.md) and completed under [TASK-P00-003](../../tasks/TASK-P00-003.md).

| Field | Value |
| --- | --- |
| Gate and phase | G00 — P00 Baseline and source reconciliation |
| Baseline / original source manifest hash | Baseline: the v10 release `docs/sources/originals/releases/gladiator-order-flow-ledger-v10 (1)/` ([DEC-011](../../decisions/README.md)) plus 10 reinstated earlier-release sections and the T19–T30 alias ([DEC-020](../../decisions/README.md), [baseline record](baseline-decision.md#reinstated-sections)), v10 archive SHA-256 `502c61404aac90979a73d712e7ff1e7601ba58ea1927351dbfe1d9ead5b3d810`; full manifest [`RECOVERED-SHA256SUMS`](../../sources/originals/RECOVERED-SHA256SUMS) (415 entries) and [inventory](../../sources/originals/recovery-inventory.json) |
| Date / owner / reviewer | 2026-10-23 / owner: the user (decision owner per DEC-008) / reviewer: **the user** (DEC-026) |
| Requirements and components | REQ-001..020 (REQ-013–020 Proposed, DEC-019); CMP-01..14 per DEC-014; original v10 components 00–27 |
| Upstream passed gate records and versions | None (G00 has no predecessor) |
| Exact acceptance criteria and pre-agreed thresholds | [Milestone register](../../milestones.md) G00 row and the [P00 exit gate](../../phases/00-baseline/README.md#g00--exit-gate): every supplied source inventoried and preserved; every requirement and component linked to a source location or an explicitly accepted proposal; all baseline conflicts with a recorded disposition; reviewer approval of scope, provenance and reconciliation. No numeric thresholds apply |
| Evidence files / source versions / dataset hashes | [Preservation review](preservation-review.md) (TASK-P00-001, PR #4); [reconciliation summary](v1.0-reconciliation.md) and packets [a](v1.0-reconciliation-a.md), [b](v1.0-reconciliation-b.md), [c](v1.0-reconciliation-c.md) (TASK-P00-002, PRs #5–#7, on `master` via #5 and #9); [baseline decision record](baseline-decision.md) (TASK-P00-003) |
| Method and environment / configuration versions | Read-only scripts and independent `gladiator-reviewer` passes; no preserved code executed; see each evidence file |
| Observed outcomes | 10 archives and 405 members preserved byte for byte and verified twice. All 349 v10 `##`/`###` sections, 2 CSV registers and 4 code files mapped (389 rows: 151 Confirmed, 44 Conflicting, 127 Source-addition, 11 Out-of-scope, 55 Informational, 1 Superseded-in-v10). 40 lineage-annex rows: 36 for content only in earlier releases (complete at heading level) and 4 for v10 text referring to it |
| Failed cases, uncertainty and limitations | PF-01: archives not compared with the browser downloads. PF-02/PF-04: v1.0 identity rests on the component 27 header; the conversation evidence (heading, download control, message IDs) is not preserved. PF-05: releases are not cumulative. Mapping relationships are interpretations against proposed workspace IDs |
| Open issues and disposition | All twelve decision requests DR-01–DR-12 ([summary](v1.0-reconciliation.md#consolidated-decision-requests)) were decided by the user on 2026-10-23 as DEC-014–DEC-025 and applied to the planning documents. The source's provisional selections are recorded, not accepted (DEC-017), and G01 decides them. Reviewer dispositions, 2026-10-24: PF-01 and PF-02/PF-04 accepted as recorded provenance limitations ("Accept as limitations (Recommended)"); the DEC-014 application confirmed ("Confirm as applied (Recommended)"). The limitations stay recorded, and the evidence may be recovered later |
| Decision: pending / passed / reopened | **Passed — 2026-10-24** |
| Decision rationale and reviewer identity | The reviewer is the user, the repository owner (DEC-026). Their answer to "G00 decision: do you, as G00 reviewer, approve the scope, provenance and reconciliation, so that G00 passes and P01 can start?" was "Pass G00", given after the two dispositions above. The rationale is the criteria table below, with the outstanding rows now satisfied by this decision. Recorded as DEC-027 |
| Affected downstream gates if changed | G01–G07 depend on G00; reopening DEC-014 (roles) or DEC-016 (phase scheme) would change P01–P07 scopes |

## Coordinator's readiness note (written before the decision)

The coordinator checked each G00 criterion against the evidence:

| Criterion (P00 exit gate) | Evidence | Coordinator's reading |
| --- | --- | --- |
| Every supplied source inventoried and preserved | [Preservation review](preservation-review.md): 10 archives and 405 members verified | Met if the reviewer accepts PF-01 and PF-02/PF-04 as limitations. The P00 gate says "Missing original v1.0 specifications keep G00 pending"; whether the missing conversation evidence counts is for the reviewer to weigh |
| Every requirement and component linked to a source location or an explicitly accepted proposal | Reverse checks in packets a–c; REQ-013–020 cite source rows; the [component register](../../traceability/components.md) names an original component for every CMP | Met |
| All baseline conflicts have a recorded disposition | DEC-014–DEC-025; [baseline record](baseline-decision.md) | Met |
| Reviewer approval of scope, provenance and reconciliation; an accepted baseline | Decision fields above; the [baseline record](baseline-decision.md) becomes the accepted baseline only on approval | Satisfied 2026-10-24: the reviewer passed G00, and the [baseline record](baseline-decision.md) is the accepted baseline |
| A dated approval linked from the milestone register | [Milestones](../../milestones.md) G00 row | Satisfied 2026-10-24: the G00 row in the milestone register links this record |
