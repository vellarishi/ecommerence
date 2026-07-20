import os

BASE_DIR = os.path.abspath(os.path.dirname(__file__))


class Config:
    # SECRET_KEY signs the session cookie (used for admin login sessions).
    # In production, set this via an environment variable instead of hardcoding.
    SECRET_KEY = os.environ.get("SECRET_KEY", "ruchi-dev-secret-change-this")

    # SQLite file lives inside /instance — Flask auto-creates this folder.
    SQLALCHEMY_DATABASE_URI = os.environ.get(
        "DATABASE_URL", f"sqlite:///{os.path.join(BASE_DIR, 'instance', 'ruchi.db')}"
    )
    SQLALCHEMY_TRACK_MODIFICATIONS = False

    # Default admin login — created automatically on first run if no admin exists.
    # CHANGE THIS PASSWORD before deploying anywhere public.
    DEFAULT_ADMIN_USERNAME = os.environ.get("ADMIN_USERNAME", "admin")
    DEFAULT_ADMIN_PASSWORD = os.environ.get("ADMIN_PASSWORD", "ruchi123")
