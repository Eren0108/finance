import sys
from pathlib import Path
from datetime import date
from dateutil.relativedelta import relativedelta

ROOT_DIR = Path(__file__).resolve().parent.parent.parent
if str(ROOT_DIR) not in sys.path:
    sys.path.insert(0, str(ROOT_DIR))

from backend.database import get_db, init_db


def seed_demo_data():
    """Populates realistic transactions and budgets across recent months for a live demo."""
    init_db()

    today = date.today()
    curr_month = today.strftime("%Y-%m")
    prev_month_1 = (today - relativedelta(months=1)).strftime("%Y-%m")
    prev_month_2 = (today - relativedelta(months=2)).strftime("%Y-%m")
    prev_month_3 = (today - relativedelta(months=3)).strftime("%Y-%m")

    with get_db() as conn:
        cursor = conn.cursor()

        # Check existing count
        cursor.execute("SELECT COUNT(*) as count FROM transactions;")
        if cursor.fetchone()["count"] > 10:
            print("Database already has demo data.")
            return

        # Fetch category map
        cursor.execute("SELECT id, name FROM categories;")
        cat_map = {r["name"]: r["id"] for r in cursor.fetchall()}

        # Sample transactions across months
        demo_txs = [
            # Current Month
            (f"{curr_month}-01", "Monthly Tech Salary", 95000.0, "income", cat_map["Salary"], "manual"),
            (f"{curr_month}-02", "Apartment Rent", 25000.0, "expense", cat_map["Rent"], "manual"),
            (f"{curr_month}-03", "Swiggy Dinner Delivery", 620.0, "expense", cat_map["Food"], "manual"),
            (f"{curr_month}-05", "Bescom Electricity Bill", 1950.0, "expense", cat_map["Bills"], "manual"),
            (f"{curr_month}-06", "Airtel Fiber Broadband", 999.0, "expense", cat_map["Bills"], "manual"),
            (f"{curr_month}-08", "BigBasket Monthly Grocery", 4200.0, "expense", cat_map["Food"], "manual"),
            (f"{curr_month}-10", "Uber Commute to Client Office", 450.0, "expense", cat_map["Travel"], "manual"),
            (f"{curr_month}-12", "Amazon Gadget Purchase", 3499.0, "expense", cat_map["Shopping"], "manual"),
            (f"{curr_month}-14", "Apollo Pharmacy Essentials", 850.0, "expense", cat_map["Health"], "manual"),
            (f"{curr_month}-15", "Freelance Web Design Payout", 18000.0, "income", cat_map["Salary"], "manual"),
            (f"{curr_month}-17", "Zomato Weekend Lunch", 780.0, "expense", cat_map["Food"], "manual"),
            (f"{curr_month}-18", "Fuel Petrol Indian Oil", 1800.0, "expense", cat_map["Travel"], "manual"),
            (f"{curr_month}-19", "Netflix & Spotify Subscriptions", 848.0, "expense", cat_map["Entertainment"], "manual"),

            # Previous Month 1
            (f"{prev_month_1}-01", "Monthly Tech Salary", 95000.0, "income", cat_map["Salary"], "manual"),
            (f"{prev_month_1}-02", "Apartment Rent", 25000.0, "expense", cat_map["Rent"], "manual"),
            (f"{prev_month_1}-04", "Grocery & Supermarket", 6500.0, "expense", cat_map["Food"], "manual"),
            (f"{prev_month_1}-07", "Electricity & Water Bills", 2400.0, "expense", cat_map["Bills"], "manual"),
            (f"{prev_month_1}-11", "Flight Ticket to Mumbai", 5800.0, "expense", cat_map["Travel"], "manual"),
            (f"{prev_month_1}-16", "Zara Clothing Shopping", 4990.0, "expense", cat_map["Shopping"], "manual"),
            (f"{prev_month_1}-20", "Cinema IMAX Movie Tickets", 1200.0, "expense", cat_map["Entertainment"], "manual"),

            # Previous Month 2
            (f"{prev_month_2}-01", "Monthly Tech Salary", 95000.0, "income", cat_map["Salary"], "manual"),
            (f"{prev_month_2}-02", "Apartment Rent", 25000.0, "expense", cat_map["Rent"], "manual"),
            (f"{prev_month_2}-05", "Grocery Restock", 5200.0, "expense", cat_map["Food"], "manual"),
            (f"{prev_month_2}-09", "Mobile Postpaid Recharge", 799.0, "expense", cat_map["Bills"], "manual"),
            (f"{prev_month_2}-15", "Consulting Bonus", 25000.0, "income", cat_map["Salary"], "manual"),
            (f"{prev_month_2}-18", "Dental Clinic Checkup", 1800.0, "expense", cat_map["Health"], "manual"),

            # Previous Month 3
            (f"{prev_month_3}-01", "Monthly Tech Salary", 90000.0, "income", cat_map["Salary"], "manual"),
            (f"{prev_month_3}-02", "Apartment Rent", 25000.0, "expense", cat_map["Rent"], "manual"),
            (f"{prev_month_3}-06", "Food and Dining", 4800.0, "expense", cat_map["Food"], "manual"),
            (f"{prev_month_3}-12", "Shopping & Home Decor", 3800.0, "expense", cat_map["Shopping"], "manual"),
        ]

        for dt, desc, amt, t_type, cat_id, src in demo_txs:
            cursor.execute("""
                INSERT INTO transactions (date, description, amount, type, category_id, source)
                VALUES (?, ?, ?, ?, ?, ?);
            """, (dt, desc, amt, t_type, cat_id, src))

        # Sample Budgets for Current Month
        demo_budgets = [
            (cat_map["Food"], curr_month, 8000.0),
            (cat_map["Rent"], curr_month, 25000.0),
            (cat_map["Travel"], curr_month, 3500.0),
            (cat_map["Bills"], curr_month, 4000.0),
            (cat_map["Shopping"], curr_month, 5000.0),
            (cat_map["Entertainment"], curr_month, 2000.0),
            (cat_map["Health"], curr_month, 3000.0),
        ]

        for cat_id, m, limit in demo_budgets:
            cursor.execute("""
                INSERT INTO budgets (category_id, month, limit_amount)
                VALUES (?, ?, ?)
                ON CONFLICT(category_id, month) DO UPDATE SET limit_amount = excluded.limit_amount;
            """, (cat_id, m, limit))

        print(f"Successfully seeded {len(demo_txs)} transactions and {len(demo_budgets)} budgets!")


if __name__ == "__main__":
    seed_demo_data()
