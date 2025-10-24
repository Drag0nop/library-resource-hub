from __future__ import annotations

from datetime import datetime

from . import db


class Book(db.Model):
    __tablename__ = "books"

    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(255), nullable=False)
    author = db.Column(db.String(255), nullable=False)
    description = db.Column(db.Text, nullable=True)
    available_count = db.Column(db.Integer, nullable=False, default=1)
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)

    def __repr__(self) -> str:
        return f"<Book {self.id} {self.title}>"
