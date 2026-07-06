"""
Tests for src/research/bootstrap_significance.py.

Per NFR-5.2: a case with a genuine, large, obvious advantage (should
show significance), and a case with no real difference at all
(should NOT show significance) - proving the test tells them apart.
"""

import numpy as np
import pandas as pd

from src.research.bootstrap_significance import paired_bootstrap_sharpe_test


def test_detects_obvious_genuine_advantage():
    np.random.seed(1)
    n = 100
    # Model has a real, large, consistent edge over baseline.
    model_returns = pd.Series(np.random.normal(0.02, 0.01, n))
    baseline_returns = pd.Series(np.random.normal(0.001, 0.01, n))

    result = paired_bootstrap_sharpe_test(
        model_returns, baseline_returns, n_iterations=1000
    )

    assert result["significant_at_95pct"]
    assert result["proportion_bootstrap_favoring_model"] > 0.9


def test_no_significance_when_series_are_identical():
    np.random.seed(1)
    n = 100
    returns = pd.Series(np.random.normal(0.005, 0.01, n))

    # Model and baseline are THE SAME series - zero real difference.
    result = paired_bootstrap_sharpe_test(returns, returns, n_iterations=1000)

    assert not result["significant_at_95pct"]
    assert abs(result["observed_sharpe_difference"]) < 1e-9
