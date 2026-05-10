def format_number(value, decimals: int = 2):
    """Format a number for display."""
    if value is None:
        return ""
    try:
        return f"{float(value):,.{decimals}f}"
    except (ValueError, TypeError):
        return str(value)
