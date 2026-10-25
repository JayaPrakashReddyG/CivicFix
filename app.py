
from functools import wraps

from flask import (
    Flask,
    jsonify,
    render_template,
    redirect,
    request,
    session,
    url_for,
)
from flask_cors import CORS

from config import Config
from database import init_db
from routes.auth import auth_bp
from routes.issues import issues_bp
from routes.admin import admin_bp


def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)

    CORS(app)

    # Initialize database
    init_db(app)

    # Register API routes
    app.register_blueprint(auth_bp, url_prefix="/api/auth")
    app.register_blueprint(issues_bp, url_prefix="/api/issues")
    app.register_blueprint(admin_bp, url_prefix="/api/admin")

    # Pages that visitors can open without logging in
    PUBLIC_ENDPOINTS = {
        "home",
        "login_entry",
        "auth.login_page",
        "auth.register_page",
        "auth.login",
        "auth.register",
        "health",
        "static",
    }

    @app.before_request
    def require_login():
        # Allow browser assets and public login/register endpoints
        if request.endpoint is None:
            return None

        if request.endpoint in PUBLIC_ENDPOINTS:
            return None

        # Allow preflight requests if frontend uses CORS
        if request.method == "OPTIONS":
            return None

        # No logged-in session: API requests get JSON;
        # browser page requests are redirected to login.
        if not session.get("user_id"):
            if request.path.startswith("/api/"):
                return jsonify({
                    "success": False,
                    "message": "Please log in to continue."
                }), 401

            return redirect(url_for("auth.login_page"))

        return None

    # Root URL: show login first, or home if already logged in
    @app.route("/")
    def login_entry():
        if session.get("user_id"):
            return render_template("index.html")

        return redirect(url_for("auth.login_page"))

    # Home page: login required
    @app.route("/home")
    def home():
        if not session.get("user_id"):
            return redirect(url_for("auth.login_page"))

        return render_template("index.html")

    # Health check
    @app.route("/api/health")
    def health():
        return jsonify({
            "success": True,
            "message": "CivicFix server is healthy"
        })

    # 404 handler
    @app.errorhandler(404)
    def not_found(error):
        if request.path.startswith("/api/"):
            return jsonify({
                "success": False,
                "message": "API endpoint not found"
            }), 404

        return "Page not found", 404

    # 500 handler
    @app.errorhandler(500)
    def internal_error(error):
        if request.path.startswith("/api/"):
            return jsonify({
                "success": False,
                "message": "Internal server error"
            }), 500

        return "Internal server error", 500

    return app


app = create_app()


if __name__ == "__main__":
    app.run(
        debug=app.config.get("DEBUG", True),
        host="127.0.0.1",
        port=5000
    )
