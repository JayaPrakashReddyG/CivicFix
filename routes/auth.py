
from flask import (
    Blueprint,
    request,
    jsonify,
    session,
    render_template,
    redirect,
    url_for,
    flash,
)

from datetime import datetime

from models.user import User
from utils.excel_export import (
    export_registered_user,
    export_login_history,
)
from utils.validators import validate_registration, validate_email


auth_bp = Blueprint("auth", __name__)


# -----------------------------
# REGISTER API
# -----------------------------
@auth_bp.route("/register", methods=["POST"])
def register():
    data = request.get_json(silent=True)

    if not isinstance(data, dict):
        data = request.form.to_dict()

    error = validate_registration(data)

    if error:
        return jsonify({
            "success": False,
            "message": error
        }), 400

    name = data.get("name", "").strip()
    email = data.get("email", "").strip().lower()
    password = data.get("password", "")

    try:
        user = User.create(name, email, password)

        # Successful registration details Excel lo save chestham
        try:
            export_registered_user(user)
        except Exception as excel_error:
            print("Excel registration export error:", excel_error)

        return jsonify({
            "success": True,
            "message": "Account created successfully.",
            "user": user
        }), 201

    except Exception as exc:
        if "UNIQUE constraint failed" in str(exc):
            return jsonify({
                "success": False,
                "message": "This email is already registered."
            }), 409

        print("Registration error:", exc)

        return jsonify({
            "success": False,
            "message": "Registration failed. Please try again."
        }), 500


# -----------------------------
# LOGIN API
# -----------------------------
@auth_bp.route("/login", methods=["POST"])
def login():
    data = request.get_json(silent=True)

    if not isinstance(data, dict):
        data = request.form.to_dict()

    email = data.get("email", "")
    password = data.get("password", "")

    if not isinstance(email, str):
        email = ""

    if not isinstance(password, str):
        password = ""

    email = email.strip().lower()

    if not validate_email(email) or not password:
        return jsonify({
            "success": False,
            "message": "Valid email and password are required."
        }), 400

    try:
        user = User.verify_password(email, password)

        if not user:
            return jsonify({
                "success": False,
                "message": "Invalid email or password."
            }), 401

        session.clear()
        session["user_id"] = user["id"]
        session["role"] = user["role"]

        # Successful login history Excel lo save chestham
        try:
            export_login_history({
                "user_id": user["id"],
                "name": user.get("name", ""),
                "email": user.get("email", email),
                "login_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            })
        except Exception as excel_error:
            print("Excel login history export error:", excel_error)

        return jsonify({
            "success": True,
            "message": "Login successful.",
            "user": user
        }), 200

    except Exception as exc:
        print("Login error:", exc)

        return jsonify({
            "success": False,
            "message": "Login failed. Please try again."
        }), 500


# -----------------------------
# CURRENT USER API
# -----------------------------
@auth_bp.route("/me", methods=["GET"])
def me():
    user_id = session.get("user_id")

    if not user_id:
        return jsonify({
            "success": False,
            "message": "Please log in."
        }), 401

    user = User.get_by_id(user_id)

    if not user:
        session.clear()

        return jsonify({
            "success": False,
            "message": "User not found."
        }), 404

    return jsonify({
        "success": True,
        "user": user
    }), 200


# -----------------------------
# LOGOUT
# -----------------------------
@auth_bp.route("/logout", methods=["POST"])
def logout():
    session.clear()

    if request.headers.get("X-Requested-With") == "XMLHttpRequest":
        return jsonify({
            "success": True,
            "message": "Logged out successfully."
        }), 200

    if request.is_json:
        return jsonify({
            "success": True,
            "message": "Logged out successfully."
        }), 200

    flash("You have logged out successfully.", "success")
    return redirect(url_for("home"))


# -----------------------------
# LOGIN PAGE
# -----------------------------
@auth_bp.route("/login-page", methods=["GET"])
def login_page():
    if session.get("user_id"):
        return redirect(url_for("home"))

    return render_template("auth/login.html")


# -----------------------------
# REGISTER PAGE
# -----------------------------
@auth_bp.route("/register-page", methods=["GET"])
def register_page():
    if session.get("user_id"):
        return redirect(url_for("home"))

    return render_template("auth/register.html")
