"""
Runs the real baseline evaluation on USD/JPY data - buy-and-hold and
SMA crossover, both WITH realistic transaction costs. This is THE bar
every future model or strategy (Phases 6-8) must beat, per the Kill
Criteria document. No model gets trusted until it clears this.
"""

import pandas as pd

from src.common.db import get_connection
from src.research.baselines import buy_and_hold_returns, sma_crossover_returns
from src.research.performance_metrics import evaluate_strategy


def print_metrics(label, metrics):
    print(f"{label}:")
    print(f"  Total return:          {metrics.total_return*100:+.2f}%")
    print(f"  Annualized return:     {metrics.annualized_return*100:+.2f}%")
    print(f"  Annualized volatility: {metrics.annualized_volatility*100:.2f}%")
    print(f"  Sharpe ratio:          {metrics.sharpe_ratio:.4f}")
    print(f"  Max drawdown:          {metrics.max_drawdown*100:.2f}%")
    print(f"  Win rate:              {metrics.win_rate*100:.2f}%")
    print()


def main():
    conn = get_connection()
    try:
        df = pd.read_sql(
            "SELECT close FROM raw_market_data "
            "WHERE validation_status = 'passed' ORDER BY timestamp_utc",
            conn,
        )
    finally:
        conn.close()

    prices = df["close"]

    bh_returns = buy_and_hold_returns(prices)
    bh_metrics = evaluate_strategy(bh_returns)
    print_metrics("BASELINE 1: Buy and Hold (with entry cost)", bh_metrics)

    sma_returns = sma_crossover_returns(prices, short_window=20, long_window=50)
    sma_metrics = evaluate_strategy(sma_returns)
    print_metrics(
        "BASELINE 2: SMA(20/50) Crossover (with transaction costs)", sma_metrics
    )


if __name__ == "__main__":
    main()
