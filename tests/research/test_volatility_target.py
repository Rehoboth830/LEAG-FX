"""
Tests for src/research/volatility_target.py.
"""

import pandas as pd

from src.research.volatility_target import (
    build_volatility_target,
    majority_class_baseline_accuracy,
    persistence_baseline_accuracy,
)


def test_build_volatility_target_known_sequence():
    regimes = pd.Series(["low", "high", "high", "medium"])
    target = build_volatility_target(regimes)

    assert target.iloc[0] == 1.0  # tomorrow (index 1) is "high"
    assert target.iloc[1] == 1.0  # tomorrow (index 2) is "high"
    assert target.iloc[2] == 0.0  # tomorrow (index 3) is "medium"
    assert pd.isna(target.iloc[3])  # no tomorrow


def test_persistence_baseline_perfect_when_regime_never_changes():
    regimes = pd.Series(["high"] * 10)
    accuracy = persistence_baseline_accuracy(regimes)
    assert accuracy == 1.0


def test_majority_class_baseline_known_proportion():
    target = pd.Series([1.0, 1.0, 1.0, 0.0])  # 75% are class 1.0
    accuracy = majority_class_baseline_accuracy(target)
    assert abs(accuracy - 0.75) < 1e-9
