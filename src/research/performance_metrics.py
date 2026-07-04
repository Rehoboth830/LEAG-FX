"""
Performance metrics module (Phase 5, Step 7).

Reusable functions for judging any strategy's performance honestly -
including the baseline itself. This is the vocabulary every future
phase (6 through 8) will use to compare results.
"""

from dataclasses import dataclass

import numpy as np
import pandas as pd

from src.common.logger import get_logger

logger = get_logger(__name__)

# Below this standard deviation, returns are treated as effectively
# constant/zero-volatility - avoids dividing by a floating-point
# near-zero value (e.g. 1e-18 instead of exact 0.0), which would
# otherwise produce a meaninglessly huge Sharpe ratio.
ZERO_VOLATILITY_THRESHOLD = 1e-10


@dataclass
class PerformanceMetrics:
    """Standard performance metrics for a series of strategy returns."""

    total_return: float
    annualized_return: float
    annualized_volatility: float
    sharpe_ratio: float
    max_drawdown: float
    win_rate: float


def compute_equity_curve(returns: pd.Series, starting_value: float = 1.0) -> pd.Series:
    """Converts a series of returns into a cumulative equity curve."""
    return starting_value * (1 + returns).cumprod()


def compute_max_drawdown(equity_curve: pd.Series) -> float:
    """
    Computes the maximum drawdown - the largest peak-to-trough decline
    in the equity curve, expressed as a negative decimal (e.g. -0.20 =
    a 20% drawdown at the worst point).
    """
    running_max = equity_curve.cummax()
    drawdown = (equity_curve - running_max) / running_max
    return float(drawdown.min())


def compute_sharpe_ratio(
    returns: pd.Series, risk_free_rate: float = 0.0, trading_days_per_year: int = 252
) -> float:
    """
    Computes the annualized Sharpe ratio: excess return per unit of
    volatility. Higher is better; a Sharpe near 0 means returns aren't
    compensating for the risk taken.
    """
    excess_returns = returns - (risk_free_rate / trading_days_per_year)
    if excess_returns.std() < ZERO_VOLATILITY_THRESHOLD:
        return 0.0
    return float(
        (excess_returns.mean() / excess_returns.std()) * np.sqrt(trading_days_per_year)
    )


def compute_win_rate(returns: pd.Series) -> float:
    """Fraction of periods with a positive return."""
    nonzero_returns = returns[returns != 0]
    if len(nonzero_returns) == 0:
        return 0.0
    return float((nonzero_returns > 0).mean())


def evaluate_strategy(
    returns: pd.Series, risk_free_rate: float = 0.0, trading_days_per_year: int = 252
) -> PerformanceMetrics:
    """
    Runs the full standard evaluation on a series of strategy returns.
    """
    equity_curve = compute_equity_curve(returns)
    total_return = float(equity_curve.iloc[-1] - 1) if len(equity_curve) > 0 else 0.0

    metrics = PerformanceMetrics(
        total_return=total_return,
        annualized_return=float(returns.mean() * trading_days_per_year),
        annualized_volatility=float(returns.std() * np.sqrt(trading_days_per_year)),
        sharpe_ratio=compute_sharpe_ratio(
            returns, risk_free_rate, trading_days_per_year
        ),
        max_drawdown=compute_max_drawdown(equity_curve),
        win_rate=compute_win_rate(returns),
    )

    logger.info(
        f"Strategy evaluation: total_return={metrics.total_return:.4f}, "
        f"sharpe={metrics.sharpe_ratio:.4f}, max_drawdown={metrics.max_drawdown:.4f}"
    )
    return metrics
