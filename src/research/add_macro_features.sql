ALTER TABLE features_daily
    ADD COLUMN IF NOT EXISTS rate_differential NUMERIC(10, 4);
