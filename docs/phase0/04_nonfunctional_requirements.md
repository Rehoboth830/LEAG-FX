# LEAG FX — Non-Functional Requirements

**Phase 0 / Step 4 — Scope: Phases 0–4 only**

---

## Why Non-Functional Requirements Matter Here

Functional requirements (Step 3) describe *what* the system does. Non-functional requirements describe *how well and how safely* it does it — logging, error handling, config management, testability. Skipping these is exactly how a project turns into "code that works on my machine right now" instead of an institutional-grade system. These apply across Phases 0–4 and become the standard every later phase inherits.

---

## 1. Modularity

- NFR-1.1: Every module (ingestion, validation, bias detection, etc.) has a single, clearly stated responsibility. If a module's purpose can't be described in one sentence, it's doing too much and should be split.
- NFR-1.2: Modules communicate through clearly defined function inputs/outputs — not shared global state or hidden side effects.

## 2. Error Handling

- NFR-2.1: No module fails silently. Every failure (bad data, missing connection, malformed input) is caught, logged, and either handled gracefully or raised with a clear, specific error message.
- NFR-2.2: A failure in one data source (e.g., one economic indicator API is down) does not crash the entire ingestion pipeline — it's logged and the pipeline continues with what it can.

## 3. Logging

- NFR-3.1: Every module logs at minimum: start of operation, successful completion, and failure, in a consistent format (timestamp, module name, level, message).
- NFR-3.2: Logs are written to a persistent location (file or database), not just printed to console — they must survive after the process ends.
- NFR-3.3: Log levels are used meaningfully (DEBUG/INFO/WARNING/ERROR) — not everything logged as one level.

## 4. Configuration Management

- NFR-4.1: No secrets (API keys, database passwords) are hardcoded anywhere in the codebase. All secrets are loaded from environment variables or a secrets file excluded from version control.
- NFR-4.2: No environment-specific values (file paths, hostnames, ports) are hardcoded — all are configurable.
- NFR-4.3: A `.env.example` file exists in the repo showing what configuration is required, without containing real secrets.

## 5. Testability

- NFR-5.1: Every core function in Phases 1–4 has at least one automated test (pytest) verifying its basic correctness.
- NFR-5.2: Validation and bias-detection logic (Phase 4) is tested against known synthetic examples with a known correct answer — not just run against real data and eyeballed.
- NFR-5.3: Tests can be run with a single command and produce a clear pass/fail result.

## 6. Documentation

- NFR-6.1: Every module has a docstring explaining its purpose, inputs, and outputs.
- NFR-6.2: Every top-level folder has a README explaining what belongs there.
- NFR-6.3: Setup steps (getting from a fresh clone to a running system) are documented and reproducible by someone who isn't you.

## 7. Reproducibility

- NFR-7.1: The entire Phase 1–4 stack can be brought up from a fresh clone using Docker, without undocumented manual steps.
- NFR-7.2: Given the same input data, validation and bias-detection modules produce the same output every time (deterministic, no hidden randomness without a fixed seed).

## 8. Maintainability

- NFR-8.1: Code follows the conventions defined in the Coding Standards document (Step 8) — consistent naming, formatting, and linting.
- NFR-8.2: No function exceeds a reasonable length/complexity where it becomes hard to reason about (a practical guideline, not a hard rule — if a function is doing five things, split it).

---

## Out of Scope for This Document

These NFRs apply to Phases 0–4. Later phases (ML models, agents, execution) will inherit these same principles but may add phase-specific NFRs (e.g., latency requirements for Phase 12 execution) when those phases are reached.
