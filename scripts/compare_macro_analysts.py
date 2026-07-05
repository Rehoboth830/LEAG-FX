"""
Real, one-off comparison between the rule-based and LLM-powered Macro
Analysts, using the SAME real current data - Phase 9.1 Step 10.
"""

import pandas as pd

from src.agents.macro_analyst import analyze as rule_based_analyze
from src.agents.macro_analyst_llm import analyze as llm_analyze
from src.common.db import get_connection


def main():
    conn = get_connection()
    try:
        differential_history = pd.read_sql(
            "SELECT rate_differential FROM features_daily "
            "WHERE rate_differential IS NOT NULL ORDER BY observation_date DESC LIMIT 400",
            conn,
        )
    finally:
        conn.close()

    current_diff = differential_history["rate_differential"].iloc[0]
    diff_3m = differential_history["rate_differential"].iloc[
        min(90, len(differential_history) - 1)
    ]
    diff_12m = differential_history["rate_differential"].iloc[
        min(365, len(differential_history) - 1)
    ]

    print("=" * 60)
    print("RULE-BASED Macro Analyst:")
    print("=" * 60)
    rule_report = rule_based_analyze(current_diff, diff_3m, diff_12m)
    print(
        f"Verdict: {rule_report.verdict.upper()}  |  Confidence: {rule_report.confidence:.2f}"
    )
    for e in rule_report.evidence:
        print(f"  - {e}")
    for r in rule_report.risks:
        print(f"  ! {r}")

    print()
    print("=" * 60)
    print("LLM-POWERED (Gemini) Macro Analyst:")
    print("=" * 60)
    llm_report = llm_analyze(current_diff, diff_3m, diff_12m)
    print(
        f"Verdict: {llm_report.verdict.upper()}  |  Confidence: {llm_report.confidence:.2f}"
    )
    for e in llm_report.evidence:
        print(f"  - {e}")
    for r in llm_report.risks:
        print(f"  ! {r}")


if __name__ == "__main__":
    main()
