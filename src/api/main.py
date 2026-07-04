"""
Minimal internal API for LEAG FX.

Exposes ingestion pipelines as HTTP endpoints so n8n (running in its own
container) can trigger them on a schedule via a simple HTTP call,
without needing to cross the Docker/Windows host boundary directly.
"""

from fastapi import FastAPI

from src.common.logger import get_logger
from src.ingestion.economic_data import run_ingestion as run_economic_ingestion
from src.ingestion.market_data import run_ingestion as run_market_ingestion

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
