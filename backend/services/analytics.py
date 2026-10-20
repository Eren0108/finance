from typing import Dict, Any, List
from backend.database import get_db
from backend.utils.helpers import get_month_date_range, get_past_n_months, format_month_label


def get_monthly_summary(month_str: str) -> Dict[str, Any]:
    """
    Computes income, expense, savings, savings rate, and category breakdown for a given month.
    """
    start_date, end_date = get_month_date_range(month_str)

    with get_db() as conn:
        cursor = conn.cursor()

        # Overall income and expense
        cursor.execute("""
            SELECT 
                type, 
                COALESCE(SUM(amount), 0.0) as total,
                COUNT(id) as count
            FROM transactions
            WHERE date >= ? AND date <= ?
            GROUP BY type;
        """, (start_date, end_date))

        totals = {"income": 0.0, "expense": 0.0, "tx_count": 0}
        for row in cursor.fetchall():
            totals[row["type"]] = round(float(row["total"]), 2)
            totals["tx_count"] += int(row["count"])

        income = totals["income"]
        expense = totals["expense"]
        savings = round(income - expense, 2)
        savings_rate = round((savings / income * 100), 1) if income > 0 else 0.0

        # Expense by category
        cursor.execute("""
            SELECT 
                c.id as category_id,
                c.name as category_name,
                c.color as category_color,
                COALESCE(SUM(t.amount), 0.0) as spent,
                COUNT(t.id) as count,
                COALESCE(b.limit_amount, 0.0) as budget_limit
            FROM categories c
            LEFT JOIN transactions t 
                ON c.id = t.category_id AND t.date >= ? AND t.date <= ? AND t.type = 'expense'
            LEFT JOIN budgets b 
                ON c.id = b.category_id AND b.month = ?
            WHERE c.type = 'expense'
            GROUP BY c.id, c.name, c.color
            HAVING spent > 0 OR budget_limit > 0
            ORDER BY spent DESC;
        """, (start_date, end_date, month_str))

        category_breakdown = []
        for row in cursor.fetchall():
            spent = round(float(row["spent"]), 2)
            limit = round(float(row["budget_limit"]), 2)
            pct_of_total = round((spent / expense * 100), 1) if expense > 0 else 0.0
            budget_pct = round((spent / limit * 100), 1) if limit > 0 else 0.0

            status = "normal"
            if limit > 0:
                if budget_pct > 100:
                    status = "danger"
                elif budget_pct >= 70:
                    status = "warning"

            category_breakdown.append({
                "category_id": row["category_id"],
                "category_name": row["category_name"],
                "category_color": row["category_color"],
                "spent": spent,
                "count": row["count"],
                "percentage_of_total": pct_of_total,
                "budget_limit": limit,
                "budget_percentage": budget_pct,
                "status": status
            })

        # Recent transactions in this month or overall
        cursor.execute("""
            SELECT 
                t.id, t.date, t.description, t.amount, t.type, t.source,
                c.id as category_id, c.name as category_name, c.color as category_color
            FROM transactions t
            JOIN categories c ON t.category_id = c.id
            WHERE t.date >= ? AND t.date <= ?
            ORDER BY t.date DESC, t.id DESC
            LIMIT 5;
        """, (start_date, end_date))

        recent_txs = [
            {
                "id": r["id"],
                "date": r["date"],
                "description": r["description"],
                "amount": round(float(r["amount"]), 2),
                "type": r["type"],
                "source": r["source"],
                "category_id": r["category_id"],
                "category_name": r["category_name"],
                "category_color": r["category_color"],
            }
            for r in cursor.fetchall()
        ]

        # Budget warnings (categories that are at >= 70% of budget)
        warnings = [cat for cat in category_breakdown if cat["budget_limit"] > 0 and cat["budget_percentage"] >= 70]

        return {
            "month": month_str,
            "month_label": format_month_label(month_str),
            "total_income": income,
            "total_expense": expense,
            "savings": savings,
            "savings_rate": savings_rate,
            "transaction_count": totals["tx_count"],
            "categories": category_breakdown,
            "recent_transactions": recent_txs,
            "budget_warnings": warnings
        }


def get_monthly_trend(months_count: int = 6, end_month: str = None) -> List[Dict[str, Any]]:
    """
    Returns monthly income, expense, and savings for the past n months.
    """
    months = get_past_n_months(n=months_count, base_date=end_month)

    with get_db() as conn:
        cursor = conn.cursor()
        trend_data = []

        for m in months:
            start_date, end_date = get_month_date_range(m)
            cursor.execute("""
                SELECT 
                    type, 
                    COALESCE(SUM(amount), 0.0) as total
                FROM transactions
                WHERE date >= ? AND date <= ?
                GROUP BY type;
            """, (start_date, end_date))

            m_totals = {"income": 0.0, "expense": 0.0}
            for row in cursor.fetchall():
                m_totals[row["type"]] = round(float(row["total"]), 2)

            inc = m_totals["income"]
            exp = m_totals["expense"]
            trend_data.append({
                "month": m,
                "label": format_month_label(m),
                "income": inc,
                "expense": exp,
                "savings": round(inc - exp, 2)
            })

        return trend_data


def get_budget_status(month_str: str) -> Dict[str, Any]:
    """
    Returns full budget status for all expense categories for a given month.
    """
    start_date, end_date = get_month_date_range(month_str)

    with get_db() as conn:
        cursor = conn.cursor()

        cursor.execute("""
            SELECT 
                c.id as category_id,
                c.name as category_name,
                c.color as category_color,
                COALESCE(b.id, NULL) as budget_id,
                COALESCE(b.limit_amount, 0.0) as limit_amount,
                COALESCE((
                    SELECT SUM(t.amount) 
                    FROM transactions t 
                    WHERE t.category_id = c.id 
                      AND t.date >= ? AND t.date <= ? 
                      AND t.type = 'expense'
                ), 0.0) as spent_amount
            FROM categories c
            LEFT JOIN budgets b ON c.id = b.category_id AND b.month = ?
            WHERE c.type = 'expense'
            ORDER BY c.name ASC;
        """, (start_date, end_date, month_str))

        rows = cursor.fetchall()
        budget_items = []
        total_budget = 0.0
        total_spent = 0.0

        for r in rows:
            limit = round(float(r["limit_amount"]), 2)
            spent = round(float(r["spent_amount"]), 2)
            total_budget += limit
            total_spent += spent

            pct = round((spent / limit * 100), 1) if limit > 0 else 0.0
            if limit == 0:
                status = "unbudgeted"
            elif pct > 100:
                status = "danger"
            elif pct >= 70:
                status = "warning"
            else:
                status = "normal"

            budget_items.append({
                "category_id": r["category_id"],
                "category_name": r["category_name"],
                "category_color": r["category_color"],
                "budget_id": r["budget_id"],
                "limit_amount": limit,
                "spent_amount": spent,
                "remaining_amount": round(max(0.0, limit - spent), 2),
                "percentage": pct,
                "status": status
            })

        overall_pct = round((total_spent / total_budget * 100), 1) if total_budget > 0 else 0.0

        return {
            "month": month_str,
            "month_label": format_month_label(month_str),
            "total_budget": round(total_budget, 2),
            "total_spent": round(total_spent, 2),
            "total_remaining": round(max(0.0, total_budget - total_spent), 2),
            "overall_percentage": overall_pct,
            "budgets": budget_items
        }
