"""
Tests for src/agents/technical_analyst.py.
"""

from src.agents.technical_analyst import analyze


def test_oversold_and_bullish_macd_produces_buy():
    report = analyze(
        rsi_14=25.0,
        macd_histogram=0.5,
        close_price=150.0,
        bb_upper=155.0,
        bb_lower=148.0,
    )
    assert report.verdict == "buy"


def test_overbought_and_bearish_macd_produces_sell():
    report = analyze(
        rsi_14=75.0,
        macd_histogram=-0.5,
        close_price=150.0,
        bb_upper=155.0,
        bb_lower=145.0,
    )
    assert report.verdict == "sell"


def test_confidence_is_deliberately_low():
    report = analyze(
        rsi_14=50.0,
        macd_histogram=0.1,
        close_price=150.0,
        bb_upper=155.0,
        bb_lower=145.0,
    )
    assert report.confidence <= 0.5


def test_risks_disclose_phase7_finding():
    report = analyze(
        rsi_14=50.0,
        macd_histogram=0.1,
        close_price=150.0,
        bb_upper=155.0,
        bb_lower=145.0,
    )
    assert any("Phase 7" in risk for risk in report.risks)
