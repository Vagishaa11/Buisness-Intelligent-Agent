import re


FORBIDDEN_KEYWORDS = [
    "DROP",
    "DELETE",
    "INSERT",
    "UPDATE",
    "ALTER",
    "CREATE",
    "TRUNCATE",
    "REPLACE",
    "EXEC",
    "EXECUTE",
    "PRAGMA",
    "ATTACH",
    "DETACH",
]


def is_safe_sql(sql: str) -> bool:
    """
    Validate that the SQL string is a safe read-only SELECT query.
    Returns True if safe, False otherwise.
    """
    if not sql or not isinstance(sql, str):
        return False

    stripped = sql.strip().upper()
    if not stripped.startswith("SELECT"):
        return False

    if stripped.endswith(";"):
        stripped = stripped[:-1]

    for keyword in FORBIDDEN_KEYWORDS:
        pattern = re.compile(rf"\b{keyword}\b", re.IGNORECASE)
        if pattern.search(sql):
            return False

    return True
