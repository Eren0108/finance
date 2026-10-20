import math
from flask import Blueprint, request
from backend.database import get_db
from backend.utils.helpers import api_response, get_month_date_range
from backend.utils.validators import validate_date, validate_amount, validate_type

transactions_bp = Blueprint("transactions", __name__, url_prefix="/api/transactions")


@transactions_bp.route("", methods=["GET"])
def list_transactions():
    """
    List transactions with pagination and filters (date range, month, category, type, search).
    """
    month = request.args.get("month")
    start_date = request.args.get("startDate")
    end_date = request.args.get("endDate")
    category_id = request.args.get("categoryId")
    txn_type = request.args.get("type")
    search = request.args.get("search")

    page = max(1, int(request.args.get("page", 1)))
    limit = int(request.args.get("limit", 20))
    if limit <= 0:
        limit = 20

    if month and not (start_date or end_date):
        try:
            start_date, end_date = get_month_date_range(month)
        except Exception:
            pass

    query_conditions = []
    params = []

    if start_date:
        query_conditions.append("t.date >= ?")
        params.append(start_date)

    if end_date:
        query_conditions.append("t.date <= ?")
        params.append(end_date)

    if category_id:
        query_conditions.append("t.category_id = ?")
        params.append(int(category_id))

    if txn_type:
        query_conditions.append("t.type = ?")
        params.append(txn_type.lower())

    if search:
        query_conditions.append("LOWER(t.description) LIKE ?")
        params.append(f"%{search.strip().lower()}%")

    where_clause = f"WHERE {' AND '.join(query_conditions)}" if query_conditions else ""

    with get_db() as conn:
        cursor = conn.cursor()

        # Count total
        count_sql = f"SELECT COUNT(*) as total FROM transactions t {where_clause};"
        cursor.execute(count_sql, params)
        total_items = cursor.fetchone()["total"]

        total_pages = max(1, math.ceil(total_items / limit)) if total_items > 0 else 1
        offset = (page - 1) * limit

        # Select items
        select_sql = f"""
            SELECT 
                t.id, t.date, t.description, t.amount, t.type, t.source, t.statement_id, t.created_at,
                c.id as category_id, c.name as category_name, c.color as category_color
            FROM transactions t
            JOIN categories c ON t.category_id = c.id
            {where_clause}
            ORDER BY t.date DESC, t.id DESC
            LIMIT ? OFFSET ?;
        """
        cursor.execute(select_sql, params + [limit, offset])
        items = [
            {
                "id": r["id"],
                "date": r["date"],
                "description": r["description"],
                "amount": round(float(r["amount"]), 2),
                "type": r["type"],
                "source": r["source"],
                "statement_id": r["statement_id"],
                "category_id": r["category_id"],
                "category_name": r["category_name"],
                "category_color": r["category_color"],
                "created_at": r["created_at"]
            }
            for r in cursor.fetchall()
        ]

        return api_response(data={
            "items": items,
            "pagination": {
                "page": page,
                "limit": limit,
                "total_items": total_items,
                "total_pages": total_pages
            }
        })


@transactions_bp.route("", methods=["POST"])
def add_transaction():
    """Add a new transaction manually."""
    payload = request.get_json(silent=True) or {}
    raw_date = payload.get("date")
    raw_desc = (payload.get("description") or "").strip()
    raw_amount = payload.get("amount")
    raw_type = payload.get("type")
    category_id = payload.get("category_id")

    if not raw_desc:
        return api_response(error="Description is required.", status_code=400)
    if not category_id:
        return api_response(error="Category is required.", status_code=400)

    try:
        clean_date = validate_date(raw_date)
        clean_amount = validate_amount(raw_amount)
        clean_type = validate_type(raw_type)
    except ValueError as e:
        return api_response(error=str(e), status_code=400)

    with get_db() as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT id FROM categories WHERE id = ?;", (category_id,))
        if not cursor.fetchone():
            return api_response(error="Invalid category selected.", status_code=400)

        cursor.execute("""
            INSERT INTO transactions (date, description, amount, type, category_id, source)
            VALUES (?, ?, ?, ?, ?, 'manual');
        """, (clean_date, raw_desc, clean_amount, clean_type, category_id))

        new_id = cursor.lastrowid
        cursor.execute("""
            SELECT 
                t.id, t.date, t.description, t.amount, t.type, t.source,
                c.id as category_id, c.name as category_name, c.color as category_color
            FROM transactions t
            JOIN categories c ON t.category_id = c.id
            WHERE t.id = ?;
        """, (new_id,))
        item = dict(cursor.fetchone())
        item["amount"] = round(float(item["amount"]), 2)

        return api_response(data=item, status_code=201)


@transactions_bp.route("/<int:tx_id>", methods=["PUT"])
def update_transaction(tx_id: int):
    """Update an existing transaction."""
    payload = request.get_json(silent=True) or {}
    raw_date = payload.get("date")
    raw_desc = (payload.get("description") or "").strip()
    raw_amount = payload.get("amount")
    raw_type = payload.get("type")
    category_id = payload.get("category_id")

    if not raw_desc:
        return api_response(error="Description is required.", status_code=400)
    if not category_id:
        return api_response(error="Category is required.", status_code=400)

    try:
        clean_date = validate_date(raw_date)
        clean_amount = validate_amount(raw_amount)
        clean_type = validate_type(raw_type)
    except ValueError as e:
        return api_response(error=str(e), status_code=400)

    with get_db() as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT id FROM transactions WHERE id = ?;", (tx_id,))
        if not cursor.fetchone():
            return api_response(error="Transaction not found.", status_code=404)

        cursor.execute("SELECT id FROM categories WHERE id = ?;", (category_id,))
        if not cursor.fetchone():
            return api_response(error="Invalid category selected.", status_code=400)

        cursor.execute("""
            UPDATE transactions
            SET date = ?, description = ?, amount = ?, type = ?, category_id = ?
            WHERE id = ?;
        """, (clean_date, raw_desc, clean_amount, clean_type, category_id, tx_id))

        cursor.execute("""
            SELECT 
                t.id, t.date, t.description, t.amount, t.type, t.source,
                c.id as category_id, c.name as category_name, c.color as category_color
            FROM transactions t
            JOIN categories c ON t.category_id = c.id
            WHERE t.id = ?;
        """, (tx_id,))
        item = dict(cursor.fetchone())
        item["amount"] = round(float(item["amount"]), 2)

        return api_response(data=item)


@transactions_bp.route("/<int:tx_id>", methods=["DELETE"])
def delete_transaction(tx_id: int):
    """Delete a transaction."""
    with get_db() as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT id FROM transactions WHERE id = ?;", (tx_id,))
        if not cursor.fetchone():
            return api_response(error="Transaction not found.", status_code=404)

        cursor.execute("DELETE FROM transactions WHERE id = ?;", (tx_id,))
        return api_response(data={"message": f"Transaction #{tx_id} deleted successfully."})
