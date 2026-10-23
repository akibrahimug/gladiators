# System map and build order

Status: design specification; not a claim of implemented functionality.

## Mission and boundary
Build a reproducible, terminal-only trading research engine. Core is the deterministic decision kernel, **not** the arena, an LLM, or the broker. The system may run without any LLM. £500 is simulated initial equity; £10,000 is an aspiration, not an optimisation target.

## Dataflow
`Sources -> Connectors -> Raw vault -> Verification/Cleaning -> Point-in-time snapshots -> Qlib/features -> Gladiators -> Forecast registry -> Core kernel -> Gatekeeper -> Paper broker -> Reconciled ledger -> Evidence -> Judges/Arena -> Management -> next challenger training`.
RAG branches from document/experiment storage into research gladiators; numeric market data goes directly to feature/model pipelines. Transport carries typed events; it does not make trading decisions.

## Ownership and ordering
1. DATA, CONNECTORS and TRANSPORT produce immutable causal snapshots.
2. FEATURES and TRAINING generate versioned calibrated forecasts.
3. CORE observes, reconciles, discovers, evaluates, sizes and issues intents.
4. GATEKEEPER alone approves intents; EXECUTION simulates or routes permitted orders.
5. LEDGER reconciles fills and outcomes; JUDGES evaluate; ARENA conducts fair comparisons.
6. MANAGEMENT schedules, budgets and promotes; CODE-OF-CONDUCT governs all.

## Phases
P0 repository/contracts/fixtures; P1 free data+validation; P2 Qlib and 3 baselines; P3 decision kernel+simulation; P4 ten gladiators+arena; P5 RAG/local LLM experiments; P6 forward paper; P7 optional cloud challengers with explicit cost approval; P8 optional live gate after separate legal/technical approval. Each phase has tests and must pass before the next.

## Interface rule
Everything is importable Python with CLI wrappers. The kernel must accept a recorded JSON snapshot and return deterministic JSON/text with no network access. No frontend.

## Operational invariants
- Phase 1: zero paid external services, no live orders, no dashboard; terminal text/number output only. Use local files and explicit, free, permitted data sources. Network pulls require explicit invocation.
- Every artifact includes `run_id`, UTC `as_of`, immutable `dataset_hash`, `code_version`, `config_hash`, and relevant `model_version`.
- Reject missing, stale, future-dated, unlicensed or unverified inputs; `ABSTAIN` is valid and preferable to guessing.
- Do not infer profitability from backtests. Keep chronological holdouts, realistic costs, and independent forward-paper validation.
- No LLM, gladiator, or management agent may modify gatekeeper limits or access live broker credentials.

## Market-intelligence layer (v0.9 amendment)
[24 — Market awareness](24-MARKET-AWARENESS-AND-REGIME-DETECTION.md) is an independent observation/fusion function between validated data and decisions. It provides point-in-time event/regime/coverage snapshots **to both** the Core and Gatekeeper. External research/news and direct market-shock sensors are independent; the latter never depend on LLM commentary. Coverage unknown/missing is explicit; the source register is [25](25-MARKET-INTELLIGENCE-SOURCE-REGISTER.csv).
