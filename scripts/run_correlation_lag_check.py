"""
ONE pre-stated follow-up test, decided in advance: does the interest
rate differential change LEAD price by one month (i.e., this month's
differential change vs. NEXT month's return), rather than moving
together in the same month? This is the last follow-up for Step 4 -
the result is reported honestly either way, not chased further.
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

    price["timestamp_utc"] = pd.to_datetime(price["timestamp_utc"]).dt.tz_localize(None)
    price_monthly = price.set_index("timestamp_utc")["close"].resample("ME").last()

    combined = pd.DataFrame(
        {"fed": fed_monthly, "boj": boj_monthly, "price": price_monthly}
    ).dropna()

    combined["differential"] = combined["fed"] - combined["boj"]
    combined["differential_change"] = combined["differential"].diff()
    combined["price_return"] = combined["price"].pct_change()
    # THE ONE CHANGE: shift return backward by one month, so this
    # month's differential change is compared to NEXT month's return.
    combined["next_month_return"] = combined["price_return"].shift(-1)

    combined = combined.dropna()

    print(f"Aligned {len(combined)} months for the lead/lag test")
    print()

    result = compute_correlation(
        combined["differential_change"], combined["next_month_return"]
    )

    print(
        "Correlation: This month's differential change vs. NEXT month's USD/JPY return"
    )
    print(f"  Correlation coefficient: {result.correlation_coefficient:.4f}")
    print(f"  p-value:                 {result.p_value:.4f}")
    print(f"  Observations:            {result.n_observations}")
    print(f"  Statistically significant? {result.is_significant}")


if __name__ == "__main__":
    main()
