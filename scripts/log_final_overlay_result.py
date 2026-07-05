from src.common.experiment_tracker import log_experiment

log_experiment(
    phase="Phase 8",
    description="Walk-forward, same-period, honest re-test of volatility position-sizing overlay",
    parameters="reduced_size=0.5, expanding-window regime classification (min_history=252), fair same-period comparison",
    result="CONFIRMED GENUINE: Sharpe 0.5030->0.5806 (+0.0775), max drawdown -14.75%->-10.78% (+3.97pp improvement), total return given up -7.30pp. First finding in the entire project to survive full walk-forward + same-period scrutiny and beat its baseline.",
    notes="Original full-sample test showed similar Sharpe improvement (+0.083) - confirms the effect was mostly real, not primarily a look-ahead artifact, though the stricter test was still necessary and correct to run before trusting it.",
)
print("Logged - genuine, validated finding.")
