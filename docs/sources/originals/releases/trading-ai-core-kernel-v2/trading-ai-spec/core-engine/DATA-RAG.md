# Data storage, point-in-time retrieval and RAG

**Numeric time series are not served through RAG.** RAG is a citation-bearing document memory, not a reliable transport for millions of OHLCV records. The core reads curated numeric features directly; the LLM queries both structured tools and retrieved documents.

## Storage tiers
1. `raw/` immutable vendor responses + provider receipt timestamps + checksums.
2. `curated/` validated Parquet, UTC, canonical instrument IDs, adjusted/unadjusted price variants, corporate-action history.
3. `features/` versioned causal feature sets, each with source watermark, computation timestamp and `available_at`.
4. SQL catalog (SQLite MVP, Postgres production): provider/source metadata, snapshots, licences, quality issues, training runs, model registry, orders, fills, costs, audit.
5. `documents/` timestamped filings, research and model postmortems. RAG embeddings in pgvector **only after document ingestion is implemented**; vector similarity is filtered by `published_at <= decision_time` and `available_at <= decision_time`.

## Data acquisition
Vendor is undecided. A legitimate provider adapter must implement `fetch_bars(symbol, start, end, interval)`, pagination/retries, quotas, timestamp semantics, adjustments and licensing. The included MVP accepts an exported vendor CSV to avoid silently using a questionable source. Never generate synthetic bars and present them as market history.

## Schema and validation
CSV MVP columns: `timestamp,symbol,open,high,low,close,volume`. Timestamp must be ISO 8601 with UTC offset; symbol nonempty; finite positive prices; `low <= open,close <= high`; nonnegative volume; unique (symbol,timestamp). Daily data only for executable MVP; production adds `interval,venue,provider,received_at,available_at,currency,adjustment_basis`.

## Leakage and causal retrieval
- No feature computed using bars after its decision timestamp; shift features appropriately for close-of-bar decisions.
- Corporate actions and news must be available *as known at the time*, not retroactively revised without versioning.
- For each retrieval, persist query, retrieved IDs, publication/availability times, ranking, model prompt/version, cited evidence and resulting hypothesis.
- RAG memories of failed trades are accessible for future research but must not leak into reconstructed historical decisions.

## Initial acceptance
Import genuine vendor CSV, reject bad rows, query a symbol's chronological history, calculate rolling features, freeze a snapshot hash and reproduce the same output. Only then add a scheduled vendor adapter, Parquet/DuckDB, Postgres and document RAG.
