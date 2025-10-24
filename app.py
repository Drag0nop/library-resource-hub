from __future__ import annotations

import os
from typing import Callable, TypeVar, Any, cast

from flask import Flask, render_template, request, redirect, url_for, flash, abort
from flask_login import login_user, login_required, logout_user, current_user

from config import Config
from models import db, login_manager
from models.user import User
from models.book import Book


F = TypeVar("F", bound=Callable[..., Any])


def create_app() -> Flask:
    app = Flask(__name__, instance_relative_config=True)

    # Ensure instance folder exists (for sqlite fallback)
    try:
        os.makedirs(app.instance_path, exist_ok=True)
    except OSError:
        pass

    # Load config
    app.config.from_object(Config)

    # Init extensions
    db.init_app(app)
    login_manager.init_app(app)
    login_manager.login_view = "login"

    # Create tables at startup if not already present
    with app.app_context():
        db.create_all()
        # Bootstrap: if no admin exists and BOOTSTRAP_ADMIN is set to true, create one
        if os.getenv("BOOTSTRAP_ADMIN", "true").lower() in {"1", "true", "yes"}:
            _maybe_bootstrap_admin()

    @login_manager.user_loader
    def load_user(user_id: str) -> User | None:
        if not user_id:
            return None
        return db.session.get(User, int(user_id))

    def admin_required(func: F) -> F:
        def wrapper(*args: Any, **kwargs: Any):
            if not current_user.is_authenticated:
                return login_manager.unauthorized()
            if not current_user.is_admin:
                abort(403)
            return func(*args, **kwargs)

        return cast(F, login_required(wrapper))

    @app.get("/")
    def index():
        if current_user.is_authenticated:
            return redirect(url_for("dashboard"))
        return redirect(url_for("login"))

    # Authentication routes
    @app.route("/login", methods=["GET", "POST"])
    def login():
        if request.method == "POST":
            username_or_email = request.form.get("username", "").strip()
            password = request.form.get("password", "")

            user = (
                User.query.filter(
                    (User.username == username_or_email) | (User.email == username_or_email)
                ).first()
            )
            if user and user.check_password(password):
                login_user(user)
                flash("Logged in successfully.", "success")
                return redirect(url_for("dashboard"))
            flash("Invalid credentials.", "error")

        return render_template("login.html")

    @app.route("/register", methods=["GET", "POST"])
    def register():
        if request.method == "POST":
            username = request.form.get("username", "").strip()
            email = request.form.get("email", "").strip().lower()
            password = request.form.get("password", "")

            if not username or not email or not password:
                flash("All fields are required.", "error")
                return render_template("register.html")

            if User.query.filter((User.username == username) | (User.email == email)).first():
                flash("Username or email already in use.", "error")
                return render_template("register.html")

            is_first_user_admin = User.query.count() == 0
            new_user = User(username=username, email=email, is_admin=is_first_user_admin)
            new_user.set_password(password)
            db.session.add(new_user)
            db.session.commit()
            flash("Registration successful. Please log in.", "success")
            return redirect(url_for("login"))

        return render_template("register.html")

    @app.get("/logout")
    @login_required
    def logout():
        logout_user()
        flash("You have been logged out.", "success")
        return redirect(url_for("login"))

    # User dashboard
    @app.get("/dashboard")
    @login_required
    def dashboard():
        books = Book.query.order_by(Book.created_at.desc()).all()
        return render_template("dashboard.html", books=books)

    # Admin area
    @app.get("/admin")
    @admin_required
    def admin_dashboard():
        total_users = User.query.count()
        total_books = Book.query.count()
        admins = User.query.filter_by(is_admin=True).count()
        return render_template(
            "admin_dashboard.html", total_users=total_users, total_books=total_books, admins=admins
        )

    @app.route("/admin/books", methods=["GET", "POST"])
    @admin_required
    def admin_books():
        if request.method == "POST":
            title = request.form.get("title", "").strip()
            author = request.form.get("author", "").strip()
            description = request.form.get("description", "").strip()
            available_count = request.form.get("available_count", "1").strip()

            if not title or not author:
                flash("Title and Author are required.", "error")
            else:
                try:
                    count = max(0, int(available_count))
                except ValueError:
                    count = 1
                book = Book(title=title, author=author, description=description, available_count=count)
                db.session.add(book)
                db.session.commit()
                flash("Book added.", "success")
        books = Book.query.order_by(Book.created_at.desc()).all()
        return render_template("admin_books.html", books=books)

    @app.post("/admin/books/delete/<int:book_id>")
    @admin_required
    def admin_delete_book(book_id: int):
        book = db.session.get(Book, book_id)
        if not book:
            flash("Book not found.", "error")
            return redirect(url_for("admin_books"))
        db.session.delete(book)
        db.session.commit()
        flash("Book deleted.", "success")
        return redirect(url_for("admin_books"))

    @app.route("/admin/users", methods=["GET", "POST"])
    @admin_required
    def admin_users():
        if request.method == "POST":
            # Create user (optionally admin)
            username = request.form.get("username", "").strip()
            email = request.form.get("email", "").strip().lower()
            password = request.form.get("password", "")
            is_admin = request.form.get("is_admin") == "on"

            if not username or not email or not password:
                flash("All fields are required.", "error")
            elif User.query.filter((User.username == username) | (User.email == email)).first():
                flash("Username or email already in use.", "error")
            else:
                user = User(username=username, email=email, is_admin=is_admin)
                user.set_password(password)
                db.session.add(user)
                db.session.commit()
                flash("User created.", "success")

        users = User.query.order_by(User.created_at.desc()).all()
        return render_template("admin_users.html", users=users)

    @app.post("/admin/users/delete/<int:user_id>")
    @admin_required
    def admin_delete_user(user_id: int):
        if user_id == current_user.id:
            flash("You cannot delete your own account while logged in.", "error")
            return redirect(url_for("admin_users"))
        user = db.session.get(User, user_id)
        if not user:
            flash("User not found.", "error")
            return redirect(url_for("admin_users"))
        db.session.delete(user)
        db.session.commit()
        flash("User deleted.", "success")
        return redirect(url_for("admin_users"))

    return app


def _maybe_bootstrap_admin() -> None:
    default_admin_username = os.getenv("DEFAULT_ADMIN_USERNAME")
    default_admin_email = os.getenv("DEFAULT_ADMIN_EMAIL")
    default_admin_password = os.getenv("DEFAULT_ADMIN_PASSWORD")

    if not (default_admin_username and default_admin_email and default_admin_password):
        # No bootstrap settings provided; skip silently
        return

    User.create_admin_if_none_exists(
        username=default_admin_username,
        email=default_admin_email.lower(),
        password=default_admin_password,
    )


if __name__ == "__main__":
    flask_app = create_app()
    flask_app.run(host="0.0.0.0", port=int(os.getenv("PORT", 5000)), debug=True)
