"""
Tests for src/research/model_evaluation.py.
"""

import numpy as np
import pandas as pd

from src.research.model_evaluation import (
    beats_baseline,
    predictions_to_strategy_returns,
)
from src.research.performance_metrics import evaluate_strategy


def test_predictions_to_returns_only_captures_predicted_long_days():
    predictions = pd.Series([1.0, 0.0, 1.0])
    actual_returns = pd.Series([0.02, 0.03, -0.01])

    strategy_returns = predictions_to_strategy_returns(
        predictions, actual_returns, spread_cost=0.0
    )

    assert abs(strategy_returns.iloc[0] - 0.02) < 1e-9
    assert abs(strategy_returns.iloc[1] - 0.0) < 1e-9
    assert abs(strategy_returns.iloc[2] - (-0.01)) < 1e-9


def test_predictions_to_returns_applies_cost_on_position_change():
    predictions = pd.Series([1.0, 1.0, 0.0])
    actual_returns = pd.Series([0.01, 0.01, 0.01])

    with_cost = predictions_to_strategy_returns(
        predictions, actual_returns, spread_cost=0.01
    )
    without_cost = predictions_to_strategy_returns(
        predictions, actual_returns, spread_cost=0.0
    )

    assert with_cost.sum() < without_cost.sum()


def test_beats_baseline_correctly_identifies_a_strong_result():
    # A genuinely strong result needs real variability with a positive
    # mean - NOT constant returns, which have zero volatility and
    # correctly produce a Sharpe of 0.0 by this project's own convention
    # (see performance_metrics.py's ZERO_VOLATILITY_THRESHOLD handling).
    np.random.seed(1)
    strong_returns = pd.Series(np.random.normal(0.003, 0.005, 300))
    metrics = evaluate_strategy(strong_returns)

    result = beats_baseline(metrics)

    assert result["beats_baseline_overall"]


def test_beats_baseline_correctly_identifies_a_weak_result():
    np.random.seed(42)
    weak_returns = pd.Series(np.random.normal(0, 0.01, 100))
    metrics = evaluate_strategy(weak_returns)

    result = beats_baseline(metrics)

    assert not result["beats_baseline_overall"]
