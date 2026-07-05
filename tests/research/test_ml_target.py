"""
Tests for src/research/ml_target.py.
"""

import pandas as pd

from src.research.ml_target import build_direction_target


def test_target_correctly_labels_known_up_and_down_moves():
    # Returns: +1%, -1%, +2%, -3% -> targets (next day's direction):
    # day0's target = day1's direction = negative -> 0
    # day1's target = day2's direction = positive -> 1
    # day2's target = day3's direction = negative -> 0
    # day3's target = no next day -> NaN
    returns = pd.Series([0.01, -0.01, 0.02, -0.03])
    target = build_direction_target(returns)

    assert target.iloc[0] == 0.0
    assert target.iloc[1] == 1.0
    assert target.iloc[2] == 0.0
    assert pd.isna(target.iloc[3])


def test_target_positive_rate_matches_known_proportion():
    # 3 positive next-moves out of 4 labeled rows.
    returns = pd.Series([0.01, 0.01, 0.01, -0.01, 0.01])
    target = build_direction_target(returns)

    labeled = target.dropna()
    assert abs(labeled.mean() - 0.75) < 1e-9
