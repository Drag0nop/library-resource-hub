from __future__ import annotations

from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager

# Initialized in app factory
db: SQLAlchemy = SQLAlchemy()
login_manager: LoginManager = LoginManager()

__all__ = ["db", "login_manager"]
