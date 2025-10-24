from flask import Flask, render_template, request, redirect, url_for, flash, jsonify, session
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, UserMixin, login_user, login_required, logout_user, current_user
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime, timedelta
import os

app = Flask(__name__)
app.config.from_object('config.Config')

# Initialize extensions
db = SQLAlchemy(app)
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'auth.login'
login_manager.login_message = 'Please log in to access this page.'

# Import models
from models.user import User
from models.book import Book
from models.transaction import Transaction

# Import routes
from routes.auth_routes import auth_bp
from routes.book_routes import book_bp
from routes.admin_routes import admin_bp

# Register blueprints
app.register_blueprint(auth_bp)
app.register_blueprint(book_bp)
app.register_blueprint(admin_bp)

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

@app.route('/')
def index():
    if current_user.is_authenticated:
        return redirect(url_for('dashboard'))
    return render_template('index.html')

@app.route('/dashboard')
@login_required
def dashboard():
    # Get recent books and user's borrowed books
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
    
    # Check if book is available
    if book.available_copies <= 0:
        flash('This book is currently not available.', 'error')
        return redirect(url_for('book_detail', book_id=book_id))
    
    # Check if user already borrowed this book
    existing_borrow = Transaction.query.filter_by(
        user_id=current_user.id, 
        book_id=book_id, 
        status='borrowed'
    ).first()
    
    if existing_borrow:
        flash('You have already borrowed this book.', 'error')
        return redirect(url_for('book_detail', book_id=book_id))
    
    # Create transaction
    transaction = Transaction(
        user_id=current_user.id,
        book_id=book_id,
        borrow_date=datetime.utcnow(),
        due_date=datetime.utcnow() + timedelta(days=14),
        status='borrowed'
    )
    
    # Update book availability
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
    
    # Update transaction
    transaction.status = 'returned'
    transaction.return_date = datetime.utcnow()
    
    # Update book availability
    book = Book.query.get(book_id)
    book.available_copies += 1
    
    db.session.commit()
    
    flash('Book returned successfully!', 'success')
    return redirect(url_for('book_detail', book_id=book_id))

@app.route('/api/stats')
def api_stats():
    """API endpoint for library statistics"""
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
    
    app.run(debug=True, host='0.0.0.0', port=5000)