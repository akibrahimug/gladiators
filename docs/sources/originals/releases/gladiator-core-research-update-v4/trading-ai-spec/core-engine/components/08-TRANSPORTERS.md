# Transporters: event delivery and replay

Status: design specification; not a claim of implemented functionality.

## Definition
Transporters move validated, versioned events between components; they do not generate predictions or approve orders. Start with in-process Python and durable SQLite append-only event log; no Kafka or paid infrastructure initially.

## Event envelope
`{event_id, type, schema_version, producer, created_at_utc, effective_at_utc, available_at_utc, correlation_id, causation_id, payload_hash, payload}`. UTC everywhere; idempotency keys; ordering per symbol/stream; at-least-once processing with deduplication; no claim of global exactly-once delivery.

## Routes
`BAR_INGESTED -> DATA_VALIDATED -> SNAPSHOT_READY -> FORECAST_READY -> INTENT_CREATED -> RISK_APPROVED|RISK_REJECTED -> ORDER_SUBMITTED -> FILL|REJECT -> LEDGER_RECONCILED -> OUTCOME_MATURED -> EVIDENCE_READY`. Queue research work separately from trading-critical events. Dead-letter invalid messages with reason and replay support.

## Safety and maintenance
Retry transient transport failures with bounded exponential backoff; do not retry order placement without broker idempotency reconciliation. Check backlog, event age, duplicates and schema compatibility daily. Durable local replay reproduces state from raw events; transport outage causes abstention.

## Tests
Out-of-order bars cannot create future features; duplicate fills counted once; crash/restart resumes from durable cursor; unknown schema version quarantined.

## Operational invariants
- Phase 1: zero paid external services, no live orders, no dashboard; terminal text/number output only. Use local files and explicit, free, permitted data sources. Network pulls require explicit invocation.
- Every artifact includes `run_id`, UTC `as_of`, immutable `dataset_hash`, `code_version`, `config_hash`, and relevant `model_version`.
- Reject missing, stale, future-dated, unlicensed or unverified inputs; `ABSTAIN` is valid and preferable to guessing.
- Do not infer profitability from backtests. Keep chronological holdouts, realistic costs, and independent forward-paper validation.
- No LLM, gladiator, or management agent may modify gatekeeper limits or access live broker credentials.

---

## v0.4 transport invariants
Event envelope: `event_id, causation_id, correlation_id, schema_version, producer, occurred_at_utc, available_at_utc, ingested_at_utc, dataset_version, payload_hash`. Consumers are idempotent, and a deterministic replay sorts by *availability* and sequence, not vendor bar close alone. Dead-letter invalid events; never silently discard or backfill into the past. Transporters cannot create a trade intent or sign a Gatekeeper approval.
