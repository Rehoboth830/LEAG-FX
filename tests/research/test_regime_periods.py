"""
Tests for src/research/regime_periods.py.
"""

import pandas as pd

from src.research.regime_periods import REGIME_PERIODS, tag_regime_period


def test_known_covid_crash_date_labeled_correctly():
    dates = pd.Series(["2020-03-23"])  # the real COVID crash peak date from Phase 5
    labels = tag_regime_period(dates)
    assert "COVID" in labels.iloc[0]


def test_known_2016_date_labeled_correctly():
    dates = pd.Series(["2016-08-01"])
    labels = tag_regime_period(dates)
    assert "2016-2019" in labels.iloc[0]


def test_periods_do_not_overlap():
    for i in range(len(REGIME_PERIODS) - 1):
        current_end = pd.Timestamp(REGIME_PERIODS[i]["end"])
        next_start = pd.Timestamp(REGIME_PERIODS[i + 1]["start"])
        assert next_start > current_end


def test_periods_have_no_gaps():
    for i in range(len(REGIME_PERIODS) - 1):
        current_end = pd.Timestamp(REGIME_PERIODS[i]["end"])
        next_start = pd.Timestamp(REGIME_PERIODS[i + 1]["start"])
        # Next period should start the day immediately after the
        # previous one ends - no unlabeled gap between them.
        assert (next_start - current_end).days == 1
