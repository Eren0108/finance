# Personal Finance Tracker

A full-stack, responsive Personal Finance Tracker built with Python (Flask, pandas, openpyxl, SQLite) and Vanilla HTML/CSS/JavaScript with Chart.js.

Designed for individuals, freelancers, and students in India to easily record expenses, import bank statements, track category budgets, and export financial reports to Excel.

---

## 🌟 Key Features

1. **Intuitive Financial Dashboard (`/`)**
   - 4 Live KPI stat cards: Total Income, Total Expenses, Net Savings, and Savings Rate (%).
   - Currency display formatted in INR (`₹`) with tabular numbers.
   - Expense by Category Doughnut Chart (Chart.js).
   - 6-Month Income vs Expenses Comparison Bar Chart.
   - Budget progress bars with real-time warning indicators.
   - Recent transactions table and quick "Add Transaction" modal.

2. **Transaction Management (`/transactions.html`)**
   - Full CRUD operations: Create, Read, Update, Delete transactions.
   - Dynamic search by description, filter by category, type (income/expense), and date range.
   - Pagination controls (20 rows per page).
   - Delete confirmation dialog.

3. **Smart Bank Statement Import (`/upload.html`)**
   - 3-Step guided stepper workflow.
   - Supports `.csv`, `.xlsx`, and `.xls` files up to 5 MB.
   - Automatic column mapping (Date, Description, Debit, Credit).
   - Keyword-based auto-categorization (e.g. Swiggy/Zomato -> Food, Uber/Ola -> Travel, Bescom/Airtel -> Bills).
   - Interactive preview table with inline category overrides and duplicate detection.

4. **Monthly Budgets (`/budgets.html`)**
   - Set monthly spending limits per category.
   - Visual progress bars with 3-tier color thresholds:
     - 🟢 **Under 70%**: On Track
     - 🟡 **70% to 100%**: Near Limit Warning
     - 🔴 **Over 100%**: Over-Budget Alert
   - Real-time overall budget utilization calculation.

5. **Reports & Excel Export (`/reports.html`)**
   - Comprehensive monthly financial summary.
   - 6-Month Net Savings trend line chart.
   - Category-wise spending breakdown table.
   - **One-click Excel Report Export (`.xlsx`)** generated using `openpyxl`:
     - **"Summary" sheet**: Formatted metrics, borders, and category breakdown.
     - **"Transactions" sheet**: Complete transaction register with currency formatting.

---

## 🏗️ Architecture & Tech Stack

```
finance-tracker/
|-- backend/
|   |-- app.py                  # Flask entry point & static server
|   |-- config.py               # Paths, limits, and default categories
|   |-- database.py             # SQLite connection & schema initialization
|   |-- models.py               # Data models
|   |-- routes/                 # REST API blueprints
|   |   |-- transactions.py
|   |   |-- categories.py
|   |   |-- budgets.py
|   |   |-- statements.py
|   |   |-- reports.py
|   |-- services/               # Core business logic
|   |   |-- statement_parser.py # CSV / Excel statement reader
|   |   |-- categorizer.py      # Keyword auto-categorization
|   |   |-- analytics.py        # Summaries, trends, budget calculations
|   |   |-- excel_exporter.py   # openpyxl multi-sheet workbook generator
|   |   |-- seed_demo_data.py   # Realistic test data generator
|   |-- utils/
|       |-- validators.py       # Input sanitation & date/amount validation
|       |-- helpers.py          # Response formatting & date math
|-- frontend/
|   |-- index.html              # Dashboard
|   |-- transactions.html       # Transactions CRUD & filters
|   |-- upload.html             # 3-step statement upload
|   |-- budgets.html            # Category budget limits
|   |-- reports.html            # Reports & Excel download
|   |-- css/
|   |   |-- style.css           # Modern design system & responsive layout
|   |-- js/
|       |-- api.js              # Centralized API fetch wrapper & toasts
|       |-- charts.js           # Chart.js renderers
|       |-- dashboard.js        # Dashboard state & charts
|       |-- transactions.js     # Transactions management
|       |-- upload.js           # Upload stepper & preview
|       |-- budgets.js          # Budgets tracking
|       |-- reports.js          # Reports & export
|-- data/                       # finance.db (SQLite database)
|-- uploads/                    # Uploaded statement files
|-- exports/                    # Generated .xlsx reports
|-- sample_data/                # Sample CSV & XLSX statements for testing
|-- tests/                      # Pytest automated test suite
|-- requirements.txt            # Python dependencies
|-- .gitignore
```

---

## 🚀 Getting Started

### 1. Prerequisites
- Python 3.11+
- Git

### 2. Installation

Clone or open the repository folder:
```bash
git clone <repo-url>
cd finance-tracker
```

Create and activate a virtual environment (optional but recommended):
```bash
python -m venv venv
# On Windows:
venv\Scripts\activate
# On macOS / Linux:
source venv/bin/activate
```

Install dependencies:
```bash
pip install -r requirements.txt
```

### 3. Initialize & Seed Demo Data

Initialize the SQLite database and seed realistic demo records:
```bash
python backend/services/seed_demo_data.py
```

### 4. Run the Application

Start the Flask server:
```bash
python backend/app.py
```

Open your browser and navigate to:
```
http://localhost:5000
```

---

## 🧪 Running Automated Tests

Run the test suite using `pytest`:
```bash
pytest tests
```

---

## 📄 License
MIT License. Built for personal finance management.
