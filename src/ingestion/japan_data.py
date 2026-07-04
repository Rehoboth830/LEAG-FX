"""
BOJ economic data ingestion pipeline (Phase 4, Fix 1).

Pulls real Japan data from the Bank of Japan Time-Series Data Search
API (launched Feb 2026, free, no registration required).

Parsing logic verified directly against a real, live API response -
the actual structure (parallel SURVEY_DATES/VALUES arrays under
RESULTSET) differs from the manual's illustrative example.

Series used:
- STRDCLUCON (DB=FM01): Uncollateralized Overnight Call Rate (average) -
  the BOJ's actual operational policy rate target, the closest real
  equivalent to the Fed Funds Rate.
"""

import requests

from src.common.db import get_connection
from src.common.logger import get_logger

logger = get_logger(__name__)

BOJ_API_BASE = "https://www.stat-search.boj.or.jp/api/v1/getDataCode"
SOURCE_NAME = "boj"

BOJ_SERIES = {
    "STRDCLUCON": {
        "db": "FM01",
        "name": "Uncollateralized Overnight Call Rate (average)",
    },
}


def fetch_boj_series(series_code: str, db: str, start_date: str, end_date: str) -> list:
    """
    Fetches a single BOJ series via the official API.

    Args:
        series_code: the BOJ series code, e.g. "STRDCLUCON".
        db: the BOJ database name the series belongs to, e.g. "FM01".
        start_date: start date in YYYYMM format (required by BOJ for
            daily-frequency series).
        end_date: end date in YYYYMM format.

    Returns:
        A list of (date_str, value) tuples, skipping null (non-trading
        day) entries. Empty list on failure - this function does not
        raise, so one series failing does not crash the whole pipeline.
    """
    params = {
        "format": "json",
        "lang": "en",
        "db": db,
        "code": series_code,
        "startDate": start_date,
        "endDate": end_date,
    }

    try:
        response = requests.get(BOJ_API_BASE, params=params, timeout=120)
        response.raise_for_status()
        data = response.json()
    except requests.RequestException as e:
        logger.error(f"BOJ API request failed for {series_code}: {e}")
        return []

    if data.get("STATUS") != 200:
        logger.error(f"BOJ API returned error for {series_code}: {data.get('MESSAGE')}")
        return []

    resultset = data.get("RESULTSET", [])
    if isinstance(resultset, dict):
        resultset = [resultset]

    observations = []
    for series in resultset:
        values_block = series.get("VALUES", {})
        dates = values_block.get("SURVEY_DATES", [])
        values = values_block.get("VALUES", [])

        for date_val, value in zip(dates, values):
            if value is None:
                continue
            observations.append((str(date_val), value))

    logger.info(f"Fetched {len(observations)} observations for {series_code}")
    return observations


def store_boj_series(series_code: str, series_name: str, observations: list) -> int:
    """
    Writes BOJ observations into raw_japan_economic_data. Duplicate rows
    are skipped, so re-running is always safe.
    """
    if not observations:
        logger.warning(f"No data to store for {series_code}")
        return 0

    conn = get_connection()
    inserted = 0
    try:
        with conn.cursor() as cur:
            for date_str, value in observations:
                clean_date = date_str.strip()
                if len(clean_date) == 8:
                    formatted_date = (
                        f"{clean_date[:4]}-{clean_date[4:6]}-{clean_date[6:8]}"
                    )
                elif len(clean_date) == 6:
                    formatted_date = f"{clean_date[:4]}-{clean_date[4:6]}-01"
                else:
                    logger.warning(f"Unrecognized date format from BOJ: {clean_date}")
                    continue

                cur.execute(
                    """
                    INSERT INTO raw_japan_economic_data
                        (series_code, series_name, observation_date, value, source)
                    VALUES (%s, %s, %s, %s, %s)
                    ON CONFLICT (series_code, observation_date, source) DO NOTHING
                    """,
                    (
                        series_code,
                        series_name,
                        formatted_date,
                        float(value),
                        SOURCE_NAME,
                    ),
                )
                if cur.rowcount > 0:
                    inserted += 1
        conn.commit()
        logger.info(f"Stored {inserted} new rows for {series_code}")
    finally:
        conn.close()

    return inserted


def run_ingestion(start_date: str = "201501", end_date: str = "202512") -> dict:
    """
    Full ingestion run for all series in BOJ_SERIES. Each series is
    isolated in its own try/except so one failure does not stop the
    others (fixes the NFR-2.2 gap found in the audit).

    Returns:
        A dict mapping series_code -> number of new rows inserted
        (or "error" if that series failed).
    """
    results = {}
    for series_code, info in BOJ_SERIES.items():
        try:
            observations = fetch_boj_series(
                series_code, info["db"], start_date, end_date
            )
            inserted = store_boj_series(series_code, info["name"], observations)
            results[series_code] = inserted
        except Exception as e:
            logger.error(f"Unexpected failure processing {series_code}: {e}")
            results[series_code] = "error"
    return results


if __name__ == "__main__":
    results = run_ingestion()
    print("BOJ ingestion complete:")
    for series_code, result in results.items():
        print(f"  {series_code}: {result}")
