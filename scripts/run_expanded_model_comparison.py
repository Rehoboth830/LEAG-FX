"""
Phase 7.1 Step 4 (CORRECTED) - fixed a real bug: the prices query had
no symbol filter, so after Step 1 added Nikkei/VIX into the SAME
raw_market_data table, it was silently pulling all three symbols'
prices mixed into one column.
"""

import pandas as pd
from sklearn.ensemble import RandomForestClassifier
from sklearn.linear_model import LogisticRegression
from sklearn.preprocessing import StandardScaler
from xgboost import XGBClassifier

from src.common.db import get_connection
from src.research.horizon_target import build_horizon_direction_target
from src.research.model_evaluation import evaluate_model_predictions
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
    "us_10yr_yield",
    "nikkei_return",
    "vix_close",
    "cpi_surprise_proxy",
]

HORIZON_DAYS = 20


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

    valid_idx = predictions.dropna().index
    result = evaluate_model_predictions(
        predictions.loc[valid_idx], df.loc[valid_idx, "horizon_return"]
    )

    print(
        f"  {model_name:20s}: Sharpe={result['metrics'].sharpe_ratio:+.4f}  "
        f"MaxDD={result['metrics'].max_drawdown*100:.2f}%  "
        f"WinRate={result['metrics'].win_rate*100:.1f}%  "
        f"BeatsBaseline={result['comparison']['beats_baseline_overall']}"
    )


def main():
    conn = get_connection()
    try:
        features = pd.read_sql(
            "SELECT * FROM features_daily ORDER BY observation_date", conn
        )
        prices = pd.read_sql(
            "SELECT timestamp_utc, close FROM raw_market_data "
            "WHERE validation_status = 'passed' AND symbol = 'USDJPY=X' "
            "ORDER BY timestamp_utc",
            conn,
        )
    finally:
        conn.close()

    prices["observation_date"] = (
        pd.to_datetime(prices["timestamp_utc"]).dt.tz_localize(None).dt.date
    )
    features["observation_date"] = pd.to_datetime(features["observation_date"]).dt.date

    merged = features.merge(
        prices[["observation_date", "close"]], on="observation_date", how="inner"
    )
    merged = merged.sort_values("observation_date").reset_index(drop=True)

    merged["target"] = build_horizon_direction_target(
        merged["close"], horizon_days=HORIZON_DAYS
    )
    merged["horizon_return"] = (
        merged["close"].shift(-HORIZON_DAYS) - merged["close"]
    ) / merged["close"]

    merged_clean = merged.dropna(
        subset=FEATURE_COLUMNS + ["target", "horizon_return"]
    ).reset_index(drop=True)
    print(
        f"Training/testing on {len(merged_clean)} complete rows, {HORIZON_DAYS}-day horizon"
    )
    print(
        f"Features used: {len(FEATURE_COLUMNS)} (including 4 new cross-asset/surprise features)"
    )
    print()

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
