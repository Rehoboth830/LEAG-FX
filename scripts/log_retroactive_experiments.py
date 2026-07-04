"""
Retroactive experiment log entries for real decisions already made
during Phases 0-4, logged now as Fix 3 to actually start using the
experiment tracker built in Phase 1.
"""

from src.common.experiment_tracker import log_experiment

log_experiment(
    phase="Phase 3",
    description="Chose market data source for USD/JPY OHLC",
    parameters="Compared yfinance, Twelve Data, Alpha Vantage, Polygon.io",
    result="Selected yfinance as primary (free, no key, good depth); Twelve Data as fallback",
    notes="See docs/phase3/01_data_cost_audit.md for full reasoning",
)

log_experiment(
    phase="Phase 3",
    description="Chose economic data sources for US and Japan indicators",
    parameters="FRED for US; BOJ Time-Series API and e-Stat considered for Japan",
    result="FRED selected for US (clear winner, free, official). BOJ API confirmed working after live-response testing; e-Stat requires registration (correction to original audit)",
    notes="BOJ manual example response structure did not match live API - had to verify against real response",
)

log_experiment(
    phase="Phase 0",
    description="Chose trading style: swing vs day trading",
    parameters="Compared data cost, infrastructure demand, and kill-criteria testability",
    result="Selected swing-style first; day trading scoped as future Phase 2.1 extension",
    notes="See docs/phase0/09_trading_style_decision.md",
)

log_experiment(
    phase="Phase 4",
    description="Chose validated-zone storage design",
    parameters="Compared separate validated tables vs a validation_status column on existing tables",
    result="Selected column-based approach - simpler, avoids duplication, sufficient at current scale",
    notes="Revisit if raw/validated data ever need different retention policies",
)

print("Retroactive experiment log entries written.")
