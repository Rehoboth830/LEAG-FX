"""
Cross-asset feature builder (Phase 7.1 - CORRECTED).

FIX: forward-fills US 10yr yield, Nikkei, and VIX using "as of" lookups
(most recently known value), instead of requiring an exact date match.
Nikkei/VIX trade on different exchange calendars than forex (different
holidays), so exact-date matching missed the vast majority of rows -
the same class of bug found and fixed in the CPI surprise proxy.
"""

import pandas as pd

from src.common.db import get_connection


def main():
    conn = get_connection()
    try:
        yield_data = pd.read_sql(
            "SELECT observation_date, value FROM raw_economic_data "
            "WHERE series_id = 'DGS10' AND validation_status = 'passed' ORDER BY observation_date",
            conn,
        )
        nikkei_data = pd.read_sql(
            "SELECT timestamp_utc, close FROM raw_market_data "
            "WHERE symbol = '^N225' AND validation_status = 'passed' ORDER BY timestamp_utc",
            conn,
        )
        vix_data = pd.read_sql(
            "SELECT timestamp_utc, close FROM raw_market_data "
            "WHERE symbol = '^VIX' AND validation_status = 'passed' ORDER BY timestamp_utc",
            conn,
        )
        feature_dates = pd.read_sql(
            "SELECT observation_date FROM features_daily ORDER BY observation_date",
            conn,
        )
    finally:
        conn.close()

    yield_data["observation_date"] = pd.to_datetime(yield_data["observation_date"])
    yield_series = yield_data.set_index("observation_date")["value"].sort_index()

    nikkei_data["observation_date"] = pd.to_datetime(
        nikkei_data["timestamp_utc"]
    ).dt.tz_localize(None)
    nikkei_data["nikkei_return"] = nikkei_data["close"].pct_change()
    nikkei_close_series = nikkei_data.set_index("observation_date")[
        "close"
    ].sort_index()
    nikkei_return_series = nikkei_data.set_index("observation_date")[
        "nikkei_return"
    ].sort_index()

    vix_data["observation_date"] = pd.to_datetime(
        vix_data["timestamp_utc"]
    ).dt.tz_localize(None)
    vix_series = vix_data.set_index("observation_date")["close"].sort_index()

    conn = get_connection()
    stored = 0
    try:
        with conn.cursor() as cur:
            for obs_date in feature_dates["observation_date"]:
                obs_date_ts = pd.Timestamp(obs_date)

                yield_known = yield_series[yield_series.index <= obs_date_ts]
                nikkei_close_known = nikkei_close_series[
                    nikkei_close_series.index <= obs_date_ts
                ]
                nikkei_return_known = nikkei_return_series[
                    nikkei_return_series.index <= obs_date_ts
                ]
                vix_known = vix_series[vix_series.index <= obs_date_ts]

                cur.execute(
                    """
                    UPDATE features_daily SET
                        us_10yr_yield = %s, nikkei_close = %s,
                        nikkei_return = %s, vix_close = %s
                    WHERE observation_date = %s
                    """,
                    (
                        float(yield_known.iloc[-1]) if not yield_known.empty else None,
                        (
                            float(nikkei_close_known.iloc[-1])
                            if not nikkei_close_known.empty
                            else None
                        ),
                        (
                            float(nikkei_return_known.iloc[-1])
                            if not nikkei_return_known.empty
                            and not pd.isna(nikkei_return_known.iloc[-1])
                            else None
                        ),
                        float(vix_known.iloc[-1]) if not vix_known.empty else None,
                        obs_date,
                    ),
                )
                stored += cur.rowcount
        conn.commit()
        print(
            f"Updated cross-asset features (forward-filled, point-in-time correct) for {stored} dates"
        )
    finally:
        conn.close()


if __name__ == "__main__":
    main()
