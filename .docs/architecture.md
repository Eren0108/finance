# Architecture: Personal Finance Tracker

## 1. Overview

A web app where a user records income and expenses, uploads bank statements (CSV / Excel), sees charts and summaries, and exports reports to Excel.

It is a classic **client-server** app:

```
 Browser (HTML + CSS + JavaScript)
        |  HTTP requests (fetch, JSON)
        v
 Flask API (Python)  -->  Services (business logic, pandas, openpyxl)
        |
        v
 SQLite database  +  uploads/ and exports/ folders
```

## 2. Tech Stack

| Layer | Technology | Why |
|---|---|---|
| Frontend structure | HTML5 | Pages, forms, tables |
| Frontend style | CSS3 (plain, later optional Bootstrap) | Layout and look |
| Frontend logic | Vanilla JavaScript (ES6) | Beginner friendly, no build tools |
| Charts | Chart.js | Simple, good docs |
| Backend | Python 3.11+ with Flask | Small, easy to learn |
| Data processing | pandas, openpyxl | Read statements, build Excel files |
| Database | SQLite (via SQLAlchemy or sqlite3) | Zero setup, single file |
| Editor | VS Code | Free, great Python and web support |
| Version control | Git + GitHub | History and backup |

## 3. Folder Structure

```
finance-tracker/
|
|-- docs/                    # architecture.md, design.md, memory.md, rules.md, task.md, PRD.md
|
|-- backend/
|   |-- app.py               # Flask entry point
|   |-- config.py            # Settings (paths, limits)
|   |-- database.py          # DB connection and table creation
|   |-- models.py            # Table definitions
|   |-- routes/
|   |   |-- transactions.py  # CRUD endpoints
|   |   |-- categories.py
|   |   |-- budgets.py
|   |   |-- statements.py    # Upload and import
|   |   |-- reports.py       # Summaries and Excel export
|   |-- services/
|   |   |-- statement_parser.py   # Read CSV/Excel into clean rows
|   |   |-- categorizer.py        # Auto-assign categories
|   |   |-- analytics.py          # Totals, trends, budget checks
|   |   |-- excel_exporter.py     # Create .xlsx reports
|   |-- utils/
|       |-- validators.py
|       |-- helpers.py
|
|-- frontend/
|   |-- index.html           # Dashboard
|   |-- transactions.html
|   |-- upload.html
|   |-- budgets.html
|   |-- reports.html
|   |-- css/
|   |   |-- style.css
|   |-- js/
|       |-- api.js           # All fetch() calls live here
|       |-- dashboard.js
|       |-- transactions.js
|       |-- upload.js
|       |-- charts.js
|
|-- data/                    # finance.db (SQLite file, git-ignored)
|-- uploads/                 # Uploaded statements (git-ignored)
|-- exports/                 # Generated Excel files (git-ignored)
|-- tests/
|-- requirements.txt
|-- .gitignore
|-- README.md
```

## 4. Database Schema

### categories
| Column | Type | Notes |
|---|---|---|
| id | INTEGER PK | |
| name | TEXT UNIQUE | e.g. Food, Rent, Salary |
| type | TEXT | `income` or `expense` |
| color | TEXT | Hex color for charts |

### transactions
| Column | Type | Notes |
|---|---|---|
| id | INTEGER PK | |
| date | DATE | Transaction date |
| description | TEXT | Merchant or note |
| amount | REAL | Always positive |
| type | TEXT | `income` or `expense` |
| category_id | INTEGER FK | -> categories.id |
| source | TEXT | `manual` or `statement` |
| statement_id | INTEGER FK | Nullable, -> statements.id |
| created_at | DATETIME | |

### budgets
| Column | Type | Notes |
|---|---|---|
| id | INTEGER PK | |
| category_id | INTEGER FK | |
| month | TEXT | Format `YYYY-MM` |
| limit_amount | REAL | |

### statements
| Column | Type | Notes |
|---|---|---|
| id | INTEGER PK | |
| filename | TEXT | |
| uploaded_at | DATETIME | |
| rows_imported | INTEGER | |

## 5. API Endpoints (REST, JSON)

| Method | Endpoint | Purpose |
|---|---|---|
| GET | `/api/transactions` | List, with filters (date range, category, type) |
| POST | `/api/transactions` | Add a transaction |
| PUT | `/api/transactions/<id>` | Edit |
| DELETE | `/api/transactions/<id>` | Delete |
| GET | `/api/categories` | List categories |
| POST | `/api/categories` | Add category |
| GET | `/api/budgets?month=YYYY-MM` | Budgets with spent amount |
| POST | `/api/budgets` | Set or update a budget |
| POST | `/api/statements/upload` | Upload file, return a preview |
| POST | `/api/statements/confirm` | Save previewed rows to DB |
| GET | `/api/reports/summary?month=YYYY-MM` | Totals, savings, category split |
| GET | `/api/reports/trend` | Monthly income vs expense |
| GET | `/api/reports/export?month=YYYY-MM` | Download Excel report |

Standard response shape:

```json
{ "success": true, "data": { }, "error": null }
```

## 6. Key Data Flows

### Add a transaction manually
Form (JS) -> `POST /api/transactions` -> validators -> DB insert -> JSON response -> table refreshes.

### Upload a bank statement
1. User picks a CSV/Excel file on `upload.html`.
2. `POST /api/statements/upload` saves the file to `uploads/`.
3. `statement_parser` reads it with pandas, normalizes columns (date, description, debit, credit).
4. `categorizer` guesses categories from keywords.
5. Preview rows are returned; the user fixes categories.
6. `POST /api/statements/confirm` inserts rows, skipping duplicates (same date + description + amount).

### Export to Excel
`GET /api/reports/export` -> `analytics` collects data -> `excel_exporter` builds .xlsx with openpyxl (Summary sheet, Transactions sheet) -> file sent as download.

## 7. Security and Quality Notes

- Validate every input on the backend, never trust the frontend.
- Allow only `.csv`, `.xlsx`, `.xls` uploads, with a size limit (5 MB).
- Rename uploaded files safely (`secure_filename`).
- Use parameterized queries or an ORM, never string-built SQL.
- Keep secrets in a `.env` file, never in Git.
- Financial data is private: the app runs locally for the MVP.

## 8. Future Extensions

- User login and multi-user support
- PDF statement parsing
- Recurring transactions and reminders
- Deployment (Render, Railway) with PostgreSQL
- Mobile-friendly PWA
