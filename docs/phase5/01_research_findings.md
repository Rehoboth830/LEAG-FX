# LEAG FX - Phase 5 Research Findings

**Phase 5 / Step 8 - Statistics & Quantitative Research, USD/JPY**

Data: 2,602 real daily price observations (2016-07-03 to 2026-07-02), validated, spanning multiple market regimes including the March 2020 COVID crash.

---

## 1. Descriptive Statistics

USD/JPY drifted upward over the 10-year window (annualized return ~4.78%), with annualized volatility of ~8.80%. Returns show negative skew (-0.24) and significant excess kurtosis (3.17, "fat tails") - extreme single-day moves (min -3.72%, max +2.70%) occur far more often than a normal distribution would predict.

## 2. Stationarity

Raw price levels are **not stationary** (ADF p-value = 0.9084) - prices genuinely drift and trend, confirmed both visually and statistically. Daily returns **are stationary** (ADF p-value approximately 0.0000). **Implication:** all future feature engineering and modeling (Phases 6-7) must work with returns, not raw price levels, to avoid spurious results.

## 3. Autocorrelation

Simple daily return **direction** shows no statistically significant autocorrelation (Ljung-Box p-value = 0.6069) - yesterday's move does not linearly predict today's move.

**Follow-up (pre-stated, not post-hoc):** squared returns (a measure of volatility, independent of direction) show strong, highly significant autocorrelation (Ljung-Box p-value approximately 0.0000, all 10 tested lags positive). **USD/JPY exhibits genuine volatility clustering - large moves cluster together, and calm periods cluster together - even though direction itself does not.**

## 4. Correlation with Interest Rate Differential

Monthly change in the Fed-BOJ interest rate differential shows **no statistically significant linear correlation** with same-month USD/JPY returns (r=0.0604, p=0.5253) or next-month returns (r=-0.0120, p=0.8999), across 112-113 aligned months.

This does not contradict the long-run uptrend found in Section 1 - it specifically means the *simple, same-period, linear* version of this relationship isn't detectable at the monthly level. Markets are widely understood to price in rate expectations ahead of actual changes; testing that properly requires modeling expectations (e.g., futures-implied rates), which is out of scope for this phase and noted as a legitimate open question for later, more sophisticated modeling (Phase 6/7), not a dead end.

## 5. Volatility Regimes

Classifying periods into low/medium/high volatility terciles (20-day rolling, annualized) shows a clean, monotonic widening of return dispersion across regimes (std dev: 0.31% to 0.49% to 0.76%), while **mean return stays close to zero and similar across all three regimes.** This confirms, from a third independent angle, that risk (magnitude) and direction are separate properties of this data - volatility is far more predictable than direction.

The 10 highest single-day volatility readings in the entire dataset all fall in March 2020 - the real, independently verifiable COVID-19 market crash - a strong sanity check that the pipeline and methodology are sound.

## 6. Baseline Performance (The Bar Every Future Model Must Beat)

Per the Kill Criteria document, no future model or strategy is trusted until it beats these baselines, net of realistic transaction costs:

| Baseline | Total Return | Sharpe Ratio | Max Drawdown |
|---|---|---|---|
| Buy and Hold | +57.39% | 0.5436 | -14.75% |
| SMA(20/50) Crossover | +25.89% | 0.3803 | -17.52% |

**Notably, the simple SMA crossover underperformed buy-and-hold on every metric** - lower return, lower Sharpe, worse drawdown - once real transaction costs are included. This is consistent with Section 3's finding that simple price direction carries no detectable linear pattern.

**The official bar for Phase 7-8: Sharpe ratio > 0.5436, max drawdown better than -14.75%, net of costs.**

---

## Summary of Honest Conclusions

1. Model on returns, not price levels (proven necessity, not preference).
2. Do not expect simple price-pattern models to find direction - none has yet, across three independent tests (autocorrelation, correlation, SMA baseline).
3. Volatility, unlike direction, is genuinely predictable - a real, usable input for feature engineering and risk management.
4. The interest rate differential's long-run relationship with USD/JPY remains real and visible in the 10-year trend, but was not captured by simple month-to-month linear correlation - worth revisiting with more sophisticated tools in later phases, not with more of the same test.
5. A concrete, evidence-based performance bar now exists for every future phase to be honestly measured against.

This phase produced more null results than positive ones - and that is reported here as a legitimate, valuable outcome, not a shortfall. Per the project's own Kill Criteria philosophy, an honest "this simple approach does not work" is exactly the kind of finding that prevents wasted effort in later, more expensive phases.
