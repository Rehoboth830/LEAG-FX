"""
Validation promotion/exclusion logic (Phase 4, Step 3-4).

Runs the structural checks (Step 1) against real pending data in
PostgreSQL and updates validation_status to "passed" or "failed" —
satisfying FR-4.4 (failing data is flagged and excluded, never silently
passed through) and FR-4.5 (a validated dataset exists for Phase 5+
to consume directly).
"""

import pandas as pd

from src.common.db import get_connection
from src.common.logger import get_logger
from src.validation.structural_checks import (
    validate_economic_dataframe,
    validate_market_dataframe,
)

logger = get_logger(__name__)


def _fetch_pending(table: str, columns: str) -> pd.DataFrame:
    """Fetches all rows with validation_status = 'pending' from a table."""
    conn = get_connection()
    try:
        query = f"SELECT {columns} FROM {table} WHERE validation_status = 'pending'"
        df = pd.read_sql(query, conn)
    finally:
        conn.close()
    return df


def _apply_statuses(table: str, passed_ids: list, failed_ids: dict) -> None:
    """
    Updates validation_status for passed and failed rows.

    Args:
        table: table name to update.
        passed_ids: list of row ids that passed all checks.
        failed_ids: dict mapping row id -> combined issue description.
    """
    conn = get_connection()
    try:
        with conn.cursor() as cur:
            if passed_ids:
                cur.execute(
                    f"UPDATE {table} SET validation_status = 'passed' "
                    f"WHERE id = ANY(%s)",
                    (passed_ids,),
                )
            for row_id, notes in failed_ids.items():
                cur.execute(
                    f"UPDATE {table} SET validation_status = 'failed', "
                    f"validation_notes = %s WHERE id = %s",
                    (notes, row_id),
                )
        conn.commit()
    finally:
        conn.close()

    logger.info(
        f"{table}: {len(passed_ids)} rows promoted to 'passed', "
        f"{len(failed_ids)} rows marked 'failed'"
    )


def promote_market_data() -> dict:
    """
    Validates all pending raw_market_data rows and updates their status.

    Returns:
        A summary dict with counts of passed/failed rows and any
        dataset-level (non-row-specific) issues found.
    """
    df = _fetch_pending(
        "raw_market_data",
        "id, symbol, timestamp_utc, open, high, low, close, volume, source",
    )
    if df.empty:
        logger.info("No pending market data to validate")
        return {"passed": 0, "failed": 0, "dataset_level_issues": []}

    df = df.sort_values("timestamp_utc").reset_index(drop=True)
    id_lookup = df["id"]
    df_for_checks = df.set_index("id")

    report = validate_market_dataframe(df_for_checks)

    failed_ids = {}
    dataset_level_issues = []
    for issue in report.issues:
        if issue.row_identifier == "dataset":
            dataset_level_issues.append(issue.description)
            continue
        row_id = int(issue.row_identifier)
        existing = failed_ids.get(row_id, "")
        failed_ids[row_id] = (existing + "; " if existing else "") + issue.description

    all_ids = set(id_lookup.tolist())
    passed_ids = list(all_ids - set(failed_ids.keys()))

    _apply_statuses("raw_market_data", passed_ids, failed_ids)

    if dataset_level_issues:
        logger.warning(f"Dataset-level issues found: {dataset_level_issues}")

    return {
        "passed": len(passed_ids),
        "failed": len(failed_ids),
        "dataset_level_issues": dataset_level_issues,
    }


def promote_economic_data() -> dict:
    """
    Validates all pending raw_economic_data rows and updates their status.

    Returns:
        A summary dict with counts of passed/failed rows.
    """
    df = _fetch_pending(
        "raw_economic_data",
        "id, series_id, series_name, observation_date, value, source",
    )
    if df.empty:
        logger.info("No pending economic data to validate")
        return {"passed": 0, "failed": 0}

    id_lookup = df["id"]
    df_for_checks = df.set_index("id")

    report = validate_economic_dataframe(df_for_checks)

    failed_ids = {}
    for issue in report.issues:
        if issue.row_identifier == "dataset":
            continue
        row_id = int(issue.row_identifier)
        existing = failed_ids.get(row_id, "")
        failed_ids[row_id] = (existing + "; " if existing else "") + issue.description

    all_ids = set(id_lookup.tolist())
    passed_ids = list(all_ids - set(failed_ids.keys()))

    _apply_statuses("raw_economic_data", passed_ids, failed_ids)

    return {"passed": len(passed_ids), "failed": len(failed_ids)}


if __name__ == "__main__":
    market_summary = promote_market_data()
    economic_summary = promote_economic_data()

    print("Market data validation summary:", market_summary)
    print("Economic data validation summary:", economic_summary)
