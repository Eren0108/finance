from datetime import date
from flask import Blueprint, request
from backend.database import get_db
from backend.utils.helpers import api_response
from backend.utils.validators import validate_month, validate_amount
from backend.services.analytics import get_budget_status

budgets_bp = Blueprint("budgets", __name__, url_prefix="/api/budgets")


@budgets_bp.route("", methods=["GET"])
def get_budgets():
    """Retrieve all category budgets and spending progress for a month."""
    month = request.args.get("month")
    if not month:
        month = date.today().strftime("%Y-%m")

    try:
        clean_month = validate_month(month)
    except ValueError as e:
        return api_response(error=str(e), status_code=400)

    status_data = get_budget_status(clean_month)
    return api_response(data=status_data)


@budgets_bp.route("", methods=["POST"])
def set_budget():
    """Set or update a category budget for a month."""
    payload = request.get_json(silent=True) or {}
    category_id = payload.get("category_id")
    raw_month = payload.get("month")
    raw_limit = payload.get("limit_amount")

    if not category_id:
        return api_response(error="Category ID is required.", status_code=400)

    try:
        clean_month = validate_month(raw_month)
        limit_val = float(raw_limit) if raw_limit is not None else 0.0
        if limit_val < 0:
            return api_response(error="Budget limit cannot be negative.", status_code=400)
        clean_limit = round(limit_val, 2)
    except ValueError as e:
        return api_response(error=str(e), status_code=400)

    with get_db() as conn:
        cursor = conn.cursor()
        # Verify category exists
        cursor.execute("SELECT id FROM categories WHERE id = ?;", (category_id,))
        if not cursor.fetchone():
            return api_response(error="Category not found.", status_code=404)

        if clean_limit == 0:
            # If set to 0, remove the budget record
            cursor.execute(
                "DELETE FROM budgets WHERE category_id = ? AND month = ?;",
                (category_id, clean_month)
            )
        else:
            cursor.execute("""
                INSERT INTO budgets (category_id, month, limit_amount)
                VALUES (?, ?, ?)
                ON CONFLICT(category_id, month) 
                DO UPDATE SET limit_amount = excluded.limit_amount;
            """, (category_id, clean_month, clean_limit))

    # Return refreshed budget status for the month
    updated_data = get_budget_status(clean_month)
    return api_response(data=updated_data)
