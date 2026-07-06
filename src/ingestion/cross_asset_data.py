"""
Cross-asset data ingestion (Phase 7.1, Step 1).

Reuses the exact same, already-tested market_data.py pipeline
(fetch_ohlc/store_ohlc) for real cross-asset signals: Nikkei 225 and
VIX. Stored in the same raw_market_data table, distinguished by symbol.
"""

from src.common.logger import get_logger
from src.ingestion.market_data import fetch_ohlc, store_ohlc

logger = get_logger(__name__)

CROSS_ASSET_SYMBOLS = {
    "^N225": "Nikkei 225",
    "^VIX": "CBOE Volatility Index",
}


def run_ingestion(period: str = "10y") -> dict:
    """
    Ingests all cross-asset symbols, each isolated in its own
    try/except so one failure doesn't stop the others (NFR-2.2).
    """
    results = {}
    for symbol, name in CROSS_ASSET_SYMBOLS.items():
        try:
            data = fetch_ohlc(symbol, period)
            inserted = store_ohlc(data, symbol)
            results[symbol] = inserted
        except Exception as e:
            logger.error(f"Unexpected failure processing {symbol}: {e}")
            results[symbol] = "error"
    return results


if __name__ == "__main__":
    results = run_ingestion()
    print("Cross-asset ingestion complete:")
    for symbol, result in results.items():
        print(f"  {symbol}: {result}")
