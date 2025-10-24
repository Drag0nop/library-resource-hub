from __future__ import annotations

from datetime import datetime
from typing import Optional

from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash

from . import db


class User(db.Model, UserMixin):
    __tablename__ = "users"

    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    email = db.Column(db.String(255), unique=True, nullable=False)
    password_hash = db.Column(db.String(255), nullable=False)
    is_admin = db.Column(db.Boolean, default=False, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)

    def set_password(self, password: str) -> None:
        self.password_hash = generate_password_hash(password)

    def check_password(self, password: str) -> bool:
        return check_password_hash(self.password_hash, password)

    @staticmethod
    def create_admin_if_none_exists(username: str, email: str, password: str) -> Optional["User"]:
        existing_admin = User.query.filter_by(is_admin=True).first()
        if existing_admin is not None:
            return None
        admin_user = User(
            username=username,
            email=email,
            is_admin=True,
        )
        admin_user.set_password(password)
        db.session.add(admin_user)
        db.session.commit()
        return admin_user
