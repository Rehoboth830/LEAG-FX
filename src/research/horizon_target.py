"""
Longer-horizon prediction target (Phase 7.1, Step 2).

Predicts direction over a longer horizon (default 20 trading days,
~1 month) instead of just the next single day. Motivated by real
evidence: Phase 5 found no daily-level directional pattern, but a
genuine, real 10-year uptrend existed - suggesting monthly-scale
dynamics might differ from daily noise.
"""

import pandas as pd

from src.common.logger import get_logger

logger = get_logger(__name__)


def build_horizon_return(prices: pd.Series, horizon_days: int = 20) -> pd.Series:
    """
    Computes the forward return over the given horizon: (price N days
    ahead - price today) / price today.

    Args:
        prices: price series, ordered by date.
        horizon_days: how many trading days ahead to look.

    Returns:
        A series of forward returns, aligned to today's date. The last
        `horizon_days` rows are NaN (not enough future data yet).
    """
    future_price = prices.shift(-horizon_days)
    horizon_return = (future_price - prices) / prices
    return horizon_return


def build_horizon_direction_target(
    prices: pd.Series, horizon_days: int = 20
) -> pd.Series:
    """
    Builds a binary target: will the price be higher in `horizon_days`
    trading days than it is today?

    Args:
        prices: price series, ordered by date.
        horizon_days: prediction horizon in trading days.

    Returns:
        Binary (0/1) target series, NaN where insufficient future data exists.
    """
    horizon_return = build_horizon_return(prices, horizon_days)
    target = (horizon_return > 0).astype(float)
    target[horizon_return.isna()] = float("nan")

    logger.info(
        f"Built {horizon_days}-day horizon target: {target.notna().sum()} labeled rows, "
        f"{target.mean():.4f} positive rate"
    )
    return target
