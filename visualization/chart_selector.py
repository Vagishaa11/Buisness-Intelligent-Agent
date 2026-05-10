import pandas as pd


class ChartSelector:
    """Deterministically picks a chart type based on result shape."""

    @staticmethod
    def select(df: pd.DataFrame) -> str:
        if df.empty or len(df.columns) < 1:
            return "table"

        num_cols = len(df.columns)
        numeric_cols = df.select_dtypes(include=["number"]).columns.tolist()
        non_numeric = [c for c in df.columns if c not in numeric_cols]

        # Detect datetime in object columns
        datetime_cols = df.select_dtypes(include=["datetime64"]).columns.tolist()
        for col in non_numeric:
            try:
                pd.to_datetime(df[col], errors="raise")
                datetime_cols.append(col)
            except (ValueError, TypeError):
                pass

        if num_cols == 1:
            if len(numeric_cols) == 1 and len(df) > 20:
                return "histogram"
            return "table"

        # Single row with metrics
        if len(df) == 1 and len(numeric_cols) >= 1:
            return "metric_cards"

        # 2 columns
        if num_cols == 2:
            if len(numeric_cols) == 1 and len(non_numeric) == 1:
                if datetime_cols:
                    return "area"
                if len(df) <= 8:
                    return "pie"
                if len(df) > 15:
                    return "hbar"
                return "bar"
            if len(numeric_cols) == 2:
                return "scatter"

        # 3 columns
        if num_cols == 3:
            if len(numeric_cols) == 1 and len(non_numeric) == 2:
                return "heatmap"
            if len(numeric_cols) >= 1:
                return "grouped_bar"

        # 4+ columns with datetime
        if datetime_cols and len(numeric_cols) >= 1:
            return "line"

        return "table"
