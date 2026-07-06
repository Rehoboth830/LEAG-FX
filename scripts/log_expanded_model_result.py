from src.common.experiment_tracker import log_experiment

log_experiment(
    phase="Phase 7.1",
    description="Expanded feature set (cross-asset + surprise proxy) + 20-day horizon target, correctly evaluated on non-overlapping periods",
    parameters="15 features including US 10yr yield, Nikkei return, VIX, CPI surprise proxy; horizon=20 trading days",
    result="PROMISING, NOT YET VALIDATED: all 3 models beat both Phase 5 baseline (0.5436) AND fair same-sample naive 'always up' baseline (0.5262). RF: Sharpe 0.7298, WinRate 65.7% vs naive 57.1%.",
    notes="CRITICAL CAVEAT: only ~96-105 independent non-overlapping periods - a small sample compared to the thousands of daily observations behind every earlier test. Two real bugs were found and fixed en route (double-counting from overlapping returns; near-total data loss from non-forward-filled cross-asset features). Needs formal significance testing or more data before being trusted as a genuine edge, not just a good small-sample outcome.",
)
print("Logged - promising but flagged as needing further validation before trust.")
