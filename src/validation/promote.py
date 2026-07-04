"""
Validation promotion/exclusion logic (Phase 4, Step 3-4).

Runs the structural checks (Step 1) against real pending data in
PostgreSQL and updates validation_status to "passed" or "failed" -
satisfying FR-4.4 and FR-4.5.
"""

import pandas as pd

from src.common.db import get_connection
from src.common.logger import get_logger
from src.validation.structural_checks import (
    check_duplicates,
    check_missing_values,
    validate_economic_dataframe,
    validate_market_dataframe,
)

logger = get_logger(__name__)


def _fetch_pending(table: str, columns: str) -> pd.DataFrame:
    conn = get_connection()
    try:
        query = f"SELECT {columns} FROM {table} WHERE validation_status = 'pending'"
        df = pd.read_sql(query, conn)
    finally:
        conn.close()
    return df


def _apply_statuses(table: str, passed_ids: list, failed_ids: dict) -> None:
    conn = get_connection()
    try:
        with conn.cursor() as cur:
            if passed_ids:
                cur.execute(
                    f"UPDATE {table} SET validation_status = 'passed' WHERE id = ANY(%s)",
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


def _issues_to_status_maps(issues, id_lookup):
    failed_ids = {}
    dataset_level_issues = []
    for issue in issues:
        if issue.row_identifier == "dataset":
            dataset_level_issues.append(issue.description)
            continue
        row_id = int(issue.row_identifier)
        existing = failed_ids.get(row_id, "")
        failed_ids[row_id] = (existing + "; " if existing else "") + issue.description

    all_ids = set(id_lookup.tolist())
    passed_ids = list(all_ids - set(failed_ids.keys()))
    return passed_ids, failed_ids, dataset_level_issues


def promote_market_data() -> dict:
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
    passed_ids, failed_ids, dataset_level_issues = _issues_to_status_maps(
        report.issues, id_lookup
    )
    _apply_statuses("raw_market_data", passed_ids, failed_ids)

    if dataset_level_issues:
        logger.warning(f"Dataset-level issues found: {dataset_level_issues}")

    return {
        "passed": len(passed_ids),
        "failed": len(failed_ids),
        "dataset_level_issues": dataset_level_issues,
    }


def promote_economic_data() -> dict:
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
    passed_ids, failed_ids, _ = _issues_to_status_maps(report.issues, id_lookup)
    _apply_statuses("raw_economic_data", passed_ids, failed_ids)

    return {"passed": len(passed_ids), "failed": len(failed_ids)}


def promote_japan_economic_data() -> dict:
    """
    Validates all pending raw_japan_economic_data rows. Uses the generic
    check functions directly (rather than validate_economic_dataframe)
    since this table uses "series_code" instead of "series_id".
    """
    df = _fetch_pending(
        "raw_japan_economic_data",
        "id, series_code, series_name, observation_date, value, source",
    )
    if df.empty:
        logger.info("No pending Japan economic data to validate")
        return {"passed": 0, "failed": 0}

    id_lookup = df["id"]
    df_for_checks = df.set_index("id")

    issues = []
    issues += check_missing_values(df_for_checks, ["value"])
    issues += check_duplicates(
        df_for_checks, ["series_code", "observation_date", "source"]
    )

    passed_ids, failed_ids, _ = _issues_to_status_maps(issues, id_lookup)
    _apply_statuses("raw_japan_economic_data", passed_ids, failed_ids)

    logger.info(
        f"Japan economic data validation: {len(df)} rows, {len(failed_ids)} issues found"
    )
    return {"passed": len(passed_ids), "failed": len(failed_ids)}


if __name__ == "__main__":
    print("Market data:", promote_market_data())
    print("Economic data:", promote_economic_data())
    print("Japan economic data:", promote_japan_economic_data())
