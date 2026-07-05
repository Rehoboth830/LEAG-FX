"""
Logistic Regression model (Phase 7, Step 4).

The simplest real ML model, deliberately - if this can't beat the
baseline, that's honest information for later, more complex models.
Uses the walk-forward framework (Step 2) so every prediction is
genuinely out-of-sample, never trained on data from its own test period.
"""

import pandas as pd
from sklearn.linear_model import LogisticRegression
from sklearn.preprocessing import StandardScaler

from src.common.logger import get_logger
from src.research.walk_forward import apply_split, generate_walk_forward_splits

logger = get_logger(__name__)

FEATURE_COLUMNS = [
    "volatility_5d",
    "volatility_20d",
    "volatility_60d",
    "rsi_14",
    "macd_line",
    "macd_signal",
    "macd_histogram",
    "atr_14",
    "rate_differential",
    "day_of_week",
    "economic_release_flag",
]


def train_and_predict_walk_forward(
    df: pd.DataFrame, train_window: int = 500, test_window: int = 60
) -> pd.Series:
    """
    Runs logistic regression through the full walk-forward process:
    for each split, train ONLY on the training window, predict ONLY
    on the following test window, then move on - never using future
    data to predict the past.

    Args:
        df: DataFrame with FEATURE_COLUMNS and a "target" column,
            sorted chronologically, index reset to a clean range.
        train_window: rows per training window.
        test_window: rows per test window.

    Returns:
        A pandas Series of out-of-sample predictions (0/1), indexed
        to match df, with NaN where no prediction was made (before
        the first test window).
    """
    splits = generate_walk_forward_splits(len(df), train_window, test_window)
    predictions = pd.Series(index=df.index, dtype=float)

    for split in splits:
        train_df, test_df = apply_split(df, split)

        X_train = train_df[FEATURE_COLUMNS]
        y_train = train_df["target"]
        X_test = test_df[FEATURE_COLUMNS]

        scaler = StandardScaler()
        X_train_scaled = scaler.fit_transform(X_train)
        X_test_scaled = scaler.transform(X_test)

        model = LogisticRegression(max_iter=1000)
        model.fit(X_train_scaled, y_train)

        test_predictions = model.predict(X_test_scaled)
        predictions.iloc[split.test_start_idx : split.test_end_idx] = test_predictions

    logger.info(
        f"Walk-forward logistic regression: {len(splits)} folds, "
        f"{predictions.notna().sum()} out-of-sample predictions made"
    )
    return predictions
