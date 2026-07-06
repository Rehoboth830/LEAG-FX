"""
CPI "surprise" proxy (Phase 7.1, Step 3 - CORRECTED).

HONEST LIMITATION: this is NOT real market expectations data. It's a
crude proxy: how far each CPI reading deviates from its own trailing
6-month average.

FIX: forward-fills the most recently known surprise value across all
days until the next release - matching the same point-in-time-correct
pattern already used for rate_differential (Phase 6). The original
version only populated the exact release day, collapsing the usable
training set to nearly nothing once combined with other daily features.
"""

import pandas as pd

from src.common.db import get_connection


def main():
    conn = get_connection()
    try:
        cpi_data = pd.read_sql(
            "SELECT observation_date, published_date, value FROM raw_economic_data "
            "WHERE series_id = 'CPIAUCSL' AND validation_status = 'passed' "
            "ORDER BY published_date",
            conn,
        )
        feature_dates = pd.read_sql(
            "SELECT observation_date FROM features_daily ORDER BY observation_date",
            conn,
        )
    finally:
        conn.close()

    cpi_data["pct_change"] = cpi_data["value"].pct_change()
    cpi_data["trailing_avg_change"] = cpi_data["pct_change"].rolling(window=6).mean()
    cpi_data["surprise_proxy"] = (
        cpi_data["pct_change"] - cpi_data["trailing_avg_change"]
    )
    cpi_data["published_date"] = pd.to_datetime(cpi_data["published_date"])

    surprise_by_publish = (
        cpi_data.set_index("published_date")["surprise_proxy"].dropna().sort_index()
    )

    conn = get_connection()
    stored = 0
    try:
        with conn.cursor() as cur:
            for obs_date in feature_dates["observation_date"]:
                obs_date_ts = pd.Timestamp(obs_date)
                known_surprises = surprise_by_publish[
                    surprise_by_publish.index <= obs_date_ts
                ]
                if known_surprises.empty:
                    continue
                # Forward-fill: use the most recently published surprise
                # value, known as of this date - not just the exact day.
                cur.execute(
                    "UPDATE features_daily SET cpi_surprise_proxy = %s WHERE observation_date = %s",
                    (float(known_surprises.iloc[-1]), obs_date),
                )
                stored += cur.rowcount
        conn.commit()
        print(
            f"Updated cpi_surprise_proxy (forward-filled, point-in-time correct) for {stored} dates"
        )
    finally:
        conn.close()


if __name__ == "__main__":
    main()
