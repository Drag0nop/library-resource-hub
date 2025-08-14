from flask import Flask, render_template, request, jsonify, session, redirect, url_for
from flask_mysqldb import MySQL
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime, timedelta
import MySQLdb.cursors
import os
import re

# Create Flask app
app = Flask(__name__)

# Configuration
app.config['MYSQL_HOST'] = os.environ.get('MYSQL_HOST', 'localhost')
app.config['MYSQL_USER'] = os.environ.get('MYSQL_USER', 'root')
app.config['MYSQL_PASSWORD'] = os.environ.get('MYSQL_PASSWORD', 'kn@g@rk0ti')
app.config['MYSQL_DB'] = os.environ.get('MYSQL_DB', 'library_management')
app.config['MYSQL_CURSORCLASS'] = 'DictCursor'
app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', 'your-secret-key-here-change-in-production')
app.config['PERMANENT_SESSION_LIFETIME'] = timedelta(hours=24)

# Initialize MySQL
mysql = MySQL(app)

# Helper function to check if user is logged in
def is_logged_in():
    return 'loggedin' in session

# Routes
@app.route('/')
def home():
    if is_logged_in():
        return redirect(url_for('dashboard'))
    return redirect(url_for('login'))

@app.route('/login')
def login():
    return render_template('login.html')

@app.route('/dashboard')
def dashboard():
    if not is_logged_in():
        return redirect(url_for('login'))
    return render_template('index.html')

@app.route('/api/login', methods=['POST'])
def api_login():
    try:
        data = request.get_json()
        username = data.get('username')
        password = data.get('password')
        remember = data.get('remember', False)
        
        if not username or not password:
            return jsonify({'success': False, 'message': 'Username and password required'})
        
        cursor = mysql.connection.cursor()
        cursor.execute('SELECT * FROM users WHERE username = %s OR email = %s', (username, username))
        user = cursor.fetchone()
        cursor.close()
        
        if user and check_password_hash(user['password'], password):
            session.permanent = remember
            session['loggedin'] = True
            session['user_id'] = user['id']
            session['username'] = user['username']
            session['email'] = user['email']
            session['role'] = user['role']
            
            return jsonify({
                'success': True, 
                'message': 'Login successful',
                'redirect': url_for('dashboard')
            })
        else:
            return jsonify({'success': False, 'message': 'Invalid username or password'})
            
    except Exception as e:
        return jsonify({'success': False, 'message': 'An error occurred during login'})

@app.route('/api/logout', methods=['POST'])
def api_logout():
    session.clear()
    return jsonify({'success': True, 'message': 'Logged out successfully'})

# Book Management APIs
@app.route('/api/books', methods=['GET'])
def get_books():
    if not is_logged_in():
        return jsonify({'success': False, 'message': 'Not authenticated'}), 401
    
    try:
        cursor = mysql.connection.cursor()
        cursor.execute('''
            SELECT b.*, 
                   CASE WHEN ib.id IS NOT NULL THEN 'issued' ELSE 'available' END as status
            FROM books b 
            LEFT JOIN issued_books ib ON b.id = ib.book_id AND ib.returned_date IS NULL
            ORDER BY b.created_at DESC
        ''')
        books = cursor.fetchall()
        cursor.close()
        
        return jsonify({'success': True, 'books': books})
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)})

@app.route('/api/books', methods=['POST'])
def add_book():
    if not is_logged_in():
        return jsonify({'success': False, 'message': 'Not authenticated'}), 401
    
    try:
        data = request.get_json()
        
        # Validate required fields
        required_fields = ['title', 'author']
        for field in required_fields:
            if not data.get(field):
                return jsonify({'success': False, 'message': f'{field.title()} is required'})
        
        cursor = mysql.connection.cursor()
        cursor.execute('''
            INSERT INTO books (title, author, isbn, category, publisher, publication_year, description, added_by)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
        ''', (
            data['title'],
            data['author'],
            data.get('isbn', ''),
            data.get('category', 'Other'),
            data.get('publisher', ''),
            data.get('year', None),
            data.get('description', ''),
            session['user_id']
        ))
        mysql.connection.commit()
        book_id = cursor.lastrowid
        cursor.close()
        
        # Update user stats
        update_user_stats(session['user_id'], 'books_added', 1)
        
        return jsonify({'success': True, 'message': 'Book added successfully', 'book_id': book_id})
        
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)})

@app.route('/api/books/<int:book_id>', methods=['DELETE'])
def delete_book(book_id):
    if not is_logged_in():
        return jsonify({'success': False, 'message': 'Not authenticated'}), 401
    
    try:
        cursor = mysql.connection.cursor()
        
        # Check if book is currently issued
        cursor.execute('SELECT * FROM issued_books WHERE book_id = %s AND returned_date IS NULL', (book_id,))
        if cursor.fetchone():
            cursor.close()
            return jsonify({'success': False, 'message': 'Cannot delete book that is currently issued'})
        
        # Delete the book
        cursor.execute('DELETE FROM books WHERE id = %s', (book_id,))
        mysql.connection.commit()
        cursor.close()
        
        # Update user stats
        update_user_stats(session['user_id'], 'books_deleted', 1)
        
        return jsonify({'success': True, 'message': 'Book deleted successfully'})
        
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)})

@app.route('/api/books/issue', methods=['POST'])
def issue_book():
    if not is_logged_in():
        return jsonify({'success': False, 'message': 'Not authenticated'}), 401
    
    try:
        data = request.get_json()
        
        # Validate required fields
        required_fields = ['member_name', 'member_email', 'book_id', 'issue_date', 'due_date']
        for field in required_fields:
            if not data.get(field):
                return jsonify({'success': False, 'message': f'{field.replace("_", " ").title()} is required'})
        
        cursor = mysql.connection.cursor()
        
        # Check if book is available
        cursor.execute('SELECT * FROM issued_books WHERE book_id = %s AND returned_date IS NULL', (data['book_id'],))
        if cursor.fetchone():
            cursor.close()
            return jsonify({'success': False, 'message': 'Book is already issued'})
        
        # Issue the book
        cursor.execute('''
            INSERT INTO issued_books (book_id, member_name, member_email, issue_date, due_date, issued_by)
            VALUES (%s, %s, %s, %s, %s, %s)
        ''', (
            data['book_id'],
            data['member_name'],
            data['member_email'],
            data['issue_date'],
            data['due_date'],
            session['user_id']
        ))
        mysql.connection.commit()
        cursor.close()
        
        # Update user stats
        update_user_stats(session['user_id'], 'books_issued', 1)
        
        return jsonify({'success': True, 'message': 'Book issued successfully'})
        
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)})

@app.route('/api/books/return/<int:issue_id>', methods=['POST'])
def return_book(issue_id):
    if not is_logged_in():
        return jsonify({'success': False, 'message': 'Not authenticated'}), 401
    
    try:
        cursor = mysql.connection.cursor()
        cursor.execute('''
            UPDATE issued_books 
            SET returned_date = %s 
            WHERE id = %s AND returned_date IS NULL
        ''', (datetime.now().date(), issue_id))
        mysql.connection.commit()
        cursor.close()
        
        return jsonify({'success': True, 'message': 'Book returned successfully'})
        
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)})

@app.route('/api/issued-books', methods=['GET'])
def get_issued_books():
    if not is_logged_in():
        return jsonify({'success': False, 'message': 'Not authenticated'}), 401
    
    try:
        cursor = mysql.connection.cursor()
        cursor.execute('''
            SELECT ib.*, b.title, b.author
            FROM issued_books ib
            JOIN books b ON ib.book_id = b.id
            WHERE ib.returned_date IS NULL
            ORDER BY ib.issue_date DESC
        ''')
        issued_books = cursor.fetchall()
        cursor.close()
        
        return jsonify({'success': True, 'issued_books': issued_books})
        
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)})

@app.route('/api/stats', methods=['GET'])
def get_stats():
    if not is_logged_in():
        return jsonify({'success': False, 'message': 'Not authenticated'}), 401
    
    try:
        cursor = mysql.connection.cursor()
        
        # Get total books
        cursor.execute('SELECT COUNT(*) as count FROM books')
        total_books = cursor.fetchone()['count']
        
        # Get issued books
        cursor.execute('SELECT COUNT(*) as count FROM issued_books WHERE returned_date IS NULL')
        issued_books = cursor.fetchone()['count']
        
        # Get available books
        available_books = total_books - issued_books
        
        # Get active members (unique members who have issued books)
        cursor.execute('SELECT COUNT(DISTINCT member_email) as count FROM issued_books')
        active_members = cursor.fetchone()['count']
        
        # Get user-specific stats
        cursor.execute('SELECT * FROM users WHERE id = %s', (session['user_id'],))
        user_stats = cursor.fetchone()
        
        cursor.close()
        
        return jsonify({
            'success': True,
            'stats': {
                'total_books': total_books,
                'issued_books': issued_books,
                'available_books': available_books,
                'active_members': active_members,
                'user_stats': {
                    'books_added': user_stats.get('books_added', 0),
                    'books_deleted': user_stats.get('books_deleted', 0),
                    'books_issued': user_stats.get('books_issued', 0)
                }
            }
        })
        
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)})

@app.route('/api/user-info', methods=['GET'])
def get_user_info():
    if not is_logged_in():
        return jsonify({'success': False, 'message': 'Not authenticated'}), 401
    
    return jsonify({
        'success': True,
        'user': {
            'username': session['username'],
            'email': session['email'],
            'role': session['role']
        }
    })

def update_user_stats(user_id, stat_type, increment=1):
    """Helper function to update user statistics"""
    try:
        cursor = mysql.connection.cursor()
        cursor.execute(f'''
            UPDATE users 
            SET {stat_type} = COALESCE({stat_type}, 0) + %s 
            WHERE id = %s
        ''', (increment, user_id))
        mysql.connection.commit()
        cursor.close()
    except Exception as e:
        print(f"Error updating user stats: {e}")

# Error handlers
@app.errorhandler(404)
def not_found(error):
    return jsonify({'success': False, 'message': 'Endpoint not found'}), 404

@app.errorhandler(500)
def internal_error(error):
    return jsonify({'success': False, 'message': 'Internal server error'}), 500

if __name__ == '__main__':
    app.run(debug=True)