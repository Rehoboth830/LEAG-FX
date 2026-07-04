"""
Phase 4 Fix 4 - proves look-ahead bias detection against REAL data.

Pulls GDP's actual first-release publication dates from FRED (not just
the observation period the data describes), then demonstrates that a
naive backtest assuming data was known immediately would be flagged
as a real information leak - the exact GDP-revision scenario described
in the bias_checks.py docstring.
"""

import os

import pandas as pd
from dotenv import load_dotenv
from fredapi import Fred

from src.bias_detection.bias_checks import detect_lookahead_bias
from src.common.logger import get_logger

logger = get_logger(__name__)

load_dotenv()


def get_real_publication_dates(
    series_id: str = "GDP", limit_recent: int = 12
) -> pd.DataFrame:
    """
    Fetches each observation's TRUE first-publication date from FRED's
    vintage history, alongside the value and the period it describes.

    Args:
        series_id: FRED series to check (GDP is quarterly, so recent
            history is a manageable number of real API calls).
        limit_recent: how many of the most recent observations to check.

    Returns:
        DataFrame with columns: observation_date, published_date, value.
    """
    api_key = os.getenv("FRED_API_KEY")
    fred = Fred(api_key=api_key)

    all_releases = fred.get_series_all_releases(series_id)
    all_releases["date"] = pd.to_datetime(all_releases["date"])
    all_releases["realtime_start"] = pd.to_datetime(all_releases["realtime_start"])

    # First publication = earliest realtime_start per observation date.
    first_releases = (
        all_releases.sort_values("realtime_start")
        .groupby("date")
        .first()
        .reset_index()
        .rename(
            columns={"date": "observation_date", "realtime_start": "published_date"}
        )
    )

    return first_releases.tail(limit_recent)[
        ["observation_date", "published_date", "value"]
    ]


def run_real_lookahead_check():
    """
    The actual proof: builds a 'naive backtest' assumption (each GDP
    figure was known on its observation_date) and checks it against
    the REAL published_date - demonstrating the detector catches a
    genuine, real information leak, not just a synthetic one.
    """
    real_data = get_real_publication_dates("GDP", limit_recent=12)
    print("Real GDP publication data from FRED:")
    print(real_data)
    print()

    # The naive (wrong) assumption a careless backtest might make:
    # "the GDP figure was known on the date it describes."
    naive_backtest = pd.DataFrame(
        {
            "decision_time": real_data["observation_date"],
            "knowledge_date": real_data["published_date"],
        }
    )

    report = detect_lookahead_bias(naive_backtest, "decision_time", "knowledge_date")

    print(f"Look-ahead bias check on REAL GDP data: {len(report.findings)} leaks found")
    for finding in report.findings[:5]:
        print(f"  - {finding.description}")

    return report


if __name__ == "__main__":
    run_real_lookahead_check()
