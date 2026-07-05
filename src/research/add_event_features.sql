ALTER TABLE features_daily
    ADD COLUMN IF NOT EXISTS economic_release_flag INTEGER DEFAULT 0;
