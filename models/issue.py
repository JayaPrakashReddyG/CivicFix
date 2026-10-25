
from database import get_db


class Issue:

    VALID_STATUSES = {
        "Pending",
        "In Progress",
        "Resolved",
        "Rejected"
    }

    @staticmethod
    def create(
        user_id,
        title,
        description,
        category,
        image_path=None,
        latitude=None,
        longitude=None,
        address=None
    ):
        db = get_db()

        cursor = db.execute(
            """
            INSERT INTO issues (
                user_id,
                title,
                description,
                category,
                image_path,
                latitude,
                longitude,
                address
            )
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (
                user_id,
                title.strip(),
                description.strip(),
                category.strip(),
                image_path,
                latitude,
                longitude,
                address
            )
        )
        db.commit()

        return Issue.get_by_id(cursor.lastrowid)

    @staticmethod
    def get_by_id(issue_id):
        db = get_db()

        row = db.execute(
            """
            SELECT
                i.*,
                u.name AS reporter_name,
                u.email AS reporter_email
            FROM issues i
            JOIN users u ON i.user_id = u.id
            WHERE i.id = ?
            """,
            (issue_id,)
        ).fetchone()

        return dict(row) if row else None

    @staticmethod
    def get_all(status=None, category=None):
        db = get_db()

        query = """
            SELECT
                i.*,
                u.name AS reporter_name
            FROM issues i
            JOIN users u ON i.user_id = u.id
            WHERE 1 = 1
        """
        params = []

        if status:
            query += " AND i.status = ?"
            params.append(status)

        if category:
            query += " AND i.category = ?"
            params.append(category)

        query += " ORDER BY i.created_at DESC"

        rows = db.execute(query, params).fetchall()
        return [dict(row) for row in rows]

    @staticmethod
    def get_by_user(user_id):
        db = get_db()

        rows = db.execute(
            """
            SELECT *
            FROM issues
            WHERE user_id = ?
            ORDER BY created_at DESC
            """,
            (user_id,)
        ).fetchall()

        return [dict(row) for row in rows]

    @staticmethod
    def update_status(issue_id, status, admin_notes=None):
        if status not in Issue.VALID_STATUSES:
            raise ValueError("Invalid issue status")

        db = get_db()

        cursor = db.execute(
            """
            UPDATE issues
            SET status = ?,
                admin_notes = ?,
                updated_at = CURRENT_TIMESTAMP
            WHERE id = ?
            """,
            (status, admin_notes, issue_id)
        )
        db.commit()

        if cursor.rowcount == 0:
            return None

        return Issue.get_by_id(issue_id)

    @staticmethod
    def delete(issue_id):
        db = get_db()

        cursor = db.execute(
            "DELETE FROM issues WHERE id = ?",
            (issue_id,)
        )
        db.commit()

        return cursor.rowcount > 0
