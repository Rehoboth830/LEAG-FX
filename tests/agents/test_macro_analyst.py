"""
Tests for src/agents/macro_analyst.py.
"""

from src.agents.macro_analyst import analyze


def test_wide_stable_differential_produces_buy():
    report = analyze(
        current_differential=4.5, differential_3m_ago=4.3, differential_12m_ago=4.0
    )
    assert report.verdict == "buy"


def test_narrow_differential_produces_sell():
    report = analyze(
        current_differential=0.2, differential_3m_ago=0.5, differential_12m_ago=1.0
    )
    assert report.verdict == "sell"


def test_moderate_stable_differential_produces_hold():
    report = analyze(
        current_differential=1.5, differential_3m_ago=1.5, differential_12m_ago=1.5
    )
    assert report.verdict == "hold"


def test_risks_disclose_phase5_correlation_finding():
    report = analyze(
        current_differential=1.5, differential_3m_ago=1.5, differential_12m_ago=1.5
    )
    assert any("Phase 5" in risk for risk in report.risks)
