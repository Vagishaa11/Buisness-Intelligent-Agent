# AI BI Dashboard

A Streamlit-based AI-powered business intelligence pipeline.

Upload a CSV, ask questions in natural language, and get SQL queries, charts, and AI-generated insights automatically.

---

## Features

- **CSV Upload** → Auto-ingests into SQLite
- **Schema Extraction** → Feeds context to the AI
- **Natural Language to SQL** → Local AI (Ollama) generates safe SELECT queries
- **SQL Validation** → Only read-only queries are allowed
- **Auto Chart Selection** → Bar, line, scatter, grouped bar, metric cards, or table
- **AI Insights** → Summarizes trends and anomalies from results

---

## Project Structure

```
ai-bi-app/
|
├── app.py                  → Streamlit entry point
├── database/               → DB handling (CSV → SQLite, schema extraction)
├── ai_engine/              → AI + prompts (SQL generation, insights)
├── analytics/              → SQL execution + post-processing
├── visualization/          → Chart selection + Plotly rendering
├── utils/                  → SQL validator + helpers
├── data/                   → Uploaded datasets (created at runtime)
├── requirements.txt
└── README.md
```

---

## Setup

### 1. Install Ollama

Download and install Ollama from [ollama.com](https://ollama.com).

### 2. Pull a model

Open a terminal and run:

```bash
ollama pull llama3.2
```

Other good options:
- `ollama pull qwen2.5-coder`
- `ollama pull mistral`
- `ollama pull gemma2`

### 3. Install Python dependencies

```bash
pip install -r requirements.txt
```

### 4. Run the app

```bash
streamlit run app.py
```

---

## Usage

1. Make sure Ollama is running in the background.
2. Open the app in your browser (Streamlit will show the URL).
3. Pick your model in the sidebar (default is `llama3.2`).
4. Upload a CSV file.
5. Type a question like:
   - "Show total sales by region"
   - "What is the average price per category?"
   - "Top 10 customers by revenue"
6. Click **Analyze**.
7. View the generated SQL, results table, auto-selected chart, and AI insights.

---

## Architecture

```
Upload
  ↓
Store in SQLite
  ↓
Extract Schema
  ↓
Take Question
  ↓
Generate SQL (Ollama)
  ↓
Validate SQL (read-only)
  ↓
Execute Query
  ↓
Post-process Results
  ↓
Select Chart Type
  ↓
Render Chart
  ↓
Generate Insights
  ↓
Display Output
```

---

## Safety

The SQL validator explicitly blocks:

- DROP, DELETE, INSERT, UPDATE, ALTER, CREATE, TRUNCATE, REPLACE
- EXEC, EXECUTE, PRAGMA, ATTACH, DETACH

Only `SELECT` statements are allowed.

---

## Next Steps / Upgrades

- Conversational memory
- Forecasting / anomaly detection
- Export reports (PDF, PNG)
- Multi-table joins
- Custom chart overrides
