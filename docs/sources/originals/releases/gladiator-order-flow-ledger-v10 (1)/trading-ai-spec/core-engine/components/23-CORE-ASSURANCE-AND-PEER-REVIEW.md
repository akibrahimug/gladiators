# 23 — Core assurance, adversarial review and release gates

**Assurance is evidence, not confidence.** This document defines what would be required to call the Core operationally reliable; no current certificate is implied.

## Four independent assurance layers

1. **Specification:** unambiguous invariants, type contracts, market assumptions, risk budgets and event-time semantics.
2. **Deterministic tests:** unit, property-based, metamorphic, mutation, differential, state-machine, crash/restart and replay tests with frozen fixtures.
3. **Empirical tests:** point-in-time historical data, strict holdout, cost sensitivity, regime robustness, forward paper trading and false-discovery controls.
4. **Independent review:** separate reviewers/models, frozen review packet, unedited responses, conflict register, reproducible challenges, formal acceptance/rejection record.

## Minimum adversarial test catalogue

| ID | Fault injection | Required behaviour |
|---|---|---|
| T01 | Forecast includes next-bar price | Detect temporal leakage, quarantine model |
| T02 | Price/volume unit mismatch | Reject execution and flag data contract |
| T03 | First period loses 10% | Drawdown includes loss from starting equity |
| T04 | Price gaps 20% beyond stop | Record real loss, never cap at stop price |
| T05 | Same fill event delivered twice | Idempotent ledger, no double position |
| T06 | Broker order acknowledgement lost | Reconcile before retry, avoid duplicate order |
| T07 | Market data feed stale | Abstain, freeze dependent decisions |
| T08 | 1,000 random noise strategies compete | No promotion on naive best backtest; correct multiple testing |
| T09 | Ten identical model outputs | No fictitious ensemble diversity |
| T10 | ETF dividend/split event | Tradable and adjusted prices remain consistent |
| T11 | Crypto symbol reused across venues | No accidental cross-venue price join |
| T12 | Model outputs NaN, infinity or stale version | Reject at typed boundary |
| T13 | Fees turn apparent alpha negative | No-trade |
| T14 | Ledger and broker position disagree | Stop new orders, reconcile |
| T15 | Generated LLM code attempts file/network escape | Sandbox denial, record incident |
| T16 | Training window overlaps label horizon of test | Purge and embargo or reject split |
| T17 | Position size rounds below minimum lot | Abstain rather than violate risk constraint |
| T18 | Volatility regime shifts and forecast calibration fails | Reduce exposure/abstain, initiate review |

## Peer-review protocol

Freeze `architecture_commit`, dependency versions, algorithm dossiers, mathematical contracts, issue register, risk policy, known defects and tests. Ask at least two **genuinely separately invoked** reviewers/models to attack the design from different roles: market microstructure/accounting and statistical ML/overfitting; optionally security and legal-market access. Request minimal counterexamples and specific failing tests. Preserve raw replies with model/version/time. Triage critical/high/medium/low and assign a resolution. Re-run the same review on changed sections. Never manufacture peer-review results.

## Gate decision

**RESEARCH ONLY:** docs and tests can be written, but no verified engine. **PAPER CANDIDATE:** deterministic financial invariants pass; source licensing/data quality pass; event replay and independent ledger agree; unseen evaluation and risk tests pass. **LIVE CANDIDATE:** adds extended forward paper evidence, broker reconciliation, operational incident drills, market permissions, explicit user approval and an independently controlled Gatekeeper. **LIVE APPROVED:** requires separate explicit authorization, not inferred from this document.

A failed critical test blocks promotion even when the model has excellent simulated returns. Target near-zero preventable defects by controlling their *likelihood and impact*, not claiming zero forecast error.
