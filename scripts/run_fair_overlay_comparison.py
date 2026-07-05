"""
CORRECTED comparison: plain Buy and Hold evaluated over the SAME
restricted period as the walk-forward overlay (post-warm-up only),
for a genuinely fair, same-period comparison - fixing a real flaw in
the previous script that compared two different time spans.
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

    all_returns = compute_daily_returns(df["close"])
    rolling_vol = compute_rolling_volatility(all_returns, window=20)
    regime_labels = classify_regimes_expanding_window(rolling_vol, min_history=252)

    plain_returns = buy_and_hold_returns(df["close"]).reset_index(drop=True)
    regime_labels = regime_labels.reset_index(drop=True)

    min_len = min(len(plain_returns), len(regime_labels))
    plain_returns = plain_returns.iloc[:min_len]
    regime_labels = regime_labels.iloc[:min_len]

    # THE FIX: restrict PLAIN buy-and-hold to the exact SAME dates as
    # the overlay, so both are measured over an identical period.
    valid = regime_labels.notna()
    plain_returns_same_period = plain_returns[valid]
    regime_labels_same_period = regime_labels[valid]

    metrics_plain_same_period = evaluate_strategy(plain_returns_same_period)
    print_metrics(
        "PLAIN Buy and Hold (SAME restricted period as overlay)",
        metrics_plain_same_period,
    )

    position_sizes = build_position_sizes(regime_labels_same_period, reduced_size=0.5)
    overlay_returns = apply_overlay(plain_returns_same_period, position_sizes)
    metrics_overlay = evaluate_strategy(overlay_returns.dropna())
    print_metrics("Walk-Forward Volatility Overlay (same period)", metrics_overlay)

    print("HONEST, SAME-PERIOD COMPARISON:")
    print(
        f"  Sharpe improvement:    {metrics_overlay.sharpe_ratio - metrics_plain_same_period.sharpe_ratio:+.4f}"
    )
    print(
        f"  Drawdown improvement:  {metrics_overlay.max_drawdown - metrics_plain_same_period.max_drawdown:+.4f}"
    )
    print(
        f"  Return difference:     {(metrics_overlay.total_return - metrics_plain_same_period.total_return)*100:+.2f}%"
    )


if __name__ == "__main__":
    main()
