# LEAG FX — Functional Requirements

**Phase 0 / Step 3 — Scope: Phases 0–4 only**

---

## Why Only Phases 0–4

Per the revised roadmap (v2), Phase 0 architects Phases 0–4 in depth and sketches 5–15 lightly. Writing detailed functional requirements for phases we haven't touched real data on yet would be guesswork, not engineering. These requirements get revisited and extended once Phase 4 ships.

Each requirement below is written to be checkable — done or not done, not a matter of opinion.

---

## Phase 0 — Vision, Requirements & Architecture

- FR-0.1: A Vision Document exists and is version-controlled in the repo.
- FR-0.2: A Kill Criteria Document exists, defining conditions for retiring models, strategies, or pausing the project.
- FR-0.3: A documented system architecture exists showing data flow for Phases 0–4 (source → ingestion → validation → storage).
- FR-0.4: A folder structure exists in the repo matching the documented architecture, with a README in each top-level directory.
- FR-0.5: A tech stack decision document exists, stating what each tool is responsible for.
- FR-0.6: A coding standards document exists (naming, docstrings, test coverage expectation, linting, commit format).

## Phase 1 — Engineering Foundation

- FR-1.1: The system runs inside Docker with a reproducible `docker-compose` setup (or equivalent) — a fresh clone of the repo can be brought up without manual, undocumented steps.
- FR-1.2: PostgreSQL is running and reachable from the Python environment, with connection details managed via environment variables/secrets — never hardcoded.
- FR-1.3: A Python virtual environment and dependency file (`requirements.txt` or `pyproject.toml`) exist and are reproducible.
- FR-1.4: A logging system is configured — every module logs key events (start, success, failure) to a consistent format/location.
- FR-1.5: A basic test framework (pytest) is installed and runnable, even with zero or minimal real tests initially.
- FR-1.6: An experiment tracking mechanism exists (even a simple structured log table) to record what was tried, when, and with what result.
- FR-1.7: n8n is installed and reachable, scoped explicitly to orchestration/scheduling — not core logic.

## Phase 2 — USD/JPY Knowledge Base

- FR-2.1: A defined, documented storage format exists for knowledge base entries (structured JSON/YAML, knowledge graph, or vector store — one is chosen and justified).
- FR-2.2: The knowledge base contains structured entries covering, at minimum: Fed policy mechanics, BOJ policy mechanics, key US economic indicators (CPI, NFP, GDP, PCE), key Japan economic indicators (CPI, GDP, Tankan), and the three major trading sessions with their overlap characteristics.
- FR-2.3: Each knowledge base entry is queryable by a Python function — i.e., not just readable by a human, but retrievable programmatically for future agent use (Phase 9).

## Phase 3 — Data Engineering

- FR-3.1: A Data Cost Audit document exists, listing each data source, whether it's free or paid, and its access method (API, download, scrape).
- FR-3.2: A pipeline exists that ingests daily USD/JPY OHLC data into PostgreSQL on a defined schedule.
- FR-3.3: A pipeline exists that ingests at least the core US and Japan economic indicators listed in FR-2.2 into PostgreSQL.
- FR-3.4: Historical data covering at least one full high-volatility regime (e.g., a known crisis period) is present in the warehouse, not just recent stable data.
- FR-3.5: All ingested data is timestamped and timezone-normalized on entry — not left for later cleanup.

## Phase 4 — Data Quality & Bias Control

- FR-4.1: A validation module exists that checks for missing values, duplicate values, and outliers in ingested data, and logs findings.
- FR-4.2: A validation module exists that checks timestamp integrity and confirms timezone normalization.
- FR-4.3: A bias-detection module exists covering, at minimum, survivorship bias and look-ahead bias, built with generic inputs (timestamped data + outcome labels) so it can be shared with CFIP rather than hardcoded to one domain.
- FR-4.4: Any dataset that fails validation or bias checks is flagged and excluded from downstream use until resolved — it does not silently pass through.
- FR-4.5: A "validated dataset" output exists that Phase 5 can consume directly, with a clear record of what validation it has passed.

---

## Out of Scope for This Document

Phases 5–15 are intentionally not detailed here. Their functional requirements will be written when each phase is reached, informed by what Phases 0–4 actually produce — not guessed in advance.
