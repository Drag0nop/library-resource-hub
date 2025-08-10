from flask import Flask, request, jsonify, render_template_string
from flask_cors import CORS
import mysql.connector
from datetime import datetime, timedelta
import os

app = Flask(__name__)
CORS(app)

# Database configuration
DB_CONFIG = {
    'host': 'localhost',
    'user': 'root',
    'password': 'your_password',  # Change this
    'database': 'library_db'
}

def get_db_connection():
    try:
        connection = mysql.connector.connect(**DB_CONFIG)
        return connection
    except mysql.connector.Error as err:
        print(f"Error: {err}")
        return None

# Initialize database tables
def init_database():
    connection = get_db_connection()
    if connection:
        cursor = connection.cursor()
        
        # Create books table
        cursor.execute('''
        CREATE TABLE IF NOT EXISTS books (
            id INT AUTO_INCREMENT PRIMARY KEY,
            title VARCHAR(255) NOT NULL,
            author VARCHAR(255) NOT NULL,
            isbn VARCHAR(20) UNIQUE,
            genre VARCHAR(100),
            publication_year INT,
            copies_available INT DEFAULT 1,
            total_copies INT DEFAULT 1,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
        ''')
        
        # Create members table
        cursor.execute('''
        CREATE TABLE IF NOT EXISTS members (
            id INT AUTO_INCREMENT PRIMARY KEY,
            name VARCHAR(255) NOT NULL,
            email VARCHAR(255) UNIQUE NOT NULL,
            phone VARCHAR(20),
            address TEXT,
            membership_date DATE DEFAULT (CURDATE()),
            status ENUM('active', 'inactive') DEFAULT 'active'
        )
        ''')
        
        # Create borrowings table
        cursor.execute('''
        CREATE TABLE IF NOT EXISTS borrowings (
            id INT AUTO_INCREMENT PRIMARY KEY,
            book_id INT,
            member_id INT,
            borrow_date DATE DEFAULT (CURDATE()),
            due_date DATE,
            return_date DATE NULL,
            status ENUM('borrowed', 'returned', 'overdue') DEFAULT 'borrowed',
            fine_amount DECIMAL(10,2) DEFAULT 0.00,
            FOREIGN KEY (book_id) REFERENCES books(id),
            FOREIGN KEY (member_id) REFERENCES members(id)
        )
        ''')
        
        connection.commit()
        cursor.close()
        connection.close()
        print("Database initialized successfully!")

# API Routes

@app.route('/')
def index():
    return render_template_string(open('frontend/index.html').read())

# Books endpoints
@app.route('/api/books', methods=['GET'])
def get_books():
    connection = get_db_connection()
    if not connection:
        return jsonify({'error': 'Database connection failed'}), 500
    
    cursor = connection.cursor(dictionary=True)
    cursor.execute('SELECT * FROM books ORDER BY title')
    books = cursor.fetchall()
    cursor.close()
    connection.close()
    
    return jsonify(books)

@app.route('/api/books', methods=['POST'])
def add_book():
    data = request.get_json()
    
    connection = get_db_connection()
    if not connection:
        return jsonify({'error': 'Database connection failed'}), 500
    
    cursor = connection.cursor()
    try:
        cursor.execute('''
        INSERT INTO books (title, author, isbn, genre, publication_year, copies_available, total_copies)
        VALUES (%s, %s, %s, %s, %s, %s, %s)
        ''', (
            data['title'], data['author'], data.get('isbn'),
            data.get('genre'), data.get('publication_year'),
            data.get('copies_available', 1), data.get('total_copies', 1)
        ))
        connection.commit()
        book_id = cursor.lastrowid
        cursor.close()
        connection.close()
        
        return jsonify({'id': book_id, 'message': 'Book added successfully'}), 201
    except mysql.connector.Error as err:
        return jsonify({'error': str(err)}), 400

@app.route('/api/books/<int:book_id>', methods=['PUT'])
def update_book(book_id):
    data = request.get_json()
    
    connection = get_db_connection()
    if not connection:
        return jsonify({'error': 'Database connection failed'}), 500
    
    cursor = connection.cursor()
    try:
        cursor.execute('''
        UPDATE books SET title=%s, author=%s, isbn=%s, genre=%s, 
        publication_year=%s, copies_available=%s, total_copies=%s
        WHERE id=%s
        ''', (
            data['title'], data['author'], data.get('isbn'),
            data.get('genre'), data.get('publication_year'),
            data.get('copies_available'), data.get('total_copies'), book_id
        ))
        connection.commit()
        cursor.close()
        connection.close()
        
        return jsonify({'message': 'Book updated successfully'})
    except mysql.connector.Error as err:
        return jsonify({'error': str(err)}), 400

@app.route('/api/books/<int:book_id>', methods=['DELETE'])
def delete_book(book_id):
    connection = get_db_connection()
    if not connection:
        return jsonify({'error': 'Database connection failed'}), 500
    
    cursor = connection.cursor()
    cursor.execute('DELETE FROM books WHERE id = %s', (book_id,))
    connection.commit()
    cursor.close()
    connection.close()
    
    return jsonify({'message': 'Book deleted successfully'})

# Members endpoints
@app.route('/api/members', methods=['GET'])
def get_members():
    connection = get_db_connection()
    if not connection:
        return jsonify({'error': 'Database connection failed'}), 500
    
    cursor = connection.cursor(dictionary=True)
    cursor.execute('SELECT * FROM members ORDER BY name')
    members = cursor.fetchall()
    cursor.close()
    connection.close()
    
    return jsonify(members)

@app.route('/api/members', methods=['POST'])
def add_member():
    data = request.get_json()
    
    connection = get_db_connection()
    if not connection:
        return jsonify({'error': 'Database connection failed'}), 500
    
    cursor = connection.cursor()
    try:
        cursor.execute('''
        INSERT INTO members (name, email, phone, address)
        VALUES (%s, %s, %s, %s)
        ''', (data['name'], data['email'], data.get('phone'), data.get('address')))
        connection.commit()
        member_id = cursor.lastrowid
        cursor.close()
        connection.close()
        
        return jsonify({'id': member_id, 'message': 'Member added successfully'}), 201
    except mysql.connector.Error as err:
        return jsonify({'error': str(err)}), 400

# Borrowings endpoints
@app.route('/api/borrowings', methods=['GET'])
def get_borrowings():
    connection = get_db_connection()
    if not connection:
        return jsonify({'error': 'Database connection failed'}), 500
    
    cursor = connection.cursor(dictionary=True)
    cursor.execute('''
    SELECT b.*, bk.title as book_title, bk.author, m.name as member_name
    FROM borrowings b
    JOIN books bk ON b.book_id = bk.id
    JOIN members m ON b.member_id = m.id
    ORDER BY b.borrow_date DESC
    ''')
    borrowings = cursor.fetchall()
    cursor.close()
    connection.close()
    
    return jsonify(borrowings)

@app.route('/api/borrow', methods=['POST'])
def borrow_book():
    data = request.get_json()
    book_id = data['book_id']
    member_id = data['member_id']
    
    connection = get_db_connection()
    if not connection:
        return jsonify({'error': 'Database connection failed'}), 500
    
    cursor = connection.cursor()
    
    # Check if book is available
    cursor.execute('SELECT copies_available FROM books WHERE id = %s', (book_id,))
    result = cursor.fetchone()
    
    if not result or result[0] <= 0:
        return jsonify({'error': 'Book not available'}), 400
    
    # Create borrowing record
    due_date = datetime.now() + timedelta(days=14)  # 2 weeks borrowing period
    
    cursor.execute('''
    INSERT INTO borrowings (book_id, member_id, due_date)
    VALUES (%s, %s, %s)
    ''', (book_id, member_id, due_date.date()))
    
    # Update book availability
    cursor.execute('''
    UPDATE books SET copies_available = copies_available - 1 WHERE id = %s
    ''', (book_id,))
    
    connection.commit()
    cursor.close()
    connection.close()
    
    return jsonify({'message': 'Book borrowed successfully'})

@app.route('/api/return/<int:borrowing_id>', methods=['PUT'])
def return_book(borrowing_id):
    connection = get_db_connection()
    if not connection:
        return jsonify({'error': 'Database connection failed'}), 500
    
    cursor = connection.cursor()
    
    # Get borrowing details
    cursor.execute('SELECT book_id, due_date FROM borrowings WHERE id = %s', (borrowing_id,))
    result = cursor.fetchone()
    
    if not result:
        return jsonify({'error': 'Borrowing record not found'}), 404
    
    book_id, due_date = result
    return_date = datetime.now().date()
    
    # Calculate fine if overdue
    fine = 0
    if return_date > due_date:
        overdue_days = (return_date - due_date).days
        fine = overdue_days * 1.0  # $1 per day fine
    
    # Update borrowing record
    cursor.execute('''
    UPDATE borrowings SET return_date = %s, status = 'returned', fine_amount = %s
    WHERE id = %s
    ''', (return_date, fine, borrowing_id))
    
    # Update book availability
    cursor.execute('''
    UPDATE books SET copies_available = copies_available + 1 WHERE id = %s
    ''', (book_id,))
    
    connection.commit()
    cursor.close()
    connection.close()
    
    return jsonify({'message': 'Book returned successfully', 'fine': fine})

if __name__ == '__main__':
    init_database()
    app.run(debug=True, port=5000)