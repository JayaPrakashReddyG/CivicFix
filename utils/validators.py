import re


def validate_email(email):
    """Check whether an email address has a valid basic format."""
    if not isinstance(email, str):
        return False

    email = email.strip()

    if len(email) > 254:
        return False

    pattern = (
        r"^[A-Za-z0-9.!#$%&'*+/=?^_`{|}~-]+"
        r"@[A-Za-z0-9-]+(?:\.[A-Za-z0-9-]+)+$"
    )

    return bool(re.fullmatch(pattern, email))


def validate_registration(data):
    """Validate the fields required to register a CivicFix user."""
    if not isinstance(data, dict):
        return "Invalid request data."

    name = data.get("name", "")
    email = data.get("email", "")
    password = data.get("password", "")

    if not all(
        isinstance(value, str)
        for value in (name, email, password)
    ):
        return "Name, email and password must be text."

    name = name.strip()
    email = email.strip()

    if not name:
        return "Name is required."

    if len(name) > 100:
        return "Name must be 100 characters or fewer."

    if not validate_email(email):
        return "Please enter a valid email address."

    if len(password) < 8:
        return "Password must contain at least 8 characters."

    if len(password) > 128:
        return "Password is too long."

    return None


def validate_issue_data(data):
    """Validate the information submitted for a civic issue."""
    if not isinstance(data, dict):
        return "Invalid issue data."

    title = data.get("title", "")
    description = data.get("description", "")
    category = data.get("category", "")

    if not all(
        isinstance(value, str)
        for value in (title, description, category)
    ):
        return "Title, description and category must be text."

    title = title.strip()
    description = description.strip()
    category = category.strip()

    if not title:
        return "Issue title is required."

    if len(title) > 150:
        return "Issue title must be 150 characters or fewer."

    if not description:
        return "Issue description is required."

    if len(description) > 5000:
        return "Description must be 5000 characters or fewer."

    allowed_categories = {
        "pothole",
        "garbage",
        "water leakage",
        "broken streetlight",
        "other",
    }

    if category.lower() not in allowed_categories:
        return (
            "Choose a valid category: Pothole, Garbage, "
            "Water Leakage, Broken Streetlight or Other."
        )

    return None
