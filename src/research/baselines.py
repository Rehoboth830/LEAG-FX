"""
Baseline strategies module (Phase 5, Step 6).

Defines the baselines every future model or strategy MUST beat, per
the Kill Criteria document. Includes realistic transaction costs
(spread) from the start, since Roadmap v2 mandates cost realism as
always-on, never a later checkbox - even at the baseline stage.
"""

import pandas as pd

from src.common.logger import get_logger

logger = get_logger(__name__)

# A conservative, realistic USD/JPY spread assumption for a retail-style
# account, expressed as a fraction of price (roughly 1-2 pips typical).
DEFAULT_SPREAD_COST = 0.0002


def buy_and_hold_returns(
    prices: pd.Series, spread_cost: float = DEFAULT_SPREAD_COST
) -> pd.Series:
    """
    Buy-and-hold baseline: buy once at the start, hold throughout.
    Only ONE transaction cost is incurred (the initial entry).

    Args:
        prices: price series.
        spread_cost: one-time cost fraction applied at entry.

    Returns:
        A series of daily returns, with the entry cost reflected in
        the first period.
    """
    returns = prices.pct_change().dropna()
    returns_with_cost = returns.copy()
    if len(returns_with_cost) > 0:
        returns_with_cost.iloc[0] -= spread_cost
    return returns_with_cost


def sma_crossover_returns(
    prices: pd.Series,
    short_window: int = 20,
    long_window: int = 50,
    spread_cost: float = DEFAULT_SPREAD_COST,
) -> pd.Series:
    """
    Simple moving average crossover baseline: long when the short-term
    average is above the long-term average, flat otherwise. A
    transaction cost is applied EVERY time the position changes
    (enters or exits), not just once - this is what makes cost realism
    honest for a strategy that trades repeatedly.

    Args:
        prices: price series.
        short_window: short SMA period.
        long_window: long SMA period.
        spread_cost: cost fraction applied on every position change.

    Returns:
        A series of daily strategy returns, net of transaction costs.
    """
    short_sma = prices.rolling(window=short_window).mean()
    long_sma = prices.rolling(window=long_window).mean()

    position = (short_sma > long_sma).astype(int)  # 1 = long, 0 = flat
    position = position.shift(1)  # trade on NEXT day's return, avoiding look-ahead

    daily_returns = prices.pct_change()
    strategy_returns = position * daily_returns

    position_changes = position.diff().abs().fillna(0)
    cost_drag = position_changes * spread_cost
    strategy_returns_net = (strategy_returns - cost_drag).dropna()

    return strategy_returns_net
