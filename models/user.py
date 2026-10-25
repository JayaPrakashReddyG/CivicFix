
from werkzeug.security import generate_password_hash, check_password_hash
from database import get_db


class User:

    @staticmethod
    def create(name, email, password, role="citizen"):
        name = name.strip()
        email = email.strip().lower()

        if role not in ("citizen", "admin"):
            raise ValueError("Invalid user role")

        password_hash = generate_password_hash(password)

        db = get_db()
        cursor = db.execute(
            """
            INSERT INTO users (name, email, password_hash, role)
            VALUES (?, ?, ?, ?)
            """,
            (name, email, password_hash, role)
        )
        db.commit()

        return User.get_by_id(cursor.lastrowid)

    @staticmethod
    def get_by_id(user_id):
        db = get_db()
        row = db.execute(
            """
            SELECT id, name, email, role, created_at
            FROM users
            WHERE id = ?
            """,
            (user_id,)
        ).fetchone()

        return dict(row) if row else None

    @staticmethod
    def get_by_email(email):
        db = get_db()
        row = db.execute(
            """
            SELECT id, name, email, password_hash, role, created_at
            FROM users
            WHERE email = ?
            """,
            (email.strip().lower(),)
        ).fetchone()

        return dict(row) if row else None

    @staticmethod
    def verify_password(email, password):
        user = User.get_by_email(email)

        if user and check_password_hash(
            user["password_hash"], password
        ):
            return {
                key: value
                for key, value in user.items()
                if key != "password_hash"
            }

        return None

    @staticmethod
    def get_all():
        db = get_db()
        rows = db.execute(
            """
            SELECT id, name, email, role, created_at
            FROM users
            ORDER BY id DESC
            """
        ).fetchall()

        return [dict(row) for row in rows]
