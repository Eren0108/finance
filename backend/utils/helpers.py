from datetime import datetime, date
from dateutil.relativedelta import relativedelta
from flask import jsonify


def api_response(data=None, error=None, status_code=200):
    """
    Standard JSON API response according to rules.md:
    { "success": bool, "data": ..., "error": ... }
    """
    success = error is None and status_code < 400
    payload = {
        "success": success,
        "data": data,
        "error": str(error) if error else None
    }
    return jsonify(payload), status_code


def get_month_date_range(month_str: str):
    """
    Given 'YYYY-MM', returns (start_date, end_date) as 'YYYY-MM-01' and 'YYYY-MM-lastday'.
    """
    start_dt = datetime.strptime(month_str, "%Y-%m")
    # Next month minus one day
    next_month = start_dt + relativedelta(months=1)
    end_dt = next_month - relativedelta(days=1)
    return start_dt.strftime("%Y-%m-%d"), end_dt.strftime("%Y-%m-%d")


def get_past_n_months(n=6, base_date=None):
    """
    Returns list of 'YYYY-MM' strings for the past n months in chronological order.
    """
    if base_date is None:
        base_date = date.today()
    elif isinstance(base_date, str):
        base_date = datetime.strptime(base_date, "%Y-%m").date()

    months = []
    # e.g., for n=6, from 5 months ago to current month
    for i in range(n - 1, -1, -1):
        dt = base_date - relativedelta(months=i)
        months.append(dt.strftime("%Y-%m"))
    return months


def format_month_label(month_str: str) -> str:
    """Format '2026-10' to 'Oct 2026'."""
    dt = datetime.strptime(month_str, "%Y-%m")
    return dt.strftime("%b %Y")
