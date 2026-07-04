"""
Tests for src/research/technical_indicators.py.

Per NFR-5.2: known, hand-calculable or logically certain cases.
"""

import pandas as pd

from src.research.technical_indicators import (
    compute_atr,
    compute_bollinger_bands,
    compute_ema,
    compute_macd,
    compute_rsi,
)


def test_ema_matches_price_when_span_is_one_and_flat_prices():
    prices = pd.Series([100.0, 100.0, 100.0])
    ema = compute_ema(prices, span=5)
    assert all(abs(ema - 100.0) < 1e-9)


def test_rsi_is_100_when_prices_only_rise():
    prices = pd.Series([100.0 + i for i in range(20)])  # steadily rising, never falls
    rsi = compute_rsi(prices, window=14)
    assert abs(rsi.iloc[-1] - 100.0) < 1e-9


def test_rsi_is_0_when_prices_only_fall():
    prices = pd.Series([100.0 - i for i in range(20)])  # steadily falling, never rises
    rsi = compute_rsi(prices, window=14)
    assert abs(rsi.iloc[-1] - 0.0) < 1e-9


def test_macd_line_is_positive_in_strong_uptrend():
    prices = pd.Series([100.0 + i * 2 for i in range(50)])  # strong, steady uptrend
    macd = compute_macd(prices)
    # Fast EMA should pull ahead of slow EMA in a strong uptrend.
    assert macd["macd_line"].iloc[-1] > 0


def test_atr_known_true_range():
    # A single, deliberately simple bar: high=110, low=100, prior close=105.
    # True range = max(high-low, |high-prevclose|, |low-prevclose|)
    #            = max(10, 5, 5) = 10.
    high = pd.Series([105.0, 110.0])
    low = pd.Series([95.0, 100.0])
    close = pd.Series([100.0, 105.0])

    # ATR with window=1 just reflects the true range directly, easiest
    # to hand-verify.
    atr = compute_atr(high, low, close, window=1)
    assert abs(atr.iloc[1] - 10.0) < 1e-9


def test_bollinger_bands_widen_with_higher_volatility():
    calm_prices = pd.Series([100.0, 100.1, 99.9, 100.0, 100.1] * 5)
    volatile_prices = pd.Series([100.0, 105.0, 95.0, 103.0, 97.0] * 5)

    calm_bands = compute_bollinger_bands(calm_prices, window=20)
    volatile_bands = compute_bollinger_bands(volatile_prices, window=20)

    calm_width = (calm_bands["bb_upper"] - calm_bands["bb_lower"]).iloc[-1]
    volatile_width = (volatile_bands["bb_upper"] - volatile_bands["bb_lower"]).iloc[-1]

    assert volatile_width > calm_width
