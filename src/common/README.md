# Common

Shared utilities used across modules: logging setup, configuration loading (env vars / secrets), database connection helpers.

Anything used by more than one of ingestion, validation, bias_detection, or knowledge_base belongs here — avoid duplicating config/logging logic per module.
