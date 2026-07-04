"""
Volatility feature builder (Phase 6, Step 2).

Builds rolling volatility features at multiple windows - the single
feature Phase 5 statistically proved has real, significant memory
(volatility clustering), unlike simple price direction.
"""

import pandas as pd

from src.common.db import get_connection
from src.common.logger import get_logger
from src.research.statistics import compute_daily_returns
from src.research.volatility_regimes import compute_rolling_volatility

logger = get_logger(__name__)


def build_volatility_features(prices: pd.Series, dates: pd.Series) -> pd.DataFrame:
    """
    Builds a DataFrame of volatility features aligned to dates.

    Args:
        prices: price series, ordered by date.
        dates: corresponding date series (same order/length as prices).

    Returns:
        DataFrame with observation_date, volatility_5d, volatility_20d,
        volatility_60d.
    """
    returns = compute_daily_returns(prices)

    features = pd.DataFrame(
        {
            "observation_date": dates.iloc[1:].reset_index(drop=True),
            "volatility_5d": compute_rolling_volatility(returns, window=5).reset_index(
                drop=True
            ),
            "volatility_20d": compute_rolling_volatility(
                returns, window=20
            ).reset_index(drop=True),
            "volatility_60d": compute_rolling_volatility(
                returns, window=60
            ).reset_index(drop=True),
        }
    )
    return features


def store_volatility_features(features: pd.DataFrame) -> int:
    """
    Writes volatility features into features_daily, upserting on
    observation_date (safe to re-run).
    """
    conn = get_connection()
    inserted = 0
    try:
        with conn.cursor() as cur:
            for _, row in features.iterrows():
                if pd.isna(row["observation_date"]):
                    continue
                cur.execute(
                    """
                    INSERT INTO features_daily (observation_date, volatility_5d, volatility_20d, volatility_60d)
                    VALUES (%s, %s, %s, %s)
                    ON CONFLICT (observation_date) DO UPDATE SET
                        volatility_5d = EXCLUDED.volatility_5d,
                        volatility_20d = EXCLUDED.volatility_20d,
                        volatility_60d = EXCLUDED.volatility_60d
                    """,
                    (
                        (
                            row["observation_date"].date()
                            if hasattr(row["observation_date"], "date")
                            else row["observation_date"]
                        ),
                        (
                            None
                            if pd.isna(row["volatility_5d"])
                            else float(row["volatility_5d"])
                        ),
                        (
                            None
                            if pd.isna(row["volatility_20d"])
                            else float(row["volatility_20d"])
                        ),
                        (
                            None
                            if pd.isna(row["volatility_60d"])
                            else float(row["volatility_60d"])
                        ),
                    ),
                )
                inserted += 1
        conn.commit()
        logger.info(f"Stored/updated volatility features for {inserted} dates")
    finally:
        conn.close()

    return inserted


if __name__ == "__main__":
    conn = get_connection()
    try:
        df = pd.read_sql(
            "SELECT timestamp_utc, close FROM raw_market_data "
            "WHERE validation_status = 'passed' ORDER BY timestamp_utc",
            conn,
        )
    finally:
        conn.close()

    df["date"] = pd.to_datetime(df["timestamp_utc"]).dt.tz_localize(None).dt.date
    features = build_volatility_features(df["close"], pd.Series(df["date"]))
    count = store_volatility_features(features)
    print(f"Volatility features built and stored for {count} dates")
