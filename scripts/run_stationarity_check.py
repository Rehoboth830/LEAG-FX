"""
Runs the real stationarity check on both USD/JPY price levels and
daily returns - we expect these to give OPPOSITE answers, which is
itself the interesting finding.
"""

import pandas as pd

from src.common.db import get_connection
from src.research.stationarity import check_stationarity
from src.research.statistics import compute_daily_returns


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

    price_result = check_stationarity(df["close"])
    print("STATIONARITY TEST: Raw Price Levels")
    print(f"  ADF statistic: {price_result.adf_statistic:.4f}")
    print(f"  p-value:       {price_result.p_value:.4f}")
    print(f"  Stationary?    {price_result.is_stationary}")
    print()

    returns = compute_daily_returns(df["close"])
    returns_result = check_stationarity(returns)
    print("STATIONARITY TEST: Daily Returns")
    print(f"  ADF statistic: {returns_result.adf_statistic:.4f}")
    print(f"  p-value:       {returns_result.p_value:.4f}")
    print(f"  Stationary?    {returns_result.is_stationary}")


if __name__ == "__main__":
    main()
