# G00 gate record — draft

[Milestones](../../milestones.md) · [Gate-record template](../gate-record-template.md) · [P00 phase](../../phases/00-baseline/README.md) · [Reconciliation summary](v1.0-reconciliation.md)

**Draft prepared by the coordinator for the designated G00 reviewer. Decision: Pending.** This record collects evidence; it is not a sign-off, and no field below is a reviewer's decision. Prepared 2026-10-23 under [TASK-P00-002c](../../tasks/TASK-P00-002c.md).

| Field | Value |
| --- | --- |
| Gate and phase | G00 — P00 Baseline and source reconciliation |
| Baseline / original source manifest hash | Proposed baseline: the v10 release `docs/sources/originals/releases/gladiator-order-flow-ledger-v10 (1)/` ([DEC-011](../../decisions/README.md)), archive SHA-256 `502c61404aac90979a73d712e7ff1e7601ba58ea1927351dbfe1d9ead5b3d810`; full manifest [`RECOVERED-SHA256SUMS`](../../sources/originals/RECOVERED-SHA256SUMS) (415 entries) and [inventory](../../sources/originals/recovery-inventory.json) |
| Date / owner / reviewer | Draft 2026-10-23 / owner unassigned / **reviewer unassigned** |
| Requirements and components | REQ-001..012; CMP-01..11 (provisional aliases); original v10 components 00–27 |
| Upstream passed gate records and versions | None (G00 has no predecessor) |
| Exact acceptance criteria and pre-agreed thresholds | [Milestone register](../../milestones.md) G00 row and the [P00 exit gate](../../phases/00-baseline/README.md#g00--exit-gate): every supplied source inventoried and preserved; every requirement and component linked to a source location or an explicitly accepted proposal; all baseline conflicts with a recorded disposition; reviewer approval of scope, provenance and reconciliation. No numeric thresholds apply |
| Evidence files / source versions / dataset hashes | [Preservation review](preservation-review.md) (TASK-P00-001, PR #4); [reconciliation summary](v1.0-reconciliation.md) and packets [a](v1.0-reconciliation-a.md), [b](v1.0-reconciliation-b.md), [c](v1.0-reconciliation-c.md) (TASK-P00-002, PRs #5 onward) |
| Method and environment / configuration versions | Read-only scripts and independent `gladiator-reviewer` passes; no preserved code executed; see each evidence file |
| Observed outcomes | 10 archives and 405 members preserved byte for byte and verified twice. All 349 v10 `##`/`###` sections, 2 CSV registers and 4 code files mapped (389 rows: 151 Confirmed, 44 Conflicting, 127 Source-addition, 11 Out-of-scope, 55 Informational, 1 Superseded-in-v10). 38 lineage-annex rows for content only in earlier releases |
| Failed cases, uncertainty and limitations | PF-01: archives not compared with the browser downloads. PF-02/PF-04: v1.0 identity rests on the component 27 header; the conversation evidence (heading, download control, message IDs) is not preserved. PF-05: releases are not cumulative. Mapping relationships are interpretations against proposed workspace IDs |
| Open issues and disposition | Decision requests DR-01–DR-12 ([summary](v1.0-reconciliation.md#consolidated-decision-requests)), all open: component/role model, primary input, phase/ID crosswalk, provisional selections, ledger meanings, proposed requirements, lineage reinstatement, live content, stack, REQ-001 wording, v10 precedence, audit tool |
| Decision: pending / passed / reopened | **Pending** |
| Decision rationale and reviewer identity | Not recorded. Requires a designated reviewer |
| Affected downstream gates if changed | G01–G07 depend on G00; DR-01 (roles) and DR-03 (phase scheme) would change P01–P07 scopes |

## Coordinator's readiness note (not a decision)

The source-recovery and mapping evidence exists. In the coordinator's reading, G00 cannot pass yet: the P00 exit gate needs "every requirement and component linked to a source location **or an explicitly accepted proposal**" and "all baseline conflicts with a recorded disposition". Several conflicts (DR-01, DR-02, DR-04, DR-05) are still open, and no proposal has been accepted. The reviewer may also weigh whether PF-01 and PF-02 are acceptable provenance limitations.
