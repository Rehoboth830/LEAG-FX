-- Fixes a real gap: FEDFUNDS rows had published_date = NULL because
-- they were inserted before that column existed, and it's a non-
-- revised series so it was excluded from the Fix 4 vintage-history
-- backfill. For a non-revised series, published_date = observation_date.
UPDATE raw_economic_data
SET published_date = observation_date
WHERE series_id = 'FEDFUNDS' AND published_date IS NULL;
