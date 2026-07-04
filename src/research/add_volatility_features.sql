-- Phase 6 / Step 2 - volatility feature columns
ALTER TABLE features_daily
    ADD COLUMN IF NOT EXISTS volatility_5d NUMERIC(10, 6),
    ADD COLUMN IF NOT EXISTS volatility_20d NUMERIC(10, 6),
    ADD COLUMN IF NOT EXISTS volatility_60d NUMERIC(10, 6);
