# 26 — Adversarial review of market awareness v0.9 (2026-10-22)

**Classification:** internal red-team desk review of design hypotheses. No independent external AI review has occurred, no actual market stream has been downloaded in this review, and no trading-engine test has run. Tests below are *acceptance specifications*, not evidence of successful detection.

## Critic 1: the impossible information-completeness assumption

**Claim attacked:** 'With all world information the system can avoid almost all losses.' **Counterexample:** a secret policy decision leaks into market prices before any approved news source reports it, causing an ETF gap while the venue is closed. No observation system can anticipate the unpublished release. **Resolution:** monitor public calendar and cross-asset stress, price/quote shock response, preapproved event-risk reduction, maximum loss policy and explicit UNKNOWN. **Residual risk:** gaps and executions beyond stops remain.

## Critic 2: news arrives too late for our trading horizon

**Counterexample:** a 1-hour strategy reads a GDELT article 15 minutes after the violent move and backfills it by article-original publication rather than **first availability to this system**. A historical model earns unrealisable returns. **Resolution:** retain publication/first-available/ingestion clocks, gate on first availability, compare news-augmented with price-only controls. **Residual risk:** news release latency and backfilled historical metadata remain uncertain.

## Critic 3: false alarms are expensive

**Counterexample:** an oversensitive change-point detector suspends every strategy after normal volatility fluctuations, missing profitable trends. **Resolution:** holdout evaluation of alert precision, recall, detection delay, net avoided loss, opportunity cost, and hysteresis. **Residual risk:** there is no threshold that dominates across regimes.

## Critic 4: source concentration creates correlated blindness

**Counterexample:** primary ETF quote from IEX shows stale or low activity while US consolidated markets are dislocated. Ten agents all rely on the same weak feed. **Resolution:** mark IEX coverage, compare with permitted second source when possible, mandate feed-health report; block market-sensitive entries if the necessary market scope is unavailable. **Residual risk:** complete NBBO/SIP may require paid access.

## Critic 5: fake narratives override market evidence

**Counterexample:** social-media posts falsely describe an exchange breach; an LLM enthusiastically interprets it as a certainty and sells, despite price/book feeds remaining healthy. **Resolution:** LLM produces evidence-bounded hypotheses only; deterministic market sensors and independent Gatekeeper govern orders; ambiguous event has uncertainty label. **Residual risk:** waiting for confirmation may lose protective response time, which is why confirmed price shock alone can restrict new risk.

## Critic 6: policy and detection are conflated

**Counterexample:** the regime classifier says 'shock' and emits a market sell despite a wide spread and no firm executable quote. **Resolution:** classifier emits observation; Core proposes; Gatekeeper independently applies tradability/cash/exit policy; broker fills only actual executable orders. **Residual risk:** ability to exit during halts is not assured.

## Critic 7: training knows revisions and hidden results

**Counterexample:** a backtest sees final revised CPI and an issuer ETF holdings file created after decision time. **Resolution:** ALFRED/initial-release vintage, public first-availability, revision IDs, audit holdouts. **Residual risk:** historical publication-time archives may be incomplete; discard or flag those observations.

## Critic 8: no persistent service means no 24/7 market intelligence

**Counterexample:** local computer sleeps overnight, misses exchange-status alerts, wakes and claims safe NORMAL because the feed reconnects. **Resolution:** persisting ingestion checkpoints, backfill if allowed, report lost observation windows; DATA_BLIND until reconciliation; active protection requires a genuinely running service and connectivity. **Residual risk:** free local infrastructure cannot guarantee 24/7 delivery.

## Prioritised unresolved decisions

| Priority | Decision | Evidence required |
|---|---|---|
| P0 | Actual approved ETF quote coverage / UK account eligibility | provider plan/terms, market feed entitlement test and alternative sources |
| P0 | Venue-specific crypto market data and outage detection | public WebSocket message formats, heartbeat/reconnect recovery, permission checks |
| P0 | Per-instrument critical source matrix | trade intent examples with `required_for_entry` and safe exit treatment |
| P0 | Time provenance of official releases and GDELT data | raw source payloads, release-clock tests, decision-time replay |
| P1 | Detection algorithms and alert thresholds | walk-forward replay, hidden stress periods, quantified false alarms/latency |
| P1 | Event narrative incremental value | price-only vs event-only vs fused held-out comparison |
| P1 | ETF holdings/history/issuer action coverage | issuer file history and effective/publication metadata |
| P2 | Paid consolidated options/rates/live feeds | evidence of net benefit after cost and subscription rights |
| P2 | External independent model review | frozen review packet and unedited reviewer/model responses |

## Proposed falsification experiments

1. **Unknown driver:** delete all news stories before a crypto crash; a price-only detector must still alert with uncertain cause.
2. **Perfect-hindsight trap:** insert a macro revision into an earlier snapshot; time gate must reject the observation.
3. **Fragile third-party feed:** drop market-data heartbeats for an entire session, keep news; Core must not interpret news availability as tradability.
4. **Mass social rumour:** feed contradictory headlines; deduplicate event cluster and prevent unsupported live order.
5. **Regime label attack:** train detectors on quiet regime only, then introduce 24/7 crypto volatility; measure false alerts and delayed flags by market.
6. **Halt and gap:** trigger emergency stop around ETF halt; record unknown fill/actual gap result, not a synthetic stop execution.
7. **Cross-market mismatch:** compare BTCUSD/BTCUSDT snapshots with asynchronous quotes; refuse to treat mismatch as risk-free arbitrage.
8. **Availability time rollback:** publish headline at 13:00 and ingest 13:17; 13:05 decision cannot use it unless there is verified source evidence of an earlier available channel.

**Exit condition for design-phase P0:** each critical test has a clearly defined fixture, oracle and failure outcome; source rights and access unknowns are identified; time and state contracts are internally consistent. This does not establish an empirically useful predictor or zero error rate.
