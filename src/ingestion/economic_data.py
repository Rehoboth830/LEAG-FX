"""
Economic data ingestion pipeline (Phase 3, updated Phase 4 Fix 4,
extended here to add PAYEMS/NFP - a real gap flagged in Phase 6 rather
than left undocumented).

PAYEMS (Total Nonfarm Payroll Employment) is FRED's actual NFP series -
previously missing despite the knowledge base having an entry for it.
Treated as revision-prone (payroll figures ARE revised in later months),
same handling as GDP/CPI/PCE.
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
    "PAYEMS": {"name": "Total Nonfarm Payroll Employment (NFP)", "revised": True},
}


def get_fred_client() -> Fred:
    api_key = os.getenv("FRED_API_KEY")
    if not api_key:
        raise ValueError("FRED_API_KEY not found in environment (.env)")
    return Fred(api_key=api_key)


def fetch_series_with_publication_dates(
    fred: Fred, series_id: str, observation_start: str = "2015-01-01"
) -> pd.DataFrame:
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
    data = fred.get_series(series_id, observation_start=observation_start)
    return data


def store_series(
    series_id: str, series_name: str, data, has_published_dates: bool = False
) -> int:
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
