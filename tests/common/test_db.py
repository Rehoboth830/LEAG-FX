"""
Tests for src/common/db.py.
"""

from src.common.db import get_connection, run_schema_file


def test_get_connection_returns_working_connection():
    conn = get_connection()
    try:
        with conn.cursor() as cur:
            cur.execute("SELECT 1")
            result = cur.fetchone()
        assert result[0] == 1
    finally:
        conn.close()


def test_run_schema_file_executes_sql(tmp_path):
    # A harmless, throwaway table - proves run_schema_file actually
    # executes arbitrary SQL, then cleans up after itself.
    schema_file = tmp_path / "test_schema.sql"
    schema_file.write_text(
        "CREATE TABLE IF NOT EXISTS _test_schema_table (id SERIAL PRIMARY KEY);"
    )

    run_schema_file(str(schema_file))

    conn = get_connection()
    try:
        with conn.cursor() as cur:
            cur.execute(
                "SELECT EXISTS (SELECT FROM information_schema.tables "
                "WHERE table_name = '_test_schema_table')"
            )
            exists = cur.fetchone()[0]
            assert exists

            # Clean up so this test never leaves residue.
            cur.execute("DROP TABLE _test_schema_table")
        conn.commit()
    finally:
        conn.close()
