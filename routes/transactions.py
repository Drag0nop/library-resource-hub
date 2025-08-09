# routes/transactions.py - Transaction Management Routes
from flask import Blueprint, render_template, request, redirect, url_for, flash, session
from models.database import get_db_connection
from utils.validators import calculate_fine
from datetime import datetime, timedelta

transactions_bp = Blueprint('transactions', __name__)

def require_login():
    if 'user_id' not in session:
        flash('Please log in to access this page.', 'error')
        return redirect(url_for('auth.login'))
    return None

@transactions_bp.route('/')
def list_transactions():
    redirect_response = require_login()
    if redirect_response:
        return redirect_response
    
    conn = get_db_connection()
    transactions = conn.execute('''
        SELECT t.*, b.title as book_title, b.author, m.name as member_name
        FROM transactions t
        JOIN books b ON t.book_id = b.id
        JOIN members m ON t.member_id = m.id
        ORDER BY t.issue_date DESC
    ''').fetchall()
    conn.close()
    return render_template('transactions/list.html', transactions=transactions)

@transactions_bp.route('/issue', methods=['GET', 'POST'])
def issue_book():
    redirect_response = require_login()
    if redirect_response:
        return redirect_response
    
    conn = get_db_connection()
    
    if request.method == 'POST':
        book_id = int(request.form['book_id'])
        member_id = int(request.form['member_id'])
        due_date = request.form['due_date']
        
        # Check if book is available
        book = conn.execute(
            'SELECT * FROM books WHERE id = ? AND available_copies > 0',
            (book_id,)
        ).fetchone()
        
        if not book:
            flash('Book is not available!', 'error')
        else:
            # Check if member is active
            member = conn.execute(
                'SELECT * FROM members WHERE id = ? AND is_active = 1',
                (member_id,)
            ).fetchone()
            
            if not member:
                flash('Member is not active!', 'error')
            else:
                # Issue the book
                conn.execute('''
                    INSERT INTO transactions (book_id, member_id, due_date)
                    VALUES (?, ?, ?)
                ''', (book_id, member_id, due_date))
                
                # Update available copies
                conn.execute(
                    'UPDATE books SET available_copies = available_copies - 1 WHERE id = ?',
                    (book_id,)
                )
                
                conn.commit()
                flash('Book issued successfully!', 'success')
                return redirect(url_for('transactions.list_transactions'))
    
    # Get available books and active members
    books = conn.execute(
        'SELECT * FROM books WHERE available_copies > 0 ORDER BY title'
    ).fetchall()
    
    members = conn.execute(
        'SELECT * FROM members WHERE is_active = 1 ORDER BY name'
    ).fetchall()
    
    conn.close()
    
    # Default due date (14 days from now)
    default_due_date = (datetime.now() + timedelta(days=14)).strftime('%Y-%m-%d')
    
    return render_template('transactions/issue.html', books=books, members=members, default_due_date=default_due_date)

@transactions_bp.route('/return/<int:transaction_id>')
def return_book(transaction_id):
    redirect_response = require_login()
    if redirect_response:
        return redirect_response
    
    conn = get_db_connection()
    
    # Get transaction details
    transaction = conn.execute(
        'SELECT * FROM transactions WHERE id = ? AND status = "issued"',
        (transaction_id,)
    ).fetchone()
    
    if not transaction:
        flash('Transaction not found or already returned!', 'error')
    else:
        # Calculate fine
        return_date = datetime.now().date()
        fine_amount = calculate_fine(transaction['due_date'], return_date)
        
        # Update transaction
        conn.execute('''
            UPDATE transactions 
            SET return_date = ?, fine_amount = ?, status = "returned"
            WHERE id = ?
        ''', (datetime.now(), fine_amount, transaction_id))
        
        # Update available copies
        conn.execute(
            'UPDATE books SET available_copies = available_copies + 1 WHERE id = ?',
            (transaction['book_id'],)
        )
        
        conn.commit()
        
        if fine_amount > 0:
            flash(f'Book returned successfully! Fine: ${fine_amount:.2f}', 'warning')
        else:
            flash('Book returned successfully!', 'success')
    
    conn.close()
    return redirect(url_for('transactions.list_transactions'))

@transactions_bp.route('/overdue')
def overdue_books():
    redirect_response = require_login()
    if redirect_response:
        return redirect_response
    
    conn = get_db_connection()
    overdue_transactions = conn.execute('''
        SELECT t.*, b.title as book_title, b.author, m.name as member_name, m.email
        FROM transactions t
        JOIN books b ON t.book_id = b.id
        JOIN members m ON t.member_id = m.id
        WHERE t.status = "issued" AND t.due_date < date('now')
        ORDER BY t.due_date
    ''').fetchall()
    
    # Calculate fines for overdue books
    overdue_with_fines = []
    for transaction in overdue_transactions:
        fine = calculate_fine(transaction['due_date'])
        overdue_with_fines.append({
            'transaction': transaction,
            'fine': fine
        })
    
    conn.close()
    return render_template('transactions/overdue.html', overdue_transactions=overdue_with_fines)
