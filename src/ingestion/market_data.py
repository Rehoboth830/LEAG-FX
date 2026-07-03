"""
Market data ingestion pipeline (Phase 3).

Pulls USD/JPY OHLC data from yfinance and writes it into the raw/staging
zone of PostgreSQL, timestamped and timezone-normalized on the way in
(FR-3.5) — not deferred to a later cleanup step. This is the permanent
pipeline; scripts/test_yfinance_connection.py was only Step 2's proof
that the connection works.
"""

from datetime import timezone

import yfinance as yf

from src.common.db import get_connection
from src.common.logger import get_logger

logger = get_logger(__name__)

DEFAULT_SYMBOL = "USDJPY=X"
SOURCE_NAME = "yfinance"


def fetch_ohlc(symbol: str = DEFAULT_SYMBOL, period: str = "5d"):
    """
    Fetches OHLC data from yfinance for the given symbol and period.
    """
    ticker = yf.Ticker(symbol)
    data = ticker.history(period=period)
    logger.info(f"Fetched {len(data)} rows for {symbol} (period={period})")
    return data


def store_ohlc(data, symbol: str = DEFAULT_SYMBOL) -> int:
    """
    Writes OHLC data into the raw_market_data table. Timestamps are
    converted to UTC on the way in (FR-3.5). Duplicate rows are skipped
    via ON CONFLICT DO NOTHING, so re-running this is always safe.
    """
    if data.empty:
        logger.warning(f"No data to store for {symbol} — empty DataFrame")
        return 0

    conn = get_connection()
    inserted = 0
    try:
        with conn.cursor() as cur:
            for timestamp, row in data.iterrows():
                timestamp_utc = timestamp.tz_convert(timezone.utc)
                cur.execute(
                    """
                    INSERT INTO raw_market_data
                        (symbol, timestamp_utc, open, high, low, close, volume, source)
                    VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
                    ON CONFLICT (symbol, timestamp_utc, source) DO NOTHING
                    """,
                    (
                        symbol,
                        timestamp_utc,
                        float(row["Open"]),
                        float(row["High"]),
                        float(row["Low"]),
                        float(row["Close"]),
                        float(row["Volume"]),
                        SOURCE_NAME,
                    ),
                )
                if cur.rowcount > 0:
                    inserted += 1
        conn.commit()
        logger.info(f"Stored {inserted} new rows for {symbol} (of {len(data)} fetched)")
    finally:
        conn.close()

    return inserted


def run_ingestion(symbol: str = DEFAULT_SYMBOL, period: str = "5d") -> int:
    """
    Full ingestion run: fetch then store.
    """
    data = fetch_ohlc(symbol, period)
    return store_ohlc(data, symbol)


if __name__ == "__main__":
    rows_inserted = run_ingestion()
    print(f"Ingestion complete. {rows_inserted} new rows inserted.")
