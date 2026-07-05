"""
Runs XGBoost on REAL USD/JPY data via walk-forward validation,
honestly checked against the Phase 5 baseline.
"""

import pandas as pd

from src.common.db import get_connection
from src.research.ml_target import build_direction_target
from src.research.model_evaluation import evaluate_model_predictions
from src.research.statistics import compute_daily_returns
from src.research.xgboost_model import train_and_predict_walk_forward


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
    returns.index = prices["observation_date"].iloc[1:].reset_index(drop=True)

    features["observation_date"] = pd.to_datetime(features["observation_date"]).dt.date
    merged = features.merge(
        returns.rename("return"),
        left_on="observation_date",
        right_index=True,
        how="inner",
    )

    target = build_direction_target(merged["return"].reset_index(drop=True))
    merged = merged.reset_index(drop=True)
    merged["target"] = target

    merged_clean = merged.dropna(
        subset=[
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
            "target",
        ]
    ).reset_index(drop=True)

    print(f"Training/testing on {len(merged_clean)} complete, aligned rows")

    predictions = train_and_predict_walk_forward(
        merged_clean, train_window=500, test_window=60
    )
    valid_idx = predictions.dropna().index

    result = evaluate_model_predictions(
        predictions.loc[valid_idx], merged_clean.loc[valid_idx, "return"]
    )

    print()
    print("XGBOOST - Real USD/JPY Results (out-of-sample, walk-forward)")
    print(f"  Total return:    {result['metrics'].total_return*100:+.2f}%")
    print(
        f"  Sharpe ratio:    {result['metrics'].sharpe_ratio:.4f}  (baseline: 0.5436)"
    )
    print(
        f"  Max drawdown:    {result['metrics'].max_drawdown*100:.2f}%  (baseline: -14.75%)"
    )
    print(f"  Win rate:        {result['metrics'].win_rate*100:.2f}%")
    print()
    print(f"  Beats baseline overall? {result['comparison']['beats_baseline_overall']}")


if __name__ == "__main__":
    main()
