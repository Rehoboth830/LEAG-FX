"""
Tests for src/research/correlation.py.

Per NFR-5.2: a deliberately constructed correlated pair (known,
positive relationship) vs. two independent random series (known,
no relationship), proving the test correctly tells them apart.
"""

import numpy as np
import pandas as pd

from src.research.correlation import compute_correlation


def test_detects_known_strong_positive_correlation():
    np.random.seed(42)
    n = 200
    series_a = pd.Series(np.random.normal(0, 1, n))
    # series_b deliberately built to be strongly correlated with series_a
    series_b = series_a * 2 + np.random.normal(0, 0.1, n)

    result = compute_correlation(series_a, series_b)

    assert result.is_significant
    assert result.correlation_coefficient > 0.9


def test_no_correlation_between_independent_series():
    np.random.seed(42)
    n = 200
    series_a = pd.Series(np.random.normal(0, 1, n))
    series_b = pd.Series(np.random.normal(0, 1, n))  # independent, unrelated

    result = compute_correlation(series_a, series_b)

    assert not result.is_significant
