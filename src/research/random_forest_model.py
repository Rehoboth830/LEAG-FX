"""
Random Forest model (Phase 7, Step 5).

A meaningfully more flexible model than logistic regression - capable
of capturing nonlinear relationships and feature interactions that
linear models and simple correlation tests structurally cannot detect.
Same walk-forward discipline as Step 4.
"""

import pandas as pd
from sklearn.ensemble import RandomForestClassifier

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
    Same walk-forward discipline as the logistic regression model:
    train only on the past, predict only on the immediately following
    test window, never look ahead.
    """
    splits = generate_walk_forward_splits(len(df), train_window, test_window)
    predictions = pd.Series(index=df.index, dtype=float)

    for split in splits:
        train_df, test_df = apply_split(df, split)

        X_train = train_df[FEATURE_COLUMNS]
        y_train = train_df["target"]
        X_test = test_df[FEATURE_COLUMNS]

        model = RandomForestClassifier(
            n_estimators=200, max_depth=5, random_state=42, n_jobs=-1
        )
        model.fit(X_train, y_train)

        test_predictions = model.predict(X_test)
        predictions.iloc[split.test_start_idx : split.test_end_idx] = test_predictions

    logger.info(
        f"Walk-forward random forest: {len(splits)} folds, "
        f"{predictions.notna().sum()} out-of-sample predictions made"
    )
    return predictions
