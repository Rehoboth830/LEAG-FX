from src.common.experiment_tracker import log_experiment

log_experiment(
    phase="Phase 7",
    description="XGBoost, walk-forward, predicting next-day USD/JPY direction from technical + macro features",
    parameters="train_window=500, test_window=60, n_estimators=100, max_depth=3, learning_rate=0.05",
    result="Does NOT beat baseline. Sharpe=-0.1888 (baseline 0.5436), max_drawdown=-19.87% (baseline -14.75%), win_rate=43.91%",
    notes="Third structurally distinct model (linear, bagging, boosting) to fail to beat baseline with negative Sharpe and sub-50% win rate. Strong convergent evidence across model families that current features/target lack exploitable directional signal.",
)
print("Logged.")
