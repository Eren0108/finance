import os
from pathlib import Path

# Base Paths
BASE_DIR = Path(__file__).resolve().parent.parent
BACKEND_DIR = BASE_DIR / "backend"
FRONTEND_DIR = BASE_DIR / "frontend"
DATA_DIR = BASE_DIR / "data"
UPLOAD_DIR = BASE_DIR / "uploads"
EXPORT_DIR = BASE_DIR / "exports"

# Ensure runtime directories exist
DATA_DIR.mkdir(parents=True, exist_ok=True)
UPLOAD_DIR.mkdir(parents=True, exist_ok=True)
EXPORT_DIR.mkdir(parents=True, exist_ok=True)

# Database
DB_PATH = DATA_DIR / "finance.db"

# Upload Constraints
MAX_CONTENT_LENGTH = 5 * 1024 * 1024  # 5 MB
ALLOWED_EXTENSIONS = {"csv", "xlsx", "xls"}

# Default Categories
DEFAULT_CATEGORIES = [
    {"name": "Food", "type": "expense", "color": "#EF4444"},
    {"name": "Rent", "type": "expense", "color": "#F59E0B"},
    {"name": "Travel", "type": "expense", "color": "#3B82F6"},
    {"name": "Shopping", "type": "expense", "color": "#EC4899"},
    {"name": "Bills", "type": "expense", "color": "#8B5CF6"},
    {"name": "Health", "type": "expense", "color": "#10B981"},
    {"name": "Entertainment", "type": "expense", "color": "#6366F1"},
    {"name": "Salary", "type": "income", "color": "#16A34A"},
    {"name": "Other", "type": "expense", "color": "#64748B"},
]
