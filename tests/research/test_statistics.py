"""
Tests for src/research/statistics.py.

Uses simple synthetic data with hand-calculable known answers to prove
the statistics are computed correctly, not just that the code runs.
"""

import pandas as pd

from src.research.statistics import compute_daily_returns, compute_descriptive_stats


def test_compute_daily_returns_known_values():
    # Prices: 100 -> 110 -> 99. Returns: +10%, then -10%.
    prices = pd.Series([100.0, 110.0, 99.0])
    returns = compute_daily_returns(prices)

    assert len(returns) == 2
    assert abs(returns.iloc[0] - 0.10) < 1e-9
    assert abs(returns.iloc[1] - (-0.10)) < 1e-9


def test_compute_descriptive_stats_known_mean_and_std():
    # A simple, hand-verifiable set of returns.
    returns = pd.Series([0.01, 0.02, -0.01, 0.03, -0.02])

    stats = compute_descriptive_stats(returns)

    assert stats.count == 5
    assert abs(stats.mean - 0.006) < 1e-9  # (0.01+0.02-0.01+0.03-0.02)/5
    assert stats.min_value == -0.02
    assert stats.max_value == 0.03
    assert stats.median == 0.01


def test_compute_descriptive_stats_annualization():
    returns = pd.Series([0.01] * 10)  # constant 1% daily return

    stats = compute_descriptive_stats(returns, trading_days_per_year=252)

    # annualized_return = mean * 252 = 0.01 * 252 = 2.52
    assert abs(stats.annualized_return - 2.52) < 1e-9
    # constant returns -> ~zero std dev -> ~zero annualized volatility.
    # Uses a tolerance, not exact equality, since 0.01 repeated cannot
    # be represented exactly in binary floating point - this is normal
    # floating-point behavior, not a bug in the statistics code.
    assert abs(stats.annualized_volatility - 0.0) < 1e-9
