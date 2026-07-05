"""
Runs all three models (logistic regression, random forest, XGBoost)
on the VOLATILITY prediction target - the target Phase 5 statistically
proved has real, learnable signal, unlike direction. Compared against
two naive baselines: persistence (today's regime continues) and
majority-class.
"""

import pandas as pd
from sklearn.ensemble import RandomForestClassifier
from sklearn.linear_model import LogisticRegression
from sklearn.preprocessing import StandardScaler
from xgboost import XGBClassifier

from src.common.db import get_connection
from src.research.statistics import compute_daily_returns
from src.research.volatility_regimes import classify_regimes, compute_rolling_volatility
from src.research.volatility_target import (
    build_volatility_target,
    majority_class_baseline_accuracy,
    persistence_baseline_accuracy,
)
from src.research.walk_forward import apply_split, generate_walk_forward_splits

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


def run_model(model_name, model, df, use_scaling=False):
    splits = generate_walk_forward_splits(len(df), train_window=500, test_window=60)
    predictions = pd.Series(index=df.index, dtype=float)

    for split in splits:
        train_df, test_df = apply_split(df, split)
        X_train, y_train = train_df[FEATURE_COLUMNS], train_df["target"]
        X_test = test_df[FEATURE_COLUMNS]

        if use_scaling:
            scaler = StandardScaler()
            X_train = scaler.fit_transform(X_train)
            X_test = scaler.transform(X_test)

        model.fit(X_train, y_train)
        predictions.iloc[split.test_start_idx : split.test_end_idx] = model.predict(
            X_test
        )

    valid = predictions.dropna().index
    accuracy = (predictions.loc[valid] == df.loc[valid, "target"]).mean()
    print(f"  {model_name:20s}: accuracy = {accuracy:.4f}")
    return accuracy


def main():
    conn = get_connection()
    try:
        features = pd.read_sql(
            "SELECT * FROM features_daily ORDER BY observation_date", conn
        )
        prices = pd.read_sql(
            "SELECT timestamp_utc, close FROM raw_market_data "
            "WHERE validation_status = 'passed' ORDER BY timestamp_utc",
            conn,
        )
    finally:
        conn.close()

    prices["observation_date"] = (
        pd.to_datetime(prices["timestamp_utc"]).dt.tz_localize(None).dt.date
    )
    returns = compute_daily_returns(prices["close"])
    rolling_vol = compute_rolling_volatility(returns, window=20)
    regime_labels, _ = classify_regimes(rolling_vol)
    regime_labels.index = prices["observation_date"].iloc[1:].reset_index(drop=True)

    features["observation_date"] = pd.to_datetime(features["observation_date"]).dt.date
    merged = features.merge(
        regime_labels.rename("regime"),
        left_on="observation_date",
        right_index=True,
        how="inner",
    )
    merged = merged.reset_index(drop=True)
    merged["target"] = build_volatility_target(merged["regime"])

    merged_clean = merged.dropna(subset=FEATURE_COLUMNS + ["target"]).reset_index(
        drop=True
    )
    print(f"Training/testing on {len(merged_clean)} complete, aligned rows")
    print()

    persistence_acc = persistence_baseline_accuracy(merged_clean["regime"])
    majority_acc = majority_class_baseline_accuracy(merged_clean["target"])
    print(
        f"BASELINE - Persistence (today's regime continues): accuracy = {persistence_acc:.4f}"
    )
    print(
        f"BASELINE - Majority class:                          accuracy = {majority_acc:.4f}"
    )
    print()

    print("MODEL RESULTS (predicting tomorrow's HIGH-volatility regime):")
    run_model(
        "Logistic Regression",
        LogisticRegression(max_iter=1000),
        merged_clean,
        use_scaling=True,
    )
    run_model(
        "Random Forest",
        RandomForestClassifier(
            n_estimators=200, max_depth=5, random_state=42, n_jobs=-1
        ),
        merged_clean,
    )
    run_model(
        "XGBoost",
        XGBClassifier(
            n_estimators=100,
            max_depth=3,
            learning_rate=0.05,
            random_state=42,
            eval_metric="logloss",
        ),
        merged_clean,
    )


if __name__ == "__main__":
    main()
