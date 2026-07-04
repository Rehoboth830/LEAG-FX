"""
Tests for src/research/performance_metrics.py.

Per NFR-5.2: known, hand-calculable synthetic examples.
"""

import pandas as pd

from src.research.performance_metrics import (
    compute_equity_curve,
    compute_max_drawdown,
    compute_sharpe_ratio,
    compute_win_rate,
    evaluate_strategy,
)


def test_compute_equity_curve_known_values():
    returns = pd.Series([0.10, -0.10])  # +10%, then -10%
    equity = compute_equity_curve(returns, starting_value=1.0)

    assert abs(equity.iloc[0] - 1.10) < 1e-9
    assert abs(equity.iloc[1] - 0.99) < 1e-9  # 1.10 * 0.90 = 0.99


def test_compute_max_drawdown_known_scenario():
    # Equity rises to 1.20, falls to 0.90 (a 25% drawdown from peak),
    # then partially recovers to 1.05.
    equity = pd.Series([1.0, 1.20, 0.90, 1.05])
    max_dd = compute_max_drawdown(equity)

    # (0.90 - 1.20) / 1.20 = -0.25
    assert abs(max_dd - (-0.25)) < 1e-9


def test_compute_win_rate_known_scenario():
    returns = pd.Series([0.01, -0.01, 0.02, -0.03, 0.01])  # 3 wins, 2 losses
    win_rate = compute_win_rate(returns)

    assert abs(win_rate - 0.6) < 1e-9


def test_compute_sharpe_ratio_zero_for_constant_returns_with_zero_volatility():
    # No volatility at all -> Sharpe is defined as 0.0 by this
    # function's convention (avoids divide-by-zero).
    returns = pd.Series([0.01] * 10)
    sharpe = compute_sharpe_ratio(returns)

    assert sharpe == 0.0


def test_evaluate_strategy_returns_consistent_total_return():
    returns = pd.Series([0.10, -0.10])
    metrics = evaluate_strategy(returns)

    assert abs(metrics.total_return - (-0.01)) < 1e-9  # 1.10*0.90 - 1 = -0.01
