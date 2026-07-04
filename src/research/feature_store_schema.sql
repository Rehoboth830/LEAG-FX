-- Phase 6 / Step 1 - Feature Store
-- One row per date, one column per feature. Simple, queryable,
-- upgradeable later to a dedicated feature-serving layer if the
-- project ever outgrows this - nothing here is wasted if that happens.
--
-- Columns are added incrementally via ALTER TABLE as each feature
-- type is built (Steps 2-6), rather than guessing the full schema
-- upfront.

CREATE TABLE IF NOT EXISTS features_daily (
    observation_date DATE PRIMARY KEY,
    validation_status VARCHAR(20) NOT NULL DEFAULT 'pending',
    validation_notes TEXT,
    created_at TIMESTAMPTZ NOT NULL DEFAULT now()
);
