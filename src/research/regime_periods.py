"""
Regime period definitions (Phase 8, Step 1).

Defined from real, documented USD/JPY and central bank policy history -
BEFORE looking at how any strategy performed in each period. This
order matters: defining periods after seeing results would risk
unconsciously choosing boundaries that flatter a conclusion.

Sources: known Fed/BOJ policy history already referenced in the
Phase 2 knowledge base (fed_funds_rate.yaml, boj_policy_rate.yaml,
currency_intervention_history.yaml).
"""

import pandas as pd

REGIME_PERIODS = [
    {
        "label": "2016-2019: Post-Brexit, gradual Fed hikes, BOJ ultra-easy",
        "start": "2016-07-01",
        "end": "2019-12-31",
    },
    {
        "label": "2020: COVID crash and recovery",
        "start": "2020-01-01",
        "end": "2020-12-31",
    },
    {
        "label": "2021: Post-COVID recovery, globally low rates",
        "start": "2021-01-01",
        "end": "2021-12-31",
    },
    {
        "label": "2022-2023: Aggressive Fed hiking cycle, widening differential, BOJ intervention",
        "start": "2022-01-01",
        "end": "2023-12-31",
    },
    {
        "label": "2024-2026: Recent period, BOJ policy normalization begins",
        "start": "2024-01-01",
        "end": "2026-12-31",
    },
]


def tag_regime_period(dates: pd.Series) -> pd.Series:
    """
    Labels each date with its regime period, per REGIME_PERIODS.

    Args:
        dates: a series of dates.

    Returns:
        A series of regime period labels, same length/order as dates.
    """
    dates = pd.to_datetime(dates)
    labels = pd.Series(index=dates.index, dtype=object)

    for period in REGIME_PERIODS:
        mask = (dates >= period["start"]) & (dates <= period["end"])
        labels[mask] = period["label"]

    return labels
