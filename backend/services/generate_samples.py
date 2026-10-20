import os
import pandas as pd
from pathlib import Path

SAMPLE_DIR = Path(__file__).resolve().parent.parent / "sample_data"
SAMPLE_DIR.mkdir(parents=True, exist_ok=True)

# 1. Sample CSV Statement
csv_rows = [
    {"Date": "2026-10-01", "Particulars": "Salary Credited by ACME Corp", "Debit": "", "Credit": "85000.00"},
    {"Date": "2026-10-02", "Particulars": "House Rent to Landlord", "Debit": "24000.00", "Credit": ""},
    {"Date": "2026-10-03", "Particulars": "Swiggy Food Delivery", "Debit": "540.00", "Credit": ""},
    {"Date": "2026-10-04", "Particulars": "Bescom Electricity Bill Payment", "Debit": "1850.00", "Credit": ""},
    {"Date": "2026-10-05", "Particulars": "Airtel Broadband Fiber", "Debit": "999.00", "Credit": ""},
    {"Date": "2026-10-06", "Particulars": "Uber Cab to Airport", "Debit": "720.00", "Credit": ""},
    {"Date": "2026-10-07", "Particulars": "BigBasket Grocery Mart", "Debit": "3450.00", "Credit": ""},
    {"Date": "2026-10-08", "Particulars": "Apollo Pharmacy Medicine", "Debit": "890.00", "Credit": ""},
    {"Date": "2026-10-10", "Particulars": "Netflix Monthly Subscription", "Debit": "649.00", "Credit": ""},
    {"Date": "2026-10-12", "Particulars": "Amazon India Retail Purchase", "Debit": "2299.00", "Credit": ""},
    {"Date": "2026-10-14", "Particulars": "Indian Oil Fuel Petrol", "Debit": "1500.00", "Credit": ""},
    {"Date": "2026-10-15", "Particulars": "Freelance Client Consultation", "Debit": "", "Credit": "15000.00"},
    {"Date": "2026-10-16", "Particulars": "Zomato Restaurant Lunch", "Debit": "680.00", "Credit": ""},
]

df_csv = pd.DataFrame(csv_rows)
csv_path = SAMPLE_DIR / "sample_hdfc_statement.csv"
df_csv.to_csv(csv_path, index=False)
print(f"Created CSV sample: {csv_path}")

# 2. Sample Excel Statement (.xlsx)
excel_rows = [
    {"Txn Date": "01/10/2026", "Description": "Direct Deposit Salary Oct 2026", "Withdrawal Amount": 0, "Deposit Amount": 92000.00},
    {"Txn Date": "02/10/2026", "Description": "Apartment Rent Payment", "Withdrawal Amount": 22000.00, "Deposit Amount": 0},
    {"Txn Date": "04/10/2026", "Description": "McDonalds Food Delivery", "Withdrawal Amount": 480.00, "Deposit Amount": 0},
    {"Txn Date": "05/10/2026", "Description": "Tata Power Utility Bill", "Withdrawal Amount": 2100.00, "Deposit Amount": 0},
    {"Txn Date": "08/10/2026", "Description": "Flipkart Online Shopping", "Withdrawal Amount": 1899.00, "Deposit Amount": 0},
    {"Txn Date": "11/10/2026", "Description": "Ola Cabs Commute", "Withdrawal Amount": 340.00, "Deposit Amount": 0},
    {"Txn Date": "13/10/2026", "Description": "BookMyShow Movie Tickets PVR", "Withdrawal Amount": 950.00, "Deposit Amount": 0},
    {"Txn Date": "15/10/2026", "Description": "MedPlus Healthcare Drugs", "Withdrawal Amount": 620.00, "Deposit Amount": 0},
]

df_xlsx = pd.DataFrame(excel_rows)
xlsx_path = SAMPLE_DIR / "sample_icici_statement.xlsx"
df_xlsx.to_excel(xlsx_path, index=False)
print(f"Created XLSX sample: {xlsx_path}")
