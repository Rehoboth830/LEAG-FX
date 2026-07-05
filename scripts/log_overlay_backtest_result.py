from src.common.experiment_tracker import log_experiment

log_experiment(
    phase="Phase 8",
    description="Backtested volatility-based position-sizing overlay vs plain Buy and Hold",
    parameters="reduced_size=0.5 during predicted high-vol days, persistence rule",
    result="PROMISING: Sharpe improved 0.5436->0.6262, max drawdown improved -14.75%->-11.98%, at cost of total return 57.39%->48.64%",
    notes="CAVEAT NOT YET RESOLVED: regime thresholds used full-sample percentiles (look-ahead risk) - this result is NOT yet trustworthy until Step 5 rebuilds it with expanding-window, point-in-time-only thresholds. Do not treat as validated yet.",
)
print("Logged - flagged as unvalidated pending Step 5.")
