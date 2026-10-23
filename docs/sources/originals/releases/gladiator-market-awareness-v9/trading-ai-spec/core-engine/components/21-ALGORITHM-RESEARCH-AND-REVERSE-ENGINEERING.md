# 21 — Algorithm research and independent reconstruction standard

**Status:** proposed research protocol, NOT an implemented or certified trading system. **Purpose:** systematically inspect published, standard and open-source algorithms, independently reconstruct their behaviour, and accept only evidence-backed adaptations for US ETFs and spot crypto.

## Non-negotiable objective

Minimise **preventable implementation, accounting, data, and governance errors** through mathematical invariants and fail-closed design. Neither market forecast errors nor financial losses can approach guaranteed zero. There is no proof of an edge until genuine unseen forward evidence. Never use a backtest's apparent win rate as a safety certification.

## Research funnel (all candidates)

1. **Discover:** primary paper, author implementation, reputable alternative implementation, release history, issue tracker, license, assumptions, known failure modes. Record links, access dates, commits and claims. Avoid extracting proprietary code or bypassing restrictions.
2. **Specify:** mathematical objective, input/output types, units, clocks, numerical stability, causal availability, transaction costs, time complexity, failure cases, applicable markets, and invariants. Mark all unknowns.
3. **Independent reconstruction:** implement from published mathematics/specification, not blindly copying code. Keep upstream source in pinned read-only reference checkout; inspect only under its license. If ambiguity exists, write competing interpretations and test them.
4. **Differential testing:** compare reconstruction to at least one trusted reference on tiny hand-calculated examples, synthetic random cases and known edge cases; differences require documented explanation, not threshold loosening.
5. **Adversarial falsification:** inject corrupted data, future leakage, duplicated models, stale forecasts, slippage spikes, missing fills, halts, corporate actions, crypto venue differences, clock shifts, zero liquidity, order rejection, and correlated losses. Fail closed.
6. **Market adaptation:** preserve proven invariants while modifying calendars, price/size precision, market data provenance, fee schedules, short/long permissions and execution assumptions. US ETFs and spot crypto are distinct domains; never reuse a rule without retesting.
7. **Statistical assessment:** use chronological walk-forward and label-aware purging/embargo where applicable; reserve an untouched holdout, track every attempted variant, adjust for multiple testing, and demand forward paper evidence. The Judges—not the model developer—control admission.
8. **Peer review:** frozen versioned research packet to independent reviewers/models; store raw critiques and version metadata; distinguish actual external reviews from internally generated objections. Resolve high-severity findings with evidence, tests or explicit rejection rationale.
9. **Promote:** documented reproducibility manifest (dataset hash, code commit, dependency pins, seeds, model weights, evaluation window, costs), independent Judge signoff and Gatekeeper veto. Roll back on drift or invariant violation.

## Algorithm families and priorities

Canonical machine-readable register: [22-ALGORITHM-REGISTER.csv](22-ALGORITHM-REGISTER.csv). **P0 is correctness infrastructure**, not an alpha strategy. P1 is baseline predictive evaluation; P2 advanced methods; P3 speculative. Avoid starting with reinforcement learning or large LLMs before accounting and data are trustworthy.

| Priority | Families | Why |
|---|---|---|
| P0 | Ledger and integer tick arithmetic; exchange clocks; purged evaluation; multiple-testing corrections; execution costs; independent risk; ETF/crypto mechanics | A correct forecast can still produce a false P&L or illegal order |
| P1 | Naive and classical baselines; calibration; robust ensembles; regime monitoring; LLM evidence controls | Test whether intelligence adds measurable value |
| P2 | Portfolio optimisation; execution scheduling; autonomous factor discovery | Complexity requires sufficient validated data and market capacity |
| P3 | Offline/constrained RL | Strong distribution-shift and simulator exploitation risk |

## Canonical algorithm dossier (one dossier per candidate)

```
ID, NAME, OWNER, VERSION, UPSTREAM_COMMIT, LICENSE
PRIMARY_SOURCE, SECONDARY_SOURCE, ISSUE_LINKS, ACCESS_DATE
MATHEMATICAL_DEFINITION, ASSUMPTIONS, UNITS, TIME_SEMANTICS
INVARIANTS, REFERENCE_EXAMPLES, EDGE_CASES
RECONSTRUCTION_DIFF, TEST_FIXTURES, MUTATION_TESTS
ETF_ADAPTATION, CRYPTO_ADAPTATION, FEES_AND_FILLS
TRAIN_SPLITS, HOLDOUT_POLICY, TRIAL_COUNT, BASELINES
RESULTS_NET_OF_COSTS, FAILURE_EVIDENCE, PEER_REVIEW
STATUS: PROPOSED | RESEARCHING | REPRODUCED | REJECTED | PAPER_APPROVED
```

## Example acceptance requirements

- **Drawdown:** calculate from the first wealth observation including initial capital; compare with hand-computed path and a separate reference.
- **Risk sizing:** `floor_to_lot(min(capital_budget/price, planned_loss_budget / conservative_loss_per_unit))`; reject if any denominator, FX rate or account state is unknown. A stop does **not** bound worst-case loss.
- **Backtest time:** order can only use information available *before* its decision timestamp; orders cannot fill on an already-observed price unless the execution model establishes feasibility.
- **Purging:** for overlapping label-information intervals, remove any train observation intersecting a test interval; embargo where temporal dependencies persist.
- **Trial count:** register all searches, variants and abandoned runs; corrections like Deflated Sharpe Ratio do not replace a genuinely untouched test.
- **Execution:** buy at feasible ask and sell at feasible bid, subject to fill availability, fees and latency; never assume every limit order fills.
- **Accounting:** `cash + marked holdings - liabilities = equity`, with realised/unrealised P&L and fees reconciled independently on every event.
- **LLM:** cannot promote itself, change risk policy, declare a proof complete, execute trades, or convert its own confidence into calibrated probabilities.

## Industry-reference projects and boundaries

- **QuantConnect LEAN**: open event-driven engine and modular accounting/execution/risk architecture; excellent *comparison oracle*, not a requirement to rewrite our Python core in C#. https://github.com/QuantConnect/Lean
- **Microsoft Qlib**: research, feature, model and evaluation baseline; separately verify performance/accounting outputs. https://github.com/microsoft/qlib
- **Purged/embargo CV**: label interval-aware cross-validation; reconstruct independently and verify leakage traps. https://github.com/hudson-and-thames/mlfinlab/blob/master/mlfinlab/cross_validation/cross_validation.py
- **Deflated Sharpe Ratio**: multiple-testing and non-normality adjustment; evaluate limitations and keep trial ledger. https://doi.org/10.3905/JPM.2014.40.5.094
- **FinRL and RD-Agent**: later challengers for RL and automated factor discovery, not trusted production dependencies by default.

Do not equate an open-source repository's popularity, a hedge fund's marketing, or a successful academic backtest with evidence of profitability in GLADIATOR.

## Governance and change controls

Management owns algorithm research backlog and upstream issue monitoring. Researchers/LLMs propose dossiers. Independent Judges own statistical evaluation and reference checks. Gatekeeper owns irreversible vetoes. Any source-code fork requires license review, pinned patchset, upstream monitoring and a replacement/exit plan. Model-generated patches are untrusted code until sandboxed and reviewed.

**Stopping rule:** do not spend indefinitely reverse-engineering every algorithm. Prioritise by failure severity, practical relevance, data feasibility and expected incremental evidence. Rejected or deferred methods remain in the register with reasons.
