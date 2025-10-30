from flask import Flask, render_template, request, redirect, url_for, flash
from models import db, User, Book, Borrow
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import LoginManager, login_user, login_required, logout_user, current_user

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///library.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SECRET_KEY'] = 'change-me-to-a-secure-random-value'

db.init_app(app)
login_manager = LoginManager()
login_manager.login_view = 'login'
login_manager.login_message = None
login_manager.init_app(app)

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

def create_tables():
    with app.app_context():
        db.create_all()
        if not User.query.filter_by(username='admin').first():
            admin = User(username='admin', password_hash=generate_password_hash('admin123'), is_admin=True)
            db.session.add(admin)
            db.session.commit()

# --- Authentication ---
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        user = User.query.filter_by(username=username).first()
        if user and check_password_hash(user.password_hash, password):
            flash('Logged in successfully.', 'success')
            login_user(user)
            next_page = request.args.get('next') or (url_for('admin_dashboard') if user.is_admin else url_for('view_books'))
            return redirect(next_page)
        flash('Invalid credentials.', 'danger')
    return render_template('login.html')

@app.route('/logout')
@login_required
def logout():
    # flash('Logged out.', 'info')
    logout_user()
    return redirect(url_for('login'))

# --- Home redirect ---
@app.route('/')
@login_required
def home():
    if current_user.is_admin:
        return redirect(url_for('admin_dashboard'))
    return redirect(url_for('view_books'))

# --- Admin Dashboard ---
@app.route('/admin')
@login_required
def admin_dashboard():
    if not current_user.is_admin:
        flash('Access denied.', 'danger')
        return redirect(url_for('view_books'))

    # --- Book Stats ---
    total_books = Book.query.count()
    total_copies = db.session.query(db.func.sum(Book.copies)).scalar() or 0
    borrowed_books = Borrow.query.filter_by(returned_at=None).count()
    available_books = total_copies - borrowed_books if total_copies > 0 else 0

    # --- For display ---
    books = Book.query.all()
    borrows = Borrow.query.order_by(Borrow.borrowed_at.desc()).all()

    return render_template(
        'admin_dashboard.html',
        total_books=total_copies,
        # total_copies=total_copies,
        borrowed_books=borrowed_books,
        available_books=available_books,
        books=books,
        borrows=borrows
    )

# --- Book Management ---
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
        title = request.form['title']
        author = request.form['author']
        isbn = request.form['isbn']
        copies = int(request.form.get('copies', 1))
        book = Book(title=title, author=author, isbn=isbn, copies=copies)
        db.session.add(book)
        db.session.commit()
        flash('Book added successfully.', 'success')
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
        book.title = request.form['title']
        book.author = request.form['author']
        book.isbn = request.form['isbn']
        book.copies = int(request.form.get('copies', 1))
        db.session.commit()
        flash('Book updated successfully.', 'success')
        return redirect(url_for('manage_books'))
    return render_template('edit_book.html', action='Edit', book=book)

@app.route('/admin/books/delete/<int:book_id>', methods=['POST'])
@login_required
def delete_book(book_id):
    if not current_user.is_admin:
        flash('Access denied.', 'danger')
        return redirect(url_for('view_books'))
    book = Book.query.get_or_404(book_id)
    db.session.delete(book)
    db.session.commit()
    flash('Book deleted.', 'info')
    return redirect(url_for('manage_books'))

# --- User Management ---
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
    password = request.form['password']
    if User.query.filter_by(username=username).first():
        flash('Username already exists.', 'danger')
        return redirect(url_for('manage_users'))
    user = User(username=username, password_hash=generate_password_hash(password), is_admin=False)
    db.session.add(user)
    db.session.commit()
    flash('User created successfully.', 'success')
    return redirect(url_for('manage_users'))

# --- Borrowing (User Only) ---
@app.route('/books')
@login_required
def view_books():
    books = Book.query.all()
    return render_template('books.html', books=books)

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
        return redirect(url_for('view_books'))

    borrow = Borrow(user_id=current_user.id, book_id=book.id)
    db.session.add(borrow)
    db.session.commit()
    flash(f'You borrowed "{book.title}".', 'success')
    return redirect(url_for('view_books'))

@app.route('/return/<int:borrow_id>', methods=['POST'])
@login_required
def return_book(borrow_id):
    borrow = Borrow.query.get_or_404(borrow_id)
    if borrow.user_id != current_user.id and not current_user.is_admin:
        flash('Not allowed.', 'danger')
        return redirect(url_for('view_books'))
    borrow.returned_at = db.func.current_timestamp()
    db.session.commit()
    flash('Book returned.', 'info')
    return redirect(url_for('home'))

# --- User History ---
@app.route('/history')
@login_required
def user_history():
    borrows = Borrow.query.filter_by(user_id=current_user.id).order_by(Borrow.borrowed_at.desc()).all()
    return render_template('user_history.html', borrows=borrows)

# --- Admin View User History ---
@app.route('/admin/user/<int:user_id>/history')
@login_required
def admin_user_history(user_id):
    if not current_user.is_admin:
        flash('Access denied.', 'danger')
        return redirect(url_for('view_books'))
    borrows = Borrow.query.filter_by(user_id=user_id).order_by(Borrow.borrowed_at.desc()).all()
    user = User.query.get_or_404(user_id)
    return render_template('user_history.html', borrows=borrows, user=user)

@app.route('/admin/users/delete/<int:user_id>')
@login_required
def delete_user(user_id):
    if not current_user.is_admin:
        flash('Access denied.', 'danger')
        return redirect(url_for('view_books'))

    user = User.query.get_or_404(user_id)

    # Prevent deleting admin accounts
    if user.is_admin:
        flash('Cannot delete admin users.', 'warning')
        return redirect(url_for('manage_users'))

    # Delete all borrow records for that user first (optional, to maintain integrity)
    Borrow.query.filter_by(user_id=user.id).delete()

    db.session.delete(user)
    db.session.commit()

    flash(f'User "{user.username}" has been deleted.', 'info')
    return redirect(url_for('manage_users'))

# --- User Registration ---
@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        # Check if user already exists
        if User.query.filter_by(username=username).first():
            flash('Username already exists.', 'danger')
            return redirect(url_for('register'))
        # Create new user (non-admin by default)
        user = User(username=username, password_hash=generate_password_hash(password), is_admin=False)
        db.session.add(user)
        db.session.commit()
        # flash('Registration successful! You can now login.', 'success')
        return redirect(url_for('login'))
    return render_template('register.html')

if __name__ == '__main__':
    create_tables()
    app.run(debug=True)
