"""
Volatility regime analysis module (Phase 5, Step 5).

Builds on the volatility clustering finding (Step 3 follow-up) by
classifying each period into a volatility regime (low/medium/high)
using rolling volatility, so we can compare behavior across genuinely
different market conditions rather than treating the whole 10-year
history as one uniform thing.
"""

from dataclasses import dataclass

import numpy as np
import pandas as pd

from src.common.logger import get_logger

logger = get_logger(__name__)


@dataclass
class RegimeThresholds:
    """The volatility thresholds used to classify regimes."""

    low_threshold: float  # 33rd percentile of rolling volatility
    high_threshold: float  # 67th percentile of rolling volatility


def compute_rolling_volatility(returns: pd.Series, window: int = 20) -> pd.Series:
    """
    Computes rolling annualized volatility over a window of days.

    Args:
        returns: daily returns series.
        window: rolling window size in days (20 ~ one trading month).

    Returns:
        A pandas Series of rolling annualized volatility, same index
        as returns (with NaN for the first `window` days).
    """
    rolling_std = returns.rolling(window=window).std()
    annualized = rolling_std * np.sqrt(252)
    return annualized


def classify_regimes(rolling_vol: pd.Series) -> tuple:
    """
    Classifies each period into "low", "medium", or "high" volatility
    regime, based on terciles (33rd/67th percentiles) of the rolling
    volatility series itself - so thresholds are derived from the data,
    not arbitrarily chosen.

    Args:
        rolling_vol: rolling volatility series (e.g. from
            compute_rolling_volatility).

    Returns:
        A tuple of (regime_labels: pd.Series, thresholds: RegimeThresholds).
    """
    clean_vol = rolling_vol.dropna()
    low_threshold = clean_vol.quantile(0.33)
    high_threshold = clean_vol.quantile(0.67)

    def label(v):
        if pd.isna(v):
            return None
        if v <= low_threshold:
            return "low"
        elif v >= high_threshold:
            return "high"
        else:
            return "medium"

    regime_labels = rolling_vol.apply(label)
    thresholds = RegimeThresholds(
        low_threshold=float(low_threshold), high_threshold=float(high_threshold)
    )

    logger.info(
        f"Regime classification: low<={thresholds.low_threshold:.4f}, "
        f"high>={thresholds.high_threshold:.4f}"
    )
    return regime_labels, thresholds
