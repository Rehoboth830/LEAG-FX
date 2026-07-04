"""
Runs real volatility regime analysis on USD/JPY data - classifying
calm vs. turbulent periods, comparing return statistics across
regimes, and checking whether the highest-volatility dates line up
with real, known market events.
"""

import pandas as pd

from src.common.db import get_connection
from src.research.statistics import compute_daily_returns
from src.research.volatility_regimes import classify_regimes, compute_rolling_volatility


def main():
    conn = get_connection()
    try:
        df = pd.read_sql(
            "SELECT timestamp_utc, close FROM raw_market_data "
            "WHERE validation_status = 'passed' ORDER BY timestamp_utc",
            conn,
        )
    finally:
        conn.close()

    returns = compute_daily_returns(df["close"])
    rolling_vol = compute_rolling_volatility(returns, window=20)
    regime_labels, thresholds = classify_regimes(rolling_vol)

    print(
        f"Regime thresholds: low <= {thresholds.low_threshold:.4f}, high >= {thresholds.high_threshold:.4f}"
    )
    print()

    combined = pd.DataFrame(
        {
            "timestamp": df["timestamp_utc"].iloc[1:].reset_index(drop=True),
            "return": returns.reset_index(drop=True),
            "rolling_vol": rolling_vol.reset_index(drop=True),
            "regime": regime_labels.reset_index(drop=True),
        }
    ).dropna()

    print("Return statistics by regime:")
    for regime in ["low", "medium", "high"]:
        subset = combined[combined["regime"] == regime]["return"]
        print(
            f"  {regime:6s}: n={len(subset):4d}, mean={subset.mean():+.5f}, "
            f"std={subset.std():.5f}, min={subset.min():+.4f}, max={subset.max():+.4f}"
        )
    print()

    print("Top 10 highest single-day volatility dates:")
    top_vol_days = combined.nlargest(10, "rolling_vol")[
        ["timestamp", "rolling_vol", "return"]
    ]
    for _, row in top_vol_days.iterrows():
        print(
            f"  {row['timestamp'].date()}: rolling_vol={row['rolling_vol']:.4f}, that day's return={row['return']:+.4f}"
        )


if __name__ == "__main__":
    main()
