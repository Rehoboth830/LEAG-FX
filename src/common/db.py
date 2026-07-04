"""
Shared PostgreSQL connection helper for LEAG FX.

Every module needing database access should use get_connection() from
here rather than building its own connection string — keeps config
handling consistent and satisfies NFR-4.1/4.2 (no hardcoded config).
"""

import os

import psycopg2
from dotenv import load_dotenv

from src.common.logger import get_logger

logger = get_logger(__name__)

load_dotenv()


def get_connection():
    """
    Returns a new psycopg2 connection using credentials from environment
    variables (loaded from .env). Caller is responsible for closing it,
    ideally via a `with` block or try/finally.
    """
    try:
        conn = psycopg2.connect(
            host=os.getenv("POSTGRES_HOST", "localhost"),
            port=os.getenv("POSTGRES_PORT", "5432"),
            dbname=os.getenv("POSTGRES_DB"),
            user=os.getenv("POSTGRES_USER"),
            password=os.getenv("POSTGRES_PASSWORD"),
        )
        return conn
    except psycopg2.OperationalError as e:
        logger.error(f"Failed to connect to PostgreSQL: {e}")
        raise


def run_schema_file(schema_path: str) -> None:
    """
    Executes a .sql schema file against the database.
    """
    # utf-8-sig strips a BOM if present (e.g. from PowerShell's Out-File
    # -Encoding utf8) and behaves identically to plain utf-8 if there's
    # no BOM — safe either way.
    with open(schema_path, "r", encoding="utf-8-sig") as f:
        sql = f.read()

    conn = get_connection()
    try:
        with conn.cursor() as cur:
            cur.execute(sql)
        conn.commit()
        logger.info(f"Successfully applied schema: {schema_path}")
    finally:
        conn.close()
