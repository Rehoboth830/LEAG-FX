"""
Runs descriptive statistics against real, validated USD/JPY price data.
"""

import pandas as pd

from src.common.db import get_connection
from src.research.statistics import compute_daily_returns, compute_descriptive_stats


def main():
    conn = get_connection()
    try:
        query = """
            SELECT timestamp_utc, close
            FROM raw_market_data
            WHERE validation_status = 'passed'
            ORDER BY timestamp_utc
        """
        df = pd.read_sql(query, conn)
    finally:
        conn.close()

    print(f"Loaded {len(df)} validated price rows")
    print(f"Date range: {df['timestamp_utc'].min()} to {df['timestamp_utc'].max()}")
    print()

    returns = compute_daily_returns(df["close"])
    stats = compute_descriptive_stats(returns)

    print("USD/JPY Daily Return Statistics:")
    print(f"  Count:                  {stats.count}")
    print(f"  Mean daily return:      {stats.mean:.6f} ({stats.mean*100:.4f}%)")
    print(f"  Std dev (daily):        {stats.std_dev:.6f} ({stats.std_dev*100:.4f}%)")
    print(
        f"  Min daily return:       {stats.min_value:.6f} ({stats.min_value*100:.2f}%)"
    )
    print(
        f"  Max daily return:       {stats.max_value:.6f} ({stats.max_value*100:.2f}%)"
    )
    print(f"  Skewness:               {stats.skewness:.4f}")
    print(f"  Kurtosis:               {stats.kurtosis:.4f}")
    print(f"  5th percentile:         {stats.percentile_5:.6f}")
    print(f"  25th percentile:        {stats.percentile_25:.6f}")
    print(f"  Median:                 {stats.median:.6f}")
    print(f"  75th percentile:        {stats.percentile_75:.6f}")
    print(f"  95th percentile:        {stats.percentile_95:.6f}")
    print(
        f"  Annualized return:      {stats.annualized_return:.4f} ({stats.annualized_return*100:.2f}%)"
    )
    print(
        f"  Annualized volatility:  {stats.annualized_volatility:.4f} ({stats.annualized_volatility*100:.2f}%)"
    )


if __name__ == "__main__":
    main()
