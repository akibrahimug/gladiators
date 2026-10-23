# Terminal CLI and acceptance gates

Status: design specification; not a claim of implemented functionality.

## Contract
Single command `gladiator` with text output default and optional machine-readable JSON. All example commands below are **target interfaces, not implemented claims**. Every command accepts `--offline` where applicable; error codes nonzero and informative.

```text
gladiator data sources
gladiator data pull --provider PROVIDER --symbols AAPL,MSFT --interval 1d --allow-network
gladiator data validate --dataset DATASET
gladiator data snapshot --as-of 2024-01-01T00:00:00Z
gladiator qlib prepare --snapshot SNAPSHOT
gladiator model train --config configs/lightgbm.yaml
gladiator model evaluate --id MODEL
gladiator core decide --snapshot SNAPSHOT --offline
gladiator arena run --config configs/arena.yaml --seed 42
gladiator judges score --arena-run RUN
gladiator gatekeeper check --intent INTENT
gladiator paper replay --arena-run RUN
gladiator ledger reconcile
gladiator management status
gladiator report costs
```

## End-to-end acceptance, in order
A. Raw source checksum and licence manifest retained; cleaning report identifies all rejected rows.
B. Same snapshot yields identical features and predictions; future bars do not affect earlier decisions.
C. Three CPU models train and emit calibrated, timestamped forecasts on a chronological holdout.
D. Core produces a structured, explained `ABSTAIN` or trade intent from actual model artifacts, not hand-entered fabricated probabilities.
E. Gatekeeper rejects over-budget, stale and unauthorised intents; kill switch blocks orders.
F. Simulator accounts for fees, spread, gaps, partial fills and ledger reconciliation; no optimistic same-bar fills.
G. Arena evaluates at least three challengers under identical conditions, then ten registered entrants as implementations become available; no fake competitors.
H. Judges produce confidence-aware ranking and documented rejection/promotion evidence; no holdout leakage.
I. RAG citations are point-in-time and optional; removal does not break core.
J. Entire run produces terminal-only reproducible numeric report; no paid network calls or live broker orders.

## Example output fields (not fabricated results)
`dataset_version, accepted_rows, rejected_rows, train_end, test_start, model_id, calibration_error, predictions, signals, abstentions, trades, gross_pnl, trading_costs, net_pnl, max_drawdown, risk_rejections, cash, equity, experiment_cost, live_enabled=false`.

## Operational invariants
- Phase 1: zero paid external services, no live orders, no dashboard; terminal text/number output only. Use local files and explicit, free, permitted data sources. Network pulls require explicit invocation.
- Every artifact includes `run_id`, UTC `as_of`, immutable `dataset_hash`, `code_version`, `config_hash`, and relevant `model_version`.
- Reject missing, stale, future-dated, unlicensed or unverified inputs; `ABSTAIN` is valid and preferable to guessing.
- Do not infer profitability from backtests. Keep chronological holdouts, realistic costs, and independent forward-paper validation.
- No LLM, gladiator, or management agent may modify gatekeeper limits or access live broker credentials.

## v0.5 design audit commands (now implemented separately)
`python audit/spec_audit.py` performs **documentation contract checks only** and prints text/numbers. It does not train models or establish profitability. `python -m unittest discover -s audit/tests -v` tests the audit tool.
- Prior to implementation, block release if design cannot explain timestamps, provider rights, holdout governance, ledger invariants, no-trade policy, and no-live capability.
