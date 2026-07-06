"""
Tests for src/research/horizon_target.py.
"""

import pandas as pd

from src.research.horizon_target import (
    build_horizon_direction_target,
    build_horizon_return,
)


def test_horizon_return_known_values():
    # 5-day horizon: price at index 0 is 100, price at index 5 is 110.
    prices = pd.Series([100.0, 101, 102, 103, 104, 110.0])
    horizon_return = build_horizon_return(prices, horizon_days=5)

    assert abs(horizon_return.iloc[0] - 0.10) < 1e-9  # (110-100)/100
    assert pd.isna(horizon_return.iloc[5])  # no future data 5 days beyond the last row


def test_horizon_direction_target_known_up_and_down():
    # horizon=2: index0 -> index2 (100->105, up), index1 -> index3 (101->95, down)
    prices = pd.Series([100.0, 101.0, 105.0, 95.0])
    target = build_horizon_direction_target(prices, horizon_days=2)

    assert target.iloc[0] == 1.0
    assert target.iloc[1] == 0.0
    assert pd.isna(target.iloc[2])
    assert pd.isna(target.iloc[3])
