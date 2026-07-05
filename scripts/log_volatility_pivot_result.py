from src.common.experiment_tracker import log_experiment

log_experiment(
    phase="Phase 7",
    description="Pivoted from direction to volatility-regime prediction, per honest self-critique that direction target was misaligned with Phase 5 evidence",
    parameters="Same 3 models (LogReg, RF, XGBoost), same walk-forward setup, new target: tomorrow's high-vol regime",
    result="Persistence baseline (assume tomorrow=today) scores 96.81% accuracy. All 3 models score LOWER (90.49%/93.97%/94.66%) despite beating majority-class baseline (68.08%). Volatility clustering confirmed again, but models add no value over the simplest baseline.",
    notes="Honest, non-manufactured finding: pivot was directionally correct (volatility genuinely predictable), but current feature set does not yet improve on naive persistence. Modeling regime TRANSITIONS specifically, rather than overall regime accuracy, is a promising honest direction for a future phase.",
)
print("Logged.")
