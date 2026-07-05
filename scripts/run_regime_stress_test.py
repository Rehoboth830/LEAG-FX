"""
Regime stress test for Buy and Hold (Phase 8, Step 2).

Answers: how did the SINGLE, ongoing buy-and-hold position (entered
once, held throughout) actually behave during each real regime period?
NOT "what if someone bought fresh at each period's start" - that would
be a different question. One entry cost, applied once, at the very
start of the full series.
"""

import pandas as pd

from src.common.db import get_connection
from src.research.baselines import buy_and_hold_returns
from src.research.performance_metrics import evaluate_strategy
from src.research.regime_periods import REGIME_PERIODS, tag_regime_period


def main():
    conn = get_connection()
    try:
        df = pd.read_sql(
            "SELECT timestamp_utc, close FROM raw_market_data "
            "WHERE validation_status = 'passed' ORDER BY timestamp_utc",
            conn,
        )
    finally:
        conn.close()

    df["date"] = pd.to_datetime(df["timestamp_utc"]).dt.tz_localize(None)

    # ONE continuous buy-and-hold return series - cost applied once,
    # at the true start, exactly as the actual position would experience it.
    full_returns = buy_and_hold_returns(df["close"])
    full_returns.index = df["date"].iloc[1:].reset_index(drop=True)

    regime_labels = tag_regime_period(pd.Series(full_returns.index))
    regime_labels.index = full_returns.index

    print("BUY AND HOLD - Stress Test Across Real Regime Periods")
    print(
        "(Same single position throughout - showing when its return was actually earned)"
    )
    print()

    for period in REGIME_PERIODS:
        period_returns = full_returns[regime_labels == period["label"]]
        if len(period_returns) == 0:
            continue

        metrics = evaluate_strategy(period_returns)
        print(f"{period['label']}")
        print(f"  Days: {len(period_returns)}")
        print(f"  Period return:  {metrics.total_return*100:+.2f}%")
        print(f"  Sharpe ratio:   {metrics.sharpe_ratio:.4f}")
        print(f"  Max drawdown:   {metrics.max_drawdown*100:.2f}%")
        print(f"  Win rate:       {metrics.win_rate*100:.2f}%")
        print()


if __name__ == "__main__":
    main()
