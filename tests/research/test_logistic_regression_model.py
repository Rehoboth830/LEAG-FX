"""
Tests for src/research/logistic_regression_model.py.

Uses a deliberately easy, separable synthetic dataset - if the model
can't learn THIS pattern, something is genuinely broken in the wiring,
not just "the market is hard to predict."
"""

import numpy as np
import pandas as pd

from src.research.logistic_regression_model import (
    FEATURE_COLUMNS,
    train_and_predict_walk_forward,
)


def test_learns_an_obviously_separable_pattern():
    np.random.seed(42)
    n = 700

    # A deliberately trivial, perfectly learnable rule: target = 1
    # whenever "volatility_5d" (reused here as a stand-in feature) is
    # above 0, else 0 - noise added to other columns to keep the
    # feature set realistic in shape.
    df = pd.DataFrame({col: np.random.normal(0, 1, n) for col in FEATURE_COLUMNS})
    df["target"] = (df["volatility_5d"] > 0).astype(float)

    predictions = train_and_predict_walk_forward(df, train_window=500, test_window=100)

    valid = predictions.dropna()
    actual = df.loc[valid.index, "target"]

    accuracy = (valid == actual).mean()
    # An easy, perfectly separable rule should be learned with high
    # accuracy - well above random guessing (0.5).
    assert accuracy > 0.85
