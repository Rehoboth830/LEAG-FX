"""
Tests the real interest rate differential hypothesis against USD/JPY
data - correlating CHANGES in the rate differential against USD/JPY
RETURNS (not raw levels), since Step 2 proved both price and rate
levels are non-stationary - correlating levels directly would risk
spurious correlation, a classic statistics trap.
"""

import pandas as pd

from src.common.db import get_connection
from src.research.correlation import compute_correlation


def main():
    conn = get_connection()
    try:
        fed = pd.read_sql(
            "SELECT observation_date, value FROM raw_economic_data "
            "WHERE series_id = 'FEDFUNDS' AND validation_status = 'passed' "
            "ORDER BY observation_date",
            conn,
        )
        boj = pd.read_sql(
            "SELECT observation_date, value FROM raw_japan_economic_data "
            "WHERE series_code = 'STRDCLUCON' AND validation_status = 'passed' "
            "ORDER BY observation_date",
            conn,
        )
        price = pd.read_sql(
            "SELECT timestamp_utc, close FROM raw_market_data "
            "WHERE validation_status = 'passed' ORDER BY timestamp_utc",
            conn,
        )
    finally:
        conn.close()

    fed["observation_date"] = pd.to_datetime(fed["observation_date"])
    fed_monthly = fed.set_index("observation_date")["value"].resample("ME").last()

    boj["observation_date"] = pd.to_datetime(boj["observation_date"])
    boj_monthly = boj.set_index("observation_date")["value"].resample("ME").last()

    # Strip timezone from price timestamps before merging - Fed/BOJ dates
    # are plain DATE (tz-naive), price timestamps are TIMESTAMPTZ
    # (tz-aware). Monthly alignment doesn't need time-of-day precision,
    # so this loses nothing meaningful.
    price["timestamp_utc"] = pd.to_datetime(price["timestamp_utc"]).dt.tz_localize(None)
    price_monthly = price.set_index("timestamp_utc")["close"].resample("ME").last()

    combined = pd.DataFrame(
        {"fed": fed_monthly, "boj": boj_monthly, "price": price_monthly}
    ).dropna()

    combined["differential"] = combined["fed"] - combined["boj"]
    combined["differential_change"] = combined["differential"].diff()
    combined["price_return"] = combined["price"].pct_change()

    combined = combined.dropna()

    print(f"Aligned {len(combined)} months of real data across Fed, BOJ, and price")
    print()

    result = compute_correlation(
        combined["differential_change"], combined["price_return"]
    )

    print(
        "Correlation: Change in (Fed - BOJ) rate differential vs. USD/JPY monthly return"
    )
    print(f"  Correlation coefficient: {result.correlation_coefficient:.4f}")
    print(f"  p-value:                 {result.p_value:.4f}")
    print(f"  Observations (months):   {result.n_observations}")
    print(f"  Statistically significant? {result.is_significant}")


if __name__ == "__main__":
    main()
