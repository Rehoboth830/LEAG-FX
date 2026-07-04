"""
Tests for src/research/build_volatility_features.py.
"""

import pandas as pd

from src.research.build_volatility_features import build_volatility_features


def test_build_volatility_features_produces_expected_columns():
    prices = pd.Series([100.0, 101.0, 99.0, 102.0, 103.0, 101.0, 104.0])
    dates = pd.Series(pd.date_range("2024-01-01", periods=7))

    features = build_volatility_features(prices, dates)

    assert list(features.columns) == [
        "observation_date",
        "volatility_5d",
        "volatility_20d",
        "volatility_60d",
    ]
    # 7 prices -> 6 returns -> 6 feature rows
    assert len(features) == 6


def test_volatility_features_are_nan_before_enough_data():
    prices = pd.Series(
        [100.0, 101.0, 102.0]
    )  # only 2 returns - not enough for a 5-day window
    dates = pd.Series(pd.date_range("2024-01-01", periods=3))

    features = build_volatility_features(prices, dates)

    assert features["volatility_5d"].isna().all()
