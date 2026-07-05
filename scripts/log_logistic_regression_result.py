"""
Logs the real, honest logistic regression result to the experiment
tracker - per the Fix 3 commitment to actually use this tool for real
decisions and findings, not just retroactively.
"""

from src.common.experiment_tracker import log_experiment

log_experiment(
    phase="Phase 7",
    description="Logistic regression, walk-forward, predicting next-day USD/JPY direction from technical + macro features",
    parameters="train_window=500, test_window=60, features=volatility/RSI/MACD/ATR/rate_differential/day_of_week/event_flag",
    result="Does NOT beat baseline. Sharpe=-0.2625 (baseline 0.5436), max_drawdown=-20.36% (baseline -14.75%), win_rate=47.10%",
    notes="Consistent with Phase 5 findings (no autocorrelation in direction, no simple rate-differential correlation). Per Kill Criteria, this model is retired, not further tuned.",
)

print("Logged.")
