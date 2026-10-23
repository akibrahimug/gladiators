# 13 — Open decisions, assumptions and launch blockers

## Decisions made provisionally
- Research US equities; verify live UK-accessible instruments separately.
- One live position slot, ten paper challenger strategies.
- 15-minute and 1-hour completed-bar evaluation initially.
- £500 initial capital, separately funded operating budget.
- No margin/leverage or derivatives v1.
- Open-weight finance LLM + independently trained quantitative predictors; RAG and MCP for research.
- Champion–challenger, immutable audit, independent hard risk service.
- No live trading until explicit approval and evidence.

## Unresolved before implementation
1. **Broker**: Alpaca vs IBKR vs alternative; UK live availability, instrument eligibility, API limits, fractional orders and official tariff.
2. **Data**: historical provider, point-in-time coverage, real-time exchange entitlements and licence.
3. **Model**: exact open-weight checkpoint and licence, hardware target, inference/training plan.
4. **Market universe**: individual liquid US stocks, eligible UCITS ETFs or both; no presumption that US-domiciled ETFs are UK retail tradable.
5. **Holding horizon**: intraday-only vs overnight strategies; initial policy blocks overnight exposure.
6. **Budget**: maximum monthly spend, fine-tuning per-run cap and acceptable ongoing cost-to-capital ratio.
7. **Live limits**: daily loss %, total drawdown %, concentration %, liquidity minimum, exposure per symbol, outage handling.
8. **Promotion**: evidence thresholds, forward-testing duration, uncertainty methodology and benchmark choice.
9. **Tax/account**: UK account type, FX funding and tax recordkeeping requirements.

## Open scientific risks
- Model confidence may be poorly calibrated under regime changes.
- A larger number of strategies increases multiple-testing and selection bias.
- More frequent trading increases cost and correlation of outcomes.
- Backtest profits may disappear under realistic execution.
- Financial fine-tuning may improve explanations without improving returns.
- A £500 account may be too small for profitable operation after fixed costs.
- No defensible timetable to £10,000 can be stated before a validated edge exists.

## Next action
Complete vendor due diligence and build the **paper-only** vertical slice. Keep unresolved launch blockers visible in CI and the dashboard.
