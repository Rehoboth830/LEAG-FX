"""
Phase 5 Step 2 - visual sanity check before the formal stationarity
test. Saves a plot of raw price levels vs. daily returns, so we can
visually judge whether prices "wander" (trend) while returns look
more like noise around a stable level - the intuitive picture behind
stationarity, before the formal ADF test confirms or corrects it.
"""

import matplotlib

matplotlib.use("Agg")  # no display needed, just save to file
import matplotlib.pyplot as plt
import pandas as pd

from src.common.db import get_connection
from src.research.statistics import compute_daily_returns


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

    returns = compute_daily_returns(df["close"])

    fig, axes = plt.subplots(2, 1, figsize=(12, 8))
    axes[0].plot(df["timestamp_utc"], df["close"])
    axes[0].set_title("USD/JPY Price Level (raw)")
    axes[0].set_ylabel("Price")

    axes[1].plot(df["timestamp_utc"].iloc[1:], returns)
    axes[1].set_title("USD/JPY Daily Returns")
    axes[1].set_ylabel("Daily Return")

    plt.tight_layout()
    plt.savefig("stationarity_visual_check.png", dpi=100)
    print("Saved plot to stationarity_visual_check.png - open it to view.")


if __name__ == "__main__":
    main()
