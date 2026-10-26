# G01 gate record (draft)

[Milestones](../../milestones.md) · [Gate-record template](../gate-record-template.md) · [P01 phase](../../phases/01-research-and-data-access/README.md) · [G00 record](../P00/g00-gate-record.md) · [Data-access decision](data-access-decision.md)

**G01 decision: pending. No reviewer has been designated.** The coordinator prepared the evidence fields, the readiness note and the decision requests under [TASK-P01-009](../../tasks/TASK-P01-009.md), on 2026-10-26. The decision fields stay "Pending" until the reviewer decides. Opening or merging this record's PR passes nothing.

| Field | Value |
| --- | --- |
| Gate and phase | G01 — P01 Research and data access |
| Baseline / original source manifest hash | The accepted G00 baseline ([baseline record](../P00/baseline-decision.md); DEC-027), v10 archive SHA-256 `502c61404aac90979a73d712e7ff1e7601ba58ea1927351dbfe1d9ead5b3d810` |
| Date / owner / reviewer | Evidence prepared 2026-10-26 / owner: the user (DEC-008) / reviewer: **Pending** (GR-01) |
| Requirements and components | REQ-001 to REQ-007, REQ-020; CMP-01, CMP-02, CMP-03, CMP-04, CMP-05, CMP-07 (P01 traceability) |
| Upstream passed gate records and versions | [G00](../P00/g00-gate-record.md), passed 2026-10-24 |
| Exact acceptance criteria and pre-agreed thresholds | The [G01 exit gate](../../phases/01-research-and-data-access/README.md#g01--exit-gate) and the milestone-register G01 row. The thresholds to be approved are the proposed values in the [acceptance-objective register](acceptance-objectives.md#for-the-g01-reviewer), selected before any measurement |
| Evidence files / source versions / dataset hashes | [Source registry](source-registry.md) (TASK-P01-001) and its follow-ups: [round 1](source-followups.md) (P01-004), [round 2](source-followups-2.md) (P01-006), [reassessment](source-reassessment.md) (P01-007), [Binance general terms](binance-general-terms.md) (P01-008); [observability map](observability-map.md) (P01-001); [research agenda](research-agenda.md) (P01-002); [acceptance-objective register](acceptance-objectives.md) (P01-003); [data-access decision and sample plan](data-access-decision.md) (P01-005). All are on `master` through PRs #13 to #20. No dataset exists yet, so no dataset hashes |
| Method and environment / configuration versions | Primary documentation and terms read on the dates each file states; quotes checked by independent `gladiator-reviewer` passes; no account, key, download, capture or vendor contact |
| Observed outcomes | See the [readiness note](#coordinators-readiness-note). In short: every required input maps to a proposed source or a recorded gap; crypto daily bars have two Conditional sources; ETF daily bars have none (DEC-029 triggered); no `source_approval` record exists; nothing has been measured |
| Failed cases, uncertainty and limitations | Terms ambiguities: F-4a (Kraken) and F-5b′ (Binance). Source semantics not yet verified by sample: F-4d, F-4f, F-4g, F-4h, F-4i, F-5c. No historical venue status (F-7, F-7b). Training and paper venues differ if Binance is used (F-8). The coordinator's terms readings are not legal advice |
| Open issues and disposition | Decision requests GR-01 to GR-10 [below](#decision-requests) |
| Decision: pending / passed / reopened | **Pending** |
| Decision rationale and reviewer identity | Pending |
| Affected downstream gates if changed | G02 to G07 depend on G01. The source baseline fixes P02's capture targets; the proposed values fix P02 to P06 thresholds |

## Coordinator's readiness note

Written before any decision. It checks each clause of the G01 exit gate against the evidence.

| G01 clause | Evidence | Coordinator's reading |
| --- | --- | --- |
| Every required event or context input in the selected scope maps to a source and access decision, or to a documented gap with an accepted scope adjustment | [Data-access decision](data-access-decision.md#proposed-source-baseline): each need has a proposed source or "None" with a recorded gap | **Mapped, not accepted.** Every row maps. The gaps need acceptance as scope adjustments (GR-08), and the sources need approval (GR-02) |
| Every selected source has evidence for its semantics and limitations | Registry rows SR-02, SR-04, SR-05 and the context rows; the follow-ups | **Documented from published text.** Several semantics are verifiable only by the sample plan (F-4f, F-4g, F-4h, F-4i, F-5c). The gate says "Access not yet demonstrated remains a dependency, never an assumed capability", so these stay listed dependencies for P02 (GR-09) |
| The research agenda identifies cited alternatives, reference baselines and data needs | [Research agenda](research-agenda.md) | Met. Its recorded gaps go to GR-08 |
| Workload and quality/latency/recovery objectives have recorded definitions, justified thresholds and evaluation methods | [Acceptance-objective register](acceptance-objectives.md) | **Recorded, not approved.** The thresholds are proposed values (GR-07). Three VAL gaps are recorded (GR-07) |
| The reviewer approves the source baseline, research agenda, evaluation criteria and unresolved exceptions before P02 starts | This record | **Not met:** no reviewer (GR-01) and no decision |
| Evidence needed: registry, map, cited primary documentation, access feasibility evidence, sample plan, agenda, register and dated approval | The files listed above | All present except the dated approval. **Access feasibility** rests on documented public, keyless endpoints; it is not demonstrated |

**Coordinator's overall reading:** the evidence is complete enough for a decision. Passing G01 needs the reviewer's answers to GR-01 to GR-10. The coordinator recommends a pass with recorded conditions rather than a further research round, because the remaining unknowns are either terms ambiguities that more reading cannot settle, or semantics only the sample can show.

## Decision requests

Each request names the affected IDs and lists options, with the coordinator's recommendation first. The reviewer may choose another option or write their own.

| ID | Question | Options (recommended first) | Affected IDs |
| --- | --- | --- | --- |
| GR-01 | Who reviews G01? | (a) **The user**, as for G00 (DEC-026). (b) Another named person | Milestone register G01 row |
| GR-02 | Crypto daily-bar history source | (a) **Binance Vision primary, Kraken archive as cross-check**: the coordinator's proposal ([reassessment](source-reassessment.md#3-comparison-for-the-crypto-first-daily-baseline)); Binance's terms expressly permit personal backtesting. (b) Kraken only: one venue, no USDT question, but §9 and retention stay ambiguous. (c) Both as equal sources | SR-04, SR-05; H-01 to H-06; W-1 |
| GR-03 | Training and paper venues (F-8) | (a) **Research on Binance; any model used in paper simulation is trained and run on Kraken.** This keeps Binance-derived models out of paper and live use, which fits the Binance terms' §2.4 and §4.2. (b) Kraken for both. (c) A venue-transfer assumption with a USDT/USD basis treatment, validated on overlapping periods | F-8, F-5d; BB; P06 |
| GR-04 | Terms ambiguities (F-4a Kraken §9 and retention; F-5b′ Binance general terms) | (a) **Accept as recorded limitations** for personal, non-commercial research (DEC-030). Draft `source_approval` records that state them, and reopen them on any change of use. (b) Treat them as blockers until a vendor confirms. DEC-033 says not to wait for vendor replies, so this would stall P02 | F-4a, F-5b′; S-1, S-2; L-025 |
| GR-05 | Quote currency (F-5d; W-1 says "quoted in USD") | (a) **Per-source quote currency:** USD on Kraken, USDT on Binance, never mixed within one model; record the USDT/USD basis as a limitation. (b) USD only, which rules out most Binance pairs | W-1, F-5d, F-8 |
| GR-06 | Historical venue status (F-7, F-7b) | (a) **Reviewer-approved rule:** for archived bars, treat a missing or zero-volume day as status-unknown, with no new entries that day; otherwise assume the venue was open; record this as an assumption with its limitation. (b) Evaluate only periods covered by forward capture, which leaves no history today. (c) Infer status from archive gaps plus a published incident history, if one is found | F-7, F-7b; `10-DATA.md:40`; T-2a |
| GR-07 | Proposed values and evaluation gaps in the [register](acceptance-objectives.md#for-the-g01-reviewer) | (a) **Approve all as proposed:** W-1, W-2, W-4, W-7, T-2a, T-3, T-5, T-6, Q-4, R-3, R-4, R-5. Add the FRED `available_at` rule ([round 2](source-followups-2.md#context-sources--s-7-publication-timing)). Record the three VAL gaps (Q-1, Q-3/Q-4, Q-7) as P02/P04 test obligations. (b) Review them one by one | Register rows; VAL-002 to VAL-012 |
| GR-08 | Recorded gaps as accepted scope adjustments | (a) **Accept them as gaps:** ETF daily source and corporate actions (DEC-029; ETFs follow crypto); historical L2 depth (forward capture only); H-OF4 (no L3); live H-OF6 (no live second venue); H-OF7 (no free source); H-OF8 and H-OF9 (out of scope, W-7); Coin Metrics S-7; context retention (S-2). (b) Reject one or more, which sends P01 back to source research for that item | Data-access decision; agenda gaps; W-7 |
| GR-09 | Provisional defaults and the sample plan | (a) **Confirm W-5 daily first and S-3 £0** (DEC-017 left both to G01). Carry the sample-plan items into P02 as dependencies: F-4d, F-4f, F-4g, F-4h, F-4i, F-5c. (b) Change the horizon or budget | W-5, S-3; DEC-017; P02 |
| GR-10 | G01 decision | (a) **Pass G01 with the conditions above recorded.** (b) Hold G01 pending listed items. (c) Reopen P01 scope | Milestone register; P02 start |

**Separate from G01: download authorisation.** The sample plan runs only after G01 **and** the user's authorisation of downloads ([data-access decision](data-access-decision.md#representative-sample-plan)). Authorising steps 0, 1 and 3 permits public file downloads only; it permits no account, key or live capture. Step 2, live capture, needs a separate capture authorisation at the P02 boundary. This authorisation is the user's to give, and it is not a gate decision.
