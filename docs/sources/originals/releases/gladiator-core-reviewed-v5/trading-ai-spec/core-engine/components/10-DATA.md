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

## v0.5 ETF and crypto source-specific controls
- Kraken's downloadable OHLCVT archives omit intervals with no trades; classify these as venue no-trade intervals before deciding how to represent them. Full-history archives may require multi-part downloads and published SHA-256 verification. Source: https://support.kraken.com/in/articles/360047124832-downloadable-historical-ohlcvt-open-high-low-close-volume-trades-data
- Binance public spot archives use **microsecond timestamps from 2025-01-01**. Normalize based on declared source era/schema, never heuristic length alone. Source: https://github.com/binance/binance-public-data/blob/master/README.md
- Qlib accepts user-provided CSV/Parquet converted into its binary data format; keep the canonical Parquet archive independent of Qlib so engine upgrades do not rewrite provenance. Source: https://github.com/microsoft/qlib/blob/main/docs/component/data.rst
- ETF total-return adjusted closes and actual executable prices are distinct; dividends are cash events, splits adjust quantity and basis. Do not use today's ETF constituents as historical universe without point-in-time evidence.
- Freeze a `source_approval` record (licence reviewed, intended use, date, allowed retention/redistribution, coverage, sample verification). A free endpoint is not automatically an approved dataset.
