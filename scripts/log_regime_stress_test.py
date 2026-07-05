from src.common.experiment_tracker import log_experiment

log_experiment(
    phase="Phase 8",
    description="Stress-tested the Buy and Hold baseline across 5 real regime periods (2016-2026)",
    parameters="Single continuous position, one entry cost, sliced by real documented regime periods",
    result="Return heavily concentrated in 2022-2023 (+22.92% of total +57.39%). 2020 (COVID) was a LOSING period (Sharpe -0.59). Worst drawdown of the full decade (-14.75%) occurred in 2022-2023, not during COVID.",
    notes="IMPORTANT: the Phase 5 Kill Criteria bar (Sharpe 0.5436) is substantially driven by one strong regime, not evenly earned across the decade. This should be kept in mind when judging future models against it - the bar may be easier or harder to clear depending on which regime a model is actually tested in.",
)
print("Logged.")
