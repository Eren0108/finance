import os
import sys
from pathlib import Path

ROOT_DIR = Path(__file__).resolve().parent.parent
if str(ROOT_DIR) not in sys.path:
    sys.path.insert(0, str(ROOT_DIR))

import sqlite3
from contextlib import contextmanager
from backend.config import DB_PATH, DEFAULT_CATEGORIES


def get_connection():
    """Create and return a configured SQLite connection."""
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys = ON;")
    return conn


@contextmanager
def get_db():
    """Context manager for SQLite database interactions."""
    conn = get_connection()
    try:
        yield conn
        conn.commit()
    except Exception:
        conn.rollback()
        raise
    finally:
        conn.close()


def init_db():
    """Initialize database tables and seed default categories."""
    with get_db() as conn:
        cursor = conn.cursor()

        # Categories table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS categories (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT UNIQUE NOT NULL,
                type TEXT NOT NULL CHECK(type IN ('income', 'expense')),
                color TEXT NOT NULL
            );
        """)

        # Statements table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS statements (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                filename TEXT NOT NULL,
                uploaded_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
                rows_imported INTEGER DEFAULT 0
            );
        """)

        # Transactions table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS transactions (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                date TEXT NOT NULL,
                description TEXT NOT NULL,
                amount REAL NOT NULL CHECK(amount >= 0),
                type TEXT NOT NULL CHECK(type IN ('income', 'expense')),
                category_id INTEGER NOT NULL REFERENCES categories(id),
                source TEXT NOT NULL DEFAULT 'manual',
                statement_id INTEGER REFERENCES statements(id),
                created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP
            );
        """)

        # Budgets table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS budgets (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                category_id INTEGER NOT NULL REFERENCES categories(id),
                month TEXT NOT NULL,
                limit_amount REAL NOT NULL CHECK(limit_amount >= 0),
                UNIQUE(category_id, month)
            );
        """)

        # Indices for performance
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_transactions_date ON transactions(date);")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_transactions_category ON transactions(category_id);")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_budgets_month ON budgets(month);")

        # Seed default categories if none exist
        cursor.execute("SELECT COUNT(*) as count FROM categories;")
        row = cursor.fetchone()
        if row["count"] == 0:
            for cat in DEFAULT_CATEGORIES:
                cursor.execute(
                    "INSERT INTO categories (name, type, color) VALUES (?, ?, ?);",
                    (cat["name"], cat["type"], cat["color"]),
                )


if __name__ == "__main__":
    init_db()
    print("Database initialized successfully at:", DB_PATH)
