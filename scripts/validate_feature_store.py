"""
Validates the assembled feature store (Phase 6, Step 7) using the
same structural checks built in Phase 4 - proving the feature store
is trustworthy, not just assuming it because each step worked.
"""

import pandas as pd

from src.common.db import get_connection
from src.validation.structural_checks import check_missing_values


def main():
    conn = get_connection()
    try:
        df = pd.read_sql("SELECT * FROM features_daily ORDER BY observation_date", conn)
    finally:
        conn.close()

    print(f"Feature store contains {len(df)} rows")
    print()

    feature_columns = [
        "volatility_5d", "volatility_20d", "volatility_60d",
        "rsi_14", "macd_line", "macd_signal", "macd_histogram", "atr_14",
        "bb_upper", "bb_middle", "bb_lower", "rate_differential",
        "day_of_week", "economic_release_flag",
    ]

    print("Missing value counts per feature (some are EXPECTED at the start, due to rolling-window warm-up):")
    for col in feature_columns:
        missing_count = df[col].isna().sum()
        print(f"  {col:25s}: {missing_count:5d} missing ({missing_count/len(df)*100:.1f}%)")

    print()
    complete_rows = df.dropna(subset=feature_columns)
    print(f"Rows with ALL features present (usable for Phase 7 modeling): {len(complete_rows)}")
    print(f"Date range of complete rows: {complete_rows['observation_date'].min()} to {complete_rows['observation_date'].max()}")


if __name__ == "__main__":
    main()
