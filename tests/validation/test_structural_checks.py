"""
Tests for src/validation/structural_checks.py.

Per NFR-5.2, these tests use synthetic data with a deliberately injected,
known problem — proving the checks actually catch what they claim to,
not just that the code runs without crashing.
"""

import pandas as pd

from src.validation.structural_checks import (
    check_duplicates,
    check_missing_values,
    check_price_outliers,
    check_timestamp_integrity,
    validate_market_dataframe,
)


def test_check_missing_values_catches_injected_null():
    df = pd.DataFrame({"close": [150.0, None, 151.0]})
    issues = check_missing_values(df, ["close"])
    assert len(issues) == 1
    assert issues[0].check_name == "missing_value"


def test_check_missing_values_passes_clean_data():
    df = pd.DataFrame({"close": [150.0, 150.5, 151.0]})
    issues = check_missing_values(df, ["close"])
    assert len(issues) == 0


def test_check_duplicates_catches_injected_duplicate():
    df = pd.DataFrame(
        {
            "symbol": ["USDJPY=X", "USDJPY=X", "USDJPY=X"],
            "timestamp_utc": ["2020-01-01", "2020-01-01", "2020-01-02"],
            "source": ["yfinance", "yfinance", "yfinance"],
        }
    )
    issues = check_duplicates(df, ["symbol", "timestamp_utc", "source"])
    assert len(issues) == 1
    assert issues[0].check_name == "duplicate_row"


def test_check_duplicates_passes_clean_data():
    df = pd.DataFrame(
        {
            "symbol": ["USDJPY=X", "USDJPY=X"],
            "timestamp_utc": ["2020-01-01", "2020-01-02"],
            "source": ["yfinance", "yfinance"],
        }
    )
    issues = check_duplicates(df, ["symbol", "timestamp_utc", "source"])
    assert len(issues) == 0


def test_check_price_outliers_catches_injected_spike():
    # A deliberate, unrealistic 50% single-day jump.
    df = pd.DataFrame({"close": [150.0, 225.0, 226.0]})
    issues = check_price_outliers(df, "close", threshold=0.10)
    assert len(issues) == 1
    assert issues[0].check_name == "price_outlier"


def test_check_price_outliers_passes_normal_movement():
    df = pd.DataFrame({"close": [150.0, 151.0, 150.5]})
    issues = check_price_outliers(df, "close", threshold=0.10)
    assert len(issues) == 0


def test_check_timestamp_integrity_catches_future_date():
    df = pd.DataFrame({"timestamp_utc": pd.to_datetime(["2099-01-01"], utc=True)})
    issues = check_timestamp_integrity(df, "timestamp_utc")
    future_issues = [i for i in issues if i.check_name == "future_timestamp"]
    assert len(future_issues) == 1


def test_check_timestamp_integrity_catches_out_of_order():
    df = pd.DataFrame(
        {"timestamp_utc": pd.to_datetime(["2020-01-02", "2020-01-01"], utc=True)}
    )
    issues = check_timestamp_integrity(df, "timestamp_utc")
    order_issues = [i for i in issues if i.check_name == "timestamp_order"]
    assert len(order_issues) == 1


def test_check_timestamp_integrity_catches_missing_timezone():
    df = pd.DataFrame({"timestamp_utc": pd.to_datetime(["2020-01-01", "2020-01-02"])})
    issues = check_timestamp_integrity(df, "timestamp_utc")
    tz_issues = [i for i in issues if i.check_name == "missing_timezone"]
    assert len(tz_issues) == 1


def test_check_timestamp_integrity_passes_clean_utc_data():
    df = pd.DataFrame(
        {"timestamp_utc": pd.to_datetime(["2020-01-01", "2020-01-02"], utc=True)}
    )
    issues = check_timestamp_integrity(df, "timestamp_utc")
    assert len(issues) == 0


def test_validate_market_dataframe_catches_multiple_injected_problems():
    # A dataset with THREE deliberate problems: a missing close value,
    # a duplicate row, and a missing timezone.
    df = pd.DataFrame(
        {
            "symbol": ["USDJPY=X", "USDJPY=X", "USDJPY=X"],
            "timestamp_utc": pd.to_datetime(
                ["2020-01-01", "2020-01-01", "2020-01-02"]
            ),  # no utc=True -> triggers missing_timezone
            "source": ["yfinance", "yfinance", "yfinance"],
            "open": [150.0, 150.0, 151.0],
            "high": [151.0, 151.0, 152.0],
            "low": [149.0, 149.0, 150.0],
            "close": [150.5, None, 151.5],
        }
    )
    report = validate_market_dataframe(df)

    assert not report.passed
    check_names_found = {issue.check_name for issue in report.issues}
    assert "missing_value" in check_names_found
    assert "duplicate_row" in check_names_found
    assert "missing_timezone" in check_names_found


def test_validate_market_dataframe_passes_genuinely_clean_data():
    df = pd.DataFrame(
        {
            "symbol": ["USDJPY=X", "USDJPY=X"],
            "timestamp_utc": pd.to_datetime(["2020-01-01", "2020-01-02"], utc=True),
            "source": ["yfinance", "yfinance"],
            "open": [150.0, 150.5],
            "high": [151.0, 151.5],
            "low": [149.5, 150.0],
            "close": [150.5, 151.0],
        }
    )
    report = validate_market_dataframe(df)
    assert report.passed
