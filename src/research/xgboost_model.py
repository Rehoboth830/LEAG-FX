"""
XGBoost model (Phase 7, Step 6).

The last model in the original roadmap's list - gradient boosting,
structurally different again from both logistic regression and random
forest. Same walk-forward discipline throughout.
"""

import pandas as pd
from xgboost import XGBClassifier

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
    """Same walk-forward discipline as Steps 4 and 5."""
    splits = generate_walk_forward_splits(len(df), train_window, test_window)
    predictions = pd.Series(index=df.index, dtype=float)

    for split in splits:
        train_df, test_df = apply_split(df, split)

        X_train = train_df[FEATURE_COLUMNS]
        y_train = train_df["target"]
        X_test = test_df[FEATURE_COLUMNS]

        model = XGBClassifier(
            n_estimators=100,
            max_depth=3,
            learning_rate=0.05,
            random_state=42,
            eval_metric="logloss",
        )
        model.fit(X_train, y_train)

        test_predictions = model.predict(X_test)
        predictions.iloc[split.test_start_idx : split.test_end_idx] = test_predictions

    logger.info(
        f"Walk-forward XGBoost: {len(splits)} folds, "
        f"{predictions.notna().sum()} out-of-sample predictions made"
    )
    return predictions
