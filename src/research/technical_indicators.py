"""
Technical indicators module (Phase 6, Step 3).

Standard indicators (EMA, RSI, MACD, ATR, Bollinger Bands), built and
tested for mathematical correctness. Per Phase 5's findings, these are
NOT assumed to be predictive just because they're standard - they are
features to be tested honestly in Phase 7, not trusted signals.
"""

import pandas as pd

from src.common.logger import get_logger

logger = get_logger(__name__)


def compute_ema(prices: pd.Series, span: int) -> pd.Series:
    """Exponential moving average."""
    return prices.ewm(span=span, adjust=False).mean()


def compute_rsi(prices: pd.Series, window: int = 14) -> pd.Series:
    """
    Relative Strength Index. Ranges 0-100; conventionally >70 = "overbought",
    <30 = "oversold" - though Phase 5 gives real reason for skepticism
    about simple price-pattern signals like this.
    """
    delta = prices.diff()
    gains = delta.clip(lower=0)
    losses = -delta.clip(upper=0)

    avg_gain = gains.rolling(window=window).mean()
    avg_loss = losses.rolling(window=window).mean()

    rs = avg_gain / avg_loss.replace(0, float("nan"))
    rsi = 100 - (100 / (1 + rs))
    # Where avg_loss is exactly 0 (all gains), RSI is defined as 100.
    rsi = rsi.where(avg_loss != 0, 100.0)
    return rsi


def compute_macd(
    prices: pd.Series, fast: int = 12, slow: int = 26, signal: int = 9
) -> pd.DataFrame:
    """MACD line, signal line, and histogram."""
    ema_fast = compute_ema(prices, fast)
    ema_slow = compute_ema(prices, slow)
    macd_line = ema_fast - ema_slow
    signal_line = compute_ema(macd_line, signal)
    histogram = macd_line - signal_line

    return pd.DataFrame(
        {"macd_line": macd_line, "signal_line": signal_line, "histogram": histogram}
    )


def compute_atr(
    high: pd.Series, low: pd.Series, close: pd.Series, window: int = 14
) -> pd.Series:
    """Average True Range - a volatility measure based on high/low/close."""
    prev_close = close.shift(1)
    true_range = pd.concat(
        [high - low, (high - prev_close).abs(), (low - prev_close).abs()], axis=1
    ).max(axis=1)
    return true_range.rolling(window=window).mean()


def compute_bollinger_bands(
    prices: pd.Series, window: int = 20, num_std: float = 2.0
) -> pd.DataFrame:
    """Bollinger Bands: a moving average with upper/lower bands at N standard deviations."""
    middle = prices.rolling(window=window).mean()
    std = prices.rolling(window=window).std()
    upper = middle + num_std * std
    lower = middle - num_std * std

    return pd.DataFrame({"bb_upper": upper, "bb_middle": middle, "bb_lower": lower})
