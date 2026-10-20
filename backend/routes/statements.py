import os
import time
from flask import Blueprint, request
from werkzeug.utils import secure_filename

from backend.config import UPLOAD_DIR, MAX_CONTENT_LENGTH
from backend.database import get_db
from backend.utils.helpers import api_response
from backend.utils.validators import validate_file_extension
from backend.services.statement_parser import parse_statement_file

statements_bp = Blueprint("statements", __name__, url_prefix="/api/statements")


@statements_bp.route("/upload", methods=["POST"])
def upload_statement():
    """
    Handles statement upload (.csv, .xlsx, .xls), parses transactions,
    detects duplicates against database, and returns preview rows for review.
    """
    if "file" not in request.files:
        return api_response(error="No file part in the request.", status_code=400)

    file = request.files["file"]
    if not file or file.filename == "":
        return api_response(error="No file selected for upload.", status_code=400)

    filename = secure_filename(file.filename)
    if not validate_file_extension(filename):
        return api_response(
            error="Unsupported file format. Please upload a .csv, .xlsx, or .xls file.",
            status_code=400
        )

    # Save to uploads directory with timestamp
    timestamp = int(time.time())
    safe_filename = f"{timestamp}_{filename}"
    save_path = os.path.join(UPLOAD_DIR, safe_filename)
    file.save(save_path)

    # Check file size limit (5MB)
    if os.path.getsize(save_path) > MAX_CONTENT_LENGTH:
        os.remove(save_path)
        return api_response(error="File size exceeds the 5 MB limit.", status_code=400)

    # Load categories from DB
    with get_db() as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT id, name, type, color FROM categories;")
        cat_rows = cursor.fetchall()
        categories = [dict(c) for c in cat_rows]
        cat_name_map = {c["name"]: c["id"] for c in categories}
        cat_id_map = {c["id"]: c for c in categories}

    # Parse file
    try:
        parsed_rows = parse_statement_file(save_path, category_names=list(cat_name_map.keys()))
    except ValueError as e:
        if os.path.exists(save_path):
            os.remove(save_path)
        return api_response(error=str(e), status_code=400)
    except Exception as e:
        if os.path.exists(save_path):
            os.remove(save_path)
        return api_response(error=f"Error processing file: {str(e)}", status_code=500)

    # Check duplicates against DB
    with get_db() as conn:
        cursor = conn.cursor()
        enriched_rows = []
        dup_count = 0

        for idx, row in enumerate(parsed_rows):
            cursor.execute("""
                SELECT id FROM transactions 
                WHERE date = ? AND description = ? AND amount = ?
                LIMIT 1;
            """, (row["date"], row["description"], row["amount"]))
            existing = cursor.fetchone()

            is_duplicate = existing is not None
            if is_duplicate:
                dup_count += 1

            sugg_name = row["suggested_category"]
            cat_id = cat_name_map.get(sugg_name)
            if not cat_id and categories:
                cat_id = categories[0]["id"]

            enriched_rows.append({
                "row_id": idx + 1,
                "date": row["date"],
                "description": row["description"],
                "amount": row["amount"],
                "type": row["type"],
                "category_id": cat_id,
                "suggested_category": sugg_name,
                "is_duplicate": is_duplicate,
                "skip": is_duplicate  # Default skip to true if duplicate
            })

    return api_response(data={
        "filename": filename,
        "saved_filename": safe_filename,
        "total_rows": len(enriched_rows),
        "duplicate_count": dup_count,
        "new_count": len(enriched_rows) - dup_count,
        "rows": enriched_rows,
        "categories": categories
    })


@statements_bp.route("/confirm", methods=["POST"])
def confirm_statement():
    """
    Saves approved preview rows into database as confirmed transactions.
    """
    payload = request.get_json(silent=True) or {}
    filename = (payload.get("filename") or "imported_statement").strip()
    transactions = payload.get("transactions") or []

    if not transactions:
        return api_response(error="No transactions provided for confirmation.", status_code=400)

    imported_count = 0
    skipped_count = 0

    with get_db() as conn:
        cursor = conn.cursor()

        # Insert statement entry
        cursor.execute(
            "INSERT INTO statements (filename, rows_imported) VALUES (?, 0);",
            (filename,)
        )
        statement_id = cursor.lastrowid

        # Insert transactions
        for tx in transactions:
            if tx.get("skip", False):
                skipped_count += 1
                continue

            date_val = tx.get("date")
            desc_val = (tx.get("description") or "").strip()
            amount_val = float(tx.get("amount", 0.0))
            type_val = tx.get("type", "expense")
            cat_id = tx.get("category_id")

            if not (date_val and desc_val and amount_val > 0 and cat_id):
                skipped_count += 1
                continue

            cursor.execute("""
                INSERT INTO transactions (date, description, amount, type, category_id, source, statement_id)
                VALUES (?, ?, ?, ?, ?, 'statement', ?);
            """, (date_val, desc_val, amount_val, type_val, cat_id, statement_id))
            imported_count += 1

        # Update statement record with imported row count
        cursor.execute(
            "UPDATE statements SET rows_imported = ? WHERE id = ?;",
            (imported_count, statement_id)
        )

    return api_response(data={
        "statement_id": statement_id,
        "rows_imported": imported_count,
        "rows_skipped": skipped_count,
        "message": f"Successfully imported {imported_count} transactions ({skipped_count} skipped)."
    }, status_code=201)
