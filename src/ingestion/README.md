# Ingestion (Phase 3)

Responsible for pulling data from external sources (market data, economic data, context sources) into the raw/staging zone of the PostgreSQL warehouse.

Single responsibility: get data in, timestamped and timezone-normalized. No validation logic lives here — that belongs in src/validation/.
