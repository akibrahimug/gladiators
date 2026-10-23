# Run the core from the terminal

Requires Python 3.12+; training/backtesting requires `numpy` and `scikit-learn`. The CSV must come from a legitimate data provider. The package deliberately does **not** claim to have pulled live data, and it does **not** generate fake market bars.

```bash
cd core-engine
python -m venv .venv
source .venv/bin/activate
pip install numpy scikit-learn
python runtime/core.py --db data/market.sqlite3 ingest --csv /absolute/path/to/your_daily_bars.csv
python runtime/core.py --db data/market.sqlite3 inspect --symbol AAPL
python runtime/core.py --db data/market.sqlite3 train --symbol AAPL
python runtime/core.py --db data/market.sqlite3 backtest --symbol AAPL --threshold 0.55 --fee 0.35
python -m unittest discover -s tests -v
```

The input CSV header must be:

```csv
timestamp,symbol,open,high,low,close,volume
```

Each timestamp must have an explicit timezone, e.g. `2025-01-02T21:00:00+00:00`. Daily bars must be chronological by timestamp when interpreted, though import can be unsorted. Supply at least 102 bars and both positive and negative next-day moves in the training period.

Terminal output is only `KEY=VALUE` lines. `ingest` is idempotent for identical rows and rejects conflicting duplicate values. `inspect` prints a deterministic content hash. `train` fits a *research-only, uncalibrated* logistic classifier and reports chronological holdout Brier score. `backtest` prints an intentionally simplified one-bar position simulation, **not** a validated execution model: it lacks real stops, bid/ask, slippage, gaps, FX, actions and commissions beyond the user-specified flat fee. The `--fee` value is charged twice per completed trade and is a **hypothetical per-side amount**, not a broker quote.

Next implementation: provider adapter + immutable raw capture; production Parquet snapshots; proper event-driven simulator; independent risk gateway; then challenger orchestration and RAG. No live trading support exists.
