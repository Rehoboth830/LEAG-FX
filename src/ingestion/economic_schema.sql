-- Phase 3 / Step 5 — raw/staging zone table for economic indicator data
-- One row per (series, date) — different shape than OHLC market data,
-- since economic indicators are single values, not open/high/low/close.

CREATE TABLE IF NOT EXISTS raw_economic_data (
    id SERIAL PRIMARY KEY,
    series_id VARCHAR(50) NOT NULL,
    series_name VARCHAR(200) NOT NULL,
    observation_date DATE NOT NULL,
    value NUMERIC(20, 6),
    source VARCHAR(50) NOT NULL,
    ingested_at TIMESTAMPTZ NOT NULL DEFAULT now(),

    CONSTRAINT unique_series_date_source UNIQUE (series_id, observation_date, source)
);

CREATE INDEX IF NOT EXISTS idx_raw_economic_data_series_date
    ON raw_economic_data (series_id, observation_date);