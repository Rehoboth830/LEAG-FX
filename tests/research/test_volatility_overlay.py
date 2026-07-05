"""
Tests for src/research/volatility_overlay.py.
"""

import pandas as pd

from src.research.volatility_overlay import apply_overlay, build_position_sizes


def test_build_position_sizes_reduces_on_high_regime():
    regimes = pd.Series(["low", "high", "medium", "high"])
    sizes = build_position_sizes(regimes, reduced_size=0.5)

    assert sizes.iloc[0] == 1.0
    assert sizes.iloc[1] == 0.5
    assert sizes.iloc[2] == 1.0
    assert sizes.iloc[3] == 0.5


def test_apply_overlay_known_scaling():
    returns = pd.Series([0.02, -0.04, 0.01])
    position_sizes = pd.Series([1.0, 0.5, 1.0])

    scaled = apply_overlay(returns, position_sizes)

    assert abs(scaled.iloc[0] - 0.02) < 1e-9
    assert abs(scaled.iloc[1] - (-0.02)) < 1e-9  # -0.04 * 0.5
    assert abs(scaled.iloc[2] - 0.01) < 1e-9


def test_overlay_reduces_volatility_on_known_scenario():
    # A scenario with one large move during a "high" regime day -
    # scaling it down should measurably reduce overall volatility.
    returns = pd.Series([0.01, -0.01, 0.05, -0.05, 0.01, -0.01])
    regimes = pd.Series(["low", "low", "high", "high", "low", "low"])

    sizes = build_position_sizes(regimes, reduced_size=0.5)
    scaled_returns = apply_overlay(returns, sizes)

    assert scaled_returns.std() < returns.std()
