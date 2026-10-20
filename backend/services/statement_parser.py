import re
import pandas as pd
from typing import List, Dict, Any
from backend.services.categorizer import guess_category
from backend.utils.validators import validate_date


DATE_COL_CANDIDATES = [
    "date", "txn date", "transaction date", "value date", "posting date",
    "tran date", "trans date", "txndate"
]

DESC_COL_CANDIDATES = [
    "description", "particulars", "narration", "transaction remarks",
    "details", "remarks", "memo", "note", "transaction details", "payee"
]

DEBIT_COL_CANDIDATES = [
    "debit", "dr", "withdrawal", "withdrawal amount", "debit amount",
    "withdrawal (dr)", "dr amount", "expense"
]

CREDIT_COL_CANDIDATES = [
    "credit", "cr", "deposit", "deposit amount", "credit amount",
    "deposit (cr)", "cr amount", "income"
]

AMOUNT_COL_CANDIDATES = [
    "amount", "txn amount", "transaction amount", "net amount"
]

TYPE_COL_CANDIDATES = [
    "type", "cr/dr", "dr/cr", "transaction type", "txn type"
]


def clean_currency_value(val: Any) -> float:
    """Clean string currency representation into a float."""
    if pd.isna(val) or val is None:
        return 0.0
    if isinstance(val, (int, float)):
        return float(val)
    
    val_str = str(val).strip()
    if not val_str or val_str in ("-", "--", "NA", "N/A", "null"):
        return 0.0
    
    # Remove currency symbols (INR, ₹, $, Rs, etc.) and commas
    cleaned = re.sub(r"[^\d.-]", "", val_str.replace(",", ""))
    try:
        return float(cleaned)
    except (ValueError, TypeError):
        return 0.0


def find_matching_column(columns: List[str], candidates: List[str]) -> str | None:
    """Find column header matching any candidate name case-insensitively."""
    lower_cols = {col.strip().lower(): col for col in columns if isinstance(col, str)}
    for candidate in candidates:
        if candidate in lower_cols:
            return lower_cols[candidate]
        # Check partial match
        for col_lower, orig in lower_cols.items():
            if candidate == col_lower or candidate in col_lower:
                return orig
    return None


def parse_statement_file(file_path: str, category_names: List[str] = None) -> List[Dict[str, Any]]:
    """
    Parses a CSV or Excel file and returns a list of normalized transaction dictionaries.
    """
    # Load DataFrame
    try:
        if file_path.lower().endswith(".csv"):
            try:
                df = pd.read_csv(file_path)
            except UnicodeDecodeError:
                df = pd.read_csv(file_path, encoding="latin1")
        elif file_path.lower().endswith((".xlsx", ".xls")):
            df = pd.read_excel(file_path)
        else:
            raise ValueError("Unsupported file format. Please upload a .csv, .xlsx, or .xls file.")
    except Exception as e:
        raise ValueError(f"Could not read the file: {str(e)}")

    if df.empty:
        raise ValueError("The uploaded statement file is empty.")

    # Drop fully empty rows and columns
    df = df.dropna(how="all")
    columns = list(df.columns)

    # Detect Date column
    date_col = find_matching_column(columns, DATE_COL_CANDIDATES)
    if not date_col:
        raise ValueError("Could not find a Date column (e.g. 'Date', 'Txn Date', 'Value Date').")

    # Detect Description column
    desc_col = find_matching_column(columns, DESC_COL_CANDIDATES)
    if not desc_col:
        raise ValueError("Could not find a Description column (e.g. 'Description', 'Particulars', 'Narration').")

    # Detect amount columns
    debit_col = find_matching_column(columns, DEBIT_COL_CANDIDATES)
    credit_col = find_matching_column(columns, CREDIT_COL_CANDIDATES)
    amount_col = find_matching_column(columns, AMOUNT_COL_CANDIDATES)
    type_col = find_matching_column(columns, TYPE_COL_CANDIDATES)

    if not ((debit_col or credit_col) or amount_col):
        raise ValueError("Could not find amount columns ('Debit'/'Credit' or 'Amount').")

    parsed_rows: List[Dict[str, Any]] = []

    for index, row in df.iterrows():
        raw_date = row.get(date_col)
        raw_desc = row.get(desc_col)

        if pd.isna(raw_date) or pd.isna(raw_desc):
            continue

        desc = str(raw_desc).strip()
        if not desc or desc.lower() in ("opening balance", "closing balance", "total"):
            continue

        # Parse Date
        try:
            if isinstance(raw_date, pd.Timestamp):
                date_val = raw_date.strftime("%Y-%m-%d")
            else:
                date_str_raw = str(raw_date).strip()
                if re.match(r"^\d{4}-\d{2}-\d{2}", date_str_raw):
                    parsed_dt = pd.to_datetime(date_str_raw, format="%Y-%m-%d")
                else:
                    parsed_dt = pd.to_datetime(date_str_raw, dayfirst=True)
                date_val = parsed_dt.strftime("%Y-%m-%d")
        except Exception:
            try:
                date_val = validate_date(str(raw_date))
            except Exception:
                continue  # Skip unparseable date row

        # Determine Amount and Type
        amount = 0.0
        txn_type = "expense"

        if debit_col or credit_col:
            debit_val = clean_currency_value(row.get(debit_col)) if debit_col else 0.0
            credit_val = clean_currency_value(row.get(credit_col)) if credit_col else 0.0

            if credit_val > 0 and debit_val == 0:
                amount = round(credit_val, 2)
                txn_type = "income"
            elif debit_val > 0:
                amount = round(debit_val, 2)
                txn_type = "expense"
            elif amount_col:
                # Fallback to amount column if both debit & credit are zero or missing
                raw_amt = clean_currency_value(row.get(amount_col))
                if raw_amt != 0:
                    amount = round(abs(raw_amt), 2)
                    txn_type = "income" if raw_amt > 0 else "expense"
        elif amount_col:
            raw_amt = clean_currency_value(row.get(amount_col))
            if raw_amt == 0:
                continue

            if type_col:
                raw_type_str = str(row.get(type_col)).strip().lower()
                if "cr" in raw_type_str or "income" in raw_type_str or "dep" in raw_type_str:
                    txn_type = "income"
                else:
                    txn_type = "expense"
                amount = round(abs(raw_amt), 2)
            else:
                if raw_amt < 0:
                    txn_type = "expense"
                    amount = round(abs(raw_amt), 2)
                else:
                    txn_type = "income"
                    amount = round(raw_amt, 2)

        if amount <= 0:
            continue

        # Suggested category
        suggested_category = guess_category(desc, category_names=category_names)

        parsed_rows.append({
            "date": date_val,
            "description": desc,
            "amount": amount,
            "type": txn_type,
            "suggested_category": suggested_category
        })

    if not parsed_rows:
        raise ValueError("No valid transaction rows found in the uploaded statement.")

    return parsed_rows
