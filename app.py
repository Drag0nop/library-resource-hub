from flask import Flask, render_template, request, redirect, url_for, flash
from models import db, User, Book, Borrow
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import LoginManager, login_user, login_required, logout_user, current_user
from datetime import datetime, timedelta
from email.mime.text import MIMEText
import smtplib
import os
from dotenv import load_dotenv
from random import randint
from collections import Counter
from io import StringIO
import csv

# Load environment variables
load_dotenv()

# Initialize Flask app
app = Flask(__name__)

# Configuration
app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv('DATABASE_URL', 'mysql+pymysql://root:password@localhost/library')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SECRET_KEY'] = os.getenv('SECRET_KEY', 'change-me-to-a-secure-random-value')

# Initialize DB and Login Manager
db.init_app(app)
login_manager = LoginManager()
login_manager.login_view = 'login'
login_manager.login_message = None
login_manager.init_app(app)

# Temporary OTP store
otp_store = {}  # {email: {'otp': <int>, 'expiry': <datetime>}}

# ------------------ LOGIN MANAGEMENT ------------------ #
@login_manager.user_loader
def load_user(user_id):
    # LegacyAPIWarning is informational; using query.get for simplicity
    return User.query.get(int(user_id))


def create_tables():
    with app.app_context():
        db.create_all()
        if not User.query.filter_by(username='admin').first():
            admin = User(
                username='admin',
                email='nagarkotikrishna1101.com',
                password_hash=generate_password_hash('admin123'),
                is_admin=True
            )
            db.session.add(admin)
            db.session.commit()
            print("✅ Default admin created.")


# ------------------ AUTH ROUTES ------------------ #
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username'].strip()
        password = request.form['password'].strip()

        user = User.query.filter_by(username=username).first()
        if user and check_password_hash(user.password_hash, password):
            login_user(user)
            next_page = request.args.get('next') or (
                url_for('admin_dashboard') if user.is_admin else url_for('user_home')
            )
            return redirect(next_page)
        flash('Invalid username or password.', 'danger')
    return render_template('login.html')


@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('login'))


@app.route('/')
@login_required
def root_redirect():
    return redirect(url_for('admin_dashboard' if current_user.is_admin else 'user_home'))


# ------------------ ADMIN ROUTES ------------------ #
@app.route('/admin')
@login_required
def admin_dashboard():
    if not current_user.is_admin:
        flash('Access denied.', 'danger')
        return redirect(url_for('view_books'))

    total_books = Book.query.count()
    total_copies = db.session.query(db.func.sum(Book.copies)).scalar() or 0
    borrowed_books = Borrow.query.filter_by(returned_at=None).count()
    available_books = max(total_copies - borrowed_books, 0)

    books = Book.query.all()
    borrows = Borrow.query.order_by(Borrow.borrowed_at.desc()).all()

    return render_template(
        'admin_dashboard.html',
        total_books=total_books,
        borrowed_books=borrowed_books,
        available_books=available_books,
        books=books,
        borrows=borrows
    )


@app.route('/admin/user/<int:user_id>/history')
@login_required
def admin_view_user_history(user_id):
    if not current_user.is_admin:
        flash('Access denied.', 'danger')
        return redirect(url_for('view_books'))

    user = User.query.get_or_404(user_id)
    days = int(request.args.get('days', 7))
    cutoff = datetime.utcnow() - timedelta(days=days)

    borrows = Borrow.query.filter_by(user_id=user_id).order_by(Borrow.borrowed_at.desc()).all()

    recent_borrows = (
        Borrow.query.join(Book, Borrow.book_id == Book.id)
        .filter(Borrow.user_id == user_id, Borrow.borrowed_at >= cutoff)
        .all()
    )

    category_counts = Counter(b.category or "Uncategorized" for b in [r.book for r in recent_borrows])
    categories = list(category_counts.keys())
    counts = list(category_counts.values()) if categories else []

    return render_template(
        'user_history.html',
        borrows=borrows,
        user=user,
        categories=categories,
        counts=counts,
        selected_days=days
    )


@app.route('/admin/books')
@login_required
def manage_books():
    if not current_user.is_admin:
        flash('Access denied.', 'danger')
        return redirect(url_for('view_books'))
    books = Book.query.all()
    return render_template('manage_books.html', books=books)


@app.route('/admin/books/add', methods=['GET', 'POST'])
@login_required
def add_book():
    if not current_user.is_admin:
        flash('Access denied.', 'danger')
        return redirect(url_for('view_books'))

    if request.method == 'POST':
        try:
            title = request.form['title']
            author = request.form['author']
            category = request.form['category']
            isbn = request.form['isbn']
            copies = int(request.form.get('copies', 1))
            book = Book(title=title, author=author, category=category, isbn=isbn, copies=copies)
            db.session.add(book)
            db.session.commit()
            flash('Book added successfully.', 'success')
        except Exception as e:
            db.session.rollback()
            flash(f'Error adding book: {str(e)}', 'danger')
        return redirect(url_for('manage_books'))

    return render_template('edit_book.html', action='Add')


@app.route('/admin/books/edit/<int:book_id>', methods=['GET', 'POST'])
@login_required
def edit_book(book_id):
    if not current_user.is_admin:
        flash('Access denied.', 'danger')
        return redirect(url_for('view_books'))

    book = Book.query.get_or_404(book_id)
    if request.method == 'POST':
        try:
            book.title = request.form['title']
            book.author = request.form['author']
            book.category = request.form['category']
            book.isbn = request.form['isbn']
            book.copies = int(request.form.get('copies', 1))
            db.session.commit()
            flash('Book updated successfully.', 'success')
        except Exception as e:
            db.session.rollback()
            flash(f'Error updating book: {str(e)}', 'danger')
        return redirect(url_for('manage_books'))

    return render_template('edit_book.html', action='Edit', book=book)


@app.route('/admin/books/delete/<int:book_id>', methods=['POST'])
@login_required
def delete_book(book_id):
    if not current_user.is_admin:
        flash('Access denied.', 'danger')
        return redirect(url_for('view_books'))

    book = Book.query.get_or_404(book_id)
    try:
        db.session.delete(book)
        db.session.commit()
        flash('Book deleted successfully.', 'info')
    except Exception as e:
        db.session.rollback()
        flash(f'Error deleting book: {str(e)}', 'danger')
    return redirect(url_for('manage_books'))


@app.route('/admin/users')
@login_required
def manage_users():
    if not current_user.is_admin:
        flash('Access denied.', 'danger')
        return redirect(url_for('view_books'))
    users = User.query.all()
    return render_template('manage_users.html', users=users)


@app.route('/admin/users/add', methods=['POST'])
@login_required
def add_user():
    if not current_user.is_admin:
        flash('Access denied.', 'danger')
        return redirect(url_for('view_books'))

    username = request.form['username']
    email = request.form['email']
    password = request.form['password']

    if User.query.filter((User.username == username) | (User.email == email)).first():
        flash('Username or Email already exists.', 'danger')
        return redirect(url_for('manage_users'))

    user = User(username=username, email=email, password_hash=generate_password_hash(password))
    db.session.add(user)
    db.session.commit()
    flash('User added successfully.', 'success')
    return redirect(url_for('manage_users'))


@app.route('/admin/users/delete/<int:user_id>')
@login_required
def delete_user(user_id):
    if not current_user.is_admin:
        flash('Access denied.', 'danger')
        return redirect(url_for('view_books'))

    user = User.query.get_or_404(user_id)
    if user.is_admin:
        flash('Cannot delete admin users.', 'warning')
        return redirect(url_for('manage_users'))

    Borrow.query.filter_by(user_id=user.id).delete()
    db.session.delete(user)
    db.session.commit()
    flash(f'User "{user.username}" deleted.', 'info')
    return redirect(url_for('manage_users'))


# ------------------ USER ROUTES ------------------ #
@app.route('/books')
@login_required
def view_books():
    books = Book.query.all()
    return render_template('books.html', books=books)


@app.route('/home')
@login_required
def user_home():
    three_days_ago = datetime.utcnow() - timedelta(days=2)
    recent_books = Book.query.filter(Book.created_at >= three_days_ago).order_by(Book.created_at.desc()).limit(8).all()

    borrowed_books = (
        Borrow.query.join(Book, Borrow.book_id == Book.id)
        .filter(Borrow.user_id == current_user.id)
        .with_entities(Book.category, Book.id)
        .all()
    )

    categories = [b.category for b in borrowed_books if b.category]
    borrowed_ids = [b.id for b in borrowed_books]
    recommended_books = []

    if categories:
        recommended_books = (
            Book.query.filter(Book.category.in_(categories), Book.id.notin_(borrowed_ids))
            .order_by(db.func.rand())
            .limit(8)
            .all()
        )

    if not recommended_books:
        recommended_books = Book.query.order_by(db.func.rand()).limit(8).all()

    return render_template('home.html', recent_books=recent_books, recommended_books=recommended_books)


@app.route('/borrow/<int:book_id>', methods=['POST'])
@login_required
def borrow_book(book_id):
    if current_user.is_admin:
        flash("Admins cannot borrow books.", "warning")
        return redirect(url_for("admin_dashboard"))

    book = Book.query.get_or_404(book_id)
    borrowed_count = Borrow.query.filter_by(book_id=book.id, returned_at=None).count()

    if borrowed_count >= book.copies:
        flash('No copies available right now.', 'warning')
        return redirect(request.referrer or url_for('view_books'))

    borrow = Borrow(
        user_id=current_user.id,
        book_id=book.id,
        due_date=datetime.utcnow() + timedelta(days=14)
    )

    db.session.add(borrow)
    db.session.commit()

    flash(
        f'You borrowed "{book.title}". Due date: {borrow.due_date.strftime("%Y-%m-%d")}',
        "success"
    )

    # ✅ Redirect back to the page where the user came from
    return redirect(request.referrer or url_for('user_home'))



@app.route('/return/<int:borrow_id>', methods=['POST'])
@login_required
def return_book(borrow_id):
    borrow = Borrow.query.get_or_404(borrow_id)

    # Only the actual user can return (admins are not allowed)
    if borrow.user_id != current_user.id:
        flash('Not allowed.', 'danger')
        return redirect(url_for('user_history'))

    # Set returned time
    borrow.returned_at = datetime.utcnow()

    # If due_date is missing (old records), set a sensible default
    if not borrow.due_date:
        borrow.due_date = borrow.borrowed_at + timedelta(days=14)

    # Late fee calculation (₹10 per day)
    if borrow.returned_at > borrow.due_date:
        days_late = (borrow.returned_at - borrow.due_date).days
        borrow.late_fee = max(0, days_late * 10)
        flash(f'Returned late by {days_late} days. Late fee: ₹{borrow.late_fee}', 'warning')
    else:
        borrow.late_fee = 0
        flash('Book returned successfully.', 'info')

    db.session.commit()
    return redirect(url_for('user_history'))

@app.route('/history')
@login_required
def user_history():
    borrows = Borrow.query.filter_by(user_id=current_user.id).order_by(Borrow.borrowed_at.desc()).all()
    return render_template('user_history.html', borrows=borrows)

# ------------------ REGISTER & PASSWORD RESET (with OTP) ------------------ #
@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form['username']
        email = request.form['email']
        password = request.form['password']

        if User.query.filter((User.username == username) | (User.email == email)).first():
            flash('Username or Email already exists.', 'danger')
            return redirect(url_for('register'))

        user = User(username=username, email=email, password_hash=generate_password_hash(password))
        db.session.add(user)
        db.session.commit()
        return redirect(url_for('login'))
    return render_template('register.html')

@app.route('/forgot_password', methods=['GET', 'POST'])
def forgot_password():
    if request.method == 'POST':
        email = request.form['email'].strip()
        user = User.query.filter_by(email=email).first()

        if not user:
            flash('Email not found.', 'danger')
            return redirect(url_for('forgot_password'))

        otp = randint(100000, 999999)
        expiry = datetime.utcnow() + timedelta(minutes=5)
        otp_store[email] = {'otp': otp, 'expiry': expiry}

        sent = send_otp_email(email, otp)
        if not sent:
            flash('Failed to send OTP email. Please try again later.', 'danger')
            otp_store.pop(email, None)
            return redirect(url_for('forgot_password'))
        return redirect(url_for('verify_otp', email=email))

    return render_template('forgot_password.html')

@app.route('/verify_otp/<email>', methods=['GET', 'POST'])
def verify_otp(email):
    if request.method == 'POST':
        entered_otp = request.form['otp'].strip()
        record = otp_store.get(email)

        if not record:
            flash('No OTP found for this email. Please try again.', 'danger')
            return redirect(url_for('forgot_password'))

        if datetime.utcnow() > record['expiry']:
            otp_store.pop(email, None)
            flash('OTP expired. Please request a new one.', 'warning')
            return redirect(url_for('forgot_password'))

        if str(record['otp']) != entered_otp:
            flash('Invalid OTP. Please try again.', 'danger')
            return redirect(url_for('verify_otp', email=email))

        otp_store.pop(email, None)
        return redirect(url_for('change_password', email=email))

    return render_template('verify_otp.html', email=email)

@app.route('/change_password/<email>', methods=['GET', 'POST'])
def change_password(email):
    if request.method == 'POST':
        new_password = request.form['password'].strip()
        user = User.query.filter_by(email=email).first()

        if not user:
            flash('User not found.', 'danger')
            return redirect(url_for('forgot_password'))

        user.password_hash = generate_password_hash(new_password)
        db.session.commit()
        return redirect(url_for('login'))

    return render_template('change_password.html', email=email)

# ------------------ EMAIL FUNCTION ------------------ #
def send_otp_email(to_email, otp):
    """
    Smart email sender:
      - If EMAIL_BACKEND=console -> prints OTP to stdout (dev-friendly)
      - If EMAIL_BACKEND=smtp -> sends OTP using SMTP creds from env
    """
    backend = os.getenv('EMAIL_BACKEND', 'console').lower()

    if backend == 'console':
        # Friendly console output for local testing
        print(f"🔔 [DEV MODE] OTP for {to_email}: {otp} (expires in 5 minutes)")
        return True

    # else: use SMTP
    sender_email = os.getenv('SMTP_EMAIL')
    sender_password = os.getenv('SMTP_PASS')
    smtp_host = os.getenv('SMTP_HOST', 'smtp.gmail.com')
    smtp_port = int(os.getenv('SMTP_PORT', 465))

    if not (sender_email and sender_password):
        print("❌ SMTP credentials are not set. Set SMTP_EMAIL and SMTP_PASS or use EMAIL_BACKEND=console.")
        return False

    msg = MIMEText(f"Your Library Hub OTP is: {otp}\n\nThis OTP will expire in 5 minutes.")
    msg['Subject'] = 'Library Hub Password Reset OTP'
    msg['From'] = sender_email
    msg['To'] = to_email

    try:
        # Use SSL for Gmail by default, fallback if port is not SSL
        with smtplib.SMTP_SSL(smtp_host, smtp_port) as server:
            server.login(sender_email, sender_password)
            server.send_message(msg)
        print("✅ OTP sent successfully via SMTP.")
        return True
    except Exception as e:
        print("❌ Failed to send OTP email via SMTP:", e)
        return False

from flask import Response

@app.route("/admin/download_recent_borrows")
@login_required
def download_recent_borrows():
    if not current_user.is_admin:
        return redirect(url_for("user_home"))
    borrows = Borrow.query.order_by(Borrow.borrowed_at.desc()).all()
    output = StringIO()
    writer = csv.writer(output)
    writer.writerow(["Book Title", "User", "Borrowed At", "Returned At"])
    for b in borrows:
        writer.writerow([
            b.book.title,
            b.user.username,
            b.borrowed_at.strftime("%Y-%m-%d"),
            b.returned_at.strftime("%Y-%m-%d") if b.returned_at else "Not Returned"
        ])
    output.seek(0)
    return Response(
        output.getvalue(),
        mimetype="text/csv",
        headers={"Content-Disposition": "attachment; filename=recent_borrows.csv"}
    )

# ------------------ MAIN ------------------ #
if __name__ == '__main__':
    create_tables()
    app.run(debug=True)
