import sys
from pathlib import Path

ROOT_DIR = Path(__file__).resolve().parent.parent.parent
if str(ROOT_DIR) not in sys.path:
    sys.path.insert(0, str(ROOT_DIR))

from backend.database import get_db


def clear_all_data():
    """Clears all transactions, budgets, and statements, keeping categories intact."""
    with get_db() as conn:
        cursor = conn.cursor()
        cursor.execute("DELETE FROM transactions;")
        cursor.execute("DELETE FROM budgets;")
        cursor.execute("DELETE FROM statements;")
        print("All transactions, budgets, and statements have been cleared.")


if __name__ == "__main__":
    clear_all_data()
