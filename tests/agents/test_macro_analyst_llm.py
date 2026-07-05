"""
Tests for src/agents/macro_analyst_llm.py.

Does NOT call the real Gemini API - even on the free tier, tests
should be deterministic and not depend on network access. Instead
tests _parse_response() directly with canned response text.
"""

import json

import pytest

from src.agents.macro_analyst_llm import _parse_response


def test_parses_valid_json_response_correctly():
    response_text = json.dumps(
        {
            "verdict": "hold",
            "confidence": 0.45,
            "evidence": ["Rate differential is moderate", "Trend is flat"],
            "risks": ["No short-term correlation found in prior research"],
        }
    )

    report = _parse_response(response_text)

    assert report.agent == "MacroCentralBankAnalyst_LLM"
    assert report.verdict == "hold"
    assert report.confidence == 0.45
    assert len(report.evidence) == 2


def test_handles_response_wrapped_in_markdown_code_fence():
    # Gemini sometimes wraps JSON in ```json ... ``` despite instructions.
    raw_json = json.dumps(
        {"verdict": "buy", "confidence": 0.6, "evidence": [], "risks": []}
    )
    response_text = f"```json\n{raw_json}\n```"

    report = _parse_response(response_text)
    assert report.verdict == "buy"


def test_handles_response_with_extra_whitespace():
    response_text = (
        "  \n"
        + json.dumps({"verdict": "buy", "confidence": 0.6, "evidence": [], "risks": []})
        + "\n  "
    )
    report = _parse_response(response_text)
    assert report.verdict == "buy"


def test_raises_clear_error_on_invalid_json():
    with pytest.raises(ValueError):
        _parse_response("This is not JSON at all")


def test_raises_clear_error_on_invalid_verdict_value():
    response_text = json.dumps(
        {"verdict": "maybe", "confidence": 0.5, "evidence": [], "risks": []}
    )
    with pytest.raises(ValueError):
        _parse_response(response_text)
