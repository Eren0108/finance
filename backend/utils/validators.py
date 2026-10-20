from datetime import datetime
from typing import Tuple, Optional
from backend.config import ALLOWED_EXTENSIONS


def validate_date(date_str: str) -> str:
    """Validate and format date string to YYYY-MM-DD."""
    if not date_str or not isinstance(date_str, str):
        raise ValueError("Date is required.")
    
    date_str = date_str.strip()
    # Try parsing common formats
    formats = ["%Y-%m-%d", "%d-%m-%Y", "%d/%m/%Y", "%Y/%m/%d", "%d.%m.%Y"]
    for fmt in formats:
        try:
            parsed = datetime.strptime(date_str, fmt)
            return parsed.strftime("%Y-%m-%d")
        except ValueError:
            continue

    raise ValueError("Invalid date format. Expected YYYY-MM-DD or DD/MM/YYYY.")


def validate_month(month_str: str) -> str:
    """Validate month string format YYYY-MM."""
    if not month_str or not isinstance(month_str, str):
        raise ValueError("Month is required in YYYY-MM format.")
    
    month_str = month_str.strip()
    try:
        parsed = datetime.strptime(month_str, "%Y-%m")
        return parsed.strftime("%Y-%m")
    except ValueError:
        raise ValueError("Invalid month format. Expected YYYY-MM (e.g. 2026-10).")


def validate_amount(amount: any) -> float:
    """Validate and return positive float rounded to 2 decimal places."""
    if amount is None or amount == "":
        raise ValueError("Amount is required.")

    try:
        val = float(amount)
    except (ValueError, TypeError):
        raise ValueError("Amount must be a valid number.")

    if val <= 0:
        raise ValueError("Amount must be greater than zero.")

    return round(val, 2)


def validate_type(type_val: str) -> str:
    """Validate type is either 'income' or 'expense'."""
    if not type_val or not isinstance(type_val, str):
        raise ValueError("Type is required.")

    clean_type = type_val.strip().lower()
    if clean_type not in ("income", "expense"):
        raise ValueError("Type must be either 'income' or 'expense'.")

    return clean_type


def validate_file_extension(filename: str) -> bool:
    """Check if uploaded file has an allowed extension."""
    if "." not in filename:
        return False
    ext = filename.rsplit(".", 1)[1].lower()
    return ext in ALLOWED_EXTENSIONS
