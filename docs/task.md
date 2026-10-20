# Tasks: Personal Finance Tracker

Tick `[x]` when a task is finished. Work strictly top to bottom, one step at a time.

---

## Phase 0: Planning

- [x] Decide project idea and tech stack
- [x] Create `architecture.md`, `design.md`, `memory.md`, `rules.md`, `task.md`, `PRD.md`

---

## Phase 1: Setup

### Step 1: Development environment
- [x] Install VS Code
- [x] Install Python (tick "Add Python to PATH" on Windows)
- [x] Run `python --version`, `py --version`, `code --version`
- [x] Install VS Code extensions: Python, Live Server

### Step 2: Project folder
- [x] Create `finance-tracker/` and open it in VS Code
- [x] Create folders: `backend`, `frontend`, `docs`, `data`, `uploads`, `exports`, `tests`
- [x] Move the six `.md` files into `docs/`

### Step 3: Git and virtual environment
- [x] Install Git and run `git init`
- [x] Create `.gitignore`
- [x] Create virtual environment `python -m venv venv` and activate it
- [x] Install packages: `flask`, `pandas`, `openpyxl`, `flask-cors`
- [x] Create `requirements.txt`
- [x] First commit

### Step 4: Flask hello world
- [x] Create `backend/app.py` with one route
- [x] Run the server and open it in the browser
- [x] Add a `/api/health` endpoint returning JSON

---

## Phase 2: Frontend Foundation

### Step 5: Base layout
- [x] Create `index.html` with sidebar, top bar, and content area
- [x] Create `style.css` with CSS variables from `design.md`
- [x] Make layout responsive
- [x] Create empty pages: transactions, upload, budgets, reports
- [x] Create `api.js` and test one fetch call to `/api/health`

---

## Phase 3: Database and Transactions

### Step 6: Database
- [x] Create `database.py` and `models.py`
- [x] Create tables: categories, transactions, budgets, statements
- [x] Insert default categories (Food, Rent, Travel, Shopping, Bills, Salary, Other)

### Step 7: Transactions CRUD
- [x] `GET /api/transactions` with filters
- [x] `POST /api/transactions` with validation
- [x] `PUT /api/transactions/<id>`
- [x] `DELETE /api/transactions/<id>`
- [x] Transactions page: table, add/edit modal, delete confirm
- [x] Filters and pagination

---

## Phase 4: Dashboard

### Step 8: Summary and charts
- [x] `GET /api/reports/summary`
- [x] `GET /api/reports/trend`
- [x] Stat cards (income, expense, savings, savings rate)
- [x] Doughnut chart: expense by category
- [x] Bar chart: income vs expense, last 6 months
- [x] Recent transactions list
- [x] Empty states and loading spinners

---

## Phase 5: Statement Import

### Step 9: Upload and parse
- [x] Upload endpoint with file type and size checks
- [x] `statement_parser.py`: read CSV and Excel with pandas
- [x] Normalize columns (date, description, debit, credit)
- [x] `categorizer.py`: keyword based category guess
- [x] Preview table with editable categories
- [x] Duplicate detection
- [x] Confirm endpoint to save rows
- [x] Test with dummy statements from at least 2 formats

---

## Phase 6: Budgets and Export

### Step 10: Budgets
- [x] Budget endpoints (get, set)
- [x] Budgets page with progress bars and color rules
- [x] Dashboard budget warnings

### Step 11: Excel export
- [x] `excel_exporter.py` with Summary and Transactions sheets
- [x] `GET /api/reports/export`
- [x] Download button on Reports page

---

## Phase 7: Quality and Finish

### Step 12: Testing and polish
- [x] Manual test of every page and edge case
- [x] Add `pytest` tests for parser and analytics
- [x] Fix UI issues on mobile
- [x] Add toasts and error messages everywhere
- [x] Write `README.md` with setup and run instructions
- [x] Final commit and push to GitHub

---

## Backlog (After MVP)

- [ ] User login and multiple users
- [ ] PDF statement parsing
- [ ] Recurring transactions
- [ ] Dark mode
- [ ] Deployment (Render or Railway)
- [ ] Savings goals
