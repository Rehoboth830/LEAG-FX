ALTER TABLE features_daily
    ADD COLUMN IF NOT EXISTS day_of_week INTEGER;
