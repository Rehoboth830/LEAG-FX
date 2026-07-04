-- Phase 4 Fix 1 — table for Japan economic data (BOJ, and later e-Stat).
-- Separate from raw_economic_data (FRED) since the source, series
-- identification scheme, and structure differ meaningfully.

CREATE TABLE IF NOT EXISTS raw_japan_economic_data (
    id SERIAL PRIMARY KEY,
    series_code VARCHAR(50) NOT NULL,
    series_name VARCHAR(200) NOT NULL,
    observation_date DATE NOT NULL,
    value NUMERIC(20, 6),
    source VARCHAR(50) NOT NULL,
    validation_status VARCHAR(20) NOT NULL DEFAULT 'pending',
    validation_notes TEXT,
    ingested_at TIMESTAMPTZ NOT NULL DEFAULT now(),

    CONSTRAINT unique_japan_series_date_source UNIQUE (series_code, observation_date, source)
);

CREATE INDEX IF NOT EXISTS idx_raw_japan_economic_data_series_date
    ON raw_japan_economic_data (series_code, observation_date);
