from src.common.experiment_tracker import log_experiment

log_experiment(
    phase="Phase 7",
    description="Random Forest, walk-forward, predicting next-day USD/JPY direction from technical + macro features",
    parameters="train_window=500, test_window=60, n_estimators=200, max_depth=5",
    result="Does NOT beat baseline. Sharpe=-0.2264 (baseline 0.5436), max_drawdown=-18.24% (baseline -14.75%), win_rate=46.19%",
    notes="Result closely mirrors logistic regression (Sharpe -0.26, win_rate 47.1%) despite being a structurally different, nonlinear model. Convergent evidence that these features lack exploitable directional signal, not just a limitation of one model type.",
)
print("Logged.")
