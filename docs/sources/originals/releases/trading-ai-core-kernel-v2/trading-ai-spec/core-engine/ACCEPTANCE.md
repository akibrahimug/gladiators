# Acceptance gates and adversarial tests

| Stage | Must pass before advancing |
|---|---|
| Data | Reject duplicate timestamps, invalid OHLC, timezone-naive timestamps, nonfinite values, stale and future-available observations; snapshot hash stable |
| Features | Time-travel and leak-injection tests; no train-fold contamination from scalers |
| Models | Chronological splits, disjoint calibration, frozen holdout, versioned artifact, reproducible probabilities, calibration report |
| LLM/RAG | Read-only tools, document provenance, point-in-time cutoff, schema-validated output, no fabricated numerical probabilities |
| Strategies | Ten separate versioned policies/ledgers; abstention; no future observations |
| Simulation | Deterministic order/fee/cash ledger; pessimistic ambiguous intrabar stops; gaps, slippage, commissions, splits and FX tests |
| Risk | Independent default-deny, <=1% planned loss, <=cash notional, <=1 live position, <=2 live entries/session, no leverage; forced rejects on stale quotes or broken broker state |
| Broker | Duplicate callback and retry tests, partial fills, unknown order state, reconciliation after outage |
| Learning | Promotion predeclared, multiple testing accounted for, forward paper independent, rollback verified |
| Costs | Line-item report and budget cap; no discretionary research when cap reached; safety functions unaffected |

## Honest status of included runnable slice
Implemented: offline CSV validation/import, SQLite store, causal rolling features, chronological logistic training, basic deterministic close-to-close simulation, cash and simple 1% stop-distance position sizing, terminal reports, smoke tests. **Not implemented**: provider API fetch, corporate actions, realistic order book/fills, calibrated event probability, 10 challengers, RAG, LLM inference/fine-tuning, broker paper/live, full risk gateway. The runnable slice must not be used to authorise real trading.
