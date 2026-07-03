"""
Lightweight experiment tracking for LEAG FX.

Purpose: record what was tried, when, with what parameters, and what
happened — so later phases (feature engineering, ML, backtesting) don't
quietly repeat failed experiments. Deliberately simple: a structured
CSV log, not a database or external tool. Can be upgraded later
(e.g., to MLflow) if the project outgrows this — nothing here is wasted
if that happens, since the CSV is just a plain record of history.
"""

import csv
from dataclasses import dataclass, fields
from datetime import datetime, timezone
from pathlib import Path

from src.common.logger import get_logger

logger = get_logger(__name__)

EXPERIMENTS_DIR = Path(__file__).resolve().parent.parent.parent / "experiments"
EXPERIMENTS_LOG = EXPERIMENTS_DIR / "experiment_log.csv"


@dataclass
class ExperimentEntry:
    """A single logged experiment."""

    timestamp: str
    phase: str
    description: str
    parameters: str
    result: str
    notes: str = ""


def log_experiment(
    phase: str,
    description: str,
    parameters: str,
    result: str,
    notes: str = "",
) -> ExperimentEntry:
    """
    Appends one experiment entry to the experiment log.

    Args:
        phase: which project phase this experiment belongs to (e.g. "Phase 1").
        description: what was tried, in plain language.
        parameters: key settings/inputs used, as a short string.
        result: what happened — outcome, metric, or observation.
        notes: optional extra context.

    Returns:
        The ExperimentEntry that was written.
    """
    entry = ExperimentEntry(
        timestamp=datetime.now(timezone.utc).isoformat(),
        phase=phase,
        description=description,
        parameters=parameters,
        result=result,
        notes=notes,
    )

    EXPERIMENTS_DIR.mkdir(parents=True, exist_ok=True)
    file_exists = EXPERIMENTS_LOG.exists()

    with open(EXPERIMENTS_LOG, "a", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        if not file_exists:
            writer.writerow([field.name for field in fields(ExperimentEntry)])
        writer.writerow(
            [
                entry.timestamp,
                entry.phase,
                entry.description,
                entry.parameters,
                entry.result,
                entry.notes,
            ]
        )

    logger.info(f"Logged experiment: [{phase}] {description} -> {result}")
    return entry
