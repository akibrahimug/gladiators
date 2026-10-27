# P01 algorithm-research agenda

[Task](../../tasks/TASK-P01-002.md) · [Source follow-ups](source-followups.md) · [Observability map](observability-map.md) · [P01 phase](../../phases/01-research-and-data-access/README.md) · [Acceptance scenarios](../../validation/acceptance-scenarios.md)

> **Reassessment, 2026-10-25:** [source-reassessment.md](source-reassessment.md) (TASK-P01-007, DEC-033) changes the data notes for H-OF3 history and H-OF6: Binance Vision trades are now Conditional (F-5b), and history and paper venues are an open G01 item (F-8). Where it changes a data note here, it takes precedence.

**Status: research evidence for G01, 2026-10-24.** This agenda frames hypotheses and baselines only:
- It selects no model, sets no threshold, runs no experiment and makes no profitability claim.
- Thresholds and the held-out design are pre-registered later: the acceptance objectives in TASK-P01-003, and the held-out evaluation in P06.
- The source's rule applies: "There is no proof of an edge until genuine unseen forward evidence" (v10 `21-ALGORITHM-RESEARCH-AND-REVERSE-ENGINEERING.md:7`).

This is the P01 deliverable "a cited algorithm-research agenda linking candidate algorithm families, reference baselines, required observations and falsifiable hypotheses to Gladiator research" (P01 README, deliverables). It covers P01 task 5.

## Basis

| Input | Use here |
| --- | --- |
| Source algorithm register `22-ALGORITHM-REGISTER.csv` (A01–A17) | Families, priorities, owners, required falsification and starting references are quoted in the tables below (column "Register"). The research funnel in file 21 (lines 11–19, steps 1–9) is the method for every candidate |
| `11-QLIB-AND-TRAINING.md:9` ("Start logistic regression, LightGBM and XGBoost") and the `06-GLADIATORS.md:9` roster | Initial predictive hypotheses |
| File 27 "Canonical signals — hypotheses to test, NOT assumed alpha" (signals 1–9, lines 22–30) | Order-flow hypotheses |
| File 27 control rules: the Arena "tests whether microstructure features beat a price-and-volume baseline **out of sample after realistic costs**" (27:75); "verify flow-based signal improves on bar-based baseline on purged, time-forward and untouched market/regime partitions; otherwise reject extra complexity" (27:90) | The null for every order-flow hypothesis |
| [Observability map](observability-map.md) and [follow-ups](source-followups.md) | Data needs and current availability |
| Research assumptions DEC-017, DEC-028 (data keys only), DEC-029 (crypto first if F-1 closes negatively), DEC-030 (personal, non-commercial), DEC-031 (no Coinbase in model research) | Feasibility |

**External papers.** Every external paper cited here is marked *(addition)*: the register names only general starting references, such as "AFML" or "Statistical learning".

**Data position.** The leading crypto candidate is Kraken:
- daily bars from SR-05, Conditional on F-4a and F-4f;
- live depth and trades from SR-02, Conditional on F-4a, with depth available only from the project's own forward capture.

Elsewhere:
- No licence-clear ETF daily source has been found (F-1 is open).
- No consolidated ETF flow is available.
- No cross-venue data is usable for model research.

**Forecast-to-position rule.** Predictive hypotheses produce forecasts, but the baselines are trading rules. Each comparison therefore uses a forecast-to-position rule that is pre-registered together with the horizon, universe, features and costs (11:12). This agenda does not set that rule.

## Reference baselines

| ID | Baseline | Definition | Source |
| --- | --- | --- | --- |
| B0 | No trade (zero edge) | Hold cash; return 0, cost 0 | Register A07 "Naive zero-edge"; 17:40 "no-trade baseline" |
| B1 | Buy and hold | Hold over the evaluation window, with entry and exit costs | *(addition)* standard reference |
| B2 | Time-series momentum | Sign of the trailing return over a pre-registered look-back | Register A07 "momentum". *(addition)* Moskowitz, Ooi & Pedersen (2012), *J. Financial Economics*, [doi:10.1016/j.jfineco.2011.11.003](https://doi.org/10.1016/j.jfineco.2011.11.003) |
| B3 | Short-term reversal | Negative sign of the trailing short-window return | Register A07 "reversal" |
| BB | Bar-based price-and-volume model, defined per order-flow hypothesis | A price-and-volume-only model at the **same venue, horizon, period and cost model** as the H-OF row it serves. Its specification is fixed and logged in the trial ledger (A04) **before** any order-flow test data is seen, and it is never chosen on the order-flow evaluation partitions (27:90 "untouched") | *(addition)* operationalisation of 27:75 and 27:90 |

## Falsifiable hypotheses — predictive (P1 families)

"Feasible" means the data each hypothesis needs is in the current candidate picture. It does not mean the hypothesis is likely to hold. Evaluation follows the [acceptance scenarios](../../validation/acceptance-scenarios.md):
- **VAL-009:** bounded fixture comparison at G05, then the held-out end-to-end comparison at G06.
- **VAL-012:** held-out evaluation with costs and fill uncertainty at G06.
- **VAL-008:** regime-shift response at G04, then G05.

| ID | Hypothesis | Null and required falsification | Register (22): family / starting reference; owner | External reference | Observations | Feasible | Evaluation |
| --- | --- | --- | --- | --- | --- | --- | --- |
| H-01 | Logistic regression on past-only daily features beats B0–B3 net of costs, through the pre-registered position rule | No improvement over the best of B0–B3 after costs and multiple-testing adjustment. A07 falsification: "benchmark against naive after all costs" | A07 Prediction baselines / Qlib; Gladiators | — | Daily bars (crypto: SR-05) | Conditional (F-4a, F-4f) for crypto; not feasible for ETFs (F-1) | VAL-009 (G05, G06); VAL-012 (G06) |
| H-02 | LightGBM (gladiator 1 "Spartacus", 06:9) beats H-01 and B0–B3 net of costs | No improvement over the best of **H-01** and B0–B3 after costs and multiple-testing adjustment (corrected 2026-10-27, PR #15 review: the null must include the logistic comparator) | A07 / Qlib; Gladiators | [Qlib](https://github.com/microsoft/qlib) (register reference) | Daily bars | As H-01 | As H-01 |
| H-03 | XGBoost (gladiator 2 "Maximus", 06:9; 11:9) beats H-01 and B0–B3 net of costs | As H-02: no improvement over the best of **H-01** and B0–B3 after costs and multiple-testing adjustment | A07 / Qlib; Gladiators | — | Daily bars | As H-01 | As H-01 |
| H-04 | Forecast probabilities stay calibrated by regime | Miscalibration beyond pre-registered bounds in any regime. A08 falsification: "calibration drift, sparse regime and small sample tests" | A08 Calibration and uncertainty / Statistical learning; Core/Judges | *(addition)* conformal diagnostics: Angelopoulos & Bates, [arXiv:2107.07511](https://arxiv.org/abs/2107.07511) | Model outputs plus regime labels | After H-01 to H-03 | VAL-009 (G05) |
| H-05 | A volatility or change-point regime filter reduces drawdown without removing net return | No drawdown reduction, or a worse net return. A10 falsification: "false alarm, delayed response and no-trade tests" | A10 Regime and change detection / Time series literature; Core/Management | *(addition)* CUSUM: Page (1954), *Biometrika* 41(1–2):100–115, [doi:10.1093/biomet/41.1-2.100](https://doi.org/10.1093/biomet/41.1-2.100) | Daily bars | As H-01 | VAL-008 (G04, G05); VAL-009 (G05); VAL-012 (G06) |
| H-06 | An ensemble adds marginal value over its best member: "Ares", the regime-aware ensemble (06:9), built by regularised stacking (A09) | No marginal utility after correlation adjustment. A09 falsification: "duplicated-model and regime-switch tests" | A09 Ensemble and diversification / Numerai principles; Core/Arena | — | Member forecasts | After H-01 to H-03 | VAL-009 (G05, G06) |

## Falsifiable hypotheses — order flow (file 27 signals 1–9)

Each H-OF*n* tests signal *n* of file 27. Every null is the source's control rule: **no improvement over the bar-based baseline BB, out of sample, after realistic costs, on purged, time-forward and untouched partitions (27:75, 27:90).** Each row adds only a signal-specific condition. Where file 27 cites no paper, the external reference is an *(addition)*; for H-OF1 it fulfils 27:22, "Implement published definitions precisely".

| ID | Hypothesis | Signal-specific condition | External reference | Observations | Feasible | Evaluation |
| --- | --- | --- | --- | --- | --- | --- |
| H-OF1 | Event-wise OFI at the best quotes adds explanatory power for short-interval mid-price changes on a crypto venue | Matched intervals; OFI defined as in the published paper | *(addition; fulfils 27:22)* Cont, Kukanov & Stoikov (2014), *J. Financial Econometrics* 12(1):47–88, [doi:10.1093/jjfinec/nbt003](https://doi.org/10.1093/jjfinec/nbt003) | Live L2 changes and trades (SR-02) | **Only after forward capture** (P02/P03); no history | VAL-009 (G05); VAL-012 (G06) |
| H-OF2 | Top-of-book queue imbalance improves next mid-move direction prediction over BB | BB at the next-mid-move horizon | *(addition)* Gould & Bonart, [arXiv:1512.03492](https://arxiv.org/abs/1512.03492) (*Market Microstructure and Liquidity*, 2016; volume per a secondary listing) | Live L2 (SR-02) | Only after forward capture | As H-OF1 |
| H-OF3 | Aggressor-signed trade notional adds information beyond BB | Daily horizon | File 27 signal 3 | Trades with aggressor side (SR-02 live; history F-4d) | Conditional: history from Binance Vision `trades` (data-access decision; DEC-036 to DEC-045, effective at the G01 pass; F-5b″); Kraken history only if F-4d closes | VAL-009 (G05); **VAL-012 (G06) held-out net-cost evaluation against BB** (added 2026-10-27, PR #15 review) |
| H-OF4 | Cancellation, addition and execution ratios separate fleeting from durable depth | Per-order lifecycles | File 27 signal 4 | Per-order (L3) events | **Not testable as stated.** Kraken L2 gives level changes. Kraken's [level3 channel](https://docs.kraken.com/api/docs/websocket-v2/level3) (read 2026-10-24) gives per-order `add`/`modify`/`delete` events with `order_id`, but "The `level3` channel is authenticated (i.e. it requires an API token to subscribe)". That token needs a Kraken exchange-account key, which DEC-028 excludes (the coordinator's reading). Only a level-based proxy is possible | Recorded gap |
| H-OF5 | Price impact and resilience after signed flow differ by regime and add information beyond BB | Per-regime breakdown (27:75) | File 27 signal 5 | Live L2 and trades plus regimes | Only after forward capture | VAL-009 (G05); VAL-012 (G06) |
| H-OF6 | Cross-venue divergence leads the slower venue | After clock and fee alignment | File 27 signal 6 | Two or more venues usable for model research | **Blocked:** Coinbase is out (DEC-031) and Binance is Unresolved (F-5) | Deferred |
| H-OF7 | ETF auction imbalance or primary-market flows inform the next session | By publication time | File 27 signal 7 | NOII (paid); issuer holdings | NOII is blocked under £0. The issuer-holdings route is Unresolved (F-3) | Deferred |
| H-OF8 | Funding, basis, open interest and liquidations improve spot risk forecasts | Context only | File 27 signal 8 | Derivatives context (F-3 Unresolved) | Unresolved | VAL-009 (G05); VAL-012 (G06) held-out net-cost evaluation against BB; both only if H-OF8 returns to scope (DEC-043) and data closes |
| H-OF9 | On-chain exchange flows add weak contextual information | Context only | File 27 signal 9 | On-chain data plus attribution. Coin Metrics Community is Documented for DEC-030 use but has limited history; whether the community tier includes exchange-flow metrics is unverified | Partly; coverage is unverified | VAL-009 (G05); VAL-012 (G06) held-out net-cost evaluation against BB; both only if data closes |

## Correctness infrastructure (P0 families)

"P0 is correctness infrastructure, not an alpha strategy" (21:23). These families are prerequisites for evaluating any hypothesis above.

| Family | Register (22): starting reference; owner; required falsification | What must hold | External or additional reference | Where verified |
| --- | --- | --- | --- | --- |
| A01 Arithmetic, ledger and event invariants | LEAN architecture; Core/Execution/Judges; "property tests, independent ledger, replay, conservation" | `cash + marked holdings - liabilities = equity` reconciled on every event (21:54) | [LEAN](https://github.com/QuantConnect/Lean) as a comparison oracle (21:59) | P03 (VAL-006) |
| A02 Clock and market microstructure | LEAN; Data/Execution; "DST, holiday, stale quote, out-of-order event fixtures" | UTC event time and calendars | — | P02–P03 (VAL-003/004) |
| A03 Purged time-series validation | AFML; Judges/Training; "no overlap proofs and synthetic leakage trap" | No overlap between training and test label intervals; embargo where dependence persists | Source-cited implementation (21:61): [mlfinlab](https://github.com/hudson-and-thames/mlfinlab/blob/master/mlfinlab/cross_validation/cross_validation.py), "reconstruct independently and verify leakage traps" | VAL-009 (G05); VAL-012 (G06) |
| A04 Multiple testing correction | Bailey & Lopez de Prado; Arena/Judges; "noise-only tournament false positive test" | Trial ledger; deflated Sharpe; PBO | Deflated Sharpe ratio [doi:10.3905/JPM.2014.40.5.094](https://doi.org/10.3905/JPM.2014.40.5.094) (source-cited, 21:62; resolves to *J. Portfolio Management* 40(5), behind a login). *(addition)* PBO: Bailey, Borwein, López de Prado & Zhu, *J. Computational Finance* 20(4), [doi:10.21314/JCF.2016.322](https://doi.org/10.21314/JCF.2016.322) | VAL-009 (G05); VAL-012 (G06) |
| A05 Execution and cost modelling | LEAN; Execution/Core; "bid/ask crossing, gap, liquidity, no fill stress" | Buy at the feasible ask and sell at the feasible bid; fees; no assumed fills (21:53) | — | P06 (VAL-012) |
| A06 Risk and allocation | Portfolio risk literature; Gatekeeper/Core; "gap beyond stop, correlated positions, stale account" | The sizing formula (21:49); a stop does not bound loss | — | P05 (VAL-011) |
| A15 Crypto market specifics | Exchange docs; Data/Execution; "cross-venue contamination, zero-trade bars, tick sizes" | 24/7 sessions; zero-trade intervals (L-025) | SR-02, SR-05 | P02–P03 (VAL-004) |
| A16 ETF market specifics | LEAN; Data/Execution; "total-return vs tradable price reconciliation" | Splits, dividends and session hours | — | Deferred with ETFs (F-1, F-2) |

## Later families

| Family | Register (22): starting reference; owner; priority; required falsification | Status | Reason |
| --- | --- | --- | --- |
| A11 Portfolio optimisation | LEAN / HRP; Core; P2; "covariance instability, fees and tiny-account feasibility" | Deferred | "tiny-account feasibility" (A11), and the universe is not fixed. *(addition)* HRP: López de Prado (2016), *J. Portfolio Management* 42(4):59–69, [doi:10.3905/jpm.2016.42.4.059](https://doi.org/10.3905/jpm.2016.42.4.059) |
| A12 Order execution algorithms | LEAN; Execution; P2; "partial fills and adverse selection tests" | Deferred | Beyond the P06 simulation scope |
| A13 Reinforcement learning | FinRL; Gladiators; P3; "offline-to-forward generalisation; fail closed" | Deferred | "Avoid starting with reinforcement learning or large LLMs before accounting and data are trustworthy" (21:23) |
| A14 Automated factor discovery | RD-Agent; Management/Training; P2; "sandbox, trials budget, untouched holdout" | Deferred | Needs a sandbox, a trials budget and an untouched holdout (A14) |
| A17 LLM research governance | LLM security; Research/Management; P1; "fabricated citation, malicious issue, no-execution tests" | Kept as a governance requirement (REQ-013, REQ-014), not a forecasting hypothesis | Phase 1 has "no mandatory LLM or GPU" (11:15) and "no cloud models" (17:11) |

## Evaluation protocol links

These are recorded here and decided elsewhere:
- pre-registration of horizon, universe, features, costs and the forecast-to-position rule before any fit (11:12);
- a trial ledger (A04);
- chronological walk-forward with purging (A03), and an untouched holdout (21:17, step 7);
- promotion only with Judge sign-off and the Gatekeeper veto (21:19, step 9).

Thresholds, holdout dates and bounds belong to TASK-P01-003 and P06.

## Gaps this agenda records for G01

1. H-OF1, H-OF2 and H-OF5 depend on forward capture. H-OF3 does too until F-4d closes. None of their evidence can exist before P02 and P03 run.
2. H-OF4 is not testable without Kraken's authenticated level3 channel, whose account key DEC-028 excludes (the coordinator's reading of DEC-028). H-OF6 has no second venue usable for model research. H-OF7 is blocked under £0, except for the unresolved issuer-holdings route.
3. The ETF variants of H-01 to H-06 wait on F-1 and F-2; otherwise DEC-029 applies.
4. Only the predictive hypotheses can be tested on history today. That applies to crypto daily bars, Conditional on F-4a and F-4f.
