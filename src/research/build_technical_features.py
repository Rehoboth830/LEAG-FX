"""
Builds and stores technical indicator features (Phase 6, Step 3) for
all real, validated USD/JPY price history.
"""

import pandas as pd

from src.common.db import get_connection
from src.common.logger import get_logger
from src.research.technical_indicators import (
    compute_atr,
    compute_bollinger_bands,
    compute_macd,
    compute_rsi,
)

logger = get_logger(__name__)


def main():
    conn = get_connection()
    try:
        df = pd.read_sql(
            "SELECT timestamp_utc, open, high, low, close FROM raw_market_data "
            "WHERE validation_status = 'passed' ORDER BY timestamp_utc",
            conn,
        )
    finally:
        conn.close()

    df["observation_date"] = (
        pd.to_datetime(df["timestamp_utc"]).dt.tz_localize(None).dt.date
    )

    rsi = compute_rsi(df["close"], window=14)
    macd = compute_macd(df["close"])
    atr = compute_atr(df["high"], df["low"], df["close"], window=14)
    bb = compute_bollinger_bands(df["close"], window=20)

    conn = get_connection()
    stored = 0
    try:
        with conn.cursor() as cur:
            for i in range(len(df)):
                if pd.isna(rsi.iloc[i]) and pd.isna(atr.iloc[i]):
                    continue
                cur.execute(
                    """
                    UPDATE features_daily SET
                        rsi_14 = %s, macd_line = %s, macd_signal = %s,
                        macd_histogram = %s, atr_14 = %s,
                        bb_upper = %s, bb_middle = %s, bb_lower = %s
                    WHERE observation_date = %s
                    """,
                    (
                        None if pd.isna(rsi.iloc[i]) else float(rsi.iloc[i]),
                        (
                            None
                            if pd.isna(macd["macd_line"].iloc[i])
                            else float(macd["macd_line"].iloc[i])
                        ),
                        (
                            None
                            if pd.isna(macd["signal_line"].iloc[i])
                            else float(macd["signal_line"].iloc[i])
                        ),
                        (
                            None
                            if pd.isna(macd["histogram"].iloc[i])
                            else float(macd["histogram"].iloc[i])
                        ),
                        None if pd.isna(atr.iloc[i]) else float(atr.iloc[i]),
                        (
                            None
                            if pd.isna(bb["bb_upper"].iloc[i])
                            else float(bb["bb_upper"].iloc[i])
                        ),
                        (
                            None
                            if pd.isna(bb["bb_middle"].iloc[i])
                            else float(bb["bb_middle"].iloc[i])
                        ),
                        (
                            None
                            if pd.isna(bb["bb_lower"].iloc[i])
                            else float(bb["bb_lower"].iloc[i])
                        ),
                        df["observation_date"].iloc[i],
                    ),
                )
                stored += cur.rowcount
        conn.commit()
        print(f"Updated technical indicator features for {stored} dates")
    finally:
        conn.close()


if __name__ == "__main__":
    main()
