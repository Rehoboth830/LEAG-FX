"""
Tests the volatility clustering hypothesis on real USD/JPY data - do
big moves tend to follow big moves, even though direction alone
(Step 3) showed no detectable pattern?
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
    squared_returns = returns**2

    result = analyze_autocorrelation(squared_returns, n_lags=10)

    print("Volatility Clustering Check (squared returns autocorrelation):")
    for lag, value in enumerate(result.acf_values, start=1):
        print(f"  Lag {lag:2d}: {value:+.4f}")
    print()
    print(f"Ljung-Box p-value: {result.ljung_box_p_value:.6f}")
    print(
        f"Significant volatility clustering? {result.has_significant_autocorrelation}"
    )


if __name__ == "__main__":
    main()
