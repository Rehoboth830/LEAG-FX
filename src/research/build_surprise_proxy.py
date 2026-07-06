"""
CPI "surprise" proxy (Phase 7.1, Step 3).

HONEST LIMITATION: this is NOT real market expectations data (which
would require paid vendors like Bloomberg or CME). It's a crude proxy:
how far each CPI reading deviates from its own trailing 6-month
average - a rough stand-in for "was this surprising," not a real
measure of what markets actually expected beforehand.
"""

import pandas as pd

from src.common.db import get_connection


def main():
    conn = get_connection()
    try:
        cpi_data = pd.read_sql(
            "SELECT observation_date, value FROM raw_economic_data "
            "WHERE series_id = 'CPIAUCSL' AND validation_status = 'passed' "
            "ORDER BY observation_date",
            conn,
        )
    finally:
        conn.close()

    cpi_data["pct_change"] = cpi_data["value"].pct_change()
    cpi_data["trailing_avg_change"] = cpi_data["pct_change"].rolling(window=6).mean()
    cpi_data["surprise_proxy"] = (
        cpi_data["pct_change"] - cpi_data["trailing_avg_change"]
    )

    conn = get_connection()
    stored = 0
    try:
        with conn.cursor() as cur:
            for _, row in cpi_data.dropna(subset=["surprise_proxy"]).iterrows():
                cur.execute(
                    "UPDATE features_daily SET cpi_surprise_proxy = %s WHERE observation_date = %s",
                    (float(row["surprise_proxy"]), row["observation_date"]),
                )
                stored += cur.rowcount
        conn.commit()
        print(
            f"Updated cpi_surprise_proxy for {stored} dates (CRUDE PROXY, not real market expectations)"
        )
    finally:
        conn.close()


if __name__ == "__main__":
    main()
