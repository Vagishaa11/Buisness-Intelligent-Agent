def build_sql_prompt(schema: dict, table_name: str, user_question: str) -> str:
    """Craft a strict prompt for SQL generation."""
    columns_desc = "\n".join(
        f"- {col}: {dtype}" for col, dtype in schema.items()
    )

    prompt = f"""You are an expert SQL analyst. Your task is to write a single SQLite SELECT query based on the user's question.

Table name: {table_name}
Columns:
{columns_desc}

Rules:
- Only output valid SQLite SELECT syntax.
- Do NOT use DELETE, DROP, INSERT, UPDATE, ALTER, CREATE, or any destructive command.
- If aggregation is needed, use standard SQL aggregate functions (SUM, AVG, COUNT, etc.).
- Use column names exactly as listed above.
- If the question is ambiguous, make a reasonable assumption and proceed.
- Return ONLY the SQL query. No markdown, no explanation, no code fences.

User question: {user_question}
"""
    return prompt


def build_insight_prompt(data_summary: str, user_question: str) -> str:
    """Craft a prompt for AI-generated business insights."""
    prompt = f"""You are a senior data analyst. Based on the query results below, write a concise 3-5 bullet point summary of key insights.

User question: {user_question}

Query result summary:
{data_summary}

Guidelines:
- Identify trends, highs, lows, or anomalies.
- Use plain business language.
- Keep each bullet to 1-2 sentences.
- Do not use markdown headers; just bullet points starting with '-'.
"""
    return prompt
