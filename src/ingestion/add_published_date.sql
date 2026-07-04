-- Phase 4 Fix 4 — add published_date to track when data was actually
-- known/available, separate from the observation_date it describes.
-- Nullable: only revision-prone series (GDP, CPI, PCE) populate this;
-- FEDFUNDS is not revised, so observation_date and published_date
-- are effectively the same for it.

ALTER TABLE raw_economic_data
    ADD COLUMN IF NOT EXISTS published_date DATE;
