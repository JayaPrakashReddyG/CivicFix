
from flask import Blueprint, request, jsonify, session
from functools import wraps
from database import get_db
from models.issue import Issue
from models.user import User

admin_bp = Blueprint("admin", __name__)


def admin_required(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        user_id = session.get("user_id")

        if not user_id or session.get("role") != "admin":
            return jsonify({
                "success": False,
                "message": "Administrator access required"
            }), 403

        return func(*args, **kwargs)

    return wrapper


@admin_bp.route("/dashboard", methods=["GET"])
@admin_required
def dashboard():
    db = get_db()

    total_users = db.execute(
        "SELECT COUNT(*) FROM users"
    ).fetchone()[0]

    total_issues = db.execute(
        "SELECT COUNT(*) FROM issues"
    ).fetchone()[0]

    rows = db.execute(
        """
        SELECT status, COUNT(*) AS count
        FROM issues
        GROUP BY status
        """
    ).fetchall()

    status_counts = {
        row["status"]: row["count"] for row in rows
    }

    return jsonify({
        "success": True,
        "statistics": {
            "total_users": total_users,
            "total_issues": total_issues,
            "pending": status_counts.get("Pending", 0),
            "in_progress": status_counts.get("In Progress", 0),
            "resolved": status_counts.get("Resolved", 0),
            "rejected": status_counts.get("Rejected", 0)
        }
    })


@admin_bp.route("/issues", methods=["GET"])
@admin_required
def all_issues():
    return jsonify({
        "success": True,
        "issues": Issue.get_all()
    })


@admin_bp.route("/issues/<int:issue_id>/status", methods=["PATCH"])
@admin_required
def update_issue_status(issue_id):
    data = request.get_json(silent=True) or {}

    status = data.get("status")
    admin_notes = data.get("admin_notes")

    if status not in Issue.VALID_STATUSES:
        return jsonify({
            "success": False,
            "message": "Invalid issue status"
        }), 400

    issue = Issue.update_status(
        issue_id,
        status,
        admin_notes
    )

    if not issue:
        return jsonify({
            "success": False,
            "message": "Issue not found"
        }), 404

    return jsonify({
        "success": True,
        "message": "Issue status updated",
        "issue": issue
    })


@admin_bp.route("/issues/<int:issue_id>", methods=["DELETE"])
@admin_required
def delete_issue(issue_id):
    if not Issue.delete(issue_id):
        return jsonify({
            "success": False,
            "message": "Issue not found"
        }), 404

    return jsonify({
        "success": True,
        "message": "Issue deleted successfully"
    })


@admin_bp.route("/users", methods=["GET"])
@admin_required
def all_users():
    return jsonify({
        "success": True,
        "users": User.get_all()
    })
