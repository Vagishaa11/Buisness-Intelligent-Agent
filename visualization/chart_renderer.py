import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots


class ChartRenderer:
    """Renders Plotly charts from a DataFrame with polished styling."""

    COLORS = [
        "#2563eb", "#3b82f6", "#60a5fa", "#93c5fd",
        "#1e40af", "#1d4ed8", "#4338ca", "#6366f1",
        "#8b5cf6", "#a78bfa", "#0ea5e9", "#38bdf8",
    ]
    TEMPLATE = "plotly_white"

    @staticmethod
    def render(df: pd.DataFrame, chart_type: str) -> go.Figure:
        if df.empty:
            fig = go.Figure()
            fig.update_layout(
                title="No data to display",
                template=ChartRenderer.TEMPLATE,
                paper_bgcolor="#ffffff",
                plot_bgcolor="#ffffff",
            )
            return fig

        numeric_cols = df.select_dtypes(include=["number"]).columns.tolist()
        non_numeric = [c for c in df.columns if c not in numeric_cols]

        if chart_type == "bar":
            x_col = non_numeric[0] if non_numeric else numeric_cols[0]
            y_col = numeric_cols[0] if numeric_cols else df.columns[1]
            fig = px.bar(
                df, x=x_col, y=y_col,
                color_discrete_sequence=ChartRenderer.COLORS,
                template=ChartRenderer.TEMPLATE,
            )
            fig.update_traces(
                marker_line_width=0,
                marker_color=ChartRenderer.COLORS[0],
            )

        elif chart_type == "hbar":
            x_col = numeric_cols[0] if numeric_cols else df.columns[1]
            y_col = non_numeric[0] if non_numeric else df.columns[0]
            fig = px.bar(
                df, x=x_col, y=y_col,
                color_discrete_sequence=ChartRenderer.COLORS,
                template=ChartRenderer.TEMPLATE, orientation="h",
            )
            fig.update_traces(
                marker_line_width=0,
                marker_color=ChartRenderer.COLORS[0],
            )
            fig.update_layout(yaxis=dict(autorange="reversed"))

        elif chart_type == "line":
            x_col = non_numeric[0] if non_numeric else df.columns[0]
            y_col = numeric_cols[0] if numeric_cols else df.columns[1]
            fig = px.line(
                df, x=x_col, y=y_col, markers=True,
                color_discrete_sequence=ChartRenderer.COLORS,
                template=ChartRenderer.TEMPLATE,
            )
            fig.update_traces(line=dict(width=3, color=ChartRenderer.COLORS[0]))

        elif chart_type == "area":
            x_col = non_numeric[0] if non_numeric else df.columns[0]
            y_col = numeric_cols[0] if numeric_cols else df.columns[1]
            fig = px.area(
                df, x=x_col, y=y_col,
                color_discrete_sequence=ChartRenderer.COLORS,
                template=ChartRenderer.TEMPLATE,
            )
            fig.update_traces(
                line=dict(width=2, color=ChartRenderer.COLORS[0]),
                fillcolor="rgba(37, 99, 235, 0.15)",
            )

        elif chart_type == "scatter":
            fig = px.scatter(
                df, x=df.columns[0], y=df.columns[1],
                size=numeric_cols[2] if len(numeric_cols) > 2 else None,
                color=non_numeric[0] if non_numeric else None,
                color_discrete_sequence=ChartRenderer.COLORS,
                template=ChartRenderer.TEMPLATE,
            )

        elif chart_type == "pie":
            names = non_numeric[0] if non_numeric else df.columns[0]
            values = numeric_cols[0] if numeric_cols else df.columns[1]
            fig = px.pie(
                df, names=names, values=values,
                hole=0.45,
                color_discrete_sequence=ChartRenderer.COLORS,
                template=ChartRenderer.TEMPLATE,
            )
            fig.update_traces(
                textinfo="percent+label",
                pull=[0.015] * len(df),
                textfont_size=12,
            )

        elif chart_type == "grouped_bar":
            x_col = non_numeric[0] if non_numeric else df.columns[0]
            y_col = numeric_cols[0] if numeric_cols else df.columns[1]
            color_col = non_numeric[1] if len(non_numeric) > 1 else None
            fig = px.bar(
                df, x=x_col, y=y_col, color=color_col,
                barmode="group",
                color_discrete_sequence=ChartRenderer.COLORS,
                template=ChartRenderer.TEMPLATE,
            )

        elif chart_type == "heatmap":
            cat_cols = non_numeric[:2]
            val_col = numeric_cols[0] if numeric_cols else df.columns[2]
            pivot = df.pivot_table(
                index=cat_cols[0], columns=cat_cols[1], values=val_col, aggfunc="sum"
            ).fillna(0)
            fig = px.imshow(
                pivot, text_auto=True, aspect="auto",
                color_continuous_scale="Blues",
                template=ChartRenderer.TEMPLATE,
            )
            fig.update_xaxes(side="top")

        elif chart_type == "histogram":
            x_col = numeric_cols[0] if numeric_cols else df.columns[0]
            fig = px.histogram(
                df, x=x_col,
                color_discrete_sequence=[ChartRenderer.COLORS[0]],
                template=ChartRenderer.TEMPLATE,
            )
            fig.update_traces(
                marker_line_width=1,
                marker_line_color="white",
                opacity=0.85,
            )
            fig.update_layout(
                bargap=0.08,
                yaxis_title="Count",
            )

        elif chart_type == "metric_cards":
            fig = ChartRenderer._metric_cards(df)

        else:
            fig = go.Figure(data=[go.Table(
                header=dict(
                    values=list(df.columns),
                    fill_color="#1a1a2e",
                    align="left",
                    font=dict(color="#ffffff", size=12),
                    line_color="#2d2d44",
                ),
                cells=dict(
                    values=[df[c] for c in df.columns],
                    fill_color=[["#f8f9fa", "#ffffff"] * (len(df) // 2 + 1)][:len(df)],
                    align="left",
                    font=dict(size=11, color="#495057"),
                    line_color="#e9ecef",
                ),
                columnwidth=[None] * len(df.columns),
            )])
            fig.update_layout(
                template=ChartRenderer.TEMPLATE,
                margin=dict(l=10, r=10, t=10, b=10),
            )

        fig.update_layout(
            margin=dict(l=20, r=20, t=50, b=20),
            title_font_size=15,
            title_font_color="#1a1a2e",
            legend_title_font_size=12,
            legend_font_size=11,
            legend_bgcolor="rgba(255,255,255,0.8)",
            paper_bgcolor="#ffffff",
            plot_bgcolor="#f8f9fa",
            font=dict(family="Inter, system-ui, -apple-system, sans-serif", color="#495057"),
            xaxis=dict(
                gridcolor="#e9ecef",
                linecolor="#dee2e6",
                tickfont=dict(size=11),
            ),
            yaxis=dict(
                gridcolor="#e9ecef",
                linecolor="#dee2e6",
                tickfont=dict(size=11),
            ),
        )
        return fig

    @staticmethod
    def _metric_cards(df: pd.DataFrame) -> go.Figure:
        numeric_cols = df.select_dtypes(include=["number"]).columns.tolist()
        fig = make_subplots(
            rows=1, cols=len(numeric_cols),
            subplot_titles=numeric_cols,
        )
        for i, col in enumerate(numeric_cols, start=1):
            val = df[col].values[0]
            fig.add_trace(
                go.Indicator(
                    mode="number",
                    value=val,
                    title={"text": col, "font": {"size": 13, "color": "#868e96"}},
                    number={
                        "font": {"size": 40, "color": "#1a1a2e"},
                        "valueformat": ",.0f",
                    },
                ),
                row=1, col=i,
            )
        fig.update_layout(
            margin=dict(l=20, r=20, t=60, b=20),
            template=ChartRenderer.TEMPLATE,
            paper_bgcolor="#ffffff",
            plot_bgcolor="#ffffff",
        )
        return fig
