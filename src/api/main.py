"""
Minimal internal API for LEAG FX.

Exposes ingestion and validation pipelines as HTTP endpoints so n8n
can trigger them on a schedule via a simple HTTP call.
"""

from fastapi import FastAPI

from src.common.logger import get_logger
from src.ingestion.economic_data import run_ingestion as run_economic_ingestion
from src.ingestion.japan_data import run_ingestion as run_japan_ingestion
from src.ingestion.market_data import run_ingestion as run_market_ingestion
from src.validation.promote import (
    promote_economic_data,
    promote_japan_economic_data,
    promote_market_data,
)

logger = get_logger(__name__)

app = FastAPI(title="LEAG FX Internal API")


@app.get("/health")
def health():
    return {"status": "ok"}


@app.post("/ingest/market-data")
def ingest_market_data():
    logger.info("Market data ingestion triggered via API")
    inserted = run_market_ingestion(period="5d")
    return {"status": "success", "rows_inserted": inserted}


@app.post("/ingest/economic-data")
def ingest_economic_data():
    logger.info("Economic data ingestion triggered via API")
    results = run_economic_ingestion()
    return {"status": "success", "results": results}


@app.post("/ingest/japan-data")
def ingest_japan_data():
    logger.info("Japan economic data ingestion triggered via API")
    results = run_japan_ingestion()
    return {"status": "success", "results": results}


@app.post("/validate/market-data")
def validate_market_data():
    logger.info("Market data validation triggered via API")
    summary = promote_market_data()
    return {"status": "success", "summary": summary}


@app.post("/validate/economic-data")
def validate_economic_data():
    logger.info("Economic data validation triggered via API")
    summary = promote_economic_data()
    return {"status": "success", "summary": summary}


@app.post("/validate/japan-data")
def validate_japan_data():
    logger.info("Japan economic data validation triggered via API")
    summary = promote_japan_economic_data()
    return {"status": "success", "summary": summary}
