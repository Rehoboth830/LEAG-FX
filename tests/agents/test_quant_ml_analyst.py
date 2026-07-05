"""
Tests for src/agents/quant_ml_analyst.py.
"""

from src.agents.quant_ml_analyst import analyze


def test_always_votes_hold_on_direction():
    report = analyze()
    assert report.verdict == "hold"


def test_confidence_is_low():
    report = analyze()
    assert report.confidence <= 0.4


def test_evidence_includes_key_phase7_findings():
    report = analyze()
    evidence_text = " ".join(report.evidence)
    assert "Random Forest" in evidence_text
    assert "volatility" in evidence_text.lower()


def test_risks_warn_about_overconfident_direction_calls():
    report = analyze()
    assert any("skepticism" in risk.lower() for risk in report.risks)
