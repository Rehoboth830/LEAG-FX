-- Phase 4 / Step 3 — validation columns added to existing raw tables.
-- Chosen over separate validated tables: simpler, avoids duplication,
-- keeps everything queryable in one place at this project's scale.

ALTER TABLE raw_market_data
    ADD COLUMN IF NOT EXISTS validation_status VARCHAR(20) NOT NULL DEFAULT 'pending',
    ADD COLUMN IF NOT EXISTS validation_notes TEXT;

ALTER TABLE raw_economic_data
    ADD COLUMN IF NOT EXISTS validation_status VARCHAR(20) NOT NULL DEFAULT 'pending',
    ADD COLUMN IF NOT EXISTS validation_notes TEXT;

CREATE INDEX IF NOT EXISTS idx_raw_market_data_validation_status
    ON raw_market_data (validation_status);
CREATE INDEX IF NOT EXISTS idx_raw_economic_data_validation_status
    ON raw_economic_data (validation_status);
