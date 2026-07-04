"""
Economic data ingestion pipeline (Phase 3, updated in Phase 4 Fix 4).

Pulls core US economic indicators from FRED. Revision-prone series
(GDP, CPIAUCSL, PCEPI) capture their REAL first-publication date
(published_date) alongside the observation date, using FRED's vintage
history - closing the Fix 4 gap so look-ahead bias checks can run on
real, not synthetic, data going forward. FEDFUNDS is not revised, so
published_date equals observation_date for it.

Each series is isolated in its own try/except so one failure does not
stop the others (Fix 2 - NFR-2.2).
"""

import os

import pandas as pd
from dotenv import load_dotenv
from fredapi import Fred

from src.common.db import get_connection
from src.common.logger import get_logger

logger = get_logger(__name__)

load_dotenv()

SOURCE_NAME = "fred"

FRED_SERIES = {
    "FEDFUNDS": {"name": "Federal Funds Effective Rate", "revised": False},
    "CPIAUCSL": {
        "name": "US Consumer Price Index (All Urban Consumers)",
        "revised": True,
    },
    "GDP": {"name": "US Gross Domestic Product", "revised": True},
    "PCEPI": {
        "name": "US Personal Consumption Expenditures Price Index",
        "revised": True,
    },
}


def get_fred_client() -> Fred:
    api_key = os.getenv("FRED_API_KEY")
    if not api_key:
        raise ValueError("FRED_API_KEY not found in environment (.env)")
    return Fred(api_key=api_key)


def fetch_series_with_publication_dates(
    fred: Fred, series_id: str, observation_start: str = "2015-01-01"
) -> pd.DataFrame:
    """
    Fetches a revision-prone series with its REAL first-publication date
    per observation, using FRED's full vintage history.

    Returns:
        DataFrame with columns: observation_date, published_date, value.
    """
    all_releases = fred.get_series_all_releases(series_id)
    all_releases["date"] = pd.to_datetime(all_releases["date"])
    all_releases["realtime_start"] = pd.to_datetime(all_releases["realtime_start"])
    all_releases = all_releases[all_releases["date"] >= observation_start]

    first_releases = (
        all_releases.sort_values("realtime_start")
        .groupby("date")
        .first()
        .reset_index()
        .rename(
            columns={"date": "observation_date", "realtime_start": "published_date"}
        )
    )
    return first_releases[["observation_date", "published_date", "value"]]


def fetch_series_simple(
    fred: Fred, series_id: str, observation_start: str = "2015-01-01"
):
    """Fetches a non-revised series with the plain get_series call."""
    data = fred.get_series(series_id, observation_start=observation_start)
    return data


def store_series(
    series_id: str, series_name: str, data, has_published_dates: bool = False
) -> int:
    """
    Writes a FRED series into raw_economic_data. If has_published_dates
    is True, `data` is a DataFrame with observation_date/published_date/
    value columns; otherwise `data` is a plain pandas Series (observation
    date == published date, since the series isn't revised).
    """
    conn = get_connection()
    inserted = 0
    try:
        with conn.cursor() as cur:
            if has_published_dates:
                if data.empty:
                    return 0
                for _, row in data.iterrows():
                    if pd.isna(row["value"]):
                        continue
                    cur.execute(
                        """
                        INSERT INTO raw_economic_data
                            (series_id, series_name, observation_date, value, source, published_date)
                        VALUES (%s, %s, %s, %s, %s, %s)
                        ON CONFLICT (series_id, observation_date, source) DO NOTHING
                        """,
                        (
                            series_id,
                            series_name,
                            row["observation_date"].date(),
                            float(row["value"]),
                            SOURCE_NAME,
                            row["published_date"].date(),
                        ),
                    )
                    if cur.rowcount > 0:
                        inserted += 1
            else:
                if data.empty:
                    return 0
                for observation_date, value in data.items():
                    if value is None or value != value:
                        continue
                    cur.execute(
                        """
                        INSERT INTO raw_economic_data
                            (series_id, series_name, observation_date, value, source, published_date)
                        VALUES (%s, %s, %s, %s, %s, %s)
                        ON CONFLICT (series_id, observation_date, source) DO NOTHING
                        """,
                        (
                            series_id,
                            series_name,
                            observation_date.date(),
                            float(value),
                            SOURCE_NAME,
                            observation_date.date(),
                        ),
                    )
                    if cur.rowcount > 0:
                        inserted += 1
        conn.commit()
        logger.info(f"Stored {inserted} new rows for {series_id}")
    finally:
        conn.close()

    return inserted


def run_ingestion(observation_start: str = "2015-01-01") -> dict:
    """
    Full ingestion run for all series in FRED_SERIES. Each series is
    isolated in its own try/except (Fix 2 - NFR-2.2).
    """
    fred = get_fred_client()
    results = {}
    for series_id, info in FRED_SERIES.items():
        try:
            if info["revised"]:
                data = fetch_series_with_publication_dates(
                    fred, series_id, observation_start
                )
                inserted = store_series(
                    series_id, info["name"], data, has_published_dates=True
                )
            else:
                data = fetch_series_simple(fred, series_id, observation_start)
                inserted = store_series(
                    series_id, info["name"], data, has_published_dates=False
                )
            results[series_id] = inserted
        except Exception as e:
            logger.error(f"Unexpected failure processing {series_id}: {e}")
            results[series_id] = "error"
    return results


if __name__ == "__main__":
    results = run_ingestion()
    print("Ingestion complete:")
    for series_id, count in results.items():
        print(f"  {series_id}: {count} new rows inserted")
