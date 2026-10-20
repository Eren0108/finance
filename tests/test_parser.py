import pytest
import os
from pathlib import Path
from backend.services.statement_parser import parse_statement_file
from backend.services.categorizer import guess_category

BASE_DIR = Path(__file__).resolve().parent.parent
SAMPLE_CSV = BASE_DIR / "sample_data" / "sample_hdfc_statement.csv"
SAMPLE_XLSX = BASE_DIR / "sample_data" / "sample_icici_statement.xlsx"


def test_categorizer_keywords():
    categories = ["Food", "Rent", "Travel", "Shopping", "Bills", "Health", "Entertainment", "Salary", "Other"]

    assert guess_category("Swiggy Order Delivery", categories) == "Food"
    assert guess_category("Uber Trip Ride", categories) == "Travel"
    assert guess_category("Monthly House Rent", categories) == "Rent"
    assert guess_category("Airtel Broadband Wi-Fi", categories) == "Bills"
    assert guess_category("Apollo Pharmacy Drugs", categories) == "Health"
    assert guess_category("Netflix Stream", categories) == "Entertainment"
    assert guess_category("Salary Payout October", categories) == "Salary"
    assert guess_category("Random unknown description", categories) == "Other"


def test_parse_csv_statement():
    assert SAMPLE_CSV.exists(), "Sample CSV file should exist."

    rows = parse_statement_file(str(SAMPLE_CSV))
    assert len(rows) > 0, "Parser should extract rows from CSV."

    # Validate first row
    first = rows[0]
    assert "date" in first
    assert "description" in first
    assert "amount" in first
    assert "type" in first
    assert "suggested_category" in first

    # Check that salary row is categorized and is income
    salary_row = next((r for r in rows if "Salary" in r["description"]), None)
    assert salary_row is not None
    assert salary_row["type"] == "income"
    assert salary_row["amount"] == 85000.00
    assert salary_row["suggested_category"] == "Salary"


def test_parse_xlsx_statement():
    assert SAMPLE_XLSX.exists(), "Sample XLSX file should exist."

    rows = parse_statement_file(str(SAMPLE_XLSX))
    assert len(rows) > 0, "Parser should extract rows from XLSX."

    # Check rent row is expense
    rent_row = next((r for r in rows if "Rent" in r["description"]), None)
    assert rent_row is not None
    assert rent_row["type"] == "expense"
    assert rent_row["amount"] == 22000.00
    assert rent_row["suggested_category"] == "Rent"


def test_invalid_file_handling():
    with pytest.raises(ValueError):
        parse_statement_file("non_existent_file.csv")
