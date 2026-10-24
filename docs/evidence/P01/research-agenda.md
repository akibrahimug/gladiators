# P01 algorithm-research agenda

[Task](../../tasks/TASK-P01-002.md) · [Source follow-ups](source-followups.md) · [Observability map](observability-map.md) · [P01 phase](../../phases/01-research-and-data-access/README.md) · [Acceptance scenarios](../../validation/acceptance-scenarios.md)

**Status: research evidence for G01, 2026-10-24.**
- It frames hypotheses and baselines. It selects no model, sets no threshold, runs no experiment and makes no profitability claim.
- Thresholds and the held-out design are pre-registered later: acceptance objectives in TASK-P01-003, held-out evaluation in P06.
- The source's own rule applies: "There is no proof of an edge until genuine unseen forward evidence" (v10 `21-ALGORITHM-RESEARCH-AND-REVERSE-ENGINEERING.md:7`).

This is the P01 deliverable "a cited algorithm-research agenda linking candidate algorithm families, reference baselines, required observations and falsifiable hypotheses to Gladiator research" (P01 README, deliverables). It covers P01 task 5.

## Basis

| Input | Use here |
| --- | --- |
| Source algorithm register `22-ALGORITHM-REGISTER.csv` (A01–A17) and the research funnel and dossier in file 21 | Families, priorities, owners, falsification and starting references are taken as written. The funnel (file 21 "Research funnel", steps 1–9) is the method for every candidate |
| `11-QLIB-AND-TRAINING.md:9` pipeline ("Start logistic regression, LightGBM and XGBoost") and `06-GLADIATORS.md:9` roster | Initial predictive baselines |
| File 27 "Canonical signals — hypotheses to test, NOT assumed alpha" (signals 1–9) | Order-flow hypotheses |
| [Observability map](observability-map.md) and [follow-ups](source-followups.md) | The data each hypothesis needs, and whether that data is available under the current assumptions |
| Research assumptions: DEC-017 defaults, DEC-028 (data keys only), DEC-029 (crypto first if F-1 closes negatively), DEC-030 (personal, non-commercial), DEC-031 (no Coinbase in model research) | Feasibility column |

**Data position used below.** The leading crypto candidate is Kraken: daily bars from SR-05 and live depth and trades from SR-02. Both are Conditional on F-4a and F-4f. Live depth exists only from the project's own forward capture. No licence-clear ETF daily source has been found yet (F-1 open). No consolidated ETF flow is available. Cross-venue model data is not available.

## Reference baselines

Every candidate is compared, net of costs, with all of these on the same data, horizon and cost model. This follows A07, "benchmark against naive after all costs".

| ID | Baseline | Definition | Source |
| --- | --- | --- | --- |
| B0 | No trade (zero edge) | Hold cash; return 0, cost 0 | A07 "Naive zero-edge"; 17:40 "no-trade baseline" |
| B1 | Buy and hold | Hold the instrument over the evaluation window, with entry and exit costs | Standard reference (an addition to the source list) |
| B2 | Time-series momentum | Sign of the trailing return over a pre-registered look-back | A07 "momentum"; Moskowitz, Ooi & Pedersen (2012), *J. Financial Economics*, [doi:10.1016/j.jfineco.2011.11.003](https://doi.org/10.1016/j.jfineco.2011.11.003) |
| B3 | Short-term reversal | Negative sign of the trailing short-window return | A07 "reversal" |

## Falsifiable hypotheses

Each hypothesis states a null, the data it needs and where it is evaluated.
- P05: bounded fixture comparison (VAL-009).
- P06: held-out, end-to-end evaluation with costs and fill uncertainty (VAL-012).

"Feasible now" means the data it needs is in the current candidate picture. It does not mean the hypothesis is likely to hold.

### Predictive (P1 families)

| ID | Hypothesis (alternative) | Null | Family / starting reference | Observations needed | Feasible now | Evaluation |
| --- | --- | --- | --- | --- | --- | --- |
| H-01 | A logistic regression on past-only daily features gives calibrated direction probabilities that beat B0–B3 net of costs | No improvement over the best of B0–B3 after costs and multiple-testing adjustment | A07; `11-QLIB-AND-TRAINING.md:9` | Daily bars (crypto: SR-05) | Yes, for crypto (Conditional F-4a); no for ETFs (F-1) | P05 VAL-009; P06 VAL-012 |
| H-02 | LightGBM (gladiator 1 "Spartacus") beats H-01 and B0–B3 net of costs | Same | A07; 06:9; [Qlib](https://github.com/microsoft/qlib) | Daily bars | As H-01 | As H-01 |
| H-03 | XGBoost (gladiator 2 "Maximus") beats H-01 and B0–B3 net of costs | Same | 06:9; 11:9 | Daily bars | As H-01 | As H-01 |
| H-04 | Forecast probabilities are calibrated by regime (reliability and Brier score within pre-set bounds) | Miscalibration exceeds the bounds in at least one regime | A08; conformal diagnostics: Angelopoulos & Bates, [arXiv:2107.07511](https://arxiv.org/abs/2107.07511) | Model outputs plus regime labels (H-05) | Once H-01 to H-03 exist | P05 (Judges, CMP-08) |
| H-05 | A volatility or change-point regime filter reduces drawdown without removing net return relative to the unfiltered model | No drawdown reduction, or net return worse | A10; CUSUM: Page (1954), *Biometrika* 41(1–2):100–115, [doi:10.1093/biomet/41.1-2.100](https://doi.org/10.1093/biomet/41.1-2.100) | Daily bars | As H-01 | P05; P06 (VAL-008 regime shift) |
| H-06 | A regularised ensemble ("Ares", 06:9) adds marginal value over its best member | No marginal utility after correlation adjustment | A09 | Member forecasts | After H-01 to H-03 | P05; P06 |

### Order flow (file 27 signals)

Each signal maps to the order-flow hypothesis with the same number: signal 1 is H-OF1, and so on. Cross-venue divergence is signal 6 in file 27; here it is H-OF6.

| ID | Hypothesis | Null | Starting reference | Observations needed | Feasible now | Evaluation |
| --- | --- | --- | --- | --- | --- | --- |
| H-OF1 | Event-wise order-flow imbalance (OFI) at the best quotes explains short-interval mid-price changes on a crypto venue | No explanatory power beyond B0 over matched intervals | Cont, Kukanov & Stoikov (2014), *J. Financial Econometrics* 12(1):47–88, [doi:10.1093/jjfinec/nbt003](https://doi.org/10.1093/jjfinec/nbt003) | Live L2 depth changes and trades (SR-02) | **Only after forward capture** (P02/P03); no history | P04 feature; P05; P06 |
| H-OF2 | Top-of-book queue imbalance predicts the direction of the next mid-price move | No improvement over a null direction model | Gould & Bonart, [arXiv:1512.03492](https://arxiv.org/abs/1512.03492) (*Market Microstructure and Liquidity*, 2016; volume per secondary listing) | Live L2 (SR-02) | Only after forward capture | As H-OF1 |
| H-OF3 | Aggressor-signed trade notional carries information beyond price returns at the daily horizon | No incremental information | File 27 signal 3 | Trades with aggressor side (SR-02 live; history F-4d) | Live only; history unresolved | P04; P05 |
| H-OF4 | Cancellation, addition and execution ratios distinguish fleeting from durable depth | No difference in subsequent execution | File 27 signal 4 | Per-order events | **Not testable as stated:** Kraken L2 gives level changes, not order lifecycles. Only a level-based proxy is possible | Recorded gap |
| H-OF5 | Price impact and resilience after signed flow differ by regime | No regime difference | File 27 signal 5 | Live L2 and trades plus regimes | Only after forward capture | P05; P06 |
| H-OF6 | Cross-venue price and flow divergence leads the slower venue | No lead after aligning clocks and fees | File 27 signal 6 | Two or more venues usable for model research | **Blocked:** Coinbase is out (DEC-031) and Binance is unresolved (F-5) | Deferred |
| H-OF7 | ETF auction imbalance or primary-market flows inform the next session | No information by publication time | File 27 signal 7 | NOII (paid); issuer holdings (unresolved) | **Blocked** under £0 | Deferred |
| H-OF8 | Crypto funding, basis, open interest and liquidations act as stress indicators for spot risk | No improvement in risk forecasts | File 27 signal 8 | Derivatives context (F-3 Unresolved) | Unresolved | P04; P05 (context only) |
| H-OF9 | On-chain exchange flows give a weak contextual signal | No incremental information | File 27 signal 9 | On-chain data plus attribution (Coin Metrics Community Documented for DEC-030 use but limited; RPC unresolved) | Partly (limited history) | P04 context; P05 |

## Correctness infrastructure (P0 families)

The source puts these first: "P0 is correctness infrastructure, not an alpha strategy" (21:23). They are not hypotheses about returns. They are prerequisites that the evaluation of any hypothesis above depends on.

| Family | What must hold | Starting reference | Where verified |
| --- | --- | --- | --- |
| A01 Arithmetic, ledger and event invariants | `cash + marked holdings - liabilities = equity` reconciled on every event (21:54) | [LEAN](https://github.com/QuantConnect/Lean) as comparison oracle (21:59) | P03 (CMP-04; VAL-006) |
| A02 Clock and microstructure | UTC event time, calendars, stale-quote and out-of-order fixtures | LEAN | P02–P03 (VAL-003/004) |
| A03 Purged time-series validation | No train and test label-interval overlap; embargo where dependence persists | Purged and embargoed CV, as cited by the source ([mlfinlab](https://github.com/hudson-and-thames/mlfinlab/blob/master/mlfinlab/cross_validation/cross_validation.py)); reconstruct independently (21:13) | P05/P06 (VAL-013) |
| A04 Multiple-testing correction | Trial ledger; deflated Sharpe; PBO; a noise-only tournament must yield no false positive | Deflated Sharpe ratio: [doi:10.3905/JPM.2014.40.5.094](https://doi.org/10.3905/JPM.2014.40.5.094) (as cited by the source; this DOI resolves to *J. Portfolio Management* 40(5), behind a login). PBO: Bailey, Borwein, López de Prado & Zhu, *J. Computational Finance* 20(4), [doi:10.21314/JCF.2016.322](https://doi.org/10.21314/JCF.2016.322) | P05 Arena/Judges; P06 |
| A05 Execution and cost modelling | Buy at the feasible ask and sell at the feasible bid; fees; no assumed fills (21:53) | LEAN | P06 (VAL-012) |
| A06 Risk and allocation | Sizing formula (21:49); a stop does not bound loss | Source formula | P05 Gatekeeper (VAL-011) |
| A15 Crypto specifics | 24/7 sessions, zero-trade intervals (L-025), no cross-venue contamination | Exchange docs (SR-02, SR-05) | P02–P03 |
| A16 ETF specifics | Splits, dividends, session hours, total-return versus tradable-price reconciliation | LEAN | Deferred with ETFs (F-1, F-2) |

## Later families (P2, P3, and the P1 governance family)

| Family | Status in this agenda | Reason |
| --- | --- | --- |
| A11 Portfolio optimisation (HRP: López de Prado (2016), *J. Portfolio Management* 42(4):59–69, [doi:10.3905/jpm.2016.42.4.059](https://doi.org/10.3905/jpm.2016.42.4.059)) | Deferred | P2. The source requires "tiny-account feasibility" (A11), and the universe is not yet fixed |
| A12 Execution algorithms (TWAP, VWAP) | Deferred | P2; paper or live execution is beyond P06 simulation scope |
| A13 Reinforcement learning (FinRL) | Deferred | P3. "Avoid starting with reinforcement learning or large LLMs before accounting and data are trustworthy" (21:23) |
| A14 Automated factor discovery (RD-Agent) | Deferred | P2; needs a sandbox and an untouched holdout (A14) |
| A17 LLM research governance | Kept as a governance requirement (REQ-013, REQ-014), not a forecasting hypothesis | P1 governance; no LLM in the £0 phase (11:15) |

## Evaluation protocol links

These items are recorded here and decided elsewhere:
- Pre-registration of horizon, universe, features and costs before any fit (11:12).
- A trial ledger for every variant (A04).
- Chronological walk-forward with purging (A03), and an untouched holdout (21:17, step 7).
- Promotion only with Judge sign-off and the Gatekeeper's veto (21:19, step 9).

Thresholds, holdout dates and acceptance bounds belong to TASK-P01-003 (objectives) and P06 (held-out pre-registration). None is set here.

## Gaps this agenda records for G01

1. All order-flow hypotheses (H-OF1, H-OF2, H-OF5) depend on forward capture, so their evidence cannot exist before P02 and P03 run.
2. H-OF4 is not testable on L2 data, H-OF6 has no second venue usable for model research, and H-OF7 is blocked under £0.
3. The ETF variants of H-01 to H-06 wait on F-1 and F-2, or DEC-029 applies.
4. The predictive hypotheses are the only ones testable on history today, for crypto daily bars, subject to F-4a and F-4f.
