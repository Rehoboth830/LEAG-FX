"""
Tests for src/bias_detection/bias_checks.py.

Per NFR-5.2, these deliberately inject known bias into synthetic data
and prove the detectors actually catch it.
"""

import pandas as pd

from src.bias_detection.bias_checks import (
    detect_lookahead_bias,
    detect_survivorship_bias,
)


def test_detect_survivorship_bias_catches_excluded_dead_entity():
    # A universe of 3 entities, one of which ("TOKEN_C") died.
    universe = pd.DataFrame(
        {
            "entity_id": ["TOKEN_A", "TOKEN_B", "TOKEN_C"],
            "is_active": [True, True, False],
        }
    )
    # The analysis only includes the survivors — TOKEN_C was dropped.
    analyzed_ids = ["TOKEN_A", "TOKEN_B"]

    report = detect_survivorship_bias(universe, analyzed_ids)

    assert report.bias_detected
    assert len(report.findings) == 1
    assert "TOKEN_C" in report.findings[0].identifier


def test_detect_survivorship_bias_passes_when_dead_entities_included():
    universe = pd.DataFrame(
        {
            "entity_id": ["TOKEN_A", "TOKEN_B", "TOKEN_C"],
            "is_active": [True, True, False],
        }
    )
    # This time the dead entity IS included — no bias.
    analyzed_ids = ["TOKEN_A", "TOKEN_B", "TOKEN_C"]

    report = detect_survivorship_bias(universe, analyzed_ids)

    assert not report.bias_detected
    assert len(report.findings) == 0


def test_detect_survivorship_bias_passes_when_no_dead_entities_exist():
    universe = pd.DataFrame(
        {
            "entity_id": ["TOKEN_A", "TOKEN_B"],
            "is_active": [True, True],
        }
    )
    analyzed_ids = ["TOKEN_A", "TOKEN_B"]

    report = detect_survivorship_bias(universe, analyzed_ids)

    assert not report.bias_detected


def test_detect_lookahead_bias_catches_injected_leak():
    # A deliberate leak: knowledge_date is AFTER decision_time —
    # this data literally could not have been known yet.
    df = pd.DataFrame(
        {
            "decision_time": ["2024-01-01", "2024-01-02"],
            "knowledge_date": ["2023-12-31", "2024-01-05"],  # row 1 leaks
        }
    )

    report = detect_lookahead_bias(df, "decision_time", "knowledge_date")

    assert report.bias_detected
    assert len(report.findings) == 1


def test_detect_lookahead_bias_passes_clean_data():
    # Knowledge always available on or before the decision — no leak.
    df = pd.DataFrame(
        {
            "decision_time": ["2024-01-01", "2024-01-02"],
            "knowledge_date": ["2023-12-31", "2024-01-01"],
        }
    )

    report = detect_lookahead_bias(df, "decision_time", "knowledge_date")

    assert not report.bias_detected
    assert len(report.findings) == 0


def test_detect_lookahead_bias_catches_gdp_revision_style_leak():
    # A realistic scenario: a GDP figure with a "known_date" showing it
    # was actually published two days AFTER the backtest claims to have
    # used it — the exact revision-leak trap the docstring describes.
    df = pd.DataFrame(
        {
            "decision_time": ["2024-03-01"],
            "knowledge_date": ["2024-03-03"],
        }
    )

    report = detect_lookahead_bias(df, "decision_time", "knowledge_date")

    assert report.bias_detected
    assert "leak" in report.findings[0].description.lower()
