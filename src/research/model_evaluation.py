"""
Model evaluation harness (Phase 7, Step 3).

Converts a model's binary predictions into actual strategy returns
(with realistic transaction costs), evaluates them with the same
performance_metrics module from Phase 5, and checks the result against
the real baseline bar - so every model is judged consistently,
automatically, and honestly against the Kill Criteria threshold.
"""

import pandas as pd

from src.common.logger import get_logger
from src.research.performance_metrics import PerformanceMetrics, evaluate_strategy

logger = get_logger(__name__)

DEFAULT_SPREAD_COST = 0.0002

# The real, evidence-based bar from Phase 5 (Buy and Hold baseline).
BASELINE_SHARPE = 0.5436
BASELINE_MAX_DRAWDOWN = -0.1475


def predictions_to_strategy_returns(
    predictions: pd.Series,
    actual_returns: pd.Series,
    spread_cost: float = DEFAULT_SPREAD_COST,
) -> pd.Series:
    """
    Converts binary predictions (1 = predict positive, 0 = predict
    negative/flat) into real strategy returns: go long when predicted
    positive, stay flat otherwise. Transaction cost applied on every
    position change, same discipline as the Phase 5 SMA baseline.

    Args:
        predictions: binary (0/1) predictions, aligned to actual_returns.
        actual_returns: the REAL return that occurred on each date.
        spread_cost: cost fraction applied on every position change.

    Returns:
        A series of net strategy returns.
    """
    position = predictions.astype(float)
    strategy_returns = position * actual_returns

    position_changes = (
        position.diff().abs().fillna(position.iloc[0] if len(position) > 0 else 0)
    )
    cost_drag = position_changes * spread_cost

    return (strategy_returns - cost_drag).dropna()


def beats_baseline(metrics: PerformanceMetrics) -> dict:
    """
    Checks a model's performance against the real Phase 5 baseline bar,
    per the Kill Criteria document. A model must beat BOTH Sharpe and
    max drawdown to be considered a genuine improvement.

    Returns:
        A dict with the comparison result and a plain-language verdict.
    """
    beats_sharpe = metrics.sharpe_ratio > BASELINE_SHARPE
    beats_drawdown = (
        metrics.max_drawdown > BASELINE_MAX_DRAWDOWN
    )  # less negative = better

    result = {
        "beats_sharpe": beats_sharpe,
        "beats_drawdown": beats_drawdown,
        "beats_baseline_overall": beats_sharpe and beats_drawdown,
        "model_sharpe": metrics.sharpe_ratio,
        "baseline_sharpe": BASELINE_SHARPE,
        "model_max_drawdown": metrics.max_drawdown,
        "baseline_max_drawdown": BASELINE_MAX_DRAWDOWN,
    }

    logger.info(
        f"Baseline comparison: beats_overall={result['beats_baseline_overall']} "
        f"(sharpe {metrics.sharpe_ratio:.4f} vs {BASELINE_SHARPE:.4f})"
    )
    return result


def evaluate_model_predictions(
    predictions: pd.Series, actual_returns: pd.Series
) -> dict:
    """
    Full pipeline: predictions -> strategy returns -> metrics -> baseline
    comparison, in one call.
    """
    strategy_returns = predictions_to_strategy_returns(predictions, actual_returns)
    metrics = evaluate_strategy(strategy_returns)
    comparison = beats_baseline(metrics)

    return {"metrics": metrics, "comparison": comparison}
