"""
Bias detection module (Phase 4, Step 2).

Deliberately generic — built with domain-agnostic inputs so this module
is shared between LEAG FX and CFIP rather than hardcoded to either
project's specific data shape (per the Kill Criteria / architecture
decision made in Phase 0).
"""

from dataclasses import dataclass, field

import pandas as pd

from src.common.logger import get_logger

logger = get_logger(__name__)


@dataclass
class BiasFinding:
    """A single detected bias issue."""

    bias_type: str
    identifier: str
    description: str


@dataclass
class BiasReport:
    """The full set of bias findings for a dataset."""

    findings: list = field(default_factory=list)

    @property
    def bias_detected(self) -> bool:
        return len(self.findings) > 0


def detect_survivorship_bias(
    full_universe: pd.DataFrame,
    analyzed_entity_ids: list,
    entity_id_col: str = "entity_id",
    is_active_col: str = "is_active",
) -> BiasReport:
    """
    Detects survivorship bias: entities that no longer exist (delisted
    stocks, dead crypto tokens, discontinued data series) being quietly
    excluded from an analysis, making results look better than reality.

    Args:
        full_universe: DataFrame of ALL entities that existed during the
            relevant period, with an entity id column and a boolean
            "is_active" column (False = no longer exists/survived).
        analyzed_entity_ids: the entity ids that were actually included
            in the analysis/backtest being checked.
        entity_id_col: name of the entity id column in full_universe.
        is_active_col: name of the is_active column in full_universe.

    Returns:
        A BiasReport. Flags a finding if any inactive ("dead") entity
        from the full universe is missing from analyzed_entity_ids.
    """
    findings = []
    dead_entities = full_universe[~full_universe[is_active_col]]

    for _, row in dead_entities.iterrows():
        entity_id = row[entity_id_col]
        if entity_id not in analyzed_entity_ids:
            findings.append(
                BiasFinding(
                    bias_type="survivorship_bias",
                    identifier=str(entity_id),
                    description=(
                        f"Entity '{entity_id}' is inactive/delisted in the full "
                        f"universe but excluded from the analyzed dataset — "
                        f"this can inflate apparent performance."
                    ),
                )
            )

    report = BiasReport(findings=findings)
    logger.info(
        f"Survivorship bias check: {len(dead_entities)} dead entities in universe, "
        f"{len(findings)} excluded from analysis"
    )
    return report


def detect_lookahead_bias(
    df: pd.DataFrame,
    decision_time_col: str,
    knowledge_date_col: str,
) -> BiasReport:
    """
    Detects look-ahead bias: using information at a decision point that
    was not actually available/published yet at that time. E.g., using
    a GDP figure's final revised value for a date when only the
    preliminary estimate had actually been published.

    Args:
        df: DataFrame representing a backtest/analysis dataset.
        decision_time_col: column name for when the decision was made.
        knowledge_date_col: column name for when that data point was
            actually known/published.

    Returns:
        A BiasReport. Flags any row where knowledge_date is AFTER the
        decision_time — meaning the data wasn't actually available yet
        when it was supposedly used.
    """
    findings = []
    decision_times = pd.to_datetime(df[decision_time_col])
    knowledge_dates = pd.to_datetime(df[knowledge_date_col])

    leak_mask = knowledge_dates > decision_times
    for idx in df[leak_mask].index:
        findings.append(
            BiasFinding(
                bias_type="lookahead_bias",
                identifier=str(idx),
                description=(
                    f"Row {idx}: data known on {knowledge_dates.loc[idx].date()} "
                    f"was used for a decision made on "
                    f"{decision_times.loc[idx].date()} — information leak "
                    f"from the future."
                ),
            )
        )

    report = BiasReport(findings=findings)
    logger.info(
        f"Look-ahead bias check: {len(df)} rows checked, {len(findings)} leaks found"
    )
    return report
