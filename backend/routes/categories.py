from flask import Blueprint, request
from backend.database import get_db
from backend.utils.helpers import api_response
from backend.utils.validators import validate_type

categories_bp = Blueprint("categories", __name__, url_prefix="/api/categories")


@categories_bp.route("", methods=["GET"])
def list_categories():
    """Retrieve all categories, optionally filtered by type."""
    cat_type = request.args.get("type")
    
    with get_db() as conn:
        cursor = conn.cursor()
        if cat_type:
            cursor.execute("SELECT * FROM categories WHERE type = ? ORDER BY name ASC;", (cat_type.lower(),))
        else:
            cursor.execute("SELECT * FROM categories ORDER BY type DESC, name ASC;")
        
        rows = [dict(r) for r in cursor.fetchall()]
        return api_response(data=rows)


@categories_bp.route("", methods=["POST"])
def add_category():
    """Add a new category."""
    payload = request.get_json(silent=True) or {}
    name = (payload.get("name") or "").strip()
    cat_type = payload.get("type")
    color = (payload.get("color") or "#4F46E5").strip()

    if not name:
        return api_response(error="Category name is required.", status_code=400)

    try:
        clean_type = validate_type(cat_type)
    except ValueError as e:
        return api_response(error=str(e), status_code=400)

    with get_db() as conn:
        cursor = conn.cursor()
        try:
            cursor.execute(
                "INSERT INTO categories (name, type, color) VALUES (?, ?, ?);",
                (name, clean_type, color)
            )
            cat_id = cursor.lastrowid
            cursor.execute("SELECT * FROM categories WHERE id = ?;", (cat_id,))
            new_cat = dict(cursor.fetchone())
            return api_response(data=new_cat, status_code=201)
        except Exception as e:
            if "UNIQUE constraint failed" in str(e):
                return api_response(error=f"Category '{name}' already exists.", status_code=400)
            return api_response(error=f"Database error: {str(e)}", status_code=500)
