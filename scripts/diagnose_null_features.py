"""
Diagnostic: checks non-null counts per feature column, to find
exactly which column(s) are causing the merged dataset to collapse
to zero rows after dropna.
"""

import pandas as pd

from src.common.db import get_connection

FEATURE_COLUMNS = [
    "volatility_5d",
    "volatility_20d",
    "volatility_60d",
    "rsi_14",
    "macd_line",
    "macd_signal",
    "macd_histogram",
    "atr_14",
    "rate_differential",
    "day_of_week",
    "economic_release_flag",
    "us_10yr_yield",
    "nikkei_return",
    "vix_close",
    "cpi_surprise_proxy",
]


def main():
    conn = get_connection()
    try:
        features = pd.read_sql(
            "SELECT * FROM features_daily ORDER BY observation_date", conn
        )
    finally:
        conn.close()

    print(f"Total rows in features_daily: {len(features)}")
    print()
    print("Non-null count per feature column:")
    for col in FEATURE_COLUMNS:
        non_null = features[col].notna().sum()
        print(f"  {col:25s}: {non_null:5d} / {len(features)}")


if __name__ == "__main__":
    main()
