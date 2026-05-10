import pandas as pd


class PostProcessor:
    """Cleans and formats result DataFrames."""

    @staticmethod
    def clean(df: pd.DataFrame) -> pd.DataFrame:
        if df.empty:
            return df
        df = df.copy()
        df = df.where(pd.notnull(df), None)
        for col in df.select_dtypes(include=["object"]):
            df[col] = df[col].astype(str).replace("nan", "")
        return df

    @staticmethod
    def summarize(df: pd.DataFrame, max_rows: int = 20) -> str:
        """Create a text summary of the DataFrame for the insight generator."""
        lines = [f"Shape: {df.shape[0]} rows x {df.shape[1]} columns"]
        lines.append("Columns: " + ", ".join(df.columns))
        preview = df.head(max_rows)
        lines.append("\nPreview:")
        lines.append(preview.to_string(index=False))
        return "\n".join(lines)
