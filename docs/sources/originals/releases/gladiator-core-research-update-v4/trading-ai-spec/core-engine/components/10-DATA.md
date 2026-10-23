# Data acquisition, verification, cleaning and usage

Status: design specification; not a claim of implemented functionality.

## Canonical storage layout
`data/raw/{provider}/{ingest_date}/` immutable response bytes + checksum + licence/receipt; `data/quarantine/` rejected records; `data/clean/{dataset_version}/` partitioned Parquet; `data/snapshots/{snapshot_id}/` as-of manifest; `data/features/{feature_version}/`; `data/documents/`; `data/experiments/`; `data/ledger/`. SQLite/DuckDB for metadata/querying; Parquet for bars/features. Backups and integrity checks required.

## Market schema
`symbol,venue,currency,interval,bar_start_utc,bar_end_utc,available_at_utc,open,high,low,close,volume,provider,source_revision,corporate_action_basis,ingested_at_utc`. Keep raw and adjusted series separately; record splits/dividends and delisting; timezone/exchange-calendar aware; distinguish traded close from adjusted close. For documents: `published_at`, `first_available_at`, `retrieved_at`, `source_url`, `content_hash`, `licence`.

## Verification sequence
1. Check terms/licence and source coverage before pull; maintain provider manifest and zero-cost constraint.
2. Preserve raw bytes and receipt with SHA-256; never silently overwrite.
3. Parse with explicit types; reject malformed/negative prices, invalid timestamps, duplicate conflicting keys, impossible OHLC ordering, negative volume, inconsistent currency/venue.
4. Validate exchange sessions, timezone and expected bar cadence; distinguish legitimate halts/holidays from missing bars.
5. Investigate splits/dividends, symbol changes, delistings, bad ticks, extreme outliers; quarantine rather than automatically winsorise true market jumps.
6. Cross-check suspect prices against an independent permitted source when possible; record disputes and corrections as new dataset versions.
7. Stamp earliest real availability for every observation; enforce `available_at <= decision_time` and completed bars only.
8. Create immutable versioned Parquet snapshot with validation report: coverage, missing %, duplicate %, quarantined count, actions, provider hashes.
9. Derive causal features using past-only windows and train-only fitted transforms; prevent lookahead in normalisation, imputation, labels and universe selection.
10. Separate training, validation, locked test and forward-paper data chronologically; label maturity and purging/embargo for overlapping targets.

## Using data
Qlib numerical training reads structured clean bars/features; simulator reads executable-price assumptions and corporate actions; RAG indexes **documents, research, model cards and experiment narratives** with as-of filtering. Do not pass unstructured RAG summaries as ground-truth prices. Retrieval must include citations and timestamps; missing data -> abstain.

## First-run dataset decision
Free daily bars are easiest to validate, but the desired 15m/1h horizon requires a separate lawful, sufficiently deep intraday source. Until one is confirmed, **run daily-horizon experiments honestly**, not synthetic intraday bars presented as real. Never infer executable bid/ask from OHLC without explicit conservative assumptions.

## CLI acceptance
`gladiator data sources`; `data pull --provider ... --allow-network`; `data validate --raw ...`; `data build --version ...`; `data snapshot --as-of ...`; `data audit --snapshot ...`. Fixture tests cover splits, DST, duplicate bars, future leakage, delisted symbols, stale prices and missing data.

## Operational invariants
- Phase 1: zero paid external services, no live orders, no dashboard; terminal text/number output only. Use local files and explicit, free, permitted data sources. Network pulls require explicit invocation.
- Every artifact includes `run_id`, UTC `as_of`, immutable `dataset_hash`, `code_version`, `config_hash`, and relevant `model_version`.
- Reject missing, stale, future-dated, unlicensed or unverified inputs; `ABSTAIN` is valid and preferable to guessing.
- Do not infer profitability from backtests. Keep chronological holdouts, realistic costs, and independent forward-paper validation.
- No LLM, gladiator, or management agent may modify gatekeeper limits or access live broker credentials.

---

## v0.4 data sourcing plan and audit gates
1. **First working experiment:** 10–20 liquid US shares, *daily* OHLCV with long history from a lawful zero-cost research source, plus trading calendar and split/dividend metadata. Do not promise 15-minute/1-hour history from a daily feed.
2. **Source manifest** must record provider URL, terms URL, access method, allowed research/commercial use, raw/adjusted definitions, universe coverage, interval, rate limit, retrieval date and checksum.
3. **Raw -> quarantine -> clean -> as-of:** preserve immutable raw, check timestamp timezone and data availability, OHLC inequalities, zero/negative prices, duplicates, corporate actions, delistings, stale/holiday bars and cross-source outliers. No blind forward-fill of missing traded bars.
4. **Two parallel datasets:** unadjusted tradable prices for simulated fills, explicitly defined adjusted series for returns/features; track dividends and split quantities in the ledger. Prevent today's surviving stocks from becoming yesterday's entire universe.
5. **Point-in-time RAG:** document publication and *first actually available* timestamp required. Text retrieved later must never appear in earlier decisions.
6. **Quality report:** counts of raw, accepted, quarantined, duplicates, missing sessions, split discontinuities and coverage; fail closed when coverage is inadequate.
7. **Licence review:** Qlib official data unavailable; yfinance describes Yahoo data as personal-use; Stooq automation reportedly restricted. Therefore the first dataset provider remains **provisional**, not guaranteed.
