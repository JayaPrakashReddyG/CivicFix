
import uuid
from pathlib import Path

from flask import current_app
from werkzeug.utils import secure_filename
from PIL import Image, UnidentifiedImageError


ALLOWED_EXTENSIONS = {"jpg", "jpeg", "png", "webp"}
MAX_IMAGE_SIZE = 5 * 1024 * 1024  # 5 MB


def save_issue_image(file):
    if not file or not file.filename:
        return None

    original_name = secure_filename(file.filename)

    if not original_name or "." not in original_name:
        raise ValueError("Invalid image filename")

    extension = original_name.rsplit(".", 1)[1].lower()

    if extension not in ALLOWED_EXTENSIONS:
        raise ValueError("Only JPG, JPEG, PNG, and WEBP images are allowed")

    # Read a bounded amount to enforce the size limit.
    file.stream.seek(0, 2)
    size = file.stream.tell()
    file.stream.seek(0)

    if size == 0:
        raise ValueError("Uploaded image is empty")

    if size > MAX_IMAGE_SIZE:
        raise ValueError("Image must be 5 MB or smaller")

    try:
        with Image.open(file.stream) as image:
            if image.format not in {"JPEG", "PNG", "WEBP"}:
                raise ValueError("Unsupported image format")
            image.verify()

        file.stream.seek(0)

    except (UnidentifiedImageError, OSError):
        raise ValueError("Uploaded file is not a valid image")

    upload_dir = Path(
        current_app.config["UPLOAD_FOLDER"]
    ).resolve()

    upload_dir.mkdir(parents=True, exist_ok=True)

    filename = f"{uuid.uuid4().hex}.{extension}"
    destination = upload_dir / filename

    file.save(destination)

    # Store only a relative filename in the database.
    return filename
