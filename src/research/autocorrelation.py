"""
Autocorrelation analysis module (Phase 5, Step 3).

Tests whether past returns have any statistically detectable
relationship with future returns - the most basic possible test of
whether trend-following or mean-reversion ideas have any real
statistical foundation, as opposed to pure randomness.
"""

from dataclasses import dataclass

import pandas as pd
from statsmodels.stats.diagnostic import acorr_ljungbox
from statsmodels.tsa.stattools import acf

from src.common.logger import get_logger

logger = get_logger(__name__)


@dataclass
class AutocorrelationResult:
    """Result of autocorrelation analysis at a set of lags."""

    acf_values: list  # autocorrelation coefficient at each lag, 1..n
    ljung_box_statistic: float
    ljung_box_p_value: float
    has_significant_autocorrelation: bool  # True if p_value < 0.05


def analyze_autocorrelation(
    series: pd.Series, n_lags: int = 10
) -> AutocorrelationResult:
    """
    Computes the autocorrelation function and runs the Ljung-Box test.

    The Ljung-Box test's null hypothesis is that the data has NO
    autocorrelation (is independently distributed / random). A low
    p-value (< 0.05) lets us reject that null, meaning we have evidence
    of real, statistically significant autocorrelation.

    Args:
        series: a pandas Series to test (typically daily returns).
        n_lags: how many lags to test, e.g. 10 = up to 10 days back.

    Returns:
        An AutocorrelationResult with per-lag ACF values and the
        overall Ljung-Box significance conclusion.
    """
    clean_series = series.dropna()

    acf_values = acf(clean_series, nlags=n_lags, fft=True)[
        1:
    ]  # drop lag 0 (always 1.0)

    lb_result = acorr_ljungbox(clean_series, lags=[n_lags], return_df=True)
    lb_statistic = float(lb_result["lb_stat"].iloc[0])
    lb_p_value = float(lb_result["lb_pvalue"].iloc[0])

    result = AutocorrelationResult(
        acf_values=list(acf_values),
        ljung_box_statistic=lb_statistic,
        ljung_box_p_value=lb_p_value,
        has_significant_autocorrelation=lb_p_value < 0.05,
    )

    logger.info(
        f"Autocorrelation analysis: Ljung-Box p-value={lb_p_value:.4f}, "
        f"significant={result.has_significant_autocorrelation}"
    )
    return result
