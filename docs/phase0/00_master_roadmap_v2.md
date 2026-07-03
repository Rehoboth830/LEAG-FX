# LEAG FX — Master Roadmap v2 (Revised)

**Definition:** An AI Operating System that researches, understands, explains, validates, simulates, and executes decisions for the USD/JPY market under strict risk governance.

**What changed from v1:** agent count reduced (8→4), Phase 0 scope narrowed, four missing disciplines added (baseline models, walk-forward validation, kill criteria, confidence calibration), consensus mechanism now explicitly defined as a deliverable, transaction cost realism made mandatory, n8n role clarified, experiment tracking added.

---

## PHASE 0 — Vision, Requirements & Architecture (Narrowed Scope)

**Change:** Fully architect Phases 0–4 only. Sketch Phases 5–15 in one paragraph each. Revisit the sketch after Phase 4 ships — designing deeply against data you haven't seen yet produces guesses, not architecture.

**Deliverables**
- Vision Document
- Functional & Non-functional Requirements (Phases 0–4 detailed; 5–15 sketched)
- System Architecture (Phases 0–4 detailed)
- Folder Structure, Tech Stack, Coding Standards
- Risk Philosophy, Success Metrics, Milestone Plan
- **New:** Kill Criteria Document — under what conditions is a model, strategy, or the project itself retired rather than endlessly patched

---

## PHASE 1 — Engineering Foundation

Unchanged. Python, Git, GitHub, Docker, PostgreSQL, VS Code, virtual environments, API testing, secrets management, logging.

**New:** Set up lightweight experiment tracking from day one (even a structured log table: what was tried, parameters, result, date). Prevents re-running failed experiments months later without realizing it.

**Clarified role of n8n:** orchestration and glue only — scheduling data pulls, sending alerts, triggering pipelines. Core research/ML/backtesting logic lives in tested Python modules that n8n *calls*, never logic built inside n8n nodes themselves. Reproducibility and testability require real code.

---

## PHASE 2 — USD/JPY Knowledge Base

Unchanged in content (Fed, BOJ, macro indicators, market structure, sessions).

**New:** Decide the storage shape now, since it determines how Phase 9 agents query it later — structured JSON/YAML docs, a knowledge graph, or a vector-searchable corpus. Don't leave this as "a folder of notes."

---

## PHASE 3 — Data Engineering

Unchanged in content (market data, economic data, sentiment, historical regimes).

**New:** Data Cost Audit — explicitly document what's free (most macro data, daily OHLC) vs. what requires payment or a lower-fidelity substitute (tick data, some news/sentiment feeds) before committing to a data source in code.

---

## PHASE 4 — Data Quality & Bias Control

Unchanged in content (validation, survivorship bias, look-ahead bias, leakage).

**Note:** Build the bias-detection engine with generic inputs (timestamped data + outcome labels) rather than hardcoding to one data domain — this component is shared with CFIP.

---

## PHASE 5 — Statistics & Quantitative Research

Unchanged in content.

**New:** Define "good" here, not later — every downstream model or strategy must be compared against a naive baseline (buy-and-hold, simple moving-average crossover, or a coin-flip adjusted for known drift) on the same data. No model is trusted until it beats the baseline. This is now a standing rule referenced in Phases 7 and 8.

---

## PHASE 6 — Feature Engineering

Unchanged in content (RSI, MACD, EMA, ATR, yield spread, event flags, etc.)

---

## PHASE 7 — Machine Learning Laboratory

Unchanged in content (classification, regression, regime detection).

**New — mandatory:**
- Every model compared against the Phase 5 baseline before being considered "working."
- Walk-forward validation only. Standard random train/test splits leak future information into the past for time series and produce misleadingly good results. Train on the past, test on the future, roll forward, never shuffle.

---

## PHASE 8 — Backtesting Laboratory

Unchanged in content (VectorBT, stress tests across regimes).

**New — mandatory:**
- Transaction cost realism (spread, slippage, execution latency) is always-on in every backtest, not a later checkbox. For FX specifically, spread cost alone can turn a profitable-looking backtest into a losing real strategy.
- Kill criterion check: a strategy that fails to beat its baseline after a defined evaluation window is retired, not endlessly patched.

---

## PHASE 9 — AI Intelligence Layer (Reduced from 8 agents to 4)

**Change:** Eight specialists created overlap (Macro Economist and Central Bank Analyst largely duplicate each other for this pair; Sentiment and News Analyst blur together) and made the consensus layer hard to debug — with 8 voices, a bad decision is hard to trace to its source.

**Revised roster for v1:**
1. **Technical Analyst** — chart-based signals
2. **Macro/Central Bank Analyst** (merged) — Fed + BOJ policy, economic releases
3. **Quant/ML Analyst** (merged) — statistical + model-based probability estimates
4. **Risk Analyst** — flags conditions that should suppress or veto a signal regardless of the other three

Each still outputs: analysis, confidence, evidence, risks — in one **shared schema** so Phase 10 doesn't need custom parsing per agent, e.g.:
```
{agent, verdict, confidence, evidence[], risks[], timestamp}
```

Splitting into more specialists (adding Sentiment, News, Performance, etc. back) is a Phase 9.1 expansion *after* the 4-agent consensus mechanism is proven to work — not before.

---

## PHASE 10 — Consensus Engine (Now Explicitly Defined)

**Change:** v1 said the engine "receives reports, produces Buy/Sell/Hold" without specifying *how*. This was the single largest undefined piece in the whole plan and arguably the hardest, highest-leverage design decision in the platform.

**Deliverable now explicitly includes choosing and justifying one of:**
- Simple/weighted averaging of agent confidence scores
- Weighting agents by their own historical accuracy (requires Phase 13 data to exist first)
- A learned meta-model trained on agent outputs vs. actual outcomes

Output: Buy/Sell/Hold + confidence + explanation + evidence + risks + alternative scenarios (unchanged from v1).

---

## PHASE 11 — Risk Governance

Unchanged in content and importance — this remains a hard gate; no decision bypasses it. Position sizing, exposure limits, loss limits, stop-loss rules, leverage caps, volatility/event filters, emergency shutdown.

---

## PHASE 12 — Paper Trading & Execution

Unchanged: Simulation → Paper Trading → Demo Account → human-supervised live only after extensive validation.

---

## PHASE 13 — Memory & Reflection

Unchanged in content (decisions, reasoning, outcomes, weekly/monthly review).

**New — Confidence Calibration:** Track predicted confidence vs. actual outcome over time. If calls made at 80% confidence don't win around 80% of the time, the confidence score is decorative, not informative, and the consensus mechanism needs recalibration. This closes the loop back into Phase 10's weighting choice.

---

## PHASE 14 — Dashboard & Monitoring

Unchanged in content.

---

## PHASE 15 — Production, Documentation & Portfolio

Unchanged in content. Treat the portfolio assets (whitepaper, diagrams, demo video, deployment guide) as their own scoped project, not something that falls out of the code for free.

---

## Summary of Structural Changes

| Area | v1 | v2 |
|---|---|---|
| Phase 0 scope | Fully architect all 15 phases upfront | Deeply architect 0–4, sketch 5–15, revisit after Phase 4 |
| Specialist agents | 8 | 4 (expand later, after consensus is proven) |
| Baseline model | Absent | Mandatory, defined in Phase 5, enforced in Phases 7–8 |
| Time-series validation | Unspecified | Walk-forward only, explicit in Phase 7 |
| Kill criteria | Absent | Defined in Phase 0, enforced in Phase 8 |
| Consensus mechanism | Undefined black box | Explicit deliverable with three named options to choose between |
| Transaction costs | Mentioned once, passing | Always-on, mandatory in every backtest |
| Confidence calibration | Absent | New line item in Phase 13, feeds back into Phase 10 |
| n8n's role | Implied as backbone | Explicitly orchestration/glue only; logic lives in tested Python |
| Experiment tracking | Absent | Introduced in Phase 1 |
| Data cost reality | Absent | Explicit audit in Phase 3 |

