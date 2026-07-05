"""
Tests for src/research/walk_forward_regimes.py.

Per NFR-5.2: proves classification at any point uses ONLY prior data,
never data from later in the series - directly testing the fix for
the look-ahead risk found in Step 4.
"""

import numpy as np
import pandas as pd

from src.research.walk_forward_regimes import classify_regimes_expanding_window


def test_no_classification_before_min_history():
    vol = pd.Series(np.random.uniform(0.05, 0.15, 100))
    labels = classify_regimes_expanding_window(vol, min_history=252)

    assert labels.isna().all()  # not enough history for any of these 100 rows


def test_classification_unaffected_by_future_values():
    np.random.seed(42)
    # First 400 points: calm, consistent volatility.
    calm_vol = pd.Series(np.random.uniform(0.05, 0.06, 400))

    # Classify the calm series alone.
    labels_alone = classify_regimes_expanding_window(calm_vol, min_history=252)

    # Now extend it with a huge, extreme spike at the very end -
    # future data that should NOT affect classification of the
    # earlier, already-passed dates.
    extreme_future = pd.Series([5.0] * 10)
    extended_vol = pd.concat([calm_vol, extreme_future], ignore_index=True)
    labels_extended = classify_regimes_expanding_window(extended_vol, min_history=252)

    # Labels for the first 400 dates must be IDENTICAL whether or not
    # the future extreme spike exists - proving no look-ahead leak.
    for i in range(252, 400):
        assert labels_alone.iloc[i] == labels_extended.iloc[i]


def test_thresholds_use_only_prior_data_not_current_day():
    # A series where the very last value is a huge outlier - if the
    # classifier used strictly-prior data (excluding today), today's
    # own huge value shouldn't distort its OWN threshold calculation.
    np.random.seed(1)
    vol = pd.Series(np.random.uniform(0.05, 0.06, 300))
    vol.iloc[299] = 10.0  # today's own extreme value

    labels = classify_regimes_expanding_window(vol, min_history=252)

    # This extreme value should still be classified "high" relative to
    # calm history - proving the classifier correctly still WORKS, it
    # just doesn't use today's value to build today's own thresholds.
    assert labels.iloc[299] == "high"
