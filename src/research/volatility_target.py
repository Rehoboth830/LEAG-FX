"""
Volatility target and classification baselines (Phase 7 pivot).

Predicting volatility is a genuinely different task than predicting
direction - it's a risk-management input, not a trade itself. Evaluated
with classification accuracy against naive baselines, not Sharpe ratio.
"""

import pandas as pd

from src.common.logger import get_logger

logger = get_logger(__name__)


def build_volatility_target(regime_labels: pd.Series) -> pd.Series:
    """
    Builds a binary target: will TOMORROW be a "high" volatility regime?
    """
    next_day_regime = regime_labels.shift(-1)
    target = (next_day_regime == "high").astype(float)
    target[next_day_regime.isna()] = float("nan")
    return target


def persistence_baseline_accuracy(regime_labels: pd.Series) -> float:
    """
    The naive baseline for THIS task: "tomorrow's regime will be the
    same as today's" - a legitimate baseline given Phase 5 proved
    volatility clusters (today's regime IS informative about tomorrow's).

    Note: the validity mask is built from the RAW shifted labels
    (checking NaN before the "== 'high'" comparison), since comparing
    NaN == "high" silently returns False rather than NaN, which would
    otherwise corrupt the last row instead of correctly excluding it.
    """
    next_day_regime = regime_labels.shift(-1)
    valid = next_day_regime.notna()

    actual_next_day_high = (next_day_regime == "high").astype(float)
    predicted_next_day_high = (regime_labels == "high").astype(float)

    accuracy = (actual_next_day_high[valid] == predicted_next_day_high[valid]).mean()
    return float(accuracy)


def majority_class_baseline_accuracy(target: pd.Series) -> float:
    """The other naive baseline: always predict the more common class."""
    valid_target = target.dropna()
    majority_class = valid_target.mode()[0]
    return float((valid_target == majority_class).mean())
