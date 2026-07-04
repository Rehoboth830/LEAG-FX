"""
Phase 4 Fix 4 - backfill published_date for existing revision-prone
rows already in raw_economic_data, since ON CONFLICT DO NOTHING
correctly skipped them during re-ingestion (they already existed) but
that meant published_date was never actually set for them.
"""

from src.common.db import get_connection
from src.common.logger import get_logger
from src.ingestion.economic_data import (
    fetch_series_with_publication_dates,
    get_fred_client,
)

logger = get_logger(__name__)

REVISED_SERIES = ["CPIAUCSL", "GDP", "PCEPI"]


def backfill_published_dates():
    fred = get_fred_client()
    conn = get_connection()
    total_updated = 0

    try:
        with conn.cursor() as cur:
            for series_id in REVISED_SERIES:
                data = fetch_series_with_publication_dates(
                    fred, series_id, "2015-01-01"
                )
                updated_for_series = 0
                for _, row in data.iterrows():
                    if row["value"] != row["value"]:  # NaN check
                        continue
                    cur.execute(
                        """
                        UPDATE raw_economic_data
                        SET published_date = %s
                        WHERE series_id = %s AND observation_date = %s AND source = 'fred'
                        """,
                        (
                            row["published_date"].date(),
                            series_id,
                            row["observation_date"].date(),
                        ),
                    )
                    updated_for_series += cur.rowcount
                logger.info(
                    f"Backfilled published_date for {updated_for_series} {series_id} rows"
                )
                total_updated += updated_for_series
        conn.commit()
    finally:
        conn.close()

    print(f"Total rows backfilled with real published_date: {total_updated}")
    return total_updated


if __name__ == "__main__":
    backfill_published_dates()
