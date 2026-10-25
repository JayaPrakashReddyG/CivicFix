
import os

from flask import (
    Blueprint,
    request,
    jsonify,
    session,
    render_template,
    redirect,
    url_for,
    flash,
    current_app,
    send_from_directory,
)

from models.issue import Issue
from services.issue_service import create_issue
from utils.validators import validate_issue_data


issues_bp = Blueprint("issues", __name__)


# --------------------------------------------------
# SERVE UPLOADED ISSUE IMAGES
# GET /api/issues/uploads/<filename>
# --------------------------------------------------
@issues_bp.route("/uploads/<path:filename>", methods=["GET"])
def uploaded_file(filename):
    """Serve an uploaded issue image from the uploads folder."""

    upload_folder = os.path.join(
        current_app.root_path,
        "uploads",
    )

    return send_from_directory(upload_folder, filename)


# --------------------------------------------------
# CATEGORY NORMALIZATION
# --------------------------------------------------
def normalize_category(data):
    """Normalize category labels before validation and saving."""

    category_map = {
        "pothole": "Pothole",
        "potholes": "Pothole",
        "road": "Pothole",
        "road & potholes": "Pothole",
        "road and potholes": "Pothole",

        "garbage": "Garbage",
        "garbage & waste": "Garbage",
        "garbage and waste": "Garbage",
        "waste": "Garbage",

        "water": "Water Leakage",
        "water leak": "Water Leakage",
        "water leakage": "Water Leakage",
        "water problem": "Water Leakage",
        "water problems": "Water Leakage",

        "streetlight": "Broken Streetlight",
        "streetlights": "Broken Streetlight",
        "street light": "Broken Streetlight",
        "street lights": "Broken Streetlight",
        "streetlights issue": "Broken Streetlight",
        "broken streetlight": "Broken Streetlight",
        "broken street light": "Broken Streetlight",

        "drain": "Other",
        "drainage": "Other",
        "other": "Other",
    }

    normalized_data = dict(data)

    raw_category = str(
        normalized_data.get("category", "")
    ).strip()

    normalized_data["category"] = category_map.get(
        raw_category.casefold(),
        raw_category,
    )

    return normalized_data


# --------------------------------------------------
# HELPER: GET CURRENT USER'S ISSUE
# --------------------------------------------------
def get_accessible_issue(issue_id):
    """Return an issue only if the current user can access it."""

    user_id = session.get("user_id")

    if not user_id:
        return None, (
            jsonify({
                "success": False,
                "message": "Please log in.",
            }),
            401,
        )

    issue = Issue.get_by_id(issue_id)

    if not issue:
        return None, (
            jsonify({
                "success": False,
                "message": "Issue not found.",
            }),
            404,
        )

    if (
        issue["user_id"] != user_id
        and session.get("role") != "admin"
    ):
        return None, (
            jsonify({
                "success": False,
                "message": "You cannot access this issue.",
            }),
            403,
        )

    return issue, None


# --------------------------------------------------
# REPORT A NEW CIVIC ISSUE
# POST /api/issues/
# --------------------------------------------------
@issues_bp.route("/", methods=["POST"])
def report_issue():
    user_id = session.get("user_id")

    if not user_id:
        if request.form:
            flash(
                "Please log in to report an issue.",
                "error",
            )
            return redirect(url_for("auth.login_page"))

        return jsonify({
            "success": False,
            "message": "Please log in to report an issue.",
        }), 401

    if request.form:
        data = request.form.to_dict()
    else:
        data = request.get_json(silent=True) or {}

    data = normalize_category(data)

    error = validate_issue_data(data)

    if error:
        if request.form:
            flash(error, "error")
            return redirect(url_for("home"))

        return jsonify({
            "success": False,
            "message": error,
        }), 400

    try:
        issue = create_issue(
            user_id=user_id,
            data=data,
            image=request.files.get("image"),
        )

        if request.form:
            flash(
                "Issue reported successfully! "
                "You can track its progress in My Reports.",
                "success",
            )
            return redirect(
                url_for("issues.my_issues_page")
            )

        return jsonify({
            "success": True,
            "message": "Issue reported successfully.",
            "issue": issue,
        }), 201

    except ValueError as exc:
        if request.form:
            flash(str(exc), "error")
            return redirect(url_for("home"))

        return jsonify({
            "success": False,
            "message": str(exc),
        }), 400


# --------------------------------------------------
# LIST ISSUES API
# GET /api/issues/
# --------------------------------------------------
@issues_bp.route("/", methods=["GET"])
def list_issues():
    if not session.get("user_id"):
        return jsonify({
            "success": False,
            "message": "Please log in.",
        }), 401

    status = request.args.get("status")
    category = request.args.get("category")

    if category:
        category = normalize_category({
            "category": category,
        })["category"]

    issues = Issue.get_all(
        status=status,
        category=category,
    )

    # Non-admin users can only see their own reports.
    if session.get("role") != "admin":
        user_id = session["user_id"]
        issues = [
            issue for issue in issues
            if issue["user_id"] == user_id
        ]

    return jsonify({
        "success": True,
        "count": len(issues),
        "issues": issues,
    })


# --------------------------------------------------
# MY REPORTS HTML PAGE
# GET /api/issues/my-page
# --------------------------------------------------
@issues_bp.route("/my-page", methods=["GET"])
def my_issues_page():
    user_id = session.get("user_id")

    if not user_id:
        flash(
            "Please log in to view your reports.",
            "error",
        )
        return redirect(url_for("auth.login_page"))

    issues = Issue.get_by_user(user_id)

    return render_template(
        "user/my_issues.html",
        issues=issues,
        count=len(issues),
    )


# --------------------------------------------------
# MY REPORTS JSON API
# GET /api/issues/my
# --------------------------------------------------
@issues_bp.route("/my", methods=["GET"])
def my_issues():
    user_id = session.get("user_id")

    if not user_id:
        return jsonify({
            "success": False,
            "message": "Please log in.",
        }), 401

    issues = Issue.get_by_user(user_id)

    return jsonify({
        "success": True,
        "count": len(issues),
        "issues": issues,
    })


# --------------------------------------------------
# ISSUE DETAILS HTML PAGE
# GET /api/issues/<issue_id>/view
# --------------------------------------------------
@issues_bp.route("/<int:issue_id>/view", methods=["GET"])
def issue_details_page(issue_id):
    if not session.get("user_id"):
        flash(
            "Please log in to view issue details.",
            "error",
        )
        return redirect(url_for("auth.login_page"))

    issue, error_response = get_accessible_issue(issue_id)

    if error_response:
        response, status_code = error_response

        if status_code == 401:
            return redirect(url_for("auth.login_page"))

        if status_code == 404:
            return render_template("errors/404.html"), 404

        if status_code == 403:
            return render_template("errors/403.html"), 403

        return response, status_code

    return render_template(
        "user/issue_details.html",
        issue=issue,
    )


# --------------------------------------------------
# ISSUE DETAILS JSON API
# GET /api/issues/<issue_id>
# --------------------------------------------------
@issues_bp.route("/<int:issue_id>", methods=["GET"])
def issue_details(issue_id):
    issue, error_response = get_accessible_issue(issue_id)

    if error_response:
        return error_response

    return jsonify({
        "success": True,
        "issue": issue,
    })
