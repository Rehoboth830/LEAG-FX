"""
Technical Analyst agent (Phase 9, Step 2).

Synthesizes real technical indicators into a verdict. Deliberately
LOW confidence by design - Phase 7 proved these indicators, fed into
three different ML models, do not predict direction. This agent's
job is to honestly report the technical state, not manufacture false
confidence the evidence doesn't support.
"""

from src.agents.schema import AgentReport


def analyze(
    rsi_14: float,
    macd_histogram: float,
    close_price: float,
    bb_upper: float,
    bb_lower: float,
) -> AgentReport:
    """
    Produces a technical verdict from current indicator values.

    Args:
        rsi_14: current RSI value (0-100).
        macd_histogram: current MACD histogram value.
        close_price: current closing price.
        bb_upper: current Bollinger upper band.
        bb_lower: current Bollinger lower band.

    Returns:
        An AgentReport with LOW confidence by design, reflecting
        Phase 7's finding that these signals alone lack predictive power.
    """
    evidence = []
    risks = []
    bullish_signals = 0
    bearish_signals = 0

    if rsi_14 > 70:
        evidence.append(f"RSI at {rsi_14:.1f} suggests overbought conditions")
        bearish_signals += 1
    elif rsi_14 < 30:
        evidence.append(f"RSI at {rsi_14:.1f} suggests oversold conditions")
        bullish_signals += 1
    else:
        evidence.append(f"RSI at {rsi_14:.1f} is neutral")

    if macd_histogram > 0:
        evidence.append(
            f"MACD histogram positive ({macd_histogram:.4f}), suggesting upward momentum"
        )
        bullish_signals += 1
    else:
        evidence.append(
            f"MACD histogram negative ({macd_histogram:.4f}), suggesting downward momentum"
        )
        bearish_signals += 1

    if close_price >= bb_upper:
        evidence.append("Price at or above upper Bollinger Band")
        bearish_signals += 1
    elif close_price <= bb_lower:
        evidence.append("Price at or below lower Bollinger Band")
        bullish_signals += 1

    if bullish_signals > bearish_signals:
        verdict = "buy"
    elif bearish_signals > bullish_signals:
        verdict = "sell"
    else:
        verdict = "hold"

    # Confidence capped LOW deliberately - Phase 7 proved these exact
    # indicators, fed into logistic regression/RF/XGBoost, produced
    # negative Sharpe ratios out-of-sample. This agent should never
    # claim more confidence than the evidence supports.
    confidence = 0.35

    risks.append(
        "Phase 7 found no ML model could profitably predict direction "
        "from these technical indicators (Sharpe -0.19 to -0.26 out-of-sample). "
        "This verdict should be weighted accordingly, not trusted alone."
    )

    return AgentReport(
        agent="TechnicalAnalyst",
        verdict=verdict,
        confidence=confidence,
        evidence=evidence,
        risks=risks,
    )
