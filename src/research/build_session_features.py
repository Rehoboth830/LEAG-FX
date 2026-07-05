"""
Day-of-week feature builder (Phase 6, Step 5 - scoped down).

Only day-of-week is built here, not true session-overlap features,
since those require intraday data this project doesn't currently
ingest (daily OHLC only). True session features are a Phase 2.1
(day-trading extension) task, honestly deferred rather than faked.
"""

import pandas as pd

from src.common.db import get_connection


def main():
    conn = get_connection()
    try:
        df = pd.read_sql("SELECT observation_date FROM features_daily", conn)
    finally:
        conn.close()

    df["observation_date"] = pd.to_datetime(df["observation_date"])
    df["day_of_week"] = df["observation_date"].dt.dayofweek  # 0=Monday ... 6=Sunday

    conn = get_connection()
    stored = 0
    try:
        with conn.cursor() as cur:
            for _, row in df.iterrows():
                cur.execute(
                    "UPDATE features_daily SET day_of_week = %s WHERE observation_date = %s",
                    (int(row["day_of_week"]), row["observation_date"].date()),
                )
                stored += cur.rowcount
        conn.commit()
        print(f"Updated day_of_week feature for {stored} dates")
    finally:
        conn.close()


if __name__ == "__main__":
    main()
