# LEAG FX — System Architecture (Phases 0–4)

**Phase 0 / Step 5 — Scope: Phases 0–4 only**

---

## Overview

This document describes how data physically flows through LEAG FX from external sources into a validated, research-ready dataset. It corresponds to the diagram shared alongside this document. Phases 5–15 are not architected here — see Phase 0 scope note in the Vision Document.

## Data Flow (Phases 3–4)

1. **External sources** — three categories, each with distinct characteristics:
   - *Market data*: OHLC price feeds, volume, spread. High frequency, structured, mostly free at daily/hourly granularity.
   - *Economic data*: Fed/BOJ releases, CPI, NFP, GDP, interest rate decisions. Low frequency (scheduled releases), structured.
   - *Context sources*: news, macro commentary, sentiment signals. Unstructured, higher cost, lower priority for v1.

2. **Ingestion pipeline (Phase 3)** — pulls from all three source categories on defined schedules (daily for market data, event-driven for economic releases). Every record is timestamped and timezone-normalized *at ingestion*, not deferred to a later cleanup step (per FR-3.5).

3. **Validation & bias control (Phase 4)** — every ingested batch passes through:
   - Structural validation: missing values, duplicates, outliers, timestamp integrity.
   - Bias checks: survivorship bias, look-ahead bias, using the generic, domain-agnostic detector (shared with CFIP).
   - Anything that fails is flagged and excluded from downstream use (per FR-4.4) — it does not pass through silently.

4. **PostgreSQL warehouse** — the single source of truth for validated data. Only data that has passed Phase 4 validation lands here as "usable." Raw/unvalidated data may be staged separately (see Storage Design below) but is never queried directly by downstream phases.

5. **Downstream (Phase 5, not built yet)** — the research engine consumes only the validated warehouse output. This boundary matters: it means Phase 5 never has to re-implement data quality logic — that responsibility lives entirely in Phase 4.

## Storage Design Principle

Two logical zones inside PostgreSQL, even in early phases:
- **Raw/staging zone**: exactly what was ingested, untouched, kept for audit and reprocessing if validation logic improves later.
- **Validated zone**: only data that has passed Phase 4 checks. This is what every phase from 5 onward reads from.

This separation means a bug found in validation logic later can be fixed and *reapplied to raw data* — without needing to re-ingest from external sources.

## Knowledge Base Note (Phase 2)

The Phase 2 knowledge base (Fed/BOJ mechanics, indicator definitions, session structure) is conceptually separate from the Phase 3/4 data pipeline — it's relatively static reference material, not a continuously ingested stream. It's stored in whatever format was chosen in FR-2.1, and queried directly by later phases (e.g., Phase 9 agents) rather than flowing through the validation pipeline shown above.

## What This Architecture Deliberately Does Not Cover Yet

- How Phase 5 (statistics) or Phase 9 (AI agents) query the warehouse — that's designed when those phases are reached.
- Any ML feature store design (Phase 6) — premature until real validated data exists to engineer features from.
- Execution or broker connectivity (Phase 12) — far downstream, not relevant to this foundation layer.

---

*This document should be revisited once Phase 4 is actually built and real data has flowed through it — some assumptions here (e.g., ingestion frequency, staging approach) may need adjustment based on what's actually encountered.*
