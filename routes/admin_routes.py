from flask import Blueprint, render_template, request, jsonify, flash, redirect, url_for
from flask_login import login_required, current_user
from app import db
from models.user import User
from models.book import Book
from models.transaction import Transaction
from datetime import datetime, timedelta

admin_bp = Blueprint('admin', __name__)

def admin_required(f):
    """Decorator to require admin role"""
    from functools import wraps
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not current_user.is_authenticated or current_user.role != 'admin':
            flash('Admin access required.', 'error')
            return redirect(url_for('index'))
        return f(*args, **kwargs)
    return decorated_function

@admin_bp.route('/admin')
@login_required
@admin_required
def admin_dashboard():
    """Admin dashboard"""
    # Get statistics
    total_users = User.query.count()
    total_books = Book.query.count()
    total_transactions = Transaction.query.count()
    active_borrows = Transaction.query.filter_by(status='borrowed').count()
    
    # Get recent transactions
    recent_transactions = Transaction.query.order_by(Transaction.created_at.desc()).limit(10).all()
    
    # Get overdue books
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

@admin_bp.route('/admin/books')
@login_required
@admin_required
def admin_books():
    """Admin books management"""
    page = request.args.get('page', 1, type=int)
    search = request.args.get('search', '', type=str)
    
    query = Book.query
    
    if search:
        query = query.filter(Book.title.contains(search) | Book.author.contains(search))
    
    books = query.paginate(
        page=page, per_page=20, error_out=False
    )
    
    return render_template('admin/books.html', books=books)

@admin_bp.route('/admin/books/add', methods=['GET', 'POST'])
@login_required
@admin_required
def admin_add_book():
    """Add new book"""
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
        return redirect(url_for('admin.admin_books'))
    
    return render_template('admin/add_book.html')

@admin_bp.route('/admin/books/edit/<int:book_id>', methods=['GET', 'POST'])
@login_required
@admin_required
def admin_edit_book(book_id):
    """Edit book"""
    book = Book.query.get_or_404(book_id)
    
    if request.method == 'POST':
        data = request.get_json() if request.is_json else request.form
        
        book.title = data.get('title', book.title)
        book.author = data.get('author', book.author)
        book.isbn = data.get('isbn', book.isbn)
        book.category = data.get('category', book.category)
        book.description = data.get('description', book.description)
        book.published_year = int(data.get('published_year')) if data.get('published_year') else book.published_year
        book.publisher = data.get('publisher', book.publisher)
        book.language = data.get('language', book.language)
        
        # Update total copies and adjust available copies
        new_total = int(data.get('total_copies', book.total_copies))
        if new_total != book.total_copies:
            diff = new_total - book.total_copies
            book.total_copies = new_total
            book.available_copies = max(0, book.available_copies + diff)
        
        book.updated_at = datetime.utcnow()
        db.session.commit()
        
        if request.is_json:
            return jsonify({'success': True, 'message': 'Book updated successfully!'})
        
        flash('Book updated successfully!', 'success')
        return redirect(url_for('admin.admin_books'))
    
    return render_template('admin/edit_book.html', book=book)

@admin_bp.route('/admin/books/delete/<int:book_id>', methods=['POST'])
@login_required
@admin_required
def admin_delete_book(book_id):
    """Delete book"""
    book = Book.query.get_or_404(book_id)
    
    # Check if book has active transactions
    active_transactions = Transaction.query.filter_by(book_id=book_id, status='borrowed').count()
    if active_transactions > 0:
        if request.is_json:
            return jsonify({'success': False, 'message': 'Cannot delete book with active borrows'})
        flash('Cannot delete book with active borrows', 'error')
        return redirect(url_for('admin.admin_books'))
    
    db.session.delete(book)
    db.session.commit()
    
    if request.is_json:
        return jsonify({'success': True, 'message': 'Book deleted successfully!'})
    
    flash('Book deleted successfully!', 'success')
    return redirect(url_for('admin.admin_books'))

@admin_bp.route('/admin/users')
@login_required
@admin_required
def admin_users():
    """Admin users management"""
    page = request.args.get('page', 1, type=int)
    search = request.args.get('search', '', type=str)
    
    query = User.query
    
    if search:
        query = query.filter(User.username.contains(search) | User.email.contains(search))
    
    users = query.paginate(
        page=page, per_page=20, error_out=False
    )
    
    return render_template('admin/users.html', users=users)

@admin_bp.route('/admin/users/toggle/<int:user_id>', methods=['POST'])
@login_required
@admin_required
def admin_toggle_user(user_id):
    """Toggle user active status"""
    user = User.query.get_or_404(user_id)
    
    if user.id == current_user.id:
        if request.is_json:
            return jsonify({'success': False, 'message': 'Cannot deactivate your own account'})
        flash('Cannot deactivate your own account', 'error')
        return redirect(url_for('admin.admin_users'))
    
    user.is_active = not user.is_active
    db.session.commit()
    
    status = 'activated' if user.is_active else 'deactivated'
    if request.is_json:
        return jsonify({'success': True, 'message': f'User {status} successfully!'})
    
    flash(f'User {status} successfully!', 'success')
    return redirect(url_for('admin.admin_users'))

@admin_bp.route('/admin/transactions')
@login_required
@admin_required
def admin_transactions():
    """Admin transactions management"""
    page = request.args.get('page', 1, type=int)
    status_filter = request.args.get('status', '', type=str)
    
    query = Transaction.query
    
    if status_filter:
        query = query.filter(Transaction.status == status_filter)
    
    transactions = query.order_by(Transaction.created_at.desc()).paginate(
        page=page, per_page=20, error_out=False
    )
    
    return render_template('admin/transactions.html', transactions=transactions)