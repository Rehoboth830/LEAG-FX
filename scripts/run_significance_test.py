"""
Runs the real, honest significance test: is Random Forest's apparent
edge over the naive 'always up' baseline statistically real, or could
it plausibly be a lucky small sample?
"""

import pandas as pd
from sklearn.ensemble import RandomForestClassifier

from src.common.db import get_connection
from src.research.bootstrap_significance import paired_bootstrap_sharpe_test
from src.research.horizon_target import build_horizon_direction_target
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


def main():
    conn = get_connection()
    try:
        features = pd.read_sql(
            "SELECT * FROM features_daily ORDER BY observation_date", conn
        )
        prices = pd.read_sql(
            "SELECT timestamp_utc, close FROM raw_market_data "
            "WHERE validation_status = 'passed' AND symbol = 'USDJPY=X' ORDER BY timestamp_utc",
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

    splits = generate_walk_forward_splits(
        len(merged_clean), train_window=500, test_window=60
    )
    predictions = pd.Series(index=merged_clean.index, dtype=float)

    for split in splits:
        train_df, test_df = apply_split(merged_clean, split)
        model = RandomForestClassifier(
            n_estimators=200, max_depth=5, random_state=42, n_jobs=-1
        )
        model.fit(train_df[FEATURE_COLUMNS], train_df["target"])
        predictions.iloc[split.test_start_idx : split.test_end_idx] = model.predict(
            test_df[FEATURE_COLUMNS]
        )

    valid_idx = predictions.dropna().index
    non_overlapping_idx = valid_idx[::HORIZON_DAYS]

    model_returns = (
        predictions.loc[non_overlapping_idx]
        * merged_clean.loc[non_overlapping_idx, "horizon_return"]
    ).dropna()
    naive_returns = merged_clean.loc[
        model_returns.index, "horizon_return"
    ]  # "always predict up"

    print(f"Testing significance on {len(model_returns)} paired periods")
    print()

    result = paired_bootstrap_sharpe_test(
        model_returns, naive_returns, n_iterations=5000
    )

    print("PAIRED BOOTSTRAP SIGNIFICANCE TEST: Random Forest vs Naive 'Always Up'")
    print(
        f"  Observed Sharpe difference:        {result['observed_sharpe_difference']:+.4f}"
    )
    print(
        f"  95% Confidence Interval:            [{result['ci_95_lower']:+.4f}, {result['ci_95_upper']:+.4f}]"
    )
    print(
        f"  Proportion of resamples favoring model: {result['proportion_bootstrap_favoring_model']*100:.1f}%"
    )
    print(f"  Statistically significant at 95%?  {result['significant_at_95pct']}")


if __name__ == "__main__":
    main()
