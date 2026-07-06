from src.common.experiment_tracker import log_experiment

log_experiment(
    phase="Phase 7.1",
    description="Paired bootstrap significance test: Random Forest (expanded features, 20-day horizon) vs naive 'always up' baseline",
    parameters="n_iterations=5000, paired resampling, 96 non-overlapping periods",
    result="NOT statistically significant at 95% (CI: -0.94 to +2.57, crosses zero). However 78.1% of bootstrap resamples favored the model - suggestive but not proven.",
    notes="FINAL HONEST CONCLUSION for Phase 7.1: the promising Step 4 result does not survive rigorous significance testing. Should NOT be treated as validated (unlike Phase 8's volatility overlay, which passed equivalent scrutiny). Should not be dismissed either - 78.1% lean is real, worth revisiting with more historical data in the future. Genuinely in-between result, reported honestly as such.",
)
print("Logged - final honest conclusion: promising but not statistically proven.")
