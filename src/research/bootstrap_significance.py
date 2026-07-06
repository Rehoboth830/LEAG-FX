"""
Paired bootstrap significance test (Phase 7.1, significance check).

Tests whether a model's Sharpe ratio is genuinely, statistically
better than a baseline's, given a SMALL sample of paired returns -
the honest tool for exactly the concern raised about the ~96-105
period result: could this be a lucky small sample rather than a
real edge?
"""

import numpy as np
import pandas as pd

from src.common.logger import get_logger
from src.research.performance_metrics import compute_sharpe_ratio

logger = get_logger(__name__)


def paired_bootstrap_sharpe_test(
    model_returns: pd.Series,
    baseline_returns: pd.Series,
    n_iterations: int = 5000,
    seed: int = 42,
) -> dict:
    """
    Runs a paired bootstrap test: resamples (with replacement) the SAME
    period indices for both model and baseline returns jointly (preserving
    the pairing), computing the Sharpe difference each time. This builds
    an honest distribution of the likely Sharpe advantage, rather than
    trusting a single point estimate from a small sample.

    Args:
        model_returns: the model's per-period returns.
        baseline_returns: the baseline's per-period returns, SAME
            periods/order as model_returns.
        n_iterations: number of bootstrap resamples.
        seed: random seed for reproducibility.

    Returns:
        A dict with the observed difference, the bootstrap confidence
        interval, and the proportion of bootstrap samples where the
        model beat the baseline (a one-sided significance measure).
    """
    assert len(model_returns) == len(
        baseline_returns
    ), "Series must be paired, same length"

    rng = np.random.default_rng(seed)
    n = len(model_returns)
    model_arr = model_returns.values
    baseline_arr = baseline_returns.values

    observed_diff = compute_sharpe_ratio(model_returns) - compute_sharpe_ratio(
        baseline_returns
    )

    bootstrap_diffs = []
    for _ in range(n_iterations):
        indices = rng.integers(0, n, size=n)  # resample WITH replacement
        resampled_model = pd.Series(model_arr[indices])
        resampled_baseline = pd.Series(baseline_arr[indices])

        diff = compute_sharpe_ratio(resampled_model) - compute_sharpe_ratio(
            resampled_baseline
        )
        bootstrap_diffs.append(diff)

    bootstrap_diffs = np.array(bootstrap_diffs)
    ci_lower = np.percentile(bootstrap_diffs, 2.5)
    ci_upper = np.percentile(bootstrap_diffs, 97.5)
    prop_model_wins = (bootstrap_diffs > 0).mean()

    result = {
        "observed_sharpe_difference": float(observed_diff),
        "ci_95_lower": float(ci_lower),
        "ci_95_upper": float(ci_upper),
        "proportion_bootstrap_favoring_model": float(prop_model_wins),
        "significant_at_95pct": ci_lower > 0,  # entire 95% CI above zero
    }

    logger.info(
        f"Bootstrap test: observed_diff={observed_diff:.4f}, "
        f"95% CI=[{ci_lower:.4f}, {ci_upper:.4f}], "
        f"significant={result['significant_at_95pct']}"
    )
    return result
