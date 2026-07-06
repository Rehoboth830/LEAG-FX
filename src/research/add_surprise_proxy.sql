ALTER TABLE features_daily
    ADD COLUMN IF NOT EXISTS cpi_surprise_proxy NUMERIC(10, 6);
