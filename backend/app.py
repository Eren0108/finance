import os
import sys
from pathlib import Path

# Ensure root directory is in sys.path
ROOT_DIR = Path(__file__).resolve().parent.parent
if str(ROOT_DIR) not in sys.path:
    sys.path.insert(0, str(ROOT_DIR))

from flask import Flask, send_from_directory, jsonify
from flask_cors import CORS

from backend.config import FRONTEND_DIR, MAX_CONTENT_LENGTH
from backend.database import init_db
from backend.utils.helpers import api_response

# Import Blueprints
from backend.routes.categories import categories_bp
from backend.routes.transactions import transactions_bp
from backend.routes.budgets import budgets_bp
from backend.routes.statements import statements_bp
from backend.routes.reports import reports_bp


def create_app():
    """Application factory for the Personal Finance Tracker Flask app."""
    # Ensure database is initialized
    init_db()

    app = Flask(
        __name__,
        static_folder=str(FRONTEND_DIR),
        static_url_path=""
    )

    # Configuration
    app.config["MAX_CONTENT_LENGTH"] = MAX_CONTENT_LENGTH
    app.config["JSON_SORT_KEYS"] = False

    # Enable Cross-Origin Resource Sharing
    CORS(app)

    # Register API Blueprints
    app.register_blueprint(categories_bp)
    app.register_blueprint(transactions_bp)
    app.register_blueprint(budgets_bp)
    app.register_blueprint(statements_bp)
    app.register_blueprint(reports_bp)

    # Health Check Endpoint
    @app.route("/api/health", methods=["GET"])
    def health_check():
        return api_response(data={
            "status": "healthy",
            "app": "Personal Finance Tracker",
            "version": "1.0.0"
        })

    # Frontend Page Serving Routes
    @app.route("/", methods=["GET"])
    def serve_index():
        return send_from_directory(FRONTEND_DIR, "index.html")

    @app.route("/<path:path>", methods=["GET"])
    def serve_frontend_static(path):
        target = FRONTEND_DIR / path
        if target.exists() and target.is_file():
            return send_from_directory(FRONTEND_DIR, path)
        # If path corresponds to an HTML page name without extension, try appending .html
        html_target = FRONTEND_DIR / f"{path}.html"
        if html_target.exists():
            return send_from_directory(FRONTEND_DIR, f"{path}.html")
        return api_response(error=f"Resource '{path}' not found.", status_code=404)

    # Global Error Handlers
    @app.errorhandler(413)
    def request_entity_too_large(error):
        return api_response(error="File exceeds the maximum allowed size of 5 MB.", status_code=413)

    @app.errorhandler(404)
    def not_found(error):
        return api_response(error="The requested endpoint was not found.", status_code=404)

    @app.errorhandler(500)
    def internal_error(error):
        return api_response(error="An internal server error occurred.", status_code=500)

    return app


# Module-level app instance for production WSGI servers (e.g. Gunicorn)
app = create_app()

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    print(f"[SERVER] Finance Tracker Server running at: http://localhost:{port}")
    app.run(host="0.0.0.0", port=port, debug=True)
