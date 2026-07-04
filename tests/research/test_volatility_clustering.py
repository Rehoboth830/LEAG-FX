"""
Tests for the volatility clustering check in
src/research/autocorrelation.py.

Per NFR-5.2: synthetic data with KNOWN volatility clustering (a simple
ARCH-like process where volatility depends on the prior period's
squared return) vs. i.i.d. noise (no clustering), proving the test
correctly tells them apart.
"""

import numpy as np
import pandas as pd

from src.research.autocorrelation import analyze_autocorrelation


def test_detects_known_volatility_clustering():
    np.random.seed(42)
    n = 1000
    returns = np.zeros(n)
    returns[0] = np.random.normal(0, 1)
    for t in range(1, n):
        # Volatility this period depends on the size of the prior move -
        # a simple, deliberate ARCH-style clustering effect.
        vol = 0.2 + 0.7 * (returns[t - 1] ** 2)
        returns[t] = np.random.normal(0, np.sqrt(vol))

    squared_returns = pd.Series(returns) ** 2
    result = analyze_autocorrelation(squared_returns, n_lags=10)

    assert result.has_significant_autocorrelation


def test_no_volatility_clustering_in_iid_noise():
    np.random.seed(42)
    iid_returns = pd.Series(np.random.normal(0, 1, 1000))

    squared_returns = iid_returns**2
    result = analyze_autocorrelation(squared_returns, n_lags=10)

    assert not result.has_significant_autocorrelation
