"""
Structural data quality validation (Phase 4, Step 1).

Checks raw market and economic data for missing values, duplicates,
outliers, and timestamp integrity issues (FR-4.1, FR-4.2). This module
only detects and reports issues — it does not decide what to do about
them (that is promotion/exclusion logic, Step 4).
"""

from dataclasses import dataclass, field

import pandas as pd

from src.common.logger import get_logger

logger = get_logger(__name__)


@dataclass
class ValidationIssue:
    """A single detected data quality problem."""

    check_name: str
    row_identifier: str
    description: str


@dataclass
class ValidationReport:
    """The full set of issues found for a dataset."""

    total_rows: int
    issues: list = field(default_factory=list)

    @property
    def passed(self) -> bool:
        return len(self.issues) == 0

    @property
    def issue_count(self) -> int:
        return len(self.issues)


def check_missing_values(df: pd.DataFrame, required_columns: list) -> list:
    """Flags rows with nulls in any required column."""
    issues = []
    for col in required_columns:
        if col not in df.columns:
            continue
        missing_rows = df[df[col].isna()]
        for idx in missing_rows.index:
            issues.append(
                ValidationIssue(
                    check_name="missing_value",
                    row_identifier=str(idx),
                    description=f"Missing value in required column '{col}'",
                )
            )
    return issues


def check_duplicates(df: pd.DataFrame, key_columns: list) -> list:
    """Flags rows that duplicate an earlier row on the given key columns."""
    issues = []
    duplicated_mask = df.duplicated(subset=key_columns, keep="first")
    for idx in df[duplicated_mask].index:
        issues.append(
            ValidationIssue(
                check_name="duplicate_row",
                row_identifier=str(idx),
                description=f"Duplicate row on key columns {key_columns}",
            )
        )
    return issues


def check_price_outliers(
    df: pd.DataFrame, price_column: str, threshold: float = 0.10
) -> list:
    """
    Flags day-over-day price changes exceeding the threshold (default 10%).
    This does not mean the data is wrong — real crisis-period moves can
    exceed this — it means the row is flagged for human/downstream review
    rather than silently trusted.
    """
    issues = []
    if price_column not in df.columns or len(df) < 2:
        return issues

    pct_change = df[price_column].pct_change().abs()
    outlier_mask = pct_change > threshold
    for idx in df[outlier_mask].index:
        change_pct = pct_change.loc[idx] * 100
        issues.append(
            ValidationIssue(
                check_name="price_outlier",
                row_identifier=str(idx),
                description=(
                    f"Price moved {change_pct:.1f}% from previous row "
                    f"(threshold {threshold*100:.0f}%)"
                ),
            )
        )
    return issues


def check_timestamp_integrity(df: pd.DataFrame, timestamp_column: str) -> list:
    """
    Flags timestamp problems: non-monotonic order, future-dated rows,
    or missing timezone information.

    Note: tz-naive and tz-aware timestamps cannot be directly compared
    in pandas without raising an error. When timestamps are tz-naive,
    they are localized to UTC solely for the future-date comparison —
    the missing_timezone issue is still raised separately, since a
    tz-naive timestamp is a real problem regardless of whether the
    future-date check can still run.
    """
    issues = []
    if timestamp_column not in df.columns:
        return issues

    timestamps = pd.to_datetime(df[timestamp_column])
    has_timezone = timestamps.dt.tz is not None

    if not timestamps.is_monotonic_increasing:
        issues.append(
            ValidationIssue(
                check_name="timestamp_order",
                row_identifier="dataset",
                description="Timestamps are not in strictly increasing order",
            )
        )

    if not has_timezone:
        issues.append(
            ValidationIssue(
                check_name="missing_timezone",
                row_identifier="dataset",
                description=(
                    "Timestamps have no timezone information "
                    "(expected UTC per FR-3.5)"
                ),
            )
        )
        timestamps_for_future_check = timestamps.dt.tz_localize("UTC")
    else:
        timestamps_for_future_check = timestamps

    now = pd.Timestamp.now(tz="UTC")
    future_mask = timestamps_for_future_check > now
    for idx in df[future_mask].index:
        issues.append(
            ValidationIssue(
                check_name="future_timestamp",
                row_identifier=str(idx),
                description="Timestamp is in the future",
            )
        )

    return issues


def validate_market_dataframe(df: pd.DataFrame) -> ValidationReport:
    """Runs all structural checks relevant to market OHLC data."""
    issues = []
    issues += check_missing_values(df, ["open", "high", "low", "close"])
    issues += check_duplicates(df, ["symbol", "timestamp_utc", "source"])
    issues += check_price_outliers(df, "close")
    issues += check_timestamp_integrity(df, "timestamp_utc")

    report = ValidationReport(total_rows=len(df), issues=issues)
    logger.info(
        f"Market data validation: {report.total_rows} rows, "
        f"{report.issue_count} issues found"
    )
    return report


def validate_economic_dataframe(df: pd.DataFrame) -> ValidationReport:
    """Runs all structural checks relevant to economic indicator data."""
    issues = []
    issues += check_missing_values(df, ["value"])
    issues += check_duplicates(df, ["series_id", "observation_date", "source"])

    report = ValidationReport(total_rows=len(df), issues=issues)
    logger.info(
        f"Economic data validation: {report.total_rows} rows, "
        f"{report.issue_count} issues found"
    )
    return report
