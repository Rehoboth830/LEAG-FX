"""
Minimal internal API for LEAG FX.

Exposes ingestion and validation pipelines as HTTP endpoints so n8n
(running in its own container) can trigger them on a schedule via a
simple HTTP call, without needing to cross the Docker/Windows host
boundary directly.
"""

from fastapi import FastAPI

from src.common.logger import get_logger
from src.ingestion.economic_data import run_ingestion as run_economic_ingestion
from src.ingestion.market_data import run_ingestion as run_market_ingestion
from src.validation.promote import promote_economic_data, promote_market_data

logger = get_logger(__name__)

app = FastAPI(title="LEAG FX Internal API")


@app.get("/health")
def health():
    """Basic health check — confirms the API is up and reachable."""
    return {"status": "ok"}


@app.post("/ingest/market-data")
def ingest_market_data():
    """Triggers the market data ingestion pipeline."""
    logger.info("Market data ingestion triggered via API")
    inserted = run_market_ingestion(period="5d")
    return {"status": "success", "rows_inserted": inserted}


@app.post("/ingest/economic-data")
def ingest_economic_data():
    """Triggers the economic data ingestion pipeline."""
    logger.info("Economic data ingestion triggered via API")
    results = run_economic_ingestion()
    return {"status": "success", "results": results}


@app.post("/validate/market-data")
def validate_market_data():
    """Triggers structural validation for pending market data (FR-4.4)."""
    logger.info("Market data validation triggered via API")
    summary = promote_market_data()
    return {"status": "success", "summary": summary}


@app.post("/validate/economic-data")
def validate_economic_data():
    """Triggers structural validation for pending economic data (FR-4.4)."""
    logger.info("Economic data validation triggered via API")
    summary = promote_economic_data()
    return {"status": "success", "summary": summary}
