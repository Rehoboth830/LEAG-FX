"""
Stationarity testing module (Phase 5, Step 2).

Uses the Augmented Dickey-Fuller (ADF) test to formally check whether
a series is stationary - i.e., whether its statistical properties
(mean, variance) stay consistent over time, rather than drifting.
"""

from dataclasses import dataclass

import pandas as pd
from statsmodels.tsa.stattools import adfuller

from src.common.logger import get_logger

logger = get_logger(__name__)


@dataclass
class StationarityResult:
    """Result of an Augmented Dickey-Fuller stationarity test."""

    adf_statistic: float
    p_value: float
    critical_value_1pct: float
    critical_value_5pct: float
    critical_value_10pct: float
    is_stationary: bool  # True if p_value < 0.05


def check_stationarity(series: pd.Series) -> StationarityResult:
    """
    Runs the Augmented Dickey-Fuller test on a series.

    The null hypothesis is that the series has a unit root (i.e., is
    NOT stationary). A low p-value (< 0.05) lets us reject that null,
    meaning we have evidence the series IS stationary.

    Note: deliberately NOT named test_stationarity - pytest treats any
    function starting with "test_" as a test to collect and run, which
    causes a real collision if this function is ever imported into a
    test file.

    Args:
        series: a pandas Series to test (e.g., price levels or returns).

    Returns:
        A StationarityResult with the test statistic, p-value, critical
        values, and a boolean conclusion.
    """
    clean_series = series.dropna()
    result = adfuller(clean_series)

    stationarity_result = StationarityResult(
        adf_statistic=result[0],
        p_value=result[1],
        critical_value_1pct=result[4]["1%"],
        critical_value_5pct=result[4]["5%"],
        critical_value_10pct=result[4]["10%"],
        is_stationary=result[1] < 0.05,
    )

    logger.info(
        f"ADF test: statistic={stationarity_result.adf_statistic:.4f}, "
        f"p-value={stationarity_result.p_value:.4f}, "
        f"stationary={stationarity_result.is_stationary}"
    )
    return stationarity_result
