# Validation (Phase 4)

Responsible for structural data quality checks: missing values, duplicates, outliers, timestamp integrity.

Consumes raw/staging data, produces the validated zone. Does not fetch data (that's src/ingestion/) and does not detect bias (that's src/bias_detection/) — kept separate so each module has one job and one set of tests.
