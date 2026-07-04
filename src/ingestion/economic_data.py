"""
Economic data ingestion pipeline (Phase 3).

Pulls core US economic indicators from FRED and writes them into the
raw/staging zone of PostgreSQL. Covers the series referenced in the
knowledge base (FR-2.2): Fed funds rate, CPI, GDP, PCE.
"""

import os

from dotenv import load_dotenv
from fredapi import Fred

from src.common.db import get_connection
from src.common.logger import get_logger

logger = get_logger(__name__)

load_dotenv()

SOURCE_NAME = "fred"

# Maps our knowledge base concepts to real FRED series IDs.
FRED_SERIES = {
    "FEDFUNDS": "Federal Funds Effective Rate",
    "CPIAUCSL": "US Consumer Price Index (All Urban Consumers)",
    "GDP": "US Gross Domestic Product",
    "PCEPI": "US Personal Consumption Expenditures Price Index",
}


def get_fred_client() -> Fred:
    """Returns an authenticated Fred client using the API key from .env."""
    api_key = os.getenv("FRED_API_KEY")
    if not api_key:
        raise ValueError("FRED_API_KEY not found in environment (.env)")
    return Fred(api_key=api_key)


def fetch_series(fred: Fred, series_id: str, observation_start: str = "2015-01-01"):
    """
    Fetches a single FRED series.

    Args:
        fred: an authenticated Fred client.
        series_id: the FRED series identifier, e.g. "CPIAUCSL".
        observation_start: earliest date to pull from.

    Returns:
        A pandas Series indexed by date.
    """
    data = fred.get_series(series_id, observation_start=observation_start)
    logger.info(f"Fetched {len(data)} observations for {series_id}")
    return data


def store_series(series_id: str, series_name: str, data) -> int:
    """
    Writes a FRED series into the raw_economic_data table. Duplicate
    rows (same series/date/source) are skipped, so re-running is safe.

    Args:
        series_id: the FRED series identifier.
        series_name: a human-readable name for the series.
        data: a pandas Series indexed by date, as returned by fetch_series().

    Returns:
        The number of rows actually inserted.
    """
    if data.empty:
        logger.warning(f"No data to store for {series_id} — empty series")
        return 0

    conn = get_connection()
    inserted = 0
    try:
        with conn.cursor() as cur:
            for observation_date, value in data.items():
                if value is None or (hasattr(value, "__float__") and value != value):
                    continue
                cur.execute(
                    """
                    INSERT INTO raw_economic_data
                        (series_id, series_name, observation_date, value, source)
                    VALUES (%s, %s, %s, %s, %s)
                    ON CONFLICT (series_id, observation_date, source) DO NOTHING
                    """,
                    (
                        series_id,
                        series_name,
                        observation_date.date(),
                        float(value),
                        SOURCE_NAME,
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
    Full ingestion run for all series in FRED_SERIES.

    Args:
        observation_start: earliest date to pull for every series.

    Returns:
        A dict mapping series_id -> number of new rows inserted.
    """
    fred = get_fred_client()
    results = {}
    for series_id, series_name in FRED_SERIES.items():
        data = fetch_series(fred, series_id, observation_start)
        inserted = store_series(series_id, series_name, data)
        results[series_id] = inserted
    return results


if __name__ == "__main__":
    results = run_ingestion()
    print("Ingestion complete:")
    for series_id, count in results.items():
        print(f"  {series_id}: {count} new rows inserted")
