"""
Tests for src/agents/schema.py.
"""

import pytest

from src.agents.schema import AgentReport


def test_valid_report_is_created_successfully():
    report = AgentReport(
        agent="TestAgent",
        verdict="buy",
        confidence=0.7,
        evidence=["some evidence"],
        risks=["some risk"],
    )
    assert report.verdict == "buy"
    assert report.confidence == 0.7


def test_invalid_verdict_is_rejected():
    with pytest.raises(ValueError):
        AgentReport(agent="TestAgent", verdict="maybe", confidence=0.5)


def test_confidence_above_one_is_rejected():
    with pytest.raises(ValueError):
        AgentReport(agent="TestAgent", verdict="hold", confidence=1.5)


def test_confidence_below_zero_is_rejected():
    with pytest.raises(ValueError):
        AgentReport(agent="TestAgent", verdict="hold", confidence=-0.1)


def test_timestamp_is_auto_generated():
    report = AgentReport(agent="TestAgent", verdict="hold", confidence=0.5)
    assert report.timestamp is not None
    assert len(report.timestamp) > 0
