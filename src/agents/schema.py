"""
Shared specialist agent output schema (Phase 9, Step 1).

Every agent (Technical, Macro/Central Bank, Quant/ML, Risk) returns
this exact structure, so Phase 10's consensus engine never needs
custom parsing per agent - decided back in the original roadmap,
built for real here.
"""

from dataclasses import dataclass, field
from datetime import datetime, timezone

VALID_VERDICTS = {"buy", "sell", "hold"}


@dataclass
class AgentReport:
    """Standard output structure for every specialist agent."""

    agent: str
    verdict: str  # one of VALID_VERDICTS
    confidence: float  # 0.0 to 1.0
    evidence: list = field(default_factory=list)
    risks: list = field(default_factory=list)
    timestamp: str = field(
        default_factory=lambda: datetime.now(timezone.utc).isoformat()
    )

    def __post_init__(self):
        if self.verdict not in VALID_VERDICTS:
            raise ValueError(
                f"Invalid verdict '{self.verdict}' - must be one of {VALID_VERDICTS}"
            )
        if not (0.0 <= self.confidence <= 1.0):
            raise ValueError(
                f"Confidence must be between 0.0 and 1.0, got {self.confidence}"
            )
