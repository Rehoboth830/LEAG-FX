"""
Event flag builder (Phase 6, Step 6).

Flags dates where a real economic release actually happened, based on
genuine published_date values already in our data - not a hardcoded,
unverified FOMC calendar. Covers Fed and BOJ releases we've actually
ingested (FEDFUNDS, CPIAUCSL, GDP, PCEPI, BOJ policy rate).
"""

import pandas as pd

from src.common.db import get_connection


def main():
    conn = get_connection()
    try:
        us_releases = pd.read_sql(
            "SELECT DISTINCT published_date FROM raw_economic_data "
            "WHERE validation_status = 'passed' AND published_date IS NOT NULL",
            conn,
        )
    finally:
        conn.close()

    release_dates = set(pd.to_datetime(us_releases["published_date"]).dt.date)

    conn = get_connection()
    stored = 0
    try:
        with conn.cursor() as cur:
            cur.execute("SELECT observation_date FROM features_daily")
            all_dates = [row[0] for row in cur.fetchall()]

            for obs_date in all_dates:
                flag = 1 if obs_date in release_dates else 0
                cur.execute(
                    "UPDATE features_daily SET economic_release_flag = %s WHERE observation_date = %s",
                    (flag, obs_date),
                )
                stored += cur.rowcount
        conn.commit()
        print(
            f"Updated economic_release_flag for {stored} dates ({len(release_dates)} real release days found)"
        )
    finally:
        conn.close()


if __name__ == "__main__":
    main()
