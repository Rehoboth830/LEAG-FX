"""
Descriptive statistics module (Phase 5, Step 1).

Computes returns and basic statistical characterization of price data.
This is the foundation every later Phase 5 step builds on.
"""

from dataclasses import dataclass

import numpy as np
import pandas as pd

from src.common.logger import get_logger

logger = get_logger(__name__)


@dataclass
class DescriptiveStats:
    """Summary statistics for a series of returns."""

    count: int
    mean: float
    std_dev: float
    min_value: float
    max_value: float
    skewness: float
    kurtosis: float
    percentile_5: float
    percentile_25: float
    median: float
    percentile_75: float
    percentile_95: float
    annualized_return: float
    annualized_volatility: float


def compute_daily_returns(prices: pd.Series) -> pd.Series:
    """
    Computes simple daily percentage returns from a price series.

    Args:
        prices: a pandas Series of prices, ordered by time.

    Returns:
        A pandas Series of daily returns (as decimals, e.g. 0.01 = 1%).
        The first value is dropped since there's no prior day to compare to.
    """
    returns = prices.pct_change().dropna()
    return returns


def compute_descriptive_stats(
    returns: pd.Series, trading_days_per_year: int = 252
) -> DescriptiveStats:
    """
    Computes standard descriptive statistics for a series of returns.

    Args:
        returns: a pandas Series of daily returns (decimals).
        trading_days_per_year: used to annualize return/volatility figures;
            252 is the standard convention for daily financial data.

    Returns:
        A DescriptiveStats object with the full summary.
    """
    stats = DescriptiveStats(
        count=len(returns),
        mean=float(returns.mean()),
        std_dev=float(returns.std()),
        min_value=float(returns.min()),
        max_value=float(returns.max()),
        skewness=float(returns.skew()),
        kurtosis=float(returns.kurtosis()),
        percentile_5=float(returns.quantile(0.05)),
        percentile_25=float(returns.quantile(0.25)),
        median=float(returns.median()),
        percentile_75=float(returns.quantile(0.75)),
        percentile_95=float(returns.quantile(0.95)),
        annualized_return=float(returns.mean() * trading_days_per_year),
        annualized_volatility=float(returns.std() * np.sqrt(trading_days_per_year)),
    )

    logger.info(
        f"Descriptive stats computed on {stats.count} returns: "
        f"mean={stats.mean:.6f}, std={stats.std_dev:.6f}"
    )
    return stats
