"""
Walk-forward validation framework (Phase 7, Step 2).

THE most important piece of engineering in this phase. Standard random
train/test splits leak future information into the past for time
series data. This module enforces: train on the past, test on the
immediate future, roll forward - never shuffle, never peek ahead.
"""

from dataclasses import dataclass

import pandas as pd

from src.common.logger import get_logger

logger = get_logger(__name__)


@dataclass
class WalkForwardSplit:
    """A single train/test split in a walk-forward sequence."""

    train_start_idx: int
    train_end_idx: int  # exclusive
    test_start_idx: int
    test_end_idx: int  # exclusive


def generate_walk_forward_splits(
    n_rows: int, train_window: int, test_window: int, step: int = None
) -> list:
    """
    Generates a sequence of walk-forward train/test splits.

    Each split trains on a fixed-size window of the PAST, then tests
    on the NEXT chunk of data immediately following it - never
    overlapping, never looking backward from the test set into data
    the model wasn't trained on yet.

    Args:
        n_rows: total number of rows in the dataset (chronologically ordered).
        train_window: number of rows in each training window.
        test_window: number of rows in each test window.
        step: how far to advance between splits; defaults to test_window
            (non-overlapping test periods).

    Returns:
        A list of WalkForwardSplit objects, in chronological order.
    """
    if step is None:
        step = test_window

    splits = []
    train_start = 0
    while True:
        train_end = train_start + train_window
        test_start = train_end
        test_end = test_start + test_window

        if test_end > n_rows:
            break

        splits.append(
            WalkForwardSplit(
                train_start_idx=train_start,
                train_end_idx=train_end,
                test_start_idx=test_start,
                test_end_idx=test_end,
            )
        )
        train_start += step

    logger.info(f"Generated {len(splits)} walk-forward splits from {n_rows} rows")
    return splits


def apply_split(df: pd.DataFrame, split: WalkForwardSplit) -> tuple:
    """
    Applies a WalkForwardSplit to a DataFrame, returning (train_df, test_df).
    """
    train_df = df.iloc[split.train_start_idx : split.train_end_idx]
    test_df = df.iloc[split.test_start_idx : split.test_end_idx]
    return train_df, test_df
