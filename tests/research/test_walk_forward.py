"""
Tests for src/research/walk_forward.py.

This is the most important test suite in Phase 7 - it proves the
walk-forward logic never lets test data leak into training, and never
lets training data come from AFTER the test period.
"""

import pandas as pd

from src.research.walk_forward import apply_split, generate_walk_forward_splits


def test_splits_never_overlap_train_and_test():
    splits = generate_walk_forward_splits(n_rows=100, train_window=20, test_window=10)

    for split in splits:
        assert split.train_end_idx <= split.test_start_idx


def test_test_period_always_comes_after_train_period():
    splits = generate_walk_forward_splits(n_rows=100, train_window=20, test_window=10)

    for split in splits:
        # Every index in the test window must be numerically greater
        # than every index in the training window - test is always
        # chronologically AFTER train, never before or overlapping.
        assert split.test_start_idx >= split.train_end_idx
        assert split.test_end_idx > split.test_start_idx


def test_splits_advance_forward_through_the_dataset():
    splits = generate_walk_forward_splits(n_rows=100, train_window=20, test_window=10)

    for i in range(1, len(splits)):
        assert splits[i].train_start_idx > splits[i - 1].train_start_idx


def test_no_splits_generated_beyond_available_data():
    splits = generate_walk_forward_splits(n_rows=25, train_window=20, test_window=10)

    # train_window(20) + test_window(10) = 30 > 25 rows available -> zero splits
    assert len(splits) == 0


def test_apply_split_returns_correct_non_overlapping_dataframes():
    df = pd.DataFrame({"value": range(100)})
    splits = generate_walk_forward_splits(n_rows=100, train_window=20, test_window=10)

    train_df, test_df = apply_split(df, splits[0])

    assert len(train_df) == 20
    assert len(test_df) == 10
    # No row index appears in both - a real, literal proof of no overlap.
    assert set(train_df.index).isdisjoint(set(test_df.index))
    # Every test row's value is numerically greater than every train
    # row's value, confirming test data is chronologically later.
    assert test_df["value"].min() > train_df["value"].max()
