"""
Correlation analysis module (Phase 5, Step 4).

Deliberately generic - tests statistical correlation between any two
aligned series, with a significance test attached. Used to check
whether real economic data (e.g., interest rate differential changes)
correlates with USD/JPY returns.
"""

from dataclasses import dataclass

import pandas as pd
from scipy import stats

from src.common.logger import get_logger

logger = get_logger(__name__)


@dataclass
class CorrelationResult:
    """Result of a Pearson correlation test between two series."""

    correlation_coefficient: float
    p_value: float
    n_observations: int
    is_significant: bool  # True if p_value < 0.05


def compute_correlation(series_a: pd.Series, series_b: pd.Series) -> CorrelationResult:
    """
    Computes Pearson correlation between two aligned series, with a
    significance test.

    Args:
        series_a: first series (must be same length/order as series_b).
        series_b: second series.

    Returns:
        A CorrelationResult with the coefficient, p-value, and a
        significance conclusion.
    """
    combined = pd.DataFrame({"a": series_a, "b": series_b}).dropna()

    corr_coef, p_value = stats.pearsonr(combined["a"], combined["b"])

    result = CorrelationResult(
        correlation_coefficient=float(corr_coef),
        p_value=float(p_value),
        n_observations=len(combined),
        is_significant=p_value < 0.05,
    )

    logger.info(
        f"Correlation: r={result.correlation_coefficient:.4f}, "
        f"p-value={result.p_value:.4f}, n={result.n_observations}, "
        f"significant={result.is_significant}"
    )
    return result
