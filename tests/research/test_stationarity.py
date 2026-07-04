"""
Tests for src/research/stationarity.py.

Per NFR-5.2, uses synthetic data with a KNOWN correct answer: a random
walk (known non-stationary) and white noise (known stationary), proving
the test correctly tells them apart.
"""

import numpy as np
import pandas as pd

from src.research.stationarity import check_stationarity


def test_detects_nonstationary_random_walk():
    np.random.seed(42)
    random_walk = pd.Series(np.cumsum(np.random.normal(0, 1, 500)))

    result = check_stationarity(random_walk)

    assert not result.is_stationary
    assert result.p_value >= 0.05


def test_detects_stationary_white_noise():
    np.random.seed(42)
    white_noise = pd.Series(np.random.normal(0, 1, 500))

    result = check_stationarity(white_noise)

    assert result.is_stationary
    assert result.p_value < 0.05
