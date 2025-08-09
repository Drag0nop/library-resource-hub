import sqlite3
import hashlib
from datetime import datetime, date
import os

DATABASE_PATH = 'library.db'

def get_db_connection():
    conn = sqlite3.connect(DATABASE_PATH)
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    conn = get_db_connection()
    
    # Users table for authentication
    conn.execute('''
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE NOT NULL,
            password_hash TEXT NOT NULL,
            role TEXT DEFAULT 'librarian',
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    
    # Books table
    conn.execute('''
        CREATE TABLE IF NOT EXISTS books (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            title TEXT NOT NULL,
            author TEXT NOT NULL,
            isbn TEXT UNIQUE,
            category TEXT,
            total_copies INTEGER DEFAULT 1,
            available_copies INTEGER DEFAULT 1,
            publication_year INTEGER,
            added_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    
    # Members table
    conn.execute('''
        CREATE TABLE IF NOT EXISTS members (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            email TEXT UNIQUE NOT NULL,
            phone TEXT,
            address TEXT,
            membership_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            is_active BOOLEAN DEFAULT 1
        )
    ''')
    
    # Transactions table
    conn.execute('''
        CREATE TABLE IF NOT EXISTS transactions (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            book_id INTEGER,
            member_id INTEGER,
            issue_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            due_date DATE,
            return_date TIMESTAMP,
            fine_amount DECIMAL(10,2) DEFAULT 0,
            status TEXT DEFAULT 'issued',
            FOREIGN KEY (book_id) REFERENCES books (id),
            FOREIGN KEY (member_id) REFERENCES members (id)
        )
    ''')
    
    # Create default admin user if not exists
    cursor = conn.execute('SELECT COUNT(*) as count FROM users WHERE username = ?', ('admin',))
    if cursor.fetchone()['count'] == 0:
        password_hash = hashlib.sha256('admin123'.encode()).hexdigest()
        conn.execute('INSERT INTO users (username, password_hash, role) VALUES (?, ?, ?)',
                    ('admin', password_hash, 'admin'))
    
    conn.commit()
    conn.close()