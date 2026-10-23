# 03 — Market data and broker connectivity

## Research market
US liquid equities and ETFs have deep historical research and data infrastructure. **Research universe is not the same as live-eligible instruments**: UK retail access to US-domiciled ETFs is generally restricted by PRIIPs/KID rules. Live universe must be broker- and account-approved; consider eligible UCITS ETFs or individual stocks.

## Providers to assess, not yet selected
- **Alpaca:** accessible paper API and stock data. Confirm current UK live onboarding, exact data entitlements, international funding, currency conversion, commissions, exchange/regulatory fees, withdrawals, and whether paper feed matches live feed.
- **Interactive Brokers (IBKR):** broad market access, paper accounts and APIs; more integration complexity. Confirm UK account eligibility, commissions/minimums, FX, subscriptions, market-data equity requirements and order types.
- **SEC EDGAR:** public US filings; ingest with filing `accepted_at` timestamps, not report-period dates.
- **Macro/event sources:** verify source licensing and publication/availability timestamps.

**Do not hardcode fees quoted in conversation as permanent facts.** Obtain dated, account-specific official schedules before activation; save PDFs/screenshots and machine-readable cost assumptions.

## Required data
- OHLCV with UTC bar close and exchange session calendars; corporate actions, delisting/survivorship-aware universe.
- Quotes/bid-ask spreads and order book where licensed; use conservative spread assumptions otherwise.
- Trading halts, session boundaries, holidays, early closes, earnings/event release timestamps.
- Currency rates and funding ledger for GBP-to-USD trades.
- Quality: nulls, duplicates, zero volume, split discontinuities, timezone and stale-feed anomalies.

## Timestamp contract
`event_time`: when market event occurred; `available_at`: first time strategy could have known it; `ingested_at`: when our service received it. Feature eligibility requires `available_at <= decision_time`. Never train on revised data as though revision existed earlier.

## Broker interface
```typescript
interface BrokerAdapter {
  getAccount(): Promise<AccountSnapshot>;
  getPositions(): Promise<Position[]>;
  getOpenOrders(): Promise<Order[]>;
  placeOrder(approved: RiskApprovedOrder): Promise<OrderReceipt>;
  cancelOrder(orderId: string): Promise<void>;
  getFills(since: string): Promise<Fill[]>;
  getMarketClock(): Promise<MarketClock>;
}
```

## Order lifecycle
`proposed -> risk_approved -> submitted -> acknowledged -> partially_filled | filled | rejected | cancelled -> reconciled`. Order submission requires stable client-generated idempotency key. Timeouts require **querying broker state before retry**, never blind resubmission. Stops and brackets must be verified broker-side; if unavailable, block live entry until an explicitly approved alternative exists.

## Execution realism
Backtest spread, per-side commissions, exchange/regulatory fees, slippage, partial fills, latency, liquidity, gaps, overnight exposure, borrow/short restrictions, fractional-share and minimum notional constraints. Treat paper results as optimistic until proven otherwise.

## UK live-readiness checklist
Broker UK eligibility; instrument eligibility; ISA/GIA constraints if applicable; API permission and terms; KYC/AML; FX costs; tax record exports; market-data licence; fractional-order support; broker order types; no assumed US-listed ETF access. No live launch before these are verified.
