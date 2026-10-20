# Memory: Project Context and Progress Log

> This file is the project's "memory". Update it after every completed step so any assistant or developer can resume instantly.

## 1. Project Snapshot

- **Project name:** Personal Finance Tracker Website
- **Goal:** Track income and expenses, import bank statements (CSV / Excel), view charts, export Excel reports.
- **Builder level:** Complete beginner friendly, production-quality implementation
- **Working style:** End-to-end built application adhering to all PRD, architecture, and design specifications.
- **Tech Stack:** Python 3.11+ / Flask, SQLite, pandas, openpyxl, Vanilla HTML/CSS/JS, Chart.js.

## 2. Tech Stack & Environment

| Item | Value |
|---|---|
| OS | Windows |
| Python | 3.13.3 |
| Git | 2.50.1 |
| Database | SQLite (`data/finance.db`) |
| Backend | Flask 3.1.1, Flask-CORS 6.0.5 |
| Data Processing | pandas 2.2.3, openpyxl 3.1.5 |
| Testing | pytest 9.1.1 (100% pass) |
| Frontend | Vanilla HTML5, CSS3 Variables, ES6 Modules, Chart.js |

## 3. Progress Tracker

| Step | Description | Status |
|---|---|---|
| 1 | Development environment setup (VS Code, Python, Git) | Done |
| 2 | Project folder and modular structure (`backend/`, `frontend/`, `docs/`, `data/`, etc.) | Done |
| 3 | Git repository init, `.gitignore`, and `requirements.txt` | Done |
| 4 | Flask application, blueprints, and `/api/health` | Done |
| 5 | Frontend layout, design system (`style.css`), and `api.js` | Done |
| 6 | Database schema (`database.py`, `models.py`) and default categories | Done |
| 7 | Transactions CRUD API, pagination, filtering, and modal UI | Done |
| 8 | Dashboard stat cards, Chart.js graphs, and budget warnings | Done |
| 9 | Statement import (`statement_parser.py`, `categorizer.py`, preview & duplicate check) | Done |
| 10 | Budgets API and management page with 3-tier color progress bars | Done |
| 11 | Excel export (`excel_exporter.py`) with Summary and Transactions sheets | Done |
| 12 | Automated pytest test suite, seed demo data, and `README.md` | Done |

## 4. Completed Milestones

- **M1: Foundation**: Flask server, routing, error handlers, and base CSS design tokens completed.
- **M2: Core**: SQLite schema created with foreign keys and indices; transactions CRUD with search, category filters, and pagination; dashboard KPI cards and Chart.js visualizations.
- **M3: Import**: Bank statement import working with CSV and Excel (`.xlsx`), column header detection, auto-categorization keywords, duplicate detection, and batch import.
- **M4: Planning**: Monthly category budget management with real-time utilization progress bars; multi-sheet Excel workbook exporter.
- **M5: Release**: Pytest suite with 7 passed tests, comprehensive `README.md`, sample statement generator, and seeded demo data.

## 5. Decisions Log

| Date | Decision | Reason |
|---|---|---|
| 20-10-2026 | Unified static serving | Configured Flask to serve `frontend/` static assets directly so users can run the entire app with a single command `python backend/app.py`. |
| 20-10-2026 | Auto-path resolution | Added dynamic `sys.path` resolution so scripts work regardless of whether executed as a module or standalone script. |
| 20-10-2026 | openpyxl styling | Styled Excel export with Segoe UI fonts, currency formatting (`₹#,##0.00`), zebra striping, and auto-fit column widths. |
| 20-10-2026 | Zero warning date parser | Added regex check for `YYYY-MM-DD` strings before pandas parsing to silence dayfirst UserWarnings. |
