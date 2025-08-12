from flask import Flask, render_template, request, redirect, url_for, session, jsonify, flash
from werkzeug.security import generate_password_hash, check_password_hash
import mysql.connector
import datetime
import config

app = Flask(__name__)
app.secret_key = config.SECRET_KEY

def get_db_connection():
    return mysql.connector.connect(
        host=config.MYSQL_HOST,
        user=config.MYSQL_USER,
        password=config.MYSQL_PASSWORD,
        database=config.MYSQL_DB
    )

def login_required(f):
    from functools import wraps
    @wraps(f)
    def decorated(*args, **kwargs):
        if 'user_id' not in session:
            return redirect(url_for('login'))
        return f(*args, **kwargs)
    return decorated

@app.route('/')
def home():
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    cursor.execute("SELECT COUNT(*) as total_books FROM books")
    total_books = cursor.fetchone()['total_books']
    cursor.execute("SELECT * FROM books")
    books = cursor.fetchall()
    cursor.close()
    conn.close()
    return render_template('home.html', total_books=total_books, books=books, username=session.get('username'))

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        data = request.form
        username = data.get('username').strip()
        password = data.get('password')
        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)
        cursor.execute("SELECT * FROM users WHERE username=%s", (username,))
        user = cursor.fetchone()
        cursor.close()
        conn.close()
        if user and check_password_hash(user['password_hash'], password):
            session['user_id'] = user['id']
            session['username'] = user['username']
            return redirect(url_for('home'))
        flash('Invalid username/password', 'error')
    return render_template('login.html')

@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('login'))

@app.route('/signup', methods=['GET', 'POST'])
def signup():
    if request.method == 'POST':
        data = request.form
        username = data.get('username').strip()
        email = data.get('email').strip()
        password = data.get('password')

        if not username or not email or not password:
            flash('Please fill all fields', 'error')
            return redirect(url_for('signup'))

        pw_hash = generate_password_hash(password)
        conn = get_db_connection()
        cursor = conn.cursor()
        try:
            cursor.execute("INSERT INTO users (username, email, password_hash) VALUES (%s,%s,%s)",
                           (username, email, pw_hash))
            conn.commit()
            flash('Signup successful — please log in', 'success')
            return redirect(url_for('login'))
        except mysql.connector.IntegrityError:
            flash('Username or email already exists', 'error')
            return redirect(url_for('signup'))
        finally:
            cursor.close()
            conn.close()
    return render_template('signup.html')

# ---------- API endpoints for frontend AJAX ----------

@app.route('/api/add_book', methods=['POST'])
@login_required
def api_add_book():
    data = request.get_json()
    title = data.get('title', '').strip()
    author = data.get('author', '').strip()
    qty = int(data.get('quantity') or 1)
    if not title or not author:
        return jsonify({'error': 'Missing fields'}), 400
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("INSERT INTO books (title, author, quantity) VALUES (%s,%s,%s)",
                   (title, author, qty))
    conn.commit()
    book_id = cursor.lastrowid
    cursor.close()
    conn.close()
    return jsonify({'success': True, 'book_id': book_id}), 201

@app.route('/api/delete_book/<int:book_id>', methods=['DELETE'])
@login_required
def api_delete_book(book_id):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM books WHERE id=%s", (book_id,))
    conn.commit()
    affected = cursor.rowcount
    cursor.close()
    conn.close()
    if affected:
        return jsonify({'success': True})
    return jsonify({'error': 'Book not found'}), 404

@app.route('/api/issue_book', methods=['POST'])
@login_required
def api_issue_book():
    data = request.get_json()
    book_id = int(data.get('book_id'))
    user_id = session['user_id']
    conn = get_db_connection()
    cursor = conn.cursor()
    # Check quantity
    cursor.execute("SELECT quantity FROM books WHERE id=%s", (book_id,))
    row = cursor.fetchone()
    if not row:
        cursor.close(); conn.close()
        return jsonify({'error': 'Book not found'}), 404
    qty = row[0]
    if qty <= 0:
        cursor.close(); conn.close()
        return jsonify({'error': 'No copies available'}), 400
    # Issue
    today = datetime.date.today()
    cursor.execute("INSERT INTO issued_books (user_id, book_id, issue_date) VALUES (%s,%s,%s)",
                   (user_id, book_id, today))
    cursor.execute("UPDATE books SET quantity = quantity - 1 WHERE id=%s", (book_id,))
    conn.commit()
    cursor.close()
    conn.close()
    return jsonify({'success': True}), 201

@app.route('/api/user_issued')
@login_required
def api_user_issued():
    user_id = session['user_id']
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    cursor.execute("""
        SELECT i.id as issue_id, b.id as book_id, b.title, b.author, i.issue_date, i.return_date
        FROM issued_books i
        JOIN books b ON i.book_id = b.id
        WHERE i.user_id=%s
        ORDER BY i.issue_date DESC
    """, (user_id,))
    rows = cursor.fetchall()
    cursor.close()
    conn.close()
    return jsonify({'issued': rows})

# convenience endpoint to list available books (quantity > 0)
@app.route('/api/available_books')
@login_required
def api_available_books():
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    cursor.execute("SELECT id, title, author, quantity FROM books WHERE quantity > 0 ORDER BY title")
    rows = cursor.fetchall()
    cursor.close()
    conn.close()
    return jsonify({'books': rows})

# ---------- Templates routes for pages that use JS ----------

@app.route('/add_book')
@login_required
def add_book_page():
    return render_template('add_book.html')

@app.route('/issue_book')
@login_required
def issue_book_page():
    return render_template('issue_book.html')

@app.route('/user_account')
@login_required
def user_account_page():
    return render_template('user_account.html')

if __name__ == '__main__':
    app.run(debug=True)
