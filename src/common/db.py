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

    Returns:
        A psycopg2 connection object.

    Raises:
        psycopg2.OperationalError: if the connection cannot be established
            (e.g., Postgres container not running, wrong credentials).
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
    Executes a .sql schema file against the database. Used to set up
    tables (e.g., CREATE TABLE IF NOT EXISTS statements).

    Args:
        schema_path: path to the .sql file to execute.
    """
    with open(schema_path, "r", encoding="utf-8") as f:
        sql = f.read()

    conn = get_connection()
    try:
        with conn.cursor() as cur:
            cur.execute(sql)
        conn.commit()
        logger.info(f"Successfully applied schema: {schema_path}")
    finally:
        conn.close()
