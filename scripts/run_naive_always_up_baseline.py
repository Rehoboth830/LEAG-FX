"""
Honest check: how would a naive "always predict up" strategy perform
on the SAME 96 non-overlapping periods, given the real 57.96% base
rate of positive 20-day moves? This tells us how much of the models'
apparent edge is genuinely new versus just capturing the known uptrend.
"""

import pandas as pd

from src.common.db import get_connection
from src.research.horizon_target import build_horizon_direction_target
from src.research.performance_metrics import evaluate_strategy

HORIZON_DAYS = 20


def main():
    conn = get_connection()
    try:
        features = pd.read_sql(
            "SELECT observation_date FROM features_daily ORDER BY observation_date",
            conn,
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
    merged_clean = merged.dropna(subset=["target", "horizon_return"]).reset_index(
        drop=True
    )

    # Match the SAME 500-train-window offset and 60-test-window
    # structure used by the models, then sample every 20th row.
    valid_range = merged_clean.iloc[500:]
    non_overlapping = valid_range.iloc[::HORIZON_DAYS]

    naive_always_up_returns = non_overlapping[
        "horizon_return"
    ]  # "always predict up" = just take the raw return
    metrics = evaluate_strategy(
        naive_always_up_returns.dropna(), trading_days_per_year=252 // HORIZON_DAYS
    )

    print(f"NAIVE 'always predict up' baseline (same {len(non_overlapping)} periods):")
    print(
        f"  Sharpe: {metrics.sharpe_ratio:+.4f}  MaxDD: {metrics.max_drawdown*100:.2f}%  WinRate: {metrics.win_rate*100:.1f}%"
    )


if __name__ == "__main__":
    main()
