# 12 — Contracts, MCP tools and configuration

## Canonical structured records (illustrative)
```typescript
type Forecast = {
  forecastId: string; modelVersion: string; datasetVersion: string;
  symbol: string; decisionTime: string; horizonMinutes: number;
  expectedNetReturn: number; expectedShortfall: number;
  probabilityTargetBeforeStop: number; probabilityCalibrationId: string;
  confidenceLowerBound: number; confidenceUpperBound: number;
  marketRegime: string; featureAvailableAtMax: string;
};
type TradeProposal = {
  proposalId: string; strategyVersion: string; forecastId: string;
  symbol: string; side: 'BUY' | 'SELL'; entryLimit: number;
  stopPrice: number; targetPrice?: number; timeExit: string;
  proposedUnits: number; maxPlannedLossGBP: number;
  expiresAt: string; paperOnly: boolean;
};
type RiskDecision = {
  proposalId: string; policyVersion: string;
  status: 'APPROVED' | 'REJECTED'; approvedUnits: number;
  reasons: string[]; decisionTime: string; approvalSignature?: string;
};
```
All currency and quantity units must be explicit; avoid floating-point money in implementation (decimal types or integer minor units). `SELL` must be validated as an exit of an existing long position in v1, not permission to short.

## Research MCP tool surface
Read-only: `get_market_history`, `get_latest_quote`, `get_filings_asof`, `get_strategy_metrics`, `get_paper_portfolio`, `get_experiment_history`, `get_model_registry`.  
Research actions: `propose_strategy`, `run_backtest`, `submit_paper_candidate`, `propose_trade`.  
**Never expose:** `place_live_order`, `change_risk_policy`, `increase_capital`, `withdraw_funds`, `rotate_broker_keys` to model-facing MCP.

## Example versioned policy (research defaults, not production approval)
```yaml
policy_version: research-v0.1
mode: PAPER_ONLY
market: US_EQUITIES
allow_margin: false
allow_short: false
allow_derivatives: false
max_concurrent_live_positions: 1
max_new_live_entries_per_day: 2
max_planned_risk_per_trade_pct: 1.0
max_overnight_exposure_pct: 0  # until separately approved
max_daily_loss_pct: null       # REQUIRED before live
max_total_drawdown_pct: null   # REQUIRED before live
max_portfolio_concentration_pct: null # REQUIRED before live
min_net_edge_confidence: null  # select via validation
require_broker_protective_order: true
human_approval_required_for_live: true
monthly_research_budget_gbp: 20
```
`null` is a deliberate live-launch blocker, not an unlimited setting. The research config must never be silently converted to live mode.

## Suggested database entities
`market_events`, `corporate_actions`, `datasets`, `features`, `model_versions`, `calibration_reports`, `strategy_versions`, `experiment_runs`, `holdout_access_log`, `forecasts`, `trade_proposals`, `risk_decisions`, `orders`, `fills`, `positions`, `paper_ledgers`, `cost_ledger`, `audit_events`, `operator_approvals`.

## Traceability
`market_data_hash -> features_hash -> forecast_id -> strategy_version -> proposal_id -> risk_decision_id -> broker_order_id -> fill_ids -> pnl_attribution -> retraining_dataset_version`.
