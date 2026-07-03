-- Phase 3 / Step 3 — raw/staging zone table for market OHLC data
-- Per the System Architecture doc: this holds exactly what was ingested,
-- untouched. Only Phase 4 validation promotes data into a "validated" zone.

CREATE TABLE IF NOT EXISTS raw_market_data (
    id SERIAL PRIMARY KEY,
    symbol VARCHAR(20) NOT NULL,
    timestamp_utc TIMESTAMPTZ NOT NULL,
    open NUMERIC(12, 6) NOT NULL,
    high NUMERIC(12, 6) NOT NULL,
    low NUMERIC(12, 6) NOT NULL,
    close NUMERIC(12, 6) NOT NULL,
    volume NUMERIC(20, 2),
    source VARCHAR(50) NOT NULL,
    ingested_at TIMESTAMPTZ NOT NULL DEFAULT now(),

    CONSTRAINT unique_symbol_timestamp_source UNIQUE (symbol, timestamp_utc, source)
);

CREATE INDEX IF NOT EXISTS idx_raw_market_data_symbol_timestamp
    ON raw_market_data (symbol, timestamp_utc);