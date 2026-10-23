# Original-specification intake checklist

[Source register](../README.md) · [Import manifest](import-manifest.md) · [Requirements](../../requirements.md)

This checklist is the source-recovery portion of baseline gate **G00**. Boxes began unchecked before any import. On 2026-10-23 the [preservation review](../../evidence/P00/preservation-review.md) (TASK-P00-001) checked the preservation and version items below; the remaining items belong to TASK-P00-002 and the G00 review. Completing intake alone does not waive any other milestone criteria.

- [x] Obtain the actual original Markdown files, attachments or complete response bodies from the referenced conversation; markers alone do not satisfy recovery.
- [x] Preserve the raw export or original files byte for byte, with original filenames and relative paths recorded. Keep separate copies for conflicting versions.
- [ ] Capture the source conversation, source-message and attachment IDs when available, together with the retrieval date and method. *(Partly met 2026-10-23: conversation ID, retrieval date and method recorded; per-archive message IDs and the v1.0 download evidence are not preserved — PF-02, PF-04.)*
- [x] Record a SHA-256 digest for every preserved file in the import manifest and verify the digests after copying.
- [x] Read each source and record its explicit version header. Identify the latest v1.0 architecture using source evidence; document uncertainty where the version cannot be established.
- [x] Record each supersession relationship with evidence. Keep earlier sources available and identify any unresolved conflict rather than selecting a version silently.
- [ ] Add every actual specification to the project catalog. Map it to requirements, phases and components, including cross-cutting specifications and documents that do not yet fit the scaffold.
- [ ] Compare component names, boundaries, inputs, outputs, dependencies and ownership with the recovered architecture. Treat Core, Judges and Managers as provisional terms until their source contracts are confirmed.
- [ ] Reconcile event ordering, source provenance, event-time/replay behavior, data integrity, market-data visibility and own-account ledger boundaries.
- [ ] Reconcile research evaluation, market context, risk-abstention behavior, simulation realism and audit reproducibility. Retain the task’s documentation-only boundary.
- [ ] Record additions, omissions and conflicts in the manifest’s findings table. Link each resolution to source evidence or an explicit documented decision.
- [ ] Check navigation and traceability links in the reconciled planning documents; ensure every actual specification has a discoverable path from the project index.
- [ ] Record a completeness assessment against the recovered export or known specification list, including any unavailable older messages or attachments. A reader response with no pagination is not enough to claim historical completeness.
- [ ] Review the reconciled baseline and its evidence against G00. Keep G00 pending while original v1.0 content, required mappings or material conflicts remain unresolved.
