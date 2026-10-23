# GLADIATOR — Competitive Intelligence and Public Quant Research

Status: research design / source discovery, 2026-10-22. No proprietary strategy, live fund return, or validated edge has been obtained.

## Mandate
Acquire *lawfully public and permitted* research, papers, factor return series, official documentation, public source code, benchmarks, issue discussions, release notes and competition methodology. Improve the Core, Judges, Management, Arena and research Gladiators. Do not represent reported results as replicated results.

## Priority source register

| Priority | Source | Verified public material | What it improves | Boundary |
|---|---|---|---|---|
| P0 | Numerai | Official docs, datasets, Signals Supernova v3, NumerAPI, example scripts | Arena scoring, era splits, feature neutralisation, model diversity, prediction-versus-trading metrics | Obfuscated tournament features are not ETF OHLCV; read dataset terms before ingestion |
| P0 | AQR | Public research library and daily/monthly factor return series (QMJ, BAB, momentum, value) | Judges' benchmark baselines, factor exposure diagnostics, robustness and portfolio attribution | Academic hypothetical returns are NOT AQR fund trading returns; dataset-specific terms apply |
| P0 | Man AHL | Public research and descriptions of systematic testing and competing execution routes | Separate execution competition, shared data provenance, reproducible research | No proprietary trade feed implied |
| P1 | WorldQuant BRAIN | Public competition methodology and descriptions of alpha simulation | Alpha hypothesis generation, research process, anti-overfit tests | Logged-in platform content and user-generated alphas are not automatically reusable; no unauthorised scraping |
| P1 | Two Sigma | Public papers, engineering writing, OSS where explicitly licensed | Data engineering, research reproducibility, operational governance | No claim to proprietary model performance |
| P1 | Quant trading open-source repositories | Licensed code, documented examples, open issues, PRs | Defect registry, independent reproductions, model challenger design | Code license and data license assessed separately |

## Specific findings to adopt

1. Numerai's Signals v3.0 Supernova (August 2026) supplies training/validation/live partitions, neutralisation data, and 20-/60-day targets. Learn from its scoring design, but keep GLADIATOR's 15-minute/1-hour ETF and crypto evaluation separate.
2. Numerai official `numerapi` supports NumerAI, Signals and Crypto API clients. The datasets may be useful for independent model-method validation; not as substitutes for exchange-specific tradable candles.
3. AQR publishes factor returns including daily Quality Minus Junk and Betting Against Beta and monthly Value and Momentum. Compare Core decisions to factor baselines and inspect inadvertent factor bets. Respect each spreadsheet's terms.
4. Man AHL describes ongoing competition among proprietary, third-party and manual execution routes. GLADIATOR must separately score forecast accuracy, portfolio construction, and execution quality.
5. WorldQuant BRAIN demonstrates large-scale alpha experimentation. Require multiple-testing control, holdout isolation, hypothesis registry and research-budget controls.
6. Popular open-source LLM-trading demos often explicitly disclaim live trading. Their reported backtests do not prove profitable live execution.

## Source acquisition policy

- Prefer official published API, RSS, dataset download, GitHub releases/issues, research-library download and permissive public documentation over crawling HTML.
- Before collecting: identify `publisher`, `canonical_url`, `license_or_terms_url`, `access_method`, `robots_and_rate_limit`, `allowed_purpose`, `attribution`, `publication_time`, `observed_time`, `content_hash`.
- Robots compliance is necessary but not sufficient: enforce terms, copyright, paywalls, login boundaries, API restrictions, privacy and request limits. No authentication bypass, scraping private dashboards or harvesting identifiable users.
- Store an immutable source snapshot and a normalised extract. Use deduplication, revision history, expiry/recheck windows and manual review for ambiguous rights.
- Do not execute downloaded scripts automatically. Review licenses and security, pin commits, sandbox research code and disable broker/network credentials.
- Public research text belongs in RAG engineering/research memory with citations and publication timestamps. Only numeric datasets with approved provenance and point-in-time semantics can enter training; no retrospective information leaks.
- Record all hypotheses generated from published papers in a research registry before evaluation. Multiple variants count as multiple tests. Freeze holdouts; use walk-forward and genuine forward paper trials.

## Governance contracts

### Intelligence finding
```
finding_id, source_url, publisher, published_at, observed_at,
license_status, evidence_class, claim, limitations,
affected_component, proposed_change, reproduction_plan,
reviewer, disposition, linked_regression_test
```
Evidence classes: official documentation; downloadable dataset; peer-reviewed study; working paper; marketing claim; third-party summary; reported GitHub issue; locally reproduced observation.

### Management
Weekly triage of new source changes; monthly re-evaluation of source permissions and benchmark revisions; record accepted/rejected changes in ADRs. No automatic promotion based on vendor claims.

### Judges
Distinguish *claimed*, *independently reproduced*, and *forward verified*. Benchmark against naive baselines, buy-and-hold, risk-free/cash, market beta, momentum, volatility and available factor series as appropriate. Track multiple comparisons, costs, turnover, drawdown and uncertainty.

### Gladiators
Use public research for hypothesis generation and feature ideas; forbid copying unknown proprietary strategies or learning from leaked evaluation targets. LLM agents may propose tests but cannot modify Judges, Gatekeeper or immutable datasets.

### Arena
Separate model skill tournaments from execution/portfolio tournaments. Test incremental information relative to existing ensemble; reject redundant challengers with no demonstrable marginal benefit.

## Suggested CLI (not yet implemented)
```
gladiator intel sources
 gladiator intel discover --source numerai
 gladiator intel fetch --source aqr --dataset qmj-daily
 gladiator intel audit --finding <id>
 gladiator intel propose --finding <id>
 gladiator intel review --proposal <id>
```

## Pre-implementation acceptance gates

- Every ingested artifact has a canonical URL, collection timestamp, rights status and content checksum.
- A denied/unknown-rights source cannot flow into automated training or redistribution.
- Source revisions never overwrite prior snapshots.
- AQR benchmark imports retain frequencies, currency, gross/net conventions and portfolio definitions.
- Numerai train/validation/round identifiers are respected and future targets are never accessible to the prediction path.
- A marketing performance claim cannot be promoted to verified alpha.
- Each accepted external insight creates an independently testable change, regression test and rollback path.

## Primary references (verified 2026-10-22)

- https://docs.numer.ai/
- https://signals.numer.ai/data
- https://docs.numer.ai/numerai-tournament/api
- https://github.com/numerai/example-scripts
- https://www.aqr.com/Insights/Datasets
- https://www.aqr.com/Insights/Datasets/About-the-AQR-Data-Library
- https://www.aqr.com/Insights/Datasets/An-Academic-Quality-Data-Library-for-Practitioners
- https://www.man.com/ahl
- https://www.worldquant.com/brain/
- https://github.com/WallStreetPete/awesome-open-source-trading (third-party research map; verify at primary source)

## Open questions

- Dataset-specific license review before actual downloads and downstream redistribution.
- Reliable publication-time reconstruction for historical documents.
- Benchmark mapping from AQR long/short factor portfolios to GLADIATOR's small long-only ETF account.
- Whether Numerai Crypto data and labels represent tradable exchange-specific prices and costs; do not assume so.
- Whether published fund-level performance has independently audited details; not established here.
