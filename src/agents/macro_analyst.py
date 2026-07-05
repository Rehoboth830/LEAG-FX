"""
Macro/Central Bank Analyst agent (Phase 9, Step 3).

Synthesizes the real interest rate differential and its trend into a
verdict. Given HIGHER confidence than the Technical Analyst - Phase 5
found a genuine 10-year uptrend consistent with the widening US-Japan
rate gap, even though simple month-to-month correlation didn't confirm
a short-term linear relationship. This agent reasons about the
long-run structural story, not short-term timing.
"""

from src.agents.schema import AgentReport


def analyze(
    current_differential: float,
    differential_3m_ago: float,
    differential_12m_ago: float,
) -> AgentReport:
    """
    Produces a macro verdict from the real interest rate differential
    and its recent trend.

    Args:
        current_differential: today's Fed - BOJ rate differential.
        differential_3m_ago: the differential 3 months ago.
        differential_12m_ago: the differential 12 months ago.

    Returns:
        An AgentReport reasoning about the structural, long-run
        interest rate story - not short-term timing, which Phase 5
        found no simple linear relationship for.
    """
    evidence = [
        f"Current Fed-BOJ rate differential: {current_differential:.2f} percentage points",
    ]
    risks = []

    trend_3m = current_differential - differential_3m_ago
    trend_12m = current_differential - differential_12m_ago

    evidence.append(f"Differential change over 3 months: {trend_3m:+.2f}pp")
    evidence.append(f"Differential change over 12 months: {trend_12m:+.2f}pp")

    if current_differential > 2.0 and trend_12m >= 0:
        verdict = "buy"
        confidence = 0.55
        evidence.append(
            "Wide, stable-or-widening differential historically associated with "
            "USD/JPY's long-run uptrend (Phase 5, Section 1 finding)"
        )
    elif current_differential < 0.5 or trend_12m < -1.0:
        verdict = "sell"
        confidence = 0.5
        evidence.append(
            "Narrowing or low differential reduces the structural USD/JPY tailwind"
        )
    else:
        verdict = "hold"
        confidence = 0.4

    risks.append(
        "Phase 5 found NO significant same-month or next-month linear correlation "
        "between differential CHANGES and returns (p=0.53, p=0.90). This verdict "
        "reflects the long-run structural trend only, not short-term timing."
    )

    return AgentReport(
        agent="MacroCentralBankAnalyst",
        verdict=verdict,
        confidence=confidence,
        evidence=evidence,
        risks=risks,
    )
