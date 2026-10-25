
from pathlib import Path

from flask import current_app

from models.issue import Issue
from utils.image_handler import save_issue_image
from utils.location_handler import validate_location


def create_issue(user_id, data, image=None):
    title = str(data.get("title", "")).strip()
    description = str(data.get("description", "")).strip()
    category = str(data.get("category", "")).strip()

    if not title:
        raise ValueError("Issue title is required")

    if not description:
        raise ValueError("Issue description is required")

    if not category:
        raise ValueError("Issue category is required")

    latitude = data.get("latitude")
    longitude = data.get("longitude")
    address = str(data.get("address", "")).strip() or None

    # Validate and normalize the supplied location.
    latitude, longitude = validate_location(latitude, longitude)

    image_path = None

    if image and image.filename:
        image_path = save_issue_image(image)

    try:
        issue = Issue.create(
            user_id=user_id,
            title=title,
            description=description,
            category=category,
            image_path=image_path,
            latitude=latitude,
            longitude=longitude,
            address=address
        )

        if issue is None:
            raise RuntimeError("Could not create issue")

        return issue

    except Exception:
        # Remove the uploaded image if database insertion fails.
        if image_path:
            upload_root = Path(
                current_app.config["UPLOAD_FOLDER"]
            ).resolve()

            saved_path = (upload_root / image_path).resolve()

            if saved_path.is_relative_to(upload_root):
                saved_path.unlink(missing_ok=True)

        raise
