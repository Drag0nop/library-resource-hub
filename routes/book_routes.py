from flask import Blueprint, render_template, request, jsonify, flash
from flask_login import login_required, current_user
from app import db
from models.book import Book
from models.transaction import Transaction

book_bp = Blueprint('books', __name__)

@book_bp.route('/api/books')
@login_required
def api_books():
    """API endpoint for books data"""
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
    
    return jsonify({
        'books': [book.to_dict() for book in books.items],
        'total': books.total,
        'pages': books.pages,
        'current_page': page,
        'has_next': books.has_next,
        'has_prev': books.has_prev
    })

@book_bp.route('/api/book/<int:book_id>')
@login_required
def api_book_detail(book_id):
    """API endpoint for single book details"""
    book = Book.query.get_or_404(book_id)
    return jsonify(book.to_dict())

@book_bp.route('/api/borrow/<int:book_id>', methods=['POST'])
@login_required
def api_borrow_book(book_id):
    """API endpoint to borrow a book"""
    book = Book.query.get_or_404(book_id)
    
    # Check if book is available
    if book.available_copies <= 0:
        return jsonify({'success': False, 'message': 'This book is currently not available.'})
    
    # Check if user already borrowed this book
    existing_borrow = Transaction.query.filter_by(
        user_id=current_user.id, 
        book_id=book_id, 
        status='borrowed'
    ).first()
    
    if existing_borrow:
        return jsonify({'success': False, 'message': 'You have already borrowed this book.'})
    
    # Create transaction
    from datetime import datetime, timedelta
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
    
    return jsonify({'success': True, 'message': 'Book borrowed successfully!'})

@book_bp.route('/api/return/<int:book_id>', methods=['POST'])
@login_required
def api_return_book(book_id):
    """API endpoint to return a book"""
    transaction = Transaction.query.filter_by(
        user_id=current_user.id, 
        book_id=book_id, 
        status='borrowed'
    ).first()
    
    if not transaction:
        return jsonify({'success': False, 'message': 'You have not borrowed this book.'})
    
    # Update transaction
    transaction.status = 'returned'
    transaction.return_date = datetime.utcnow()
    
    # Update book availability
    book = Book.query.get(book_id)
    book.available_copies += 1
    
    db.session.commit()
    
    return jsonify({'success': True, 'message': 'Book returned successfully!'})