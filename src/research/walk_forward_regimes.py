"""
Walk-forward regime classification (Phase 8, Step 5).

Fixes a real look-ahead risk found in Step 4: the original
classify_regimes() used FULL-SAMPLE percentile thresholds, meaning
"high volatility" was defined partly using data from the future
relative to any historical point in time. This version computes
thresholds using ONLY data known up to (not including) each date -
a genuinely point-in-time-correct classification.
"""

import pandas as pd

from src.common.logger import get_logger

logger = get_logger(__name__)


def classify_regimes_expanding_window(
    rolling_vol: pd.Series, min_history: int = 252
) -> pd.Series:
    """
    Classifies each date's volatility regime using ONLY historical data
    known strictly before that date - never using future information,
    unlike the full-sample version used in Phase 5/Step 4.

    Args:
        rolling_vol: rolling volatility series, ordered by date.
        min_history: minimum number of prior observations required
            before classification begins (252 ~ one trading year) -
            avoids unstable thresholds from too little history.

    Returns:
        A series of "low"/"medium"/"high" labels, with None for the
        initial warm-up period where insufficient history exists yet.
    """
    labels = pd.Series(index=rolling_vol.index, dtype=object)

    for i in range(len(rolling_vol)):
        if i < min_history:
            labels.iloc[i] = None
            continue

        # Only data STRICTLY BEFORE index i - today's own value is not
        # included in defining today's thresholds, avoiding any
        # same-day circularity as well as future leakage.
        historical_vol = rolling_vol.iloc[:i].dropna()
        if len(historical_vol) < min_history:
            labels.iloc[i] = None
            continue

        low_threshold = historical_vol.quantile(0.33)
        high_threshold = historical_vol.quantile(0.67)

        current_value = rolling_vol.iloc[i]
        if pd.isna(current_value):
            labels.iloc[i] = None
        elif current_value <= low_threshold:
            labels.iloc[i] = "low"
        elif current_value >= high_threshold:
            labels.iloc[i] = "high"
        else:
            labels.iloc[i] = "medium"

    logger.info(
        f"Expanding-window regime classification: {labels.notna().sum()} classified dates"
    )
    return labels
