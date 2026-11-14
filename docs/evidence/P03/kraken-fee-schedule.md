# Kraken Pro published fee schedule, read 2026-11-14

[Task](../../tasks/TASK-P03-006.md) · [P03 phase](../../phases/03-market-state-and-ledger/README.md)

**Status: recorded for the P03 ledger fixtures, 2026-11-14.** This record is published terms only. Nobody contacted Kraken, and nothing waits on a reply.

**Basis:** DEC-082 says the fixtures use Kraken's published schedule, with its date, at the base maker/taker tier. The P03 source map ([#40](https://github.com/akibrahimug/gladiators/pull/40)) lists the related constraints: L5 (crypto maker/taker fees and minimum size) and L13 (no hardcoded fees; use dated official schedules).

## Source and method

| Item | Value |
| --- | --- |
| Page | `https://www.kraken.com/pro/fees` (the general fee page `https://www.kraken.com/features/fee-schedule` says "Kraken Pro fees are priced separately" and links to it) |
| Read | 2026-11-14 (UTC), three reads through the coordinator's WebFetch tool, which converts the page to text and answers a question about it. The second read asked for the table rows character for character |
| Stored copy | **None.** Downloading the raw HTML for a stored, hashed copy was refused by this session's permission settings. The figures below are the tool's quotes, consistent across the three reads, not a byte copy |
| Page date | None given; the footer reads "© 2011–2026 Payward, Inc." |

## Spot tiers

The page heading reads "Maker and taker fees for spot and futures across all 17 Kraken Pro volume tiers". The figures below are as quoted by the tool. The raw first two rows were:
- "1 $0+ $0+ — 0.40% 0.80% 0.02% 0.05%"
- "2 $2.5K+ $5M+ — 0.30% 0.60% 0.0175% 0.045%"

The columns are: tier, spot 30-day volume, futures 30-day volume or assets, spot maker, spot taker, futures maker, futures taker.

| Tier | 30-day spot volume (USD) | Maker | Taker |
| --- | --- | --- | --- |
| **1** | **$0+** | **0.40 %** | **0.80 %** |
| 2 | $2.5K+ | 0.30 % | 0.60 % |
| 3 | $10K+ | 0.22 % | 0.38 % |
| 4 | $25K+ | 0.20 % | 0.35 % |
| 5 | $50K+ | 0.15 % | 0.30 % |
| 6 | $100K+ | 0.12 % | 0.25 % |
| 7 | $250K+ | 0.10 % | 0.22 % |
| 8 | $500K+ | 0.08 % | 0.20 % |
| 9 | $1M+ | 0.06 % | 0.18 % |
| 10 | $2.5M+ | 0.04 % | 0.15 % |
| 11 | $5M+ | 0.02 % | 0.12 % |
| 12 | $10M+ | 0.00 % | 0.10 % |
| 13 to 17 | $50M+ to $500M+ | 0.00 % | 0.09 % to 0.05 % |

Only rows 1 and 2 were quoted raw; rows 3 to 17 come from the tool's first, summarised read.

**Separate tiers** apply to "FX, stablecoin-base and pegged-token pairs" (for example USDT/USD), symmetric from 0.20 %. They do not apply to BTC/USD or ETH/USD.

## What the page does not say

- **Pair discounts.** A section "Eligible discounted pairs" offers "-0.02% off the selected spot pairs below". Its list ("Show all 634 pairs") was not in the page content, so **whether BTC/USD or ETH/USD is discounted is unknown.**
- **How fees are charged.** The page gives no fee currency or rounding rule, and no minimum order size. Minimum order size and precision come from `AssetPairs` (`ordermin`, `lot_decimals`, `pair_decimals`). The 30-day pull already records it daily (DEC-057).

## Values for the P03 fixtures (DEC-082)

- **Rates:** maker 0.40 %, taker 0.80 %, the undiscounted tier 1. This is the conservative choice, since a discount, if it applies, would only lower the fee.
- **Arithmetic:** the fee is charged in the quote currency (USD), on the fill's quote notional. The ledger contract decides the rounding (source map Q12); the fixtures state theirs explicitly.
- **Versioning:** the fee schedule is versioned by its read date, 2026-11-14. A later schedule is a new version, never an edit to this one (L13).
