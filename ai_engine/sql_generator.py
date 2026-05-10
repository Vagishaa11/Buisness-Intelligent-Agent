import os
import ollama


class SQLGenerator:
    """Generates SQL from natural language using Ollama."""

    def __init__(self, model: str = None):
        self.model = model or os.getenv("OLLAMA_MODEL", "llama3.2")
        try:
            ollama.list()
        except Exception as exc:
            raise ConnectionError(
                "Cannot connect to Ollama. Make sure Ollama is installed and running.\n"
                "Download: https://ollama.com\n"
                f"Error: {exc}"
            )

    def generate(self, prompt: str) -> str:
        response = ollama.generate(
            model=self.model,
            prompt=prompt,
            options={"temperature": 0.1, "num_predict": 500},
        )
        sql = response["response"].strip()
        return self._clean_sql(sql)

    @staticmethod
    def _clean_sql(sql: str) -> str:
        sql = sql.replace("```sql", "").replace("```", "").strip()
        # Sometimes models add extra text; try to extract SELECT block
        lower = sql.lower()
        if "select" in lower:
            start = lower.find("select")
            end = lower.find(";")
            if end == -1:
                end = len(sql)
            sql = sql[start:end].strip()
            return sql
        raise ValueError("Generated response does not appear to be a SELECT query.")
