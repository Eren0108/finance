import os
from datetime import date
from flask import Blueprint, request, send_file
from backend.utils.helpers import api_response
from backend.utils.validators import validate_month
from backend.services.analytics import get_monthly_summary, get_monthly_trend
from backend.services.excel_exporter import generate_excel_report

reports_bp = Blueprint("reports", __name__, url_prefix="/api/reports")


@reports_bp.route("/summary", methods=["GET"])
def monthly_summary():
    """Returns income, expense, savings, and category breakdown for a month."""
    month = request.args.get("month")
    if not month:
        month = date.today().strftime("%Y-%m")

    try:
        clean_month = validate_month(month)
    except ValueError as e:
        return api_response(error=str(e), status_code=400)

    summary = get_monthly_summary(clean_month)
    return api_response(data=summary)


@reports_bp.route("/trend", methods=["GET"])
def monthly_trend():
    """Returns 6-month income vs expense trend data for charts."""
    months_count = int(request.args.get("months", 6))
    end_month = request.args.get("end_month")
    trend = get_monthly_trend(months_count=months_count, end_month=end_month)
    return api_response(data=trend)


@reports_bp.route("/export", methods=["GET"])
def export_excel():
    """Generates and downloads an Excel report workbook for a month."""
    month = request.args.get("month")
    if not month:
        month = date.today().strftime("%Y-%m")

    try:
        clean_month = validate_month(month)
    except ValueError as e:
        return api_response(error=str(e), status_code=400)

    try:
        file_path = generate_excel_report(clean_month)
        if not os.path.exists(file_path):
            return api_response(error="Failed to generate Excel report file.", status_code=500)

        filename = f"finance_report_{clean_month}.xlsx"
        return send_file(
            file_path,
            as_attachment=True,
            download_name=filename,
            mimetype="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
        )
    except Exception as e:
        return api_response(error=f"Export failed: {str(e)}", status_code=500)
