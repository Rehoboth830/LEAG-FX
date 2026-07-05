"""
Runs all four Phase 9 specialist agents against REAL, current LEAG FX
data - the first time the agents actually analyze live data rather
than synthetic test scenarios.
"""

import pandas as pd

from src.agents.macro_analyst import analyze as macro_analyze
from src.agents.quant_ml_analyst import analyze as quant_analyze
from src.agents.risk_analyst import analyze as risk_analyze
from src.agents.technical_analyst import analyze as technical_analyze
from src.common.db import get_connection


def print_report(report):
    print(f"=== {report.agent} ===")
    print(f"Verdict: {report.verdict.upper()}  |  Confidence: {report.confidence:.2f}")
    print("Evidence:")
    for e in report.evidence:
        print(f"  - {e}")
    if report.risks:
        print("Risks:")
        for r in report.risks:
            print(f"  ! {r}")
    print()


def main():
    conn = get_connection()
    try:
        latest_features = pd.read_sql(
            "SELECT f.*, r.close AS real_close_price FROM features_daily f "
            "JOIN raw_market_data r ON f.observation_date = r.timestamp_utc::date "
            "WHERE f.rsi_14 IS NOT NULL AND r.validation_status = 'passed' "
            "ORDER BY f.observation_date DESC LIMIT 1",
            conn,
        )
        differential_history = pd.read_sql(
            "SELECT observation_date, rate_differential FROM features_daily "
            "WHERE rate_differential IS NOT NULL ORDER BY observation_date DESC LIMIT 400",
            conn,
        )
        vol_history = pd.read_sql(
            "SELECT volatility_20d FROM features_daily WHERE volatility_20d IS NOT NULL "
            "ORDER BY observation_date",
            conn,
        )
    finally:
        conn.close()

    latest = latest_features.iloc[0]
    print(f"Analysis date: {latest['observation_date']}")
    print()

    current_diff = differential_history["rate_differential"].iloc[0]
    diff_3m = differential_history["rate_differential"].iloc[
        min(90, len(differential_history) - 1)
    ]
    diff_12m = differential_history["rate_differential"].iloc[
        min(365, len(differential_history) - 1)
    ]

    low_thresh = vol_history["volatility_20d"].quantile(0.33)
    high_thresh = vol_history["volatility_20d"].quantile(0.67)
    current_vol = latest["volatility_20d"]
    if current_vol <= low_thresh:
        current_regime = "low"
    elif current_vol >= high_thresh:
        current_regime = "high"
    else:
        current_regime = "medium"

    reports = [
        technical_analyze(
            rsi_14=latest["rsi_14"],
            macd_histogram=latest["macd_histogram"],
            close_price=latest["real_close_price"],  # FIXED: real close, not bb_middle
            bb_upper=latest["bb_upper"],
            bb_lower=latest["bb_lower"],
        ),
        macro_analyze(current_diff, diff_3m, diff_12m),
        quant_analyze(),
        risk_analyze(current_regime),
    ]

    for report in reports:
        print_report(report)


if __name__ == "__main__":
    main()
