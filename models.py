from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin
from datetime import datetime

db = SQLAlchemy()

class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=True)
    password_hash = db.Column(db.String(200), nullable=False)
    is_admin = db.Column(db.Boolean, default=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    # Forgot Password (optional fields)
    reset_token = db.Column(db.String(255), nullable=True)
    token_expiration = db.Column(db.DateTime, nullable=True)

    # Correct relationship
    borrows = db.relationship('Borrow', back_populates='user', cascade="all, delete-orphan")


class Book(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(200), nullable=False)
    author = db.Column(db.String(200))
    category = db.Column(db.String(100))
    isbn = db.Column(db.String(50))
    copies = db.Column(db.Integer, default=1)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    # Correct relationship
    borrows = db.relationship('Borrow', back_populates='book', cascade="all, delete-orphan")


class Borrow(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    book_id = db.Column(db.Integer, db.ForeignKey('book.id'))
    borrowed_at = db.Column(db.DateTime, default=datetime.utcnow)
    returned_at = db.Column(db.DateTime, nullable=True)

    due_date = db.Column(db.DateTime)
    late_fee = db.Column(db.Float, default=0.0)

    # FIXED — Use back_populates (matches User and Book)
    user = db.relationship('User', back_populates='borrows')
    book = db.relationship('Book', back_populates='borrows')
