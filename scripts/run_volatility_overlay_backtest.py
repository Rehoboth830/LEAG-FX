"""
Backtests the volatility-based position-sizing overlay against plain
Buy and Hold on REAL USD/JPY data - does reducing exposure during
predicted high-vol days actually improve risk-adjusted return, or not?
"""

import pandas as pd

from src.common.db import get_connection
from src.research.baselines import buy_and_hold_returns
from src.research.performance_metrics import evaluate_strategy
from src.research.statistics import compute_daily_returns
from src.research.volatility_overlay import apply_overlay, build_position_sizes
from src.research.volatility_regimes import classify_regimes, compute_rolling_volatility


def print_metrics(label, metrics):
    print(f"{label}:")
    print(f"  Total return:    {metrics.total_return*100:+.2f}%")
    print(f"  Sharpe ratio:    {metrics.sharpe_ratio:.4f}")
    print(f"  Max drawdown:    {metrics.max_drawdown*100:.2f}%")
    print(f"  Annualized vol:  {metrics.annualized_volatility*100:.2f}%")
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

    plain_returns = buy_and_hold_returns(df["close"])
    metrics_plain = evaluate_strategy(plain_returns)
    print_metrics("PLAIN Buy and Hold (Phase 5 baseline)", metrics_plain)

    all_returns = compute_daily_returns(df["close"])
    rolling_vol = compute_rolling_volatility(all_returns, window=20)
    regime_labels, _ = classify_regimes(rolling_vol)

    # Persistence rule: TODAY's regime sizes TODAY's position for
    # tomorrow's already-realized return in plain_returns - aligned
    # by using regime_labels shifted to match plain_returns' index
    # (plain_returns already excludes the first day via pct_change).
    aligned_regimes = regime_labels.reset_index(drop=True)
    aligned_returns = plain_returns.reset_index(drop=True)
    min_len = min(len(aligned_regimes), len(aligned_returns))
    aligned_regimes = aligned_regimes.iloc[:min_len]
    aligned_returns = aligned_returns.iloc[:min_len]

    position_sizes = build_position_sizes(aligned_regimes, reduced_size=0.5)
    overlay_returns = apply_overlay(aligned_returns, position_sizes)

    metrics_overlay = evaluate_strategy(overlay_returns.dropna())
    print_metrics(
        "Buy and Hold WITH Volatility Overlay (reduced_size=0.5)", metrics_overlay
    )

    print(
        f"Sharpe improvement: {metrics_overlay.sharpe_ratio - metrics_plain.sharpe_ratio:+.4f}"
    )
    print(
        f"Drawdown improvement: {metrics_overlay.max_drawdown - metrics_plain.max_drawdown:+.4f}"
    )
    print(
        f"Return given up: {metrics_overlay.total_return - metrics_plain.total_return:+.4f}"
    )


if __name__ == "__main__":
    main()
