import os
import sys
from dotenv import load_dotenv

PROJECT_ROOT = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, PROJECT_ROOT)
load_dotenv(os.path.join(PROJECT_ROOT, ".env"))

import streamlit as st
import pandas as pd

from database import DatabaseHandler
from ai_engine import SQLGenerator, InsightGenerator, build_sql_prompt, build_insight_prompt
from analytics import QueryExecutor, PostProcessor
from visualization import ChartSelector, ChartRenderer
from utils import is_safe_sql

st.set_page_config(
    page_title="Business Intelligence AI Agent",
    layout="wide",
    page_icon="◆",
)

# ------------------------------------------------------------------
# Enterprise CSS Theme
# ------------------------------------------------------------------
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&display=swap');

    /* Hide Streamlit chrome */
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    header {visibility: hidden;}

    /* Main background */
    .stApp {
        background-color: #f5f6f8;
    }
    .main .block-container {
        padding-top: 1.5rem;
        padding-bottom: 2rem;
        max-width: 1400px;
    }

    /* Sidebar */
    section[data-testid="stSidebar"] {
        background-color: #ffffff;
        border-right: 1px solid #e9ecef;
    }
    section[data-testid="stSidebar"] > div {
        padding-top: 1.5rem;
        padding-left: 1.2rem;
        padding-right: 1.2rem;
    }

    /* Primary button */
    .stButton > button[kind="primary"] {
        background-color: #1a1a2e;
        color: #ffffff;
        border-radius: 10px;
        padding: 0.65rem 2rem;
        font-weight: 600;
        font-size: 0.95rem;
        border: none;
        box-shadow: 0 2px 8px rgba(26, 26, 46, 0.12);
        transition: all 0.2s ease;
        letter-spacing: 0.3px;
    }
    .stButton > button[kind="primary"]:hover {
        background-color: #2d2d44;
        box-shadow: 0 4px 14px rgba(26, 26, 46, 0.18);
        transform: translateY(-1px);
    }
    .stButton > button[kind="primary"]:active {
        transform: translateY(0);
    }

    /* Secondary / pill buttons */
    .stButton > button:not([kind="primary"]) {
        background-color: #f1f3f5;
        color: #495057;
        border-radius: 8px;
        border: 1px solid #e9ecef;
        font-weight: 500;
        font-size: 0.78rem;
        padding: 0.35rem 0.7rem;
        transition: all 0.15s ease;
        white-space: nowrap;
    }
    .stButton > button:not([kind="primary"]):hover {
        background-color: #e9ecef;
        border-color: #dee2e6;
        color: #343a40;
    }

    /* Text input - large query field */
    .stTextInput > div > div > input {
        border-radius: 12px;
        border: 1.5px solid #e9ecef;
        padding: 16px 20px;
        font-size: 1.05rem;
        background-color: #ffffff;
        color: #1a1a2e;
        transition: all 0.2s ease;
        font-family: 'Inter', sans-serif;
    }
    .stTextInput > div > div > input::placeholder {
        color: #adb5bd;
    }
    .stTextInput > div > div > input:focus {
        border-color: #4c6ef5;
        box-shadow: 0 0 0 4px rgba(76, 110, 245, 0.08);
    }

    /* File uploader */
    .stFileUploader > div > div {
        border-radius: 12px;
        border: 2px dashed #dee2e6;
        background-color: #f8f9fa;
        padding: 1rem;
    }
    .stFileUploader > div > div:hover {
        border-color: #4c6ef5;
        background-color: #f1f3f5;
    }

    /* Code blocks - dark professional */
    pre {
        border-radius: 12px !important;
        background-color: #161622 !important;
        border: 1px solid #2d2d44 !important;
        padding: 1.2rem !important;
    }
    code {
        font-family: 'SFMono-Regular', Consolas, 'Liberation Mono', Menlo, monospace !important;
        font-size: 0.82rem !important;
        color: #e9ecef !important;
    }

    /* Dataframe */
    .stDataFrame {
        border-radius: 10px;
    }
    .stDataFrame th {
        background-color: #f8f9fa !important;
        color: #495057 !important;
        font-weight: 600 !important;
        font-size: 0.8rem !important;
        text-transform: uppercase;
        letter-spacing: 0.5px;
    }
    .stDataFrame td {
        font-size: 0.85rem !important;
        color: #343a40 !important;
    }

    /* Native Streamlit containers with border */
    [data-testid="stVerticalBlockBorderWrapper"] {
        background-color: #ffffff;
        border-radius: 14px;
        border: 1px solid #e9ecef;
        box-shadow: 0 1px 3px rgba(0,0,0,0.03);
    }

    /* Expander */
    .streamlit-expanderHeader {
        font-weight: 600;
        color: #495057;
        font-size: 0.88rem;
        border-radius: 10px;
    }
    .streamlit-expanderContent {
        border-radius: 0 0 10px 10px;
    }

    /* Tabs */
    .stTabs [data-baseweb="tab-list"] {
        gap: 6px;
        background-color: transparent;
        padding: 4px;
        border-bottom: 1px solid #e9ecef;
    }
    .stTabs [data-baseweb="tab"] {
        padding: 10px 20px;
        border-radius: 8px 8px 0 0;
        font-weight: 500;
        font-size: 0.88rem;
        color: #868e96;
        border: none;
        background: transparent;
        letter-spacing: 0.2px;
    }
    .stTabs [aria-selected="true"] {
        color: #1a1a2e !important;
        background-color: #ffffff !important;
        border-bottom: 2px solid #4c6ef5 !important;
        font-weight: 600 !important;
    }

    /* Progress bar */
    .stProgress > div > div {
        background-color: #4c6ef5;
        border-radius: 4px;
    }

    /* Metric - sidebar compact */
    div[data-testid="stMetricValue"] {
        font-size: 1.5rem;
        font-weight: 700;
        color: #1a1a2e;
    }
    div[data-testid="stMetricLabel"] {
        font-size: 0.72rem;
        color: #868e96;
        text-transform: uppercase;
        letter-spacing: 0.8px;
    }

    /* Selectbox / text area */
    .stSelectbox > div > div, .stTextArea > div > div > textarea {
        border-radius: 10px;
        border: 1.5px solid #e9ecef;
    }

    /* Status pills */
    .status-pill {
        display: inline-block;
        padding: 3px 10px;
        border-radius: 20px;
        font-size: 0.72rem;
        font-weight: 600;
        text-transform: uppercase;
        letter-spacing: 0.5px;
    }
    .status-ok { background: #d3f9d8; color: #2b8a3e; }
    .status-err { background: #ffe3e3; color: #c92a2a; }
    .status-warn { background: #fff3bf; color: #e67700; }

    /* Insight card left accent */
    .insight-card {
        background: #ffffff;
        border-radius: 12px;
        border-left: 4px solid #4c6ef5;
        padding: 1.5rem;
        box-shadow: 0 1px 3px rgba(0,0,0,0.03);
    }

    /* Chart badge */
    .chart-badge {
        display: inline-block;
        background: #e7f5ff;
        color: #1864ab;
        padding: 4px 12px;
        border-radius: 20px;
        font-size: 0.72rem;
        font-weight: 700;
        text-transform: uppercase;
        letter-spacing: 0.8px;
    }

    /* Scrollbar */
    ::-webkit-scrollbar { width: 6px; height: 6px; }
    ::-webkit-scrollbar-track { background: transparent; }
    ::-webkit-scrollbar-thumb { background: #ced4da; border-radius: 3px; }
    ::-webkit-scrollbar-thumb:hover { background: #adb5bd; }
</style>
""", unsafe_allow_html=True)


# ------------------------------------------------------------------
# Helpers
# ------------------------------------------------------------------
def _schema_table(schema: dict) -> str:
    rows = ""
    for col, dtype in schema.items():
        badge_color = "#e7f5ff" if dtype == "numeric" else "#fff9db" if dtype == "datetime" else "#f3f0ff"
        text_color = "#1864ab" if dtype == "numeric" else "#e67700" if dtype == "datetime" else "#5f3dc4"
        rows += f"""
        <div style="display:flex; justify-content:space-between; align-items:center;
                    padding:6px 0; border-bottom:1px solid #f1f3f5; font-size:0.82rem;">
            <span style="font-weight:500; color:#343a40; font-family:monospace;">{col}</span>
            <span style="background:{badge_color}; color:{text_color}; padding:2px 8px;
                        border-radius:12px; font-size:0.68rem; font-weight:600;">{dtype}</span>
        </div>
        """
    return rows


# ------------------------------------------------------------------
# Sidebar
# ------------------------------------------------------------------
with st.sidebar:
    # Branding
    st.markdown("""
    <div style="margin-bottom:1.5rem;">
        <div style="font-size:1.25rem; font-weight:700; color:#1a1a2e; letter-spacing:-0.3px; line-height:1.2;">
            Business Intelligence
        </div>
        <div style="font-size:1.25rem; font-weight:700; color:#4c6ef5; letter-spacing:-0.3px; line-height:1.2;">
            AI Agent
        </div>
    </div>
    """, unsafe_allow_html=True)

    # Upload
    st.markdown('<div style="font-size:0.85rem; font-weight:600; color:#495057; margin-bottom:0.5rem;">Dataset Upload</div>', unsafe_allow_html=True)
    uploaded_file = st.file_uploader(
        "Drop CSV here", type=["csv"], label_visibility="collapsed"
    )

    if uploaded_file:
        save_path = os.path.join("data", uploaded_file.name)
        os.makedirs("data", exist_ok=True)
        with open(save_path, "wb") as f:
            f.write(uploaded_file.getbuffer())

        if "db" not in st.session_state:
            st.session_state.db = DatabaseHandler()
            st.session_state.db.ingest_csv(save_path, table_name="dataset")
        else:
            st.session_state.db.ingest_csv(save_path, table_name="dataset")
        st.success("Uploaded")

    if st.button("Reset Workspace", use_container_width=True):
        for key in list(st.session_state.keys()):
            del st.session_state[key]
        st.rerun()

    # Dataset info (only if loaded)
    if "db" in st.session_state:
        st.divider()
        st.markdown('<div style="font-size:0.85rem; font-weight:600; color:#495057; margin-bottom:0.6rem;">Dataset Summary</div>', unsafe_allow_html=True)

        db = st.session_state.db
        stats = db.get_dataset_stats()
        schema = db.get_schema()

        # Compact metric cards
        c1, c2, c3 = st.columns(3)
        c1.metric("Rows", f"{stats['rows']:,}")
        c2.metric("Cols", stats["columns"])
        c3.metric("Missing", f"{stats['missing']:,}")



# ------------------------------------------------------------------
# Main: empty state
# ------------------------------------------------------------------
if "db" not in st.session_state:
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        st.markdown("""
        <div style="text-align:center; padding:4rem 2rem; color:#868e96;">
            <div style="font-size:3rem; margin-bottom:1rem;">◆</div>
            <div style="font-size:1.1rem; font-weight:600; color:#495057; margin-bottom:0.5rem;">
                Workspace
            </div>
            <div style="font-size:0.9rem;">
                Upload a CSV dataset from the sidebar to begin your analysis.
            </div>
        </div>
        """, unsafe_allow_html=True)
    st.stop()

# ------------------------------------------------------------------
# Main: loaded state
# ------------------------------------------------------------------
db = st.session_state.db
schema = db.get_schema()
table_name = db.get_table_name()

# Header
st.markdown("""
<div style="margin-bottom:1.5rem;">
    <div style="font-size:1.4rem; font-weight:700; color:#1a1a2e; letter-spacing:-0.3px;">
        Workspace
    </div>
    <div style="font-size:0.88rem; color:#868e96; margin-top:2px;">
        Ask questions in plain English. The AI generates SQL, visualizations, and business insights.
    </div>
</div>
""", unsafe_allow_html=True)

# ------------------------------------------------------------------
# Query Card
# ------------------------------------------------------------------
with st.container(border=True):
    st.markdown('<div style="font-size:0.85rem; font-weight:600; color:#868e96; text-transform:uppercase; letter-spacing:1px; margin-bottom:0.8rem;">Ask Query</div>', unsafe_allow_html=True)

    sample_questions = [
        "Show total sales by region",
        "What is the average price per category?",
        "Top 10 customers by revenue",
        "Count of orders per month",
        "Sum of quantity by product",
    ]

    if "user_question" not in st.session_state:
        st.session_state.user_question = ""

    def set_question(q):
        st.session_state.user_question = q

    user_question = st.text_input(
        "",
        value=st.session_state.user_question,
        placeholder="e.g. What were total sales by region last quarter?",
        label_visibility="collapsed",
    )

    # Sample chips
    chip_cols = st.columns(len(sample_questions))
    for i, q in enumerate(sample_questions):
        chip_cols[i].button(q, key=f"sample_{i}", on_click=set_question, args=(q,), use_container_width=True)

    # Analyze button
    _, btn_col, _ = st.columns([1.5, 1, 1.5])
    analyze_clicked = btn_col.button("Analyze Data", type="primary", use_container_width=True)

# ------------------------------------------------------------------
# Analysis Pipeline
# ------------------------------------------------------------------
if analyze_clicked and user_question:
    progress = st.progress(0, text="Building prompt...")
    sql_prompt = build_sql_prompt(schema, table_name, user_question)

    progress.progress(20, text="Generating SQL...")
    with st.spinner(""):
        try:
            sql_gen = SQLGenerator()
            raw_sql = sql_gen.generate(sql_prompt)
        except Exception as exc:
            progress.empty()
            st.error(f"SQL generation failed: {exc}")
            st.stop()

    progress.progress(45, text="Validating SQL...")
    if not is_safe_sql(raw_sql):
        progress.empty()
        st.error("Generated SQL failed safety checks. Only SELECT queries are allowed.")
        st.stop()

    progress.progress(65, text="Executing query...")
    with st.spinner(""):
        try:
            executor = QueryExecutor(db.conn)
            result_df = executor.execute(raw_sql)
        except Exception as exc:
            progress.empty()
            st.error(f"Query execution failed: {exc}")
            st.stop()

    processor = PostProcessor()
    result_df = processor.clean(result_df)

    progress.progress(85, text="Creating visualization...")
    chart_type = ChartSelector.select(result_df)

    progress.progress(100, text="Complete")
    progress.empty()

    # ------------------------------------------------------------------
    # SQL Section
    # ------------------------------------------------------------------
    with st.container(border=True):
        st.markdown('<div style="font-size:0.8rem; font-weight:600; color:#868e96; text-transform:uppercase; letter-spacing:1px; margin-bottom:0.6rem;">Generated SQL</div>', unsafe_allow_html=True)
        st.code(raw_sql, language="sql")

    # ------------------------------------------------------------------
    # Visualization (Centerpiece)
    # ------------------------------------------------------------------
    with st.container(border=True):
        header_col, badge_col = st.columns([6, 1])
        with header_col:
            st.markdown('<div style="font-size:0.8rem; font-weight:600; color:#868e96; text-transform:uppercase; letter-spacing:1px;">Visualization</div>', unsafe_allow_html=True)
        with badge_col:
            st.markdown(
                f'<div style="text-align:right;"><span class="chart-badge">{chart_type.replace("_", " ").title()}</span></div>',
                unsafe_allow_html=True,
            )

        if not result_df.empty:
            fig = ChartRenderer.render(result_df, chart_type)
            st.plotly_chart(fig, use_container_width=True, height=550, key="main_chart")
        else:
            st.warning("No data returned for visualization.")

    # ------------------------------------------------------------------
    # Results + Insights (Two columns)
    # ------------------------------------------------------------------
    res_col, ins_col = st.columns([3, 2])

    with res_col:
        with st.container(border=True):
            st.markdown('<div style="font-size:0.8rem; font-weight:600; color:#868e96; text-transform:uppercase; letter-spacing:1px; margin-bottom:0.6rem;">Query Results</div>', unsafe_allow_html=True)
            st.dataframe(result_df, use_container_width=True, height=320)
            csv = result_df.to_csv(index=False).encode("utf-8")
            st.download_button(
                "Export CSV",
                data=csv,
                file_name="query_results.csv",
                mime="text/csv",
                use_container_width=True,
            )

    with ins_col:
        with st.container(border=True):
            st.markdown('<div style="font-size:0.8rem; font-weight:600; color:#868e96; text-transform:uppercase; letter-spacing:1px; margin-bottom:0.6rem;">AI Business Insights</div>', unsafe_allow_html=True)
            with st.spinner("Analyzing..."):
                try:
                    insight_gen = InsightGenerator()
                    summary = processor.summarize(result_df)
                    insight_prompt = build_insight_prompt(summary, user_question)
                    insights = insight_gen.generate(insight_prompt)
                except Exception as exc:
                    insights = f"Insight generation failed: {exc}"

            # Clean up insights formatting
            insights = insights.replace("```", "").strip()
            if not insights.startswith("-") and not insights.startswith("*"):
                insights = "- " + insights.replace("\n", "\n- ")

            st.markdown(
                f"""
                <div style="background: #f8f9fa; border-radius: 10px; padding: 1rem 1.2rem;
                            border-left: 3px solid #4c6ef5;">
                    <div style="font-size: 0.75rem; font-weight: 600; color: #4c6ef5;
                                text-transform: uppercase; letter-spacing: 0.8px;
                                margin-bottom: 0.6rem;">
                        Generated Analysis
                    </div>
                    <div style="color: #343a40; font-size: 0.9rem; line-height: 1.6;">
                        {insights.replace(chr(10), "<br>")}
                    </div>
                </div>
                """,
                unsafe_allow_html=True,
            )
