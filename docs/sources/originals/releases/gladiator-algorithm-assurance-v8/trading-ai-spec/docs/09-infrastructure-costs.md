# 09 — Infrastructure, model, API and broker cost model

## Principles
- Keep **£500 trading capital separate** from infrastructure/training budget.
- Treat all figures as **planning estimates until confirmed with dated official vendor price pages and account-specific schedules**.
- No assumption that ten paper agents require ten GPUs; CPU quant inference is the default.
- Measure cost **per month, per experiment and per completed round trip**.

## Preliminary lean research budget (GBP/month, not vendor quotes)
| Item | Lean research estimate | Notes |
|---|---:|---|
| CPU VPS | £5–£12 | Small instance; verify memory/storage/backup |
| PostgreSQL + pgvector | £0 incremental | Self-hosted, included VPS compute |
| CPU quant training | £0 incremental | Limited by VPS capacity |
| Open-weight LLM inference | £0–£30+ | Local hardware or metered on-demand GPU; **not guaranteed within VPS budget** |
| Occasional external LLM API | £0–£15 | Optional development/research; cap spend |
| Monitoring/backups | £2–£5 | Validate retention/egress |
| Market data | £0–£100+ | Free feed may have coverage/delay limits |
| Broker commissions and regulatory fees | Variable | Per order/share/venue; confirm official schedules |
| FX conversion and funding | Variable | GBP/USD spread, transfer and withdrawal fees |
| GPU fine-tuning | Per run, extra | Depends on model, tokens, VRAM, hours and provider |

A **£12–£32/month** envelope is only plausible for a CPU-first research system with free/basic data and minimal or no GPU use. A continuously hosted finance LLM or full-market real-time data can cost materially more.

## Detailed cost inventory to verify
### Models and compute
- Model licence, commercial use terms, checkpoint download and storage.
- Fine-tuning: GPU instance hourly price × hours, setup/idle time, VRAM, storage snapshots, network egress, retries, failed experiments, evaluation compute.
- Inference: prompt+completion tokens if hosted API; or GPU-hours, power, cooling, memory and maintenance if self-hosted.
- Embeddings, vector indexing, batch requests, rate-limit surcharges, tool-specific fees.
- Logging, observability, cloud bandwidth, backups, snapshots, IP addresses, tax/VAT and FX billing.

### Market data
- Exchange entitlements (IEX vs consolidated SIP), historical depth, corporate actions, delayed versus real-time, API call limits, overage, redistribution/automated use rights, cancellation terms.

### Broker
- Per-share/per-order minimum, routing, exchange/clearing/regulatory fees, spread/slippage, fractional order constraints, overnight financing (if any), margin interest (disabled v1), inactivity/platform fees, market data, FX conversion, wire deposit/withdrawal, rejected-order and corporate-action charges, UK tax implications.

## Net growth mathematics
For starting equity `E0=£500`, target `T=£10,000`, constant **net** monthly rate `r > 0`:
`months = ln(T/E0) / ln(1+r)`.

Approximate horizons without deposits: 1% ≈ 301 months (25.1 years); 2% ≈ 151 months (12.6 years); 3% ≈ 101 months (8.4 years); 5% ≈ 61.4 months (5.1 years); 8% ≈ 38.9 months (3.2 years); 10% ≈ 31.4 months (2.6 years). All assume constant positive net returns, which are **not expected or guaranteed**.

If monthly fixed infrastructure cost is `C`, simple break-even return on current capital `E` is `C/E` before tax. At `C=£20` and `E=£500`, the system must earn 4% **after trading costs** just to cover operating expenses. If costs are paid externally, portfolio balance and all-in project economics must be reported separately.

## Financial controls
- Default initial research operations spending cap: £20/month **only if deployment architecture can satisfy it**; otherwise pause and revise explicitly.
- Set provider hard spend caps, per-agent tool budgets, max GPU-hours per experiment, rate limits and alert at 50/80/100% budget.
- No automatic upgrades, paid data subscriptions or broker funding.
- Monthly cost report: compute, GPU, LLM tokens, embeddings, market data, broker fees, FX, slippage estimate, tax/VAT, all-in net return.

## Price verification procedure
Before selecting vendors, capture dated official price pages and terms, UK account-specific broker tariff, paper/live data entitlement, and one end-to-end example invoice. Recheck before live activation and after vendor pricing changes. This spec intentionally does not treat historical quoted prices as current contractual terms.
