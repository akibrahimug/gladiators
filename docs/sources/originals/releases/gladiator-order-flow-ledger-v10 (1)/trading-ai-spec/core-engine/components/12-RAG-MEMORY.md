# RAG and institutional memory

Status: design specification; not a claim of implemented functionality.

## Scope
RAG is retrieval of **textual evidence**: financial filings, model cards, research hypotheses, experiment reports, incident postmortems and lessons from failed gladiators. It is not the authoritative price database or a trading signal by itself.

## Pipeline
`licensed documents -> timestamped raw text -> chunk -> local embedding -> index -> time-filtered retrieval -> cite sources -> LLM hypothesis -> numerical validation`. Start SQLite full-text search/BM25 before adding local vector embeddings; both can cost £0 in provider fees. Store content hashes, publication time, ingestion time, access licence and chunk provenance.

## Anti-leakage
For a decision at time t, retrieve only documents whose real-world first-available time <= t. Ignore prompt instructions found inside retrieved content. Do not allow retrieved text to invoke execution tools or mutate risk limits. Keep model training and retrieval snapshots distinct.

## Feedback
After every experiment, store structured metrics and narrative diagnosis; index only after evidence finalised. Distinguish correlation from causation; do not let repeated agent-written summaries masquerade as independent evidence. Compare LLM-assisted vs non-LLM strategies on held-out data to justify inclusion.

## Acceptance
A post-dated filing never appears in earlier retrieval; every returned chunk includes citation and as-of time; removing RAG leaves quantitative core operational.

## Operational invariants
- Phase 1: zero paid external services, no live orders, no dashboard; terminal text/number output only. Use local files and explicit, free, permitted data sources. Network pulls require explicit invocation.
- Every artifact includes `run_id`, UTC `as_of`, immutable `dataset_hash`, `code_version`, `config_hash`, and relevant `model_version`.
- Reject missing, stale, future-dated, unlicensed or unverified inputs; `ABSTAIN` is valid and preferable to guessing.
- Do not infer profitability from backtests. Keep chronological holdouts, realistic costs, and independent forward-paper validation.
- No LLM, gladiator, or management agent may modify gatekeeper limits or access live broker credentials.

## LLM role during market shifts (v0.9 amendment)
RAG may surface versioned official releases, filings, verified incident notices and attributable third-party commentary to propose **hypotheses**, with evidence IDs, timestamps and contradictory-source handling. It must not invent causes, interpret future articles as past evidence, convert narrative confidence into probabilities or trigger live broker operations. Price-only detectors and independent Gatekeeper safety responses must function when the LLM is unavailable or hallucinating. See [24](24-MARKET-AWARENESS-AND-REGIME-DETECTION.md).
