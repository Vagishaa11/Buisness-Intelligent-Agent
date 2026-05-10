import sqlite3
import pandas as pd
from pathlib import Path


class DatabaseHandler:
    """Handles CSV ingestion, SQLite storage, and schema extraction."""

    def __init__(self, db_path: str = "data/app.db"):
        self.db_path = Path(db_path)
        self.db_path.parent.mkdir(parents=True, exist_ok=True)
        self.conn = sqlite3.connect(str(self.db_path), check_same_thread=False)
        self._table_name = None

    def ingest_csv(self, csv_path: str, table_name: str = "dataset") -> str:
        """Load a CSV into SQLite and return the table name."""
        df = pd.read_csv(csv_path)
        df.to_sql(table_name, self.conn, if_exists="replace", index=False)
        self._table_name = table_name
        return table_name

    def get_schema(self, table_name: str = None) -> dict:
        """Extract column names and inferred types for a table."""
        table = table_name or self._table_name
        if not table:
            raise ValueError("No table loaded. Ingest a CSV first.")

        cursor = self.conn.execute(f'PRAGMA table_info("{table}")')
        rows = cursor.fetchall()

        schema = {}
        for row in rows:
            col_name = row[1]
            col_type = row[2].upper()
            schema[col_name] = self._simplify_type(col_type)

        return schema

    def get_preview(self, table_name: str = None, n: int = 5) -> pd.DataFrame:
        """Return first n rows of the table."""
        table = table_name or self._table_name
        return pd.read_sql_query(f'SELECT * FROM "{table}" LIMIT {n}', self.conn)

    def get_table_name(self) -> str:
        return self._table_name

    def get_dataset_stats(self, table_name: str = None) -> dict:
        """Return row count, column count, and missing value count."""
        table = table_name or self._table_name
        if not table:
            return {"rows": 0, "columns": 0, "missing": 0}

        cursor = self.conn.execute(f'SELECT COUNT(*) FROM "{table}"')
        rows = cursor.fetchone()[0]

        cursor = self.conn.execute(f'PRAGMA table_info("{table}")')
        columns = [row[1] for row in cursor.fetchall()]

        missing = 0
        for col in columns:
            cursor = self.conn.execute(
                f'SELECT COUNT(*) FROM "{table}" WHERE "{col}" IS NULL'
            )
            missing += cursor.fetchone()[0]

        return {"rows": rows, "columns": len(columns), "missing": missing}

    @staticmethod
    def _simplify_type(sqlite_type: str) -> str:
        if sqlite_type in ("INT", "INTEGER", "BIGINT", "SMALLINT", "TINYINT"):
            return "numeric"
        if sqlite_type in ("REAL", "FLOAT", "DOUBLE", "NUMERIC", "DECIMAL"):
            return "numeric"
        if sqlite_type in ("TEXT", "VARCHAR", "CHAR", "STRING"):
            return "categorical"
        if sqlite_type in ("DATE", "DATETIME", "TIMESTAMP"):
            return "datetime"
        return "categorical"

    def close(self):
        if self.conn:
            self.conn.close()
            self.conn = None

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.close()
