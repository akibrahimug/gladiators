# 10 — Security, compliance and failure handling

## Safety model
Research models are untrusted proposal generators. RAG content and market news may contain prompt injections. MCP exposes read-only research tools and `propose_trade`, not direct `place_live_order`. The execution gateway accepts only signed, schema-valid, risk-approved instructions from an authorised service identity.

## Controls
- Separate paper/live API credentials and environments; live disabled by default.
- Vault/secret manager or secure host secret injection; never place credentials in prompts, logs or embeddings.
- RBAC, least privilege, key rotation, audit trail, MFA for broker and admin accounts.
- Versioned risk configuration managed outside the model; human approval for any increase in exposure, policy changes, model promotion or funding.
- Replay/duplicate prevention, signed requests, idempotent order handling, time-bound trade proposals.
- Reconcile actual broker state on startup and after any network timeout.
- Kill switch blocks **new** orders; existing protective orders must remain valid and be reconciled.

## Failure matrix
| Failure | Default action |
|---|---|
| Market feed stale/inconsistent | Stop new entries; alert |
| Broker API timeout | Query order state; do not blindly retry |
| Missing protective order | Block further entries; escalate immediately |
| Portfolio/broker mismatch | Freeze new orders; reconcile |
| Model or RAG outage | No new entries; broker-side protections remain |
| Spend cap exceeded | Disable nonessential inference/training |
| Quant calibration/drift alarm | Suspend affected strategy |
| Risk policy tampering | Reject, audit, alert |
| Data publication time unknown | Exclude from historical predictive features |
| Unexpected gap/slippage | Update realised risk; trigger limits and review |

## UK compliance and tax readiness
- Confirm UK resident brokerage eligibility and whether instrument is available to UK retail clients.
- Verify broker's API terms and data redistribution/trading automation permissions.
- Determine whether instruments/account generate UK capital gains, dividends, stamp taxes or other obligations; maintain full transaction and FX records and obtain professional advice if needed.
- Research model is for user's own account; managing other people's money or selling signals may trigger additional regulatory obligations.
- No claim of FCA authorisation or investment-adviser status.

## Operator runbooks
- Startup: validate credentials, clock, market calendar, feed, strategy version, account cash, open orders, risk policy and protection.
- Incident: freeze entries, inspect broker orders, preserve stops, alert, capture event trace, remediate and require reapproval.
- Rollback: pin prior signed model/config, verify reproducibility and paper replay before reactivation.
- Shutdown: stop research jobs and new orders; reconcile/secure existing live positions rather than blindly abandoning them.
