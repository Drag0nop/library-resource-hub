import os
from typing import Optional


def _build_mysql_uri() -> Optional[str]:
    user = os.getenv("MYSQL_USER")
    password = os.getenv("MYSQL_PASSWORD")
    host = os.getenv("MYSQL_HOST", "localhost")
    port = os.getenv("MYSQL_PORT", "3306")
    dbname = os.getenv("MYSQL_DBNAME")

    if user and password and dbname:
        return f"mysql+pymysql://{user}:{password}@{host}:{port}/{dbname}"
    return None


class Config:
    SECRET_KEY = os.getenv("SECRET_KEY", "dev-secret-change-me")

    # Prefer full DATABASE_URL if provided; else build from MYSQL_*; else sqlite
    SQLALCHEMY_DATABASE_URI = (
        os.getenv("DATABASE_URL")
        or _build_mysql_uri()
        or ("sqlite:///instance/library.db")
    )
    SQLALCHEMY_TRACK_MODIFICATIONS = False

    # Session cookie settings
    SESSION_COOKIE_HTTPONLY = True
    REMEMBER_COOKIE_HTTPONLY = True

