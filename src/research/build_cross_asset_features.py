"""
Cross-asset feature builder (Phase 7.1) - US 10-year yield, Nikkei
225, and VIX, real data ingested in Step 1.
"""

import pandas as pd

from src.common.db import get_connection


def main():
    conn = get_connection()
    try:
        yield_data = pd.read_sql(
            "SELECT observation_date, value FROM raw_economic_data "
            "WHERE series_id = 'DGS10' AND validation_status = 'passed'",
            conn,
        )
        nikkei_data = pd.read_sql(
            "SELECT timestamp_utc, close FROM raw_market_data "
            "WHERE symbol = '^N225' AND validation_status = 'passed' ORDER BY timestamp_utc",
            conn,
        )
        vix_data = pd.read_sql(
            "SELECT timestamp_utc, close FROM raw_market_data "
            "WHERE symbol = '^VIX' AND validation_status = 'passed'",
            conn,
        )
    finally:
        conn.close()

    yield_data["observation_date"] = pd.to_datetime(yield_data["observation_date"]).dt.date
    nikkei_data["observation_date"] = pd.to_datetime(nikkei_data["timestamp_utc"]).dt.tz_localize(None).dt.date
    nikkei_data["nikkei_return"] = nikkei_data["close"].pct_change()
    vix_data["observation_date"] = pd.to_datetime(vix_data["timestamp_utc"]).dt.tz_localize(None).dt.date

    conn = get_connection()
    stored = 0
    try:
        with conn.cursor() as cur:
            cur.execute("SELECT observation_date FROM features_daily")
            all_dates = [row[0] for row in cur.fetchall()]

            yield_lookup = yield_data.set_index("observation_date")["value"].to_dict()
            nikkei_lookup = nikkei_data.set_index("observation_date")["close"].to_dict()
            nikkei_return_lookup = nikkei_data.set_index("observation_date")["nikkei_return"].to_dict()
            vix_lookup = vix_data.set_index("observation_date")["close"].to_dict()

            for obs_date in all_dates:
                cur.execute(
                    """
                    UPDATE features_daily SET
                        us_10yr_yield = %s, nikkei_close = %s,
                        nikkei_return = %s, vix_close = %s
                    WHERE observation_date = %s
                    """,
                    (
                        yield_lookup.get(obs_date), nikkei_lookup.get(obs_date),
                        nikkei_return_lookup.get(obs_date), vix_lookup.get(obs_date),
                        obs_date,
                    ),
                )
                stored += cur.rowcount
        conn.commit()
        print(f"Updated cross-asset features for {stored} dates")
    finally:
        conn.close()


if __name__ == "__main__":
    main()
