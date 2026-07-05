"""
Risk Analyst agent (Phase 9, Step 5).

Directly implements Phase 8's validated volatility overlay finding -
the ONE proven, walk-forward-tested result in this entire project.
This agent doesn't vote on direction at all - it flags position
SIZING conditions, and can effectively veto full-size exposure
regardless of what the other three agents say.
"""

from src.agents.schema import AgentReport


def analyze(current_regime: str, recommended_full_size: bool = True) -> AgentReport:
    """
    Produces a risk verdict based on the current volatility regime,
    using the exact logic validated in Phase 8.

    Args:
        current_regime: "low", "medium", or "high" - today's classified
            volatility regime (walk-forward classification).
        recommended_full_size: whether other agents are recommending
            a full-size position (used only for context in evidence).

    Returns:
        An AgentReport. Verdict is always "hold" (this agent doesn't
        vote on direction), but confidence and risks communicate a
        real, validated sizing recommendation.
    """
    evidence = [f"Current volatility regime: {current_regime}"]
    risks = []

    if current_regime == "high":
        evidence.append(
            "Phase 8 (validated, walk-forward): reducing position size during "
            "predicted high-volatility regimes improved Sharpe from 0.5030 to "
            "0.5806 and reduced max drawdown from -14.75% to -10.78%"
        )
        risks.append(
            "HIGH VOLATILITY REGIME: recommend reducing position size to 50% "
            "of normal, regardless of other agents' direction verdicts."
        )
        confidence = 0.85  # HIGH confidence - this is the validated finding
        recommended_position_size = 0.5
    else:
        evidence.append(f"Regime is '{current_regime}' - no size reduction warranted")
        confidence = 0.85
        recommended_position_size = 1.0

    return AgentReport(
        agent="RiskAnalyst",
        verdict="hold",  # this agent sizes risk, it doesn't call direction
        confidence=confidence,
        evidence=evidence
        + [f"Recommended position size: {recommended_position_size*100:.0f}%"],
        risks=risks,
    )
