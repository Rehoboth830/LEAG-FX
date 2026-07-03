# LEAG FX — Kill Criteria Document

**Phase 0 / Step 2**

---

## Why This Document Exists

This is written now — before any model, strategy, or dashboard exists — on purpose. It's much easier to define honest failure conditions before there's anything to be emotionally attached to. Once a model "almost works" or a strategy "just needs one more tweak," judgment gets cloudy. This document is the pre-commitment that keeps LEAG FX honest with itself later.

Some numeric thresholds below are marked **[SET AFTER BASELINE]** — they genuinely cannot be set responsibly until Phase 5 produces a real baseline and Phase 8 produces real backtest data. Setting fake numbers now would be worse than leaving them open, since it would create false precision. The *structure* and *commitment* are what matter today; the numbers get filled in honestly when the data exists.

---

## 1. Feature / Model Kill Criteria (Phases 6–7)

A feature or model is dropped if:
- It does not improve performance over the Phase 5 baseline on out-of-sample, walk-forward validated data.
- Its apparent performance disappears or reverses when transaction costs (spread/slippage) are applied.
- It relies on data that turns out to be leaked (look-ahead bias) or unrepresentative (survivorship bias) — caught by Phase 4's validation.

## 2. Strategy Kill Criteria (Phase 8 — Backtesting)

A backtested strategy is retired, not endlessly re-tuned, if:
- It fails to beat the naive baseline (buy-and-hold or simple MA crossover) over the full historical test window, **including realistic transaction costs**.
- It only "works" in one market regime (e.g., only trending markets) and fails stress tests in ranging, crisis, or high-volatility regimes.
- Maximum drawdown in backtest exceeds **[SET AFTER BASELINE]**% — a threshold decided once real drawdown distributions are known, not guessed now.

## 3. Paper Trading Kill Criteria (Phase 12)

A strategy that passed backtesting is pulled from paper trading if:
- Live paper performance diverges significantly (statistically, not just "it lost twice") from backtest expectations over a minimum evaluation window of **[SET AFTER BASELINE]** weeks/months.
- Realized slippage/execution behavior consistently exceeds what was modeled in Phase 8.
- Risk Governance (Phase 11) triggers more than a defined number of interventions in a short period — a sign the strategy is generating consistently risky signals, not just occasional edge cases.

## 4. Confidence Calibration Kill Criteria (Phase 13)

The consensus engine's confidence scoring is flagged as broken (not just imperfect) if, over a meaningful sample of decisions:
- Calls made at high confidence (e.g., 80%+) do not win meaningfully more often than calls made at low confidence.
- Confidence scores show no correlation with actual outcomes at all.

If this happens, Phase 10's consensus mechanism goes back for redesign before any further live-adjacent testing continues.

## 5. Project-Level Kill / Pause Criteria

The project itself pauses for reassessment (not necessarily abandoned) if:
- After completing Phases 0–8 honestly, **no model or strategy beats the baseline** on validated, cost-adjusted, walk-forward tested data. This is a real possible outcome, not a hypothetical — and if it happens, the honest conclusion is that USD/JPY (at least with the data and features tried) may not have enough exploitable structure, and that's valuable, legitimate research output — not a failure of the builder.
- The engineering burden (maintenance, data costs, infrastructure) becomes unsustainable relative to the learning/portfolio value being produced.

## 6. What "Kill" Does Not Mean

Killing a model, feature, or strategy does not mean deleting the work. Every kill decision and the evidence behind it gets logged (Phase 13 — Memory & Reflection). A killed approach is a completed experiment with a documented negative result — which has real value, both for future research direction and as evidence of rigor in the eventual portfolio writeup.

---

*Numeric thresholds marked [SET AFTER BASELINE] must be filled in during Phase 5, once real baseline performance and volatility figures exist — not before. Revisit this document at that point.*
