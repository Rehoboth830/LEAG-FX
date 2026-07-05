from src.common.experiment_tracker import log_experiment

log_experiment(
    phase="Phase 9.1",
    description="First live comparison: rule-based vs Gemini LLM-powered Macro Analyst, same real data",
    parameters="Gemini 2.5 Flash (free tier), current_diff=2.90, 3m_trend=-0.01, 12m_trend=-0.95",
    result="Rule-based: HOLD (0.40) - narrowly missed sell threshold by 0.05pp. LLM: BUY (0.65) - weighed current level vs trend as separate nuanced factors, correctly carried forward Phase 5 honesty caveat.",
    notes="PROMISING BUT NOT YET VALIDATED: single observation, not a multi-trial test. LLM reasoning showed genuine nuance advantage over rigid thresholds, but consistency across many dates/calls has not been tested. Do not treat as proven superior yet.",
)
print("Logged - single promising observation, not yet validated.")
