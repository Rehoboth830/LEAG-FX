# LEAG FX

An AI Operating System that researches, understands, explains, validates, simulates, and executes decisions for the USD/JPY market under strict risk governance.

See `docs/phase0/` for the Vision Document, Kill Criteria, Requirements, and Architecture that govern this project.

## Status
Phase 0 — Vision, Requirements & Architecture. No production code yet.

## Structure
- `docs/` — planning and architecture documents
- `src/` — application source code, organized by responsibility
- `tests/` — automated tests (pytest)
- `data/` — local data zones (raw/staging and validated); not committed to version control
- `notebooks/` — exploratory analysis, not production code
- `scripts/` — one-off or scheduled utility scripts
- `docker/` — container definitions
- `n8n_workflows/` — exported n8n workflow JSON (orchestration/scheduling only, not core logic)
