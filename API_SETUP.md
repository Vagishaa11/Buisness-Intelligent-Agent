# API Setup Guide

## Overview

The API provides REST endpoints to access your AI BI functionality programmatically. It's built with FastAPI and can be deployed independently from the Streamlit app.

## Installation

1. **Install dependencies** (if not already installed):

```bash
pip install -r requirements.txt
```

2. **Set OpenAI API key**:

```bash
# Windows (PowerShell)
$env:OPENAI_API_KEY="sk-..."

# Windows (CMD)
set OPENAI_API_KEY=sk-...

# macOS / Linux
export OPENAI_API_KEY="sk-..."
```

## Running the API

### Development Mode

```bash
python api.py
```

The API will start at `http://localhost:8000`

### With Uvicorn (Production)

```bash
uvicorn api:app --host 0.0.0.0 --port 8000 --reload
```

## API Endpoints

### 1. Health Check
```
GET /health
```
Check if the API is running.

**Response:**
```json
{
  "status": "healthy",
  "service": "AI BI API"
}
```

---

### 2. Upload CSV
```
POST /upload
```
Upload a CSV file and ingest it into SQLite.

**Parameters:**
- `file` (required): CSV file to upload

**Example (curl):**
```bash
curl -X POST "http://localhost:8000/upload" \
  -F "file=@data/kohli_ipl.csv"
```

**Response:**
```json
{
  "message": "File uploaded successfully",
  "filename": "kohli_ipl.csv",
  "table_name": "kohli_ipl",
  "rows": 1000,
  "columns": ["runs", "wickets", "matches", ...]
}
```

---

### 3. Get Schema
```
GET /schema
```
Retrieve the current dataset schema.

**Example (curl):**
```bash
curl -X GET "http://localhost:8000/schema"
```

**Response:**
```json
{
  "table_name": "kohli_ipl",
  "schema": {
    "runs": "INTEGER",
    "wickets": "INTEGER",
    "matches": "INTEGER"
  },
  "preview_rows": 10,
  "columns": ["runs", "wickets", "matches"]
}
```

---

### 4. Generate SQL
```
POST /generate-sql
Content-Type: application/json
```
Generate SQL from a natural language question (without executing).

**Request Body:**
```json
{
  "question": "Show total runs by year"
}
```

**Example (curl):**
```bash
curl -X POST "http://localhost:8000/generate-sql" \
  -H "Content-Type: application/json" \
  -d '{"question": "Show total runs by year"}'
```

**Response:**
```json
{
  "sql": "SELECT year, SUM(runs) as total_runs FROM kohli_ipl GROUP BY year ORDER BY year;",
  "valid": true
}
```

---

### 5. Execute Query
```
POST /execute-query
Content-Type: application/json
```
Generate and execute a SQL query, return results.

**Request Body:**
```json
{
  "question": "Show top 10 matches by runs"
}
```

**Example (curl):**
```bash
curl -X POST "http://localhost:8000/execute-query" \
  -H "Content-Type: application/json" \
  -d '{"question": "Show top 10 matches by runs"}'
```

**Response:**
```json
{
  "sql": "SELECT * FROM kohli_ipl ORDER BY runs DESC LIMIT 10;",
  "rows": 10,
  "columns": ["runs", "wickets", "matches", "venue"],
  "data": [
    {"runs": 183, "wickets": 0, "matches": 5, "venue": "MCG"},
    ...
  ]
}
```

---

### 6. Get Insights
```
POST /insights
Content-Type: application/json
```
Generate AI-powered insights from query results.

**Request Body:**
```json
{
  "question": "What are the trends in my sales data?"
}
```

**Example (curl):**
```bash
curl -X POST "http://localhost:8000/insights" \
  -H "Content-Type: application/json" \
  -d '{"question": "What are the trends in my sales data?"}'
```

**Response:**
```json
{
  "insights": "Based on the analysis, sales have increased by 15% over the past quarter. The top performing region is North America..."
}
```

---

### 7. Full Analysis (Recommended)
```
POST /analyze
Content-Type: application/json
```
Complete end-to-end analysis including SQL generation, execution, chart selection, and insights.

**Request Body:**
```json
{
  "question": "Analyze sales performance by region"
}
```

**Example (curl):**
```bash
curl -X POST "http://localhost:8000/analyze" \
  -H "Content-Type: application/json" \
  -d '{"question": "Analyze sales performance by region"}'
```

**Response:**
```json
{
  "sql": "SELECT region, SUM(sales) as total_sales, AVG(revenue) as avg_revenue FROM dataset GROUP BY region;",
  "query_result": {
    "sql": "SELECT ...",
    "rows": 5,
    "columns": ["region", "total_sales", "avg_revenue"],
    "data": [
      {"region": "North", "total_sales": 50000, "avg_revenue": 1000},
      ...
    ]
  },
  "chart_type": "bar",
  "chart_config": {
    "type": "bar",
    "title": "Sales by Region",
    "xaxis": "region",
    "yaxis": "total_sales"
  },
  "insights": "North region leads with 50,000 in total sales. Revenue consistency is highest in the South region..."
}
```

---

## Interactive API Documentation

Once the API is running, visit:
- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc

These provide interactive endpoints where you can test each endpoint directly.

---

## Usage Flow

### Simple Flow (Web App)
1. Upload CSV → 2. View Schema → 3. Ask Question → 4. Get Results

### Complete Flow (For Integration)
```
1. Upload CSV file (POST /upload)
2. Ask a question (POST /analyze)
3. Receive: SQL + data + chart configuration + insights
4. Render chart and display insights in your application
```

---

## Error Handling

All endpoints return appropriate HTTP status codes:
- `200` - Success
- `400` - Bad request (invalid input, no dataset loaded)
- `500` - Server error (query failed, API error)

Example error response:
```json
{
  "detail": "No dataset loaded. Upload a CSV first."
}
```

---

## Running Both Streamlit and API

You can run both simultaneously in different terminals:

**Terminal 1 - Streamlit App:**
```bash
streamlit run app.py
```

**Terminal 2 - API:**
```bash
python api.py
```

---

## Deployment

For production deployment:

1. Use a production ASGI server like **Gunicorn** with Uvicorn:
```bash
gunicorn -w 4 -k uvicorn.workers.UvicornWorker api:app
```

2. Use environment variables for API keys:
```bash
export OPENAI_API_KEY="sk-..."
python api.py
```

3. Consider adding authentication (JWT tokens) to secure your API.

---

## Integration Example (Python)

```python
import requests
import json

BASE_URL = "http://localhost:8000"

# 1. Upload CSV
with open("data/sales.csv", "rb") as f:
    files = {"file": f}
    response = requests.post(f"{BASE_URL}/upload", files=files)
    print(response.json())

# 2. Ask a question and get full analysis
question = {"question": "What are the top selling products?"}
response = requests.post(f"{BASE_URL}/analyze", json=question)
analysis = response.json()

print(f"SQL: {analysis['sql']}")
print(f"Rows: {analysis['query_result']['rows']}")
print(f"Chart Type: {analysis['chart_type']}")
print(f"Insights: {analysis['insights']}")
```

---

## Next Steps

- Test endpoints using the interactive Swagger UI at `/docs`
- Integrate with your frontend application
- Deploy to a cloud platform (AWS, Azure, Heroku, etc.)
