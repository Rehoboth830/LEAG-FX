"""
Tests for src/research/random_forest_model.py.
"""

import numpy as np
import pandas as pd

from src.research.random_forest_model import (
    FEATURE_COLUMNS,
    train_and_predict_walk_forward,
)


def test_learns_an_obviously_separable_pattern():
    np.random.seed(42)
    n = 700

    df = pd.DataFrame({col: np.random.normal(0, 1, n) for col in FEATURE_COLUMNS})
    df["target"] = (df["volatility_5d"] > 0).astype(float)

    predictions = train_and_predict_walk_forward(df, train_window=500, test_window=100)

    valid = predictions.dropna()
    actual = df.loc[valid.index, "target"]

    accuracy = (valid == actual).mean()
    assert accuracy > 0.85
