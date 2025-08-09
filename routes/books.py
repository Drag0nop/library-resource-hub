# routes/books.py - Book Management Routes
from flask import Blueprint, render_template, request, redirect, url_for, flash, session
import sqlite3
from models.database import get_db_connection
from utils.validators import validate_isbn

books_bp = Blueprint('books', __name__)

def require_login():
    if 'user_id' not in session:
        flash('Please log in to access this page.', 'error')
        return redirect(url_for('auth.login'))
    return None

@books_bp.route('/')
def list_books():
    redirect_response = require_login()
    if redirect_response:
        return redirect_response
    
    conn = get_db_connection()
    books = conn.execute('SELECT * FROM books ORDER BY title').fetchall()
    conn.close()
    return render_template('books/list.html', books=books)

@books_bp.route('/add', methods=['GET', 'POST'])
def add_book():
    redirect_response = require_login()
    if redirect_response:
        return redirect_response
    
    if request.method == 'POST':
        title = request.form['title']
        author = request.form['author']
        isbn = request.form['isbn']
        category = request.form['category']
        total_copies = int(request.form['total_copies'])
        publication_year = request.form['publication_year']
        
        if isbn and not validate_isbn(isbn):
            flash('Invalid ISBN format!', 'error')
            return render_template('books/add.html')
        
        conn = get_db_connection()
        try:
            conn.execute('''
                INSERT INTO books (title, author, isbn, category, total_copies, 
                                 available_copies, publication_year)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            ''', (title, author, isbn, category, total_copies, total_copies, publication_year))
            conn.commit()
            flash('Book added successfully!', 'success')
            return redirect(url_for('books.list_books'))
        except sqlite3.IntegrityError:
            flash('ISBN already exists!', 'error')
        finally:
            conn.close()
    
    return render_template('books/add.html')

@books_bp.route('/edit/<int:book_id>', methods=['GET', 'POST'])
def edit_book(book_id):
    redirect_response = require_login()
    if redirect_response:
        return redirect_response
    
    conn = get_db_connection()
    
    if request.method == 'POST':
        title = request.form['title']
        author = request.form['author']
        isbn = request.form['isbn']
        category = request.form['category']
        total_copies = int(request.form['total_copies'])
        publication_year = request.form['publication_year']
        
        # Get current available copies
        current_book = conn.execute('SELECT * FROM books WHERE id = ?', (book_id,)).fetchone()
        issued_copies = current_book['total_copies'] - current_book['available_copies']
        available_copies = total_copies - issued_copies
        
        if available_copies < 0:
            flash('Cannot reduce total copies below issued copies!', 'error')
            book = current_book
        else:
            try:
                conn.execute('''
                    UPDATE books SET title = ?, author = ?, isbn = ?, category = ?,
                                   total_copies = ?, available_copies = ?, publication_year = ?
                    WHERE id = ?
                ''', (title, author, isbn, category, total_copies, available_copies, publication_year, book_id))
                conn.commit()
                flash('Book updated successfully!', 'success')
                return redirect(url_for('books.list_books'))
            except sqlite3.IntegrityError:
                flash('ISBN already exists!', 'error')
                book = current_book
    else:
        book = conn.execute('SELECT * FROM books WHERE id = ?', (book_id,)).fetchone()
    
    conn.close()
    return render_template('books/edit.html', book=book)

@books_bp.route('/delete/<int:book_id>')
def delete_book(book_id):
    redirect_response = require_login()
    if redirect_response:
        return redirect_response
    
    conn = get_db_connection()
    
    # Check if book has active transactions
    active_transactions = conn.execute(
        'SELECT COUNT(*) as count FROM transactions WHERE book_id = ? AND status = "issued"',
        (book_id,)
    ).fetchone()
    
    if active_transactions['count'] > 0:
        flash('Cannot delete book with active transactions!', 'error')
    else:
        conn.execute('DELETE FROM books WHERE id = ?', (book_id,))
        conn.commit()
        flash('Book deleted successfully!', 'success')
    
    conn.close()
    return redirect(url_for('books.list_books'))