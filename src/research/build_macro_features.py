"""
Macro feature builder (Phase 6, Step 4) - interest rate differential.

Point-in-time correct: for each date, uses only the Fed rate and BOJ
rate that were ACTUALLY KNOWN as of that date (per published_date),
never a value from the future. This directly guards against the
look-ahead bias Phase 4 (Fix 4) proved is a real risk with this data.
"""

import pandas as pd

from src.common.db import get_connection
from src.common.logger import get_logger

logger = get_logger(__name__)


def main():
    conn = get_connection()
    try:
        fed = pd.read_sql(
            "SELECT observation_date, published_date, value FROM raw_economic_data "
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
        feature_dates = pd.read_sql(
            "SELECT observation_date FROM features_daily ORDER BY observation_date",
            conn,
        )
    finally:
        conn.close()

    # FEDFUNDS is monthly, not revised, but IS published with a delay -
    # use published_date (when it was actually known), not observation_date.
    fed["published_date"] = pd.to_datetime(fed["published_date"])
    fed_by_publish = fed.set_index("published_date")["value"].sort_index()

    boj["observation_date"] = pd.to_datetime(boj["observation_date"])
    boj_by_date = boj.set_index("observation_date")["value"].sort_index()

    conn = get_connection()
    stored = 0
    try:
        with conn.cursor() as cur:
            for obs_date in feature_dates["observation_date"]:
                obs_date_ts = pd.Timestamp(obs_date)

                # "As of" lookup: the most recent Fed rate PUBLISHED on
                # or before this date - never a later, not-yet-known value.
                fed_known = fed_by_publish[fed_by_publish.index <= obs_date_ts]
                boj_known = boj_by_date[boj_by_date.index <= obs_date_ts]

                if fed_known.empty or boj_known.empty:
                    continue

                differential = float(fed_known.iloc[-1]) - float(boj_known.iloc[-1])

                cur.execute(
                    "UPDATE features_daily SET rate_differential = %s WHERE observation_date = %s",
                    (differential, obs_date),
                )
                stored += cur.rowcount
        conn.commit()
        print(f"Updated rate_differential feature for {stored} dates")
    finally:
        conn.close()


if __name__ == "__main__":
    main()
