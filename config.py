
import os
from pathlib import Path


BASE_DIR = Path(__file__).resolve().parent


class Config:
    SECRET_KEY = os.environ.get(
        "SECRET_KEY",
        "change-this-secret-key-before-deployment"
    )

    DEBUG = os.environ.get("FLASK_DEBUG", "true").lower() == "true"

    DATABASE_PATH = BASE_DIR / "instance" / "civicfix.db"
    UPLOAD_FOLDER = BASE_DIR / "uploads"

    MAX_CONTENT_LENGTH = 5 * 1024 * 1024  # 5 MB
    ALLOWED_IMAGE_EXTENSIONS = {"png", "jpg", "jpeg", "webp"}

    JSON_SORT_KEYS = False
