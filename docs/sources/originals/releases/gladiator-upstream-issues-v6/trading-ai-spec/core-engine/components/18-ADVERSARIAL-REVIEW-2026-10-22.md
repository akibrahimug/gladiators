# GLADIATOR v0.5 — adversarial design review and research gate

Date: 2026-10-22. Status: **design review, not empirical model validation or external AI peer review**.

## Review method and honesty boundary
Reviewed the existing v0.4 Markdown components for architectural consistency, conducted adversarial tabletop reasoning, and checked primary-source Qlib/Binance/Kraken documentation. No external LLM was invoked and no other AI's independent opinion is claimed. The `audit/spec_audit.py` tool checks documentation invariants, not financial validity.

## Major findings and disposition
| Severity | Finding | Impact | Resolution | Status |
|---|---|---|---|---|
| CRITICAL | No proven, licensed, point-in-time ETF dataset | Cannot certify ETF research | Source approval and coverage gate; daily-only until verified | OPEN |
| CRITICAL | No actual integrated core execution/QLib training run | Cannot claim engine works | Explicit runtime acceptance gates | OPEN |
| CRITICAL | Repeated model search can contaminate holdout | False discoveries promoted | Research/validation/sealed test/forward paper separation, trial registry | SPEC UPDATED |
| HIGH | Same OHLC bar can hit both TP and SL | Optimistic backtest P&L | Conservative ambiguity policy and event ordering | SPEC UPDATED |
| HIGH | Predicting positive return is not first-passage TP probability | Invalid stop/target EV | Explicit target and path-dependent forecast contracts | SPEC UPDATED |
| HIGH | Crypto and ETFs have incompatible calendars/precision | Missing or fictional bars | Separate venue profiles, bar semantics and timestamp precision | SPEC UPDATED |
| HIGH | Qlib recorder artifacts can execute code when loaded | Supply-chain/code-execution exposure | Pin and validate v0.9.8 artifact trust semantics | SPEC UPDATED |
| HIGH | Broker loss caps based only on stop price understate gap risk | Loss exceeds planned £2.50–£5 | Stressed-loss sizing and gap simulations | SPEC UPDATED |
| HIGH | LLM peer review may sound independent without being so | False assurance | External critique provenance and dissent register | OPEN |
| MEDIUM | Ten gladiators can share one correlated signal | Inflated evidence | Track lineage, correlation, effective sample size | SPEC UPDATED |
| MEDIUM | Free data might not permit automated/redistributable use | Operational/legal blockage | Provider rights approval before ingestion | OPEN |
| MEDIUM | Qlib metric bug reports not reproduced | Misleading performance | Independent accounting/metric reference fixtures | OPEN |

## Research updates verified against primary sources
1. Qlib release list includes v0.9.8 with security hardening around executable recorder artifact loading, feature parsing and trusted local imports: https://github.com/microsoft/qlib/releases . Validate installed version before adopting syntax.
2. Qlib supports converting user-provided CSV/Parquet into Qlib format: https://github.com/microsoft/qlib/blob/main/docs/component/data.rst . This supports canonical Parquet independent of Qlib.
3. Binance spot public data timestamps use microseconds from 2025-01-01: https://github.com/binance/binance-public-data/blob/master/README.md .
4. Kraken downloadable OHLCVT archives omit bars for intervals with no trades and publish archive/checksum guidance: https://support.kraken.com/in/articles/360047124832-downloadable-historical-ohlcvt-open-high-low-close-volume-trades-data .

## Adversarial review: counterarguments to our own design
**Critic A — Quant research:** Qlib offers research infrastructure, not predictive alpha. A collection of models trained on the same weak OHLCV inputs may create the illusion of diversity. **Response:** mandate simple benchmarks, ablation studies and feature-level correlation audits.

**Critic B — Market microstructure:** A backtest based on 15-minute candles cannot know queue position, exact spread or whether stop and target were hit first. **Response:** separate bar-based research from execution-grade simulation, apply pessimistic fills and prohibit false precision.

**Critic C — Statistical validity:** Choosing the best of ten (and then hundreds of automatically generated) challengers inflates apparent performance. **Response:** trial ledger, multiple-comparison controls, sealed test, forward paper, and no automatic champion.

**Critic D — Systems engineering:** A self-improving agent can degrade a stable production model or edit its own reward function. **Response:** immutable risk policy, frozen champion, challenger-only training, signed promotion and rollback.

**Critic E — Economics:** On £500, fixed costs and minimum commissions can overwhelm any plausible edge. **Response:** £0 paid-service phase, track expected costs per trade, allow zero trades and keep live off.

These are **internal adversarial critiques authored in this review**, not independent external model outputs.

## Formal external-model peer-review protocol (not yet executed)
- Freeze the same spec bundle, date, version hash, evaluation rubric and relevant source links.
- Submit independently to at least two genuinely separate model providers or research reviewers; no shared answer or sequential priming.
- Ask each to identify fatal flaws, falsifiable assumptions, missing tests, unsupported model claims, data-rights problems and cheapest safe alternatives. Require evidence URLs and severity.
- Preserve raw outputs, model IDs, dates, costs, prompts and hashes; redact secrets. Do not silently merge critiques.
- Have a third pass reconcile disagreements; author a disposition register with ACCEPT/REJECT/DEFER and justification.
- Re-run design audit and empirical fixtures after changes. External review is advisory, not a substitute for reproducible tests.

## Release gates before implementation
G0: Complete architecture, invariants, threat model, and acceptance cases.
G1: Source licence and dataset checksums; verified sample and as-of provenance.
G2: Executable independent ledger and deterministic event replay; adversarial fills.
G3: Qlib baseline and alternative model train/evaluate reproducibly; no future leakage.
G4: Ten actual challengers, robust out-of-sample comparisons and abstention.
G5: Forward paper with realistic costs and model-drift monitoring.
G6: Separately approved live readiness, never inferred from previous gates.

## Remaining blocker list
- Provider rights and ETF intraday depth not established.
- No runnable integrated kernel, arena, independent judges, or gatekeeper proven.
- No external AI peer review yet performed.
- No empirical alpha, live execution readiness or credible £10k timeline established.
