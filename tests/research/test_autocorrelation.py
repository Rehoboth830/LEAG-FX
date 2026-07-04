"""
Tests for src/research/autocorrelation.py.

Per NFR-5.2: an AR(1) process (known, real autocorrelation by
construction) vs. white noise (known, no autocorrelation), proving the
test correctly tells them apart.
"""

import numpy as np
import pandas as pd

from src.research.autocorrelation import analyze_autocorrelation


def test_detects_known_autocorrelation_in_ar1_process():
    np.random.seed(42)
    n = 1000
    phi = 0.7  # strong, deliberate autocorrelation coefficient
    series = np.zeros(n)
    noise = np.random.normal(0, 1, n)
    for t in range(1, n):
        series[t] = phi * series[t - 1] + noise[t]

    result = analyze_autocorrelation(pd.Series(series), n_lags=10)

    assert result.has_significant_autocorrelation
    # Lag-1 autocorrelation should be positive and reasonably close to phi.
    assert result.acf_values[0] > 0.5


def test_detects_no_autocorrelation_in_white_noise():
    np.random.seed(42)
    white_noise = pd.Series(np.random.normal(0, 1, 1000))

    result = analyze_autocorrelation(white_noise, n_lags=10)

    assert not result.has_significant_autocorrelation
