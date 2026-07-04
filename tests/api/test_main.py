"""
Tests for src/api/main.py.

Mocks the underlying ingestion/validation functions rather than calling
real external APIs or the real database - this tests that each endpoint
correctly wires request to function to response, not the pipelines
themselves (those are already tested in tests/ingestion and
tests/validation).
"""

from fastapi.testclient import TestClient

import src.api.main as api_main

client = TestClient(api_main.app)


def test_health_endpoint():
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json() == {"status": "ok"}


def test_ingest_market_data_endpoint(monkeypatch):
    monkeypatch.setattr(api_main, "run_market_ingestion", lambda period: 7)

    response = client.post("/ingest/market-data")

    assert response.status_code == 200
    assert response.json() == {"status": "success", "rows_inserted": 7}


def test_ingest_economic_data_endpoint(monkeypatch):
    fake_results = {"FEDFUNDS": 1, "CPIAUCSL": 2}
    monkeypatch.setattr(api_main, "run_economic_ingestion", lambda: fake_results)

    response = client.post("/ingest/economic-data")

    assert response.status_code == 200
    assert response.json() == {"status": "success", "results": fake_results}


def test_ingest_japan_data_endpoint(monkeypatch):
    fake_results = {"STRDCLUCON": 3}
    monkeypatch.setattr(api_main, "run_japan_ingestion", lambda: fake_results)

    response = client.post("/ingest/japan-data")

    assert response.status_code == 200
    assert response.json() == {"status": "success", "results": fake_results}


def test_validate_market_data_endpoint(monkeypatch):
    fake_summary = {"passed": 5, "failed": 0, "dataset_level_issues": []}
    monkeypatch.setattr(api_main, "promote_market_data", lambda: fake_summary)

    response = client.post("/validate/market-data")

    assert response.status_code == 200
    assert response.json() == {"status": "success", "summary": fake_summary}


def test_validate_economic_data_endpoint(monkeypatch):
    fake_summary = {"passed": 10, "failed": 1}
    monkeypatch.setattr(api_main, "promote_economic_data", lambda: fake_summary)

    response = client.post("/validate/economic-data")

    assert response.status_code == 200
    assert response.json() == {"status": "success", "summary": fake_summary}


def test_validate_japan_data_endpoint(monkeypatch):
    fake_summary = {"passed": 20, "failed": 0}
    monkeypatch.setattr(api_main, "promote_japan_economic_data", lambda: fake_summary)

    response = client.post("/validate/japan-data")

    assert response.status_code == 200
    assert response.json() == {"status": "success", "summary": fake_summary}
