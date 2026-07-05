"""
Re-runs the volatility overlay backtest using WALK-FORWARD regime
classification (Step 5) instead of the full-sample version (Step 4) -
the real, honest test of whether the earlier improvement survives
once look-ahead bias is removed.
"""

import pandas as pd

from src.common.db import get_connection
from src.research.baselines import buy_and_hold_returns
from src.research.performance_metrics import evaluate_strategy
from src.research.statistics import compute_daily_returns
from src.research.volatility_overlay import apply_overlay, build_position_sizes
from src.research.volatility_regimes import compute_rolling_volatility
from src.research.walk_forward_regimes import classify_regimes_expanding_window


def print_metrics(label, metrics):
    print(f"{label}:")
    print(f"  Total return:    {metrics.total_return*100:+.2f}%")
    print(f"  Sharpe ratio:    {metrics.sharpe_ratio:.4f}")
    print(f"  Max drawdown:    {metrics.max_drawdown*100:.2f}%")
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
    print_metrics("PLAIN Buy and Hold", metrics_plain)

    all_returns = compute_daily_returns(df["close"])
    rolling_vol = compute_rolling_volatility(all_returns, window=20)

    # THE FIX: walk-forward classification instead of full-sample.
    regime_labels = classify_regimes_expanding_window(rolling_vol, min_history=252)

    aligned_regimes = regime_labels.reset_index(drop=True)
    aligned_returns = plain_returns.reset_index(drop=True)
    min_len = min(len(aligned_regimes), len(aligned_returns))
    aligned_regimes = aligned_regimes.iloc[:min_len]
    aligned_returns = aligned_returns.iloc[:min_len]

    # Only evaluate where classification actually exists (excludes the
    # min_history warm-up period, same honest handling as elsewhere).
    valid = aligned_regimes.notna()
    aligned_regimes = aligned_regimes[valid]
    aligned_returns = aligned_returns[valid]

    position_sizes = build_position_sizes(aligned_regimes, reduced_size=0.5)
    overlay_returns = apply_overlay(aligned_returns, position_sizes)

    metrics_overlay = evaluate_strategy(overlay_returns.dropna())
    print_metrics("Buy and Hold WITH WALK-FORWARD Volatility Overlay", metrics_overlay)

    print(
        f"Sharpe improvement: {metrics_overlay.sharpe_ratio - metrics_plain.sharpe_ratio:+.4f}"
    )
    print(
        f"Drawdown improvement: {metrics_overlay.max_drawdown - metrics_plain.max_drawdown:+.4f}"
    )
    print(
        f"Note: comparison period is shorter (excludes {min_history if False else 252}-day warm-up)"
    )


if __name__ == "__main__":
    main()
