"""
Runs real autocorrelation analysis on USD/JPY daily returns - the
actual test of whether yesterday's move tells us anything statistically
about today's.
"""

import pandas as pd

from src.common.db import get_connection
from src.research.autocorrelation import analyze_autocorrelation
from src.research.statistics import compute_daily_returns


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

    returns = compute_daily_returns(df["close"])
    result = analyze_autocorrelation(returns, n_lags=10)

    print("Autocorrelation at each lag (1 to 10 days back):")
    for lag, value in enumerate(result.acf_values, start=1):
        print(f"  Lag {lag:2d}: {value:+.4f}")
    print()
    print(f"Ljung-Box test statistic: {result.ljung_box_statistic:.4f}")
    print(f"Ljung-Box p-value:        {result.ljung_box_p_value:.4f}")
    print(
        f"Statistically significant autocorrelation? {result.has_significant_autocorrelation}"
    )


if __name__ == "__main__":
    main()
