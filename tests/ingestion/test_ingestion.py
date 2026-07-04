"""
Tests for src/ingestion/market_data.py and economic_data.py.

Uses a distinct test source name ("test_source") so these tests never
collide with or pollute real ingested data, and cleans up after itself.
"""

import pandas as pd
import pytest

from src.common.db import get_connection
from src.ingestion.economic_data import store_series
from src.ingestion.market_data import store_ohlc

TEST_MARKET_SOURCE = "test_source"


@pytest.fixture(autouse=True)
def cleanup_test_rows():
    """Removes any test rows before and after each test, so tests never
    leave residue in the real database."""
    yield
    conn = get_connection()
    try:
        with conn.cursor() as cur:
            cur.execute(
                "DELETE FROM raw_market_data WHERE source = %s", (TEST_MARKET_SOURCE,)
            )
            cur.execute(
                "DELETE FROM raw_economic_data WHERE source = %s", ("test_source",)
            )
        conn.commit()
    finally:
        conn.close()


def test_store_ohlc_inserts_new_rows(monkeypatch):
    monkeypatch.setattr("src.ingestion.market_data.SOURCE_NAME", TEST_MARKET_SOURCE)

    data = pd.DataFrame(
        {
            "Open": [150.0],
            "High": [151.0],
            "Low": [149.5],
            "Close": [150.5],
            "Volume": [0],
        },
        index=pd.to_datetime(["2020-01-01"], utc=True),
    )

    inserted = store_ohlc(data, symbol="TEST/PAIR")
    assert inserted == 1


def test_store_ohlc_skips_duplicates(monkeypatch):
    monkeypatch.setattr("src.ingestion.market_data.SOURCE_NAME", TEST_MARKET_SOURCE)

    data = pd.DataFrame(
        {
            "Open": [150.0],
            "High": [151.0],
            "Low": [149.5],
            "Close": [150.5],
            "Volume": [0],
        },
        index=pd.to_datetime(["2020-01-02"], utc=True),
    )

    first_run = store_ohlc(data, symbol="TEST/PAIR")
    second_run = store_ohlc(data, symbol="TEST/PAIR")

    assert first_run == 1
    assert second_run == 0


def test_store_ohlc_handles_empty_dataframe():
    empty_data = pd.DataFrame()
    inserted = store_ohlc(empty_data, symbol="TEST/PAIR")
    assert inserted == 0


def test_store_series_inserts_new_rows():
    data = pd.Series([2.5], index=pd.to_datetime(["2020-01-01"]), name="TEST_SERIES")
    inserted = store_series("TEST_SERIES", "Test Series", data)
    assert inserted == 1


def test_store_series_skips_nan_values():
    data = pd.Series(
        [float("nan")], index=pd.to_datetime(["2020-01-01"]), name="TEST_SERIES"
    )
    inserted = store_series("TEST_SERIES", "Test Series", data)
    assert inserted == 0
