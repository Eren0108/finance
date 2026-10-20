import pytest
from datetime import date
from backend.database import get_db, init_db
from backend.services.analytics import get_monthly_summary, get_budget_status, get_monthly_trend
from backend.utils.helpers import get_month_date_range


@pytest.fixture(autouse=True)
def setup_database():
    init_db()
    # Clean up test transactions and budgets
    with get_db() as conn:
        cursor = conn.cursor()
        cursor.execute("DELETE FROM transactions;")
        cursor.execute("DELETE FROM budgets;")
        cursor.execute("DELETE FROM statements;")

        # Insert known test categories
        cursor.execute("SELECT id FROM categories WHERE name = 'Salary';")
        salary_cat = cursor.fetchone()
        cursor.execute("SELECT id FROM categories WHERE name = 'Food';")
        food_cat = cursor.fetchone()
        cursor.execute("SELECT id FROM categories WHERE name = 'Rent';")
        rent_cat = cursor.fetchone()

        salary_id = salary_cat["id"] if salary_cat else 1
        food_id = food_cat["id"] if food_cat else 2
        rent_id = rent_cat["id"] if rent_cat else 3

        # Insert test transactions for month 2026-10
        cursor.execute("""
            INSERT INTO transactions (date, description, amount, type, category_id, source)
            VALUES 
                ('2026-10-01', 'Monthly Salary', 80000.0, 'income', ?, 'manual'),
                ('2026-10-02', 'House Rent', 25000.0, 'expense', ?, 'manual'),
                ('2026-10-05', 'Dinner Restaurant', 5000.0, 'expense', ?, 'manual');
        """, (salary_id, rent_id, food_id))

        # Insert test budget
        cursor.execute("""
            INSERT INTO budgets (category_id, month, limit_amount)
            VALUES (?, '2026-10', 6000.0);
        """, (food_id,))

    yield


def test_monthly_summary_calculation():
    summary = get_monthly_summary("2026-10")

    assert summary["month"] == "2026-10"
    assert summary["total_income"] == 80000.0
    assert summary["total_expense"] == 30000.0
    assert summary["savings"] == 50000.0
    # savings_rate = 50000 / 80000 * 100 = 62.5%
    assert summary["savings_rate"] == 62.5
    assert summary["transaction_count"] == 3


def test_budget_status_calculation():
    budget_data = get_budget_status("2026-10")

    assert budget_data["total_budget"] == 6000.0
    assert budget_data["total_spent"] == 30000.0

    # Food budget should have limit 6000 and spent 5000 (83.3% -> warning)
    food_budget = next((b for b in budget_data["budgets"] if b["category_name"] == "Food"), None)
    assert food_budget is not None
    assert food_budget["limit_amount"] == 6000.0
    assert food_budget["spent_amount"] == 5000.0
    assert food_budget["remaining_amount"] == 1000.0
    assert food_budget["status"] == "warning"


def test_monthly_trend_length():
    trend = get_monthly_trend(months_count=6, end_month="2026-10")
    assert len(trend) == 6
    assert trend[-1]["month"] == "2026-10"
    assert trend[-1]["income"] == 80000.0
    assert trend[-1]["expense"] == 30000.0
