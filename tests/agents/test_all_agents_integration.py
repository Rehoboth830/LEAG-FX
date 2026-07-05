"""
Integration test (Phase 9, Step 6) - proves all four agents genuinely
conform to the shared AgentReport schema together, not just individually.
"""

from src.agents.macro_analyst import analyze as macro_analyze
from src.agents.quant_ml_analyst import analyze as quant_analyze
from src.agents.risk_analyst import analyze as risk_analyze
from src.agents.schema import AgentReport
from src.agents.technical_analyst import analyze as technical_analyze


def test_all_four_agents_return_valid_agent_reports():
    reports = [
        technical_analyze(
            rsi_14=55.0,
            macd_histogram=0.1,
            close_price=150.0,
            bb_upper=152.0,
            bb_lower=148.0,
        ),
        macro_analyze(
            current_differential=3.0, differential_3m_ago=2.8, differential_12m_ago=2.5
        ),
        quant_analyze(),
        risk_analyze(current_regime="medium"),
    ]

    agent_names = set()
    for report in reports:
        assert isinstance(report, AgentReport)
        assert report.verdict in {"buy", "sell", "hold"}
        assert 0.0 <= report.confidence <= 1.0
        assert len(report.evidence) > 0
        agent_names.add(report.agent)

    # All four are genuinely distinct agents, not duplicates.
    assert len(agent_names) == 4
