"""
Prediction target builder (Phase 7, Step 1).

Defines the target as: will the NEXT day's return be positive?
Binary classification target - the simplest, most interpretable
starting point, and Phase 5's findings warrant modest expectations,
not an ambitious multi-class or regression target on the first attempt.
"""

import pandas as pd

from src.common.logger import get_logger

logger = get_logger(__name__)


def build_direction_target(returns: pd.Series) -> pd.Series:
    """
    Builds a binary target: 1 if the return on date t+1 is positive,
    0 otherwise. The target for date t is aligned to date t (not t+1),
    since this is "what we're trying to predict as of date t" - the
    feature values on date t should predict this target.

    Args:
        returns: daily returns series, ordered by date.

    Returns:
        A pandas Series of 0/1 values, same index as returns, with the
        LAST value being NaN (no next day exists yet to know the answer).
    """
    next_day_return = returns.shift(-1)
    target = (next_day_return > 0).astype(float)
    target[next_day_return.isna()] = float("nan")

    logger.info(
        f"Built direction target: {target.notna().sum()} labeled rows, "
        f"{target.mean():.4f} positive rate"
    )
    return target
