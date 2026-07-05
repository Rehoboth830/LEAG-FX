"""
Tests for src/agents/risk_analyst.py.
"""

from src.agents.risk_analyst import analyze


def test_high_regime_recommends_reduced_size():
    report = analyze(current_regime="high")
    evidence_text = " ".join(report.evidence)
    assert "50%" in evidence_text


def test_low_regime_recommends_full_size():
    report = analyze(current_regime="low")
    evidence_text = " ".join(report.evidence)
    assert "100%" in evidence_text


def test_high_regime_has_explicit_risk_warning():
    report = analyze(current_regime="high")
    assert len(report.risks) > 0
    assert "HIGH VOLATILITY" in report.risks[0]


def test_confidence_is_high_since_this_is_validated():
    report = analyze(current_regime="high")
    # This agent's confidence should be HIGH - unlike the others,
    # its recommendation is backed by validated, walk-forward-tested
    # evidence (Phase 8), not speculation.
    assert report.confidence >= 0.8
