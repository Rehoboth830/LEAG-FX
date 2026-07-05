"""
Quant/ML Analyst agent (Phase 9, Step 4).

This agent's job is fundamentally different from the other three: it
honestly reports what Phases 5-8 actually found, preventing the other
agents from being over-trusted by the eventual consensus engine. It
always votes "hold" with low confidence for DIRECTION, since no
direction model beat baseline - but flags the validated volatility
finding as real, separate information for the Risk Analyst to use.
"""

from src.agents.schema import AgentReport


def analyze() -> AgentReport:
    """
    Produces the quant verdict - a permanent, evidence-based reality
    check, not a live calculation. Always "hold" with low confidence
    for direction, since Phase 7 found no model beats baseline.

    Returns:
        An AgentReport documenting the actual, honest state of
        quantitative evidence for USD/JPY direction and volatility.
    """
    evidence = [
        "Phase 5: no significant autocorrelation in return direction (Ljung-Box p=0.61)",
        "Phase 5: no significant correlation between rate differential changes and returns (p=0.53, p=0.90)",
        "Phase 5: SMA(20/50) crossover underperformed Buy and Hold on every metric",
        "Phase 7: Logistic Regression, Random Forest, and XGBoost all produced NEGATIVE "
        "out-of-sample Sharpe ratios predicting direction (-0.26, -0.23, -0.19)",
        "Phase 5 & 7 (CONFIRMED TWICE): volatility clustering/persistence IS real and strong "
        "(Ljung-Box p<0.0001; persistence baseline 96.81% classification accuracy)",
        "Phase 8 (VALIDATED, walk-forward, same-period): volatility-based position sizing "
        "genuinely improves Sharpe (+0.0775) and reduces max drawdown (-3.97pp)",
    ]

    risks = [
        "No model in this project has ever beaten the Buy and Hold baseline on DIRECTION. "
        "Any agent voting buy/sell with high confidence on direction should be weighted "
        "with significant skepticism by the consensus engine.",
    ]

    return AgentReport(
        agent="QuantMLAnalyst",
        verdict="hold",  # honest default: no validated directional edge exists
        confidence=0.3,
        evidence=evidence,
        risks=risks,
    )
