import pandas as pd
import sqlite3


class QueryExecutor:
    """Runs generated SQL and returns a DataFrame."""

    def __init__(self, conn: sqlite3.Connection):
        self.conn = conn

    def execute(self, sql: str) -> pd.DataFrame:
        try:
            return pd.read_sql_query(sql, self.conn)
        except Exception as exc:
            raise RuntimeError(f"Query execution failed: {exc}") from exc
