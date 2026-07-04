"""
Tests for src/research/baselines.py.

Per NFR-5.2: deliberately constructed price series where the correct
behavior is known in advance.
"""

import pandas as pd

from src.research.baselines import buy_and_hold_returns, sma_crossover_returns


def test_buy_and_hold_applies_cost_only_once():
    prices = pd.Series([100.0, 101.0, 102.0, 103.0])
    returns = buy_and_hold_returns(prices, spread_cost=0.001)

    # First return: (101-100)/100 - 0.001 = 0.01 - 0.001 = 0.009
    assert abs(returns.iloc[0] - 0.009) < 1e-9
    # Later returns have NO cost applied - only entry incurs it.
    assert abs(returns.iloc[1] - (102.0 - 101.0) / 101.0) < 1e-9


def test_sma_crossover_goes_long_when_short_above_long():
    # A steadily rising price series - the short-term average should
    # stay above the long-term average through most of it, so the
    # strategy should be long (not flat) for the majority of the
    # period once both averages have enough data.
    prices = pd.Series([100.0 + i * 0.5 for i in range(100)])  # steady uptrend

    returns = sma_crossover_returns(
        prices, short_window=5, long_window=20, spread_cost=0.0
    )

    # In a clean, steady uptrend, most captured returns should be
    # positive, since the strategy should be long most of the time.
    assert (returns > 0).mean() > 0.7


def test_sma_crossover_stays_flat_in_flat_market():
    # A perfectly flat price series - short and long SMAs are equal,
    # so the strategy should never go long, meaning zero returns
    # throughout (no position ever taken).
    prices = pd.Series([100.0] * 100)

    returns = sma_crossover_returns(
        prices, short_window=5, long_window=20, spread_cost=0.001
    )

    assert (returns == 0).all()


def test_sma_crossover_applies_cost_on_position_change():
    # A price series designed to cross the SMA threshold exactly once,
    # triggering exactly one position change and one cost charge.
    prices = pd.Series([100.0] * 25 + [110.0] * 25)  # a clean, one-time jump

    returns_with_cost = sma_crossover_returns(
        prices, short_window=5, long_window=20, spread_cost=0.01
    )
    returns_no_cost = sma_crossover_returns(
        prices, short_window=5, long_window=20, spread_cost=0.0
    )

    # With a cost applied, total returns should be strictly lower than
    # without, since at least one position change occurs.
    assert returns_with_cost.sum() < returns_no_cost.sum()
