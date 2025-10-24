from flask import Flask, render_template, request, redirect, url_for, flash, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, UserMixin, login_user, login_required, logout_user, current_user
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime, timedelta
import os

app = Flask(__name__)
app.config['SECRET_KEY'] = 'dev-secret-key-change-in-production'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///library_hub.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['WTF_CSRF_ENABLED'] = True

# Initialize extensions
db = SQLAlchemy(app)
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'
login_manager.login_message = 'Please log in to access this page.'

# Models
class User(UserMixin, db.Model):
    __tablename__ = 'users'
    
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(128), nullable=False)
    role = db.Column(db.String(20), default='user')
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    is_active = db.Column(db.Boolean, default=True)
    
    def __repr__(self):
        return f'<User {self.username}>'

class Book(db.Model):
    __tablename__ = 'books'
    
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(200), nullable=False)
    author = db.Column(db.String(200), nullable=False)
    isbn = db.Column(db.String(20), unique=True)
    category = db.Column(db.String(100))
    description = db.Column(db.Text)
    total_copies = db.Column(db.Integer, default=1)
    available_copies = db.Column(db.Integer, default=1)
    published_year = db.Column(db.Integer)
    publisher = db.Column(db.String(200))
    language = db.Column(db.String(50), default='English')
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    def __repr__(self):
        return f'<Book {self.title}>'

class Transaction(db.Model):
    __tablename__ = 'transactions'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    book_id = db.Column(db.Integer, db.ForeignKey('books.id'), nullable=False)
    borrow_date = db.Column(db.DateTime, nullable=False)
    due_date = db.Column(db.DateTime, nullable=False)
    return_date = db.Column(db.DateTime)
    status = db.Column(db.String(20), default='borrowed')
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    def __repr__(self):
        return f'<Transaction {self.id}>'

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

@app.route('/')
def index():
    if current_user.is_authenticated:
        return redirect(url_for('dashboard'))
    return render_template('index.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('dashboard'))
    
    if request.method == 'POST':
        data = request.get_json() if request.is_json else request.form
        email = data.get('email')
        password = data.get('password')
        
        user = User.query.filter_by(email=email).first()
        
        if user and check_password_hash(user.password_hash, password):
            if not user.is_active:
                flash('Your account has been deactivated.', 'error')
                return redirect(url_for('login'))
            
            login_user(user, remember=True)
            next_page = request.args.get('next')
            
            if request.is_json:
                return {'success': True, 'redirect': next_page or url_for('dashboard')}
            
            return redirect(next_page) if next_page else redirect(url_for('dashboard'))
        else:
            if request.is_json:
                return {'success': False, 'message': 'Invalid email or password'}
            flash('Invalid email or password', 'error')
    
    return render_template('login.html')

@app.route('/register', methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('dashboard'))
    
    if request.method == 'POST':
        data = request.get_json() if request.is_json else request.form
        username = data.get('username')
        email = data.get('email')
        password = data.get('password')
        confirm_password = data.get('confirm_password')
        
        if not username or not email or not password:
            if request.is_json:
                return {'success': False, 'message': 'All fields are required'}
            flash('All fields are required', 'error')
            return render_template('register.html')
        
        if password != confirm_password:
            if request.is_json:
                return {'success': False, 'message': 'Passwords do not match'}
            flash('Passwords do not match', 'error')
            return render_template('register.html')
        
        if len(password) < 6:
            if request.is_json:
                return {'success': False, 'message': 'Password must be at least 6 characters long'}
            flash('Password must be at least 6 characters long', 'error')
            return render_template('register.html')
        
        if User.query.filter_by(username=username).first():
            if request.is_json:
                return {'success': False, 'message': 'Username already exists'}
            flash('Username already exists', 'error')
            return render_template('register.html')
        
        if User.query.filter_by(email=email).first():
            if request.is_json:
                return {'success': False, 'message': 'Email already registered'}
            flash('Email already registered', 'error')
            return render_template('register.html')
        
        user = User(
            username=username,
            email=email,
            password_hash=generate_password_hash(password)
        )
        
        db.session.add(user)
        db.session.commit()
        
        if request.is_json:
            return {'success': True, 'message': 'Registration successful! Please log in.'}
        
        flash('Registration successful! Please log in.', 'success')
        return redirect(url_for('login'))
    
    return render_template('register.html')

@app.route('/logout')
@login_required
def logout():
    logout_user()
    flash('You have been logged out successfully.', 'info')
    return redirect(url_for('index'))

@app.route('/dashboard')
@login_required
def dashboard():
    recent_books = Book.query.order_by(Book.created_at.desc()).limit(6).all()
    user_books = Transaction.query.filter_by(user_id=current_user.id, status='borrowed').all()
    
    return render_template('dashboard.html', 
                         recent_books=recent_books, 
                         user_books=user_books)

@app.route('/books')
@login_required
def books():
    page = request.args.get('page', 1, type=int)
    search = request.args.get('search', '', type=str)
    category = request.args.get('category', '', type=str)
    
    query = Book.query
    
    if search:
        query = query.filter(Book.title.contains(search) | Book.author.contains(search))
    
    if category:
        query = query.filter(Book.category == category)
    
    books = query.paginate(
        page=page, per_page=12, error_out=False
    )
    
    categories = db.session.query(Book.category).distinct().all()
    categories = [cat[0] for cat in categories if cat[0]]
    
    return render_template('books.html', books=books, categories=categories)

@app.route('/book/<int:book_id>')
@login_required
def book_detail(book_id):
    book = Book.query.get_or_404(book_id)
    is_borrowed = Transaction.query.filter_by(
        user_id=current_user.id, 
        book_id=book_id, 
        status='borrowed'
    ).first() is not None
    
    return render_template('book_detail.html', book=book, is_borrowed=is_borrowed)

@app.route('/borrow/<int:book_id>', methods=['POST'])
@login_required
def borrow_book(book_id):
    book = Book.query.get_or_404(book_id)
    
    if book.available_copies <= 0:
        flash('This book is currently not available.', 'error')
        return redirect(url_for('book_detail', book_id=book_id))
    
    existing_borrow = Transaction.query.filter_by(
        user_id=current_user.id, 
        book_id=book_id, 
        status='borrowed'
    ).first()
    
    if existing_borrow:
        flash('You have already borrowed this book.', 'error')
        return redirect(url_for('book_detail', book_id=book_id))
    
    transaction = Transaction(
        user_id=current_user.id,
        book_id=book_id,
        borrow_date=datetime.utcnow(),
        due_date=datetime.utcnow() + timedelta(days=14),
        status='borrowed'
    )
    
    book.available_copies -= 1
    
    db.session.add(transaction)
    db.session.commit()
    
    flash('Book borrowed successfully!', 'success')
    return redirect(url_for('book_detail', book_id=book_id))

@app.route('/return/<int:book_id>', methods=['POST'])
@login_required
def return_book(book_id):
    transaction = Transaction.query.filter_by(
        user_id=current_user.id, 
        book_id=book_id, 
        status='borrowed'
    ).first()
    
    if not transaction:
        flash('You have not borrowed this book.', 'error')
        return redirect(url_for('book_detail', book_id=book_id))
    
    transaction.status = 'returned'
    transaction.return_date = datetime.utcnow()
    
    book = Book.query.get(book_id)
    book.available_copies += 1
    
    db.session.commit()
    
    flash('Book returned successfully!', 'success')
    return redirect(url_for('book_detail', book_id=book_id))

@app.route('/api/stats')
def api_stats():
    total_books = Book.query.count()
    total_users = User.query.count()
    books_borrowed = Transaction.query.filter_by(status='borrowed').count()
    categories = db.session.query(Book.category).distinct().count()
    
    return jsonify({
        'total_books': total_books,
        'total_users': total_users,
        'books_borrowed': books_borrowed,
        'categories': categories
    })

@app.route('/admin')
@login_required
def admin_dashboard():
    if current_user.role != 'admin':
        flash('Admin access required.', 'error')
        return redirect(url_for('index'))
    
    total_users = User.query.count()
    total_books = Book.query.count()
    total_transactions = Transaction.query.count()
    active_borrows = Transaction.query.filter_by(status='borrowed').count()
    
    recent_transactions = Transaction.query.order_by(Transaction.created_at.desc()).limit(10).all()
    overdue_transactions = Transaction.query.filter(
        Transaction.status == 'borrowed',
        Transaction.due_date < datetime.utcnow()
    ).all()
    
    return render_template('admin/dashboard.html',
                         total_users=total_users,
                         total_books=total_books,
                         total_transactions=total_transactions,
                         active_borrows=active_borrows,
                         recent_transactions=recent_transactions,
                         overdue_transactions=overdue_transactions)

@app.route('/admin/books')
@login_required
def admin_books():
    if current_user.role != 'admin':
        flash('Admin access required.', 'error')
        return redirect(url_for('index'))
    
    page = request.args.get('page', 1, type=int)
    search = request.args.get('search', '', type=str)
    
    query = Book.query
    
    if search:
        query = query.filter(Book.title.contains(search) | Book.author.contains(search))
    
    books = query.paginate(
        page=page, per_page=20, error_out=False
    )
    
    return render_template('admin/books.html', books=books)

@app.route('/admin/books/add', methods=['GET', 'POST'])
@login_required
def admin_add_book():
    if current_user.role != 'admin':
        flash('Admin access required.', 'error')
        return redirect(url_for('index'))
    
    if request.method == 'POST':
        data = request.get_json() if request.is_json else request.form
        
        book = Book(
            title=data.get('title'),
            author=data.get('author'),
            isbn=data.get('isbn'),
            category=data.get('category'),
            description=data.get('description'),
            total_copies=int(data.get('total_copies', 1)),
            available_copies=int(data.get('total_copies', 1)),
            published_year=int(data.get('published_year')) if data.get('published_year') else None,
            publisher=data.get('publisher'),
            language=data.get('language', 'English')
        )
        
        db.session.add(book)
        db.session.commit()
        
        if request.is_json:
            return jsonify({'success': True, 'message': 'Book added successfully!'})
        
        flash('Book added successfully!', 'success')
        return redirect(url_for('admin_books'))
    
    return render_template('admin/add_book.html')

@app.route('/admin/users')
@login_required
def admin_users():
    if current_user.role != 'admin':
        flash('Admin access required.', 'error')
        return redirect(url_for('index'))
    
    page = request.args.get('page', 1, type=int)
    search = request.args.get('search', '', type=str)
    
    query = User.query
    
    if search:
        query = query.filter(User.username.contains(search) | User.email.contains(search))
    
    users = query.paginate(
        page=page, per_page=20, error_out=False
    )
    
    return render_template('admin/users.html', users=users)

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
        
        # Create admin user if it doesn't exist
        admin = User.query.filter_by(email='admin@library.com').first()
        if not admin:
            admin = User(
                username='admin',
                email='admin@library.com',
                password_hash=generate_password_hash('admin123'),
                role='admin'
            )
            db.session.add(admin)
            db.session.commit()
            print("Admin user created: admin@library.com / admin123")
        
        # Add sample books if none exist
        if Book.query.count() == 0:
            sample_books = [
                {
                    'title': 'The Great Gatsby',
                    'author': 'F. Scott Fitzgerald',
                    'isbn': '9780743273565',
                    'category': 'Literature',
                    'description': 'A classic American novel set in the Jazz Age.',
                    'total_copies': 3,
                    'available_copies': 3,
                    'published_year': 1925,
                    'publisher': 'Scribner',
                    'language': 'English'
                },
                {
                    'title': 'To Kill a Mockingbird',
                    'author': 'Harper Lee',
                    'isbn': '9780061120084',
                    'category': 'Literature',
                    'description': 'A gripping tale of racial injustice and childhood innocence.',
                    'total_copies': 2,
                    'available_copies': 2,
                    'published_year': 1960,
                    'publisher': 'J.B. Lippincott & Co.',
                    'language': 'English'
                },
                {
                    'title': '1984',
                    'author': 'George Orwell',
                    'isbn': '9780451524935',
                    'category': 'Fiction',
                    'description': 'A dystopian social science fiction novel.',
                    'total_copies': 4,
                    'available_copies': 4,
                    'published_year': 1949,
                    'publisher': 'Secker & Warburg',
                    'language': 'English'
                },
                {
                    'title': 'Pride and Prejudice',
                    'author': 'Jane Austen',
                    'isbn': '9780141439518',
                    'category': 'Literature',
                    'description': 'A romantic novel of manners written by Jane Austen.',
                    'total_copies': 2,
                    'available_copies': 2,
                    'published_year': 1813,
                    'publisher': 'T. Egerton, Whitehall',
                    'language': 'English'
                },
                {
                    'title': 'The Catcher in the Rye',
                    'author': 'J.D. Salinger',
                    'isbn': '9780316769174',
                    'category': 'Literature',
                    'description': 'A coming-of-age story about teenage rebellion.',
                    'total_copies': 3,
                    'available_copies': 3,
                    'published_year': 1951,
                    'publisher': 'Little, Brown and Company',
                    'language': 'English'
                }
            ]
            
            for book_data in sample_books:
                book = Book(**book_data)
                db.session.add(book)
            
            db.session.commit()
            print(f"Added {len(sample_books)} sample books")
    
    print("="*60)
    print("LIBRARY RESOURCE HUB - READY TO USE")
    print("="*60)
    print("Admin Login: admin@library.com / admin123")
    print("Application running at: http://localhost:5000")
    print("="*60)
    
    app.run(debug=True, host='0.0.0.0', port=5000)