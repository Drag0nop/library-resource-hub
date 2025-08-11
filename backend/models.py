from database import Database
import bcrypt
import datetime

class User:
    def __init__(self):
        self.db = Database()
    
    def create_user(self, username, password, role='member'):
        # Check if user exists
        existing_user = self.db.fetch_query(
            "SELECT id FROM users WHERE username = %s", (username,)
        )
        
        if existing_user:
            return False, "Username already exists"
        
        # Hash password
        hashed_password = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt())
        
        # Insert user
        query = "INSERT INTO users (username, password, role, created_at) VALUES (%s, %s, %s, %s)"
        params = (username, hashed_password, role, datetime.datetime.now())
        
        cursor = self.db.execute_query(query, params)
        if cursor:
            return True, "User created successfully"
        return False, "Error creating user"
    
    def authenticate_user(self, username, password):
        user = self.db.fetch_query(
            "SELECT * FROM users WHERE username = %s", (username,)
        )
        
        if user and bcrypt.checkpw(password.encode('utf-8'), user[0]['password'].encode('utf-8')):
            return True, user[0]
        return False, None

class Book:
    def __init__(self):
        self.db = Database()
    
    def add_book(self, title, author, isbn, category, copies):
        query = """INSERT INTO books (title, author, isbn, category, total_copies, available_copies, created_at) 
                   VALUES (%s, %s, %s, %s, %s, %s, %s)"""
        params = (title, author, isbn, category, copies, copies, datetime.datetime.now())
        
        cursor = self.db.execute_query(query, params)
        return cursor is not None
    
    def get_all_books(self):
        return self.db.fetch_query("SELECT * FROM books ORDER BY title")
    
    def search_books(self, search_term):
        query = """SELECT * FROM books WHERE 
                   title LIKE %s OR author LIKE %s OR category LIKE %s"""
        search_pattern = f"%{search_term}%"
        return self.db.fetch_query(query, (search_pattern, search_pattern, search_pattern))
    
    def update_book(self, book_id, title, author, isbn, category, copies):
        query = """UPDATE books SET title=%s, author=%s, isbn=%s, category=%s, total_copies=%s 
                   WHERE id=%s"""
        params = (title, author, isbn, category, copies, book_id)
        cursor = self.db.execute_query(query, params)
        return cursor is not None

class Transaction:
    def __init__(self):
        self.db = Database()
    
    def issue_book(self, user_id, book_id):
        # Check if book is available
        book = self.db.fetch_query("SELECT available_copies FROM books WHERE id = %s", (book_id,))
        if not book or book[0]['available_copies'] <= 0:
            return False, "Book not available"
        
        # Check if user already has this book
        existing = self.db.fetch_query(
            "SELECT id FROM transactions WHERE user_id=%s AND book_id=%s AND return_date IS NULL",
            (user_id, book_id)
        )
        if existing:
            return False, "Book already issued to this user"
        
        # Issue book
        issue_date = datetime.datetime.now()
        due_date = issue_date + datetime.timedelta(days=14)  # 14 days borrowing period
        
        query = """INSERT INTO transactions (user_id, book_id, issue_date, due_date) 
                   VALUES (%s, %s, %s, %s)"""
        cursor = self.db.execute_query(query, (user_id, book_id, issue_date, due_date))
        
        if cursor:
            # Update available copies
            self.db.execute_query(
                "UPDATE books SET available_copies = available_copies - 1 WHERE id = %s",
                (book_id,)
            )
            return True, "Book issued successfully"
        
        return False, "Error issuing book"
    
    def return_book(self, user_id, book_id):
        # Update transaction
        query = """UPDATE transactions SET return_date = %s 
                   WHERE user_id = %s AND book_id = %s AND return_date IS NULL"""
        cursor = self.db.execute_query(query, (datetime.datetime.now(), user_id, book_id))
        
        if cursor:
            # Update available copies
            self.db.execute_query(
                "UPDATE books SET available_copies = available_copies + 1 WHERE id = %s",
                (book_id,)
            )
            return True, "Book returned successfully"
        
        return False, "Error returning book"
    
    def get_user_books(self, user_id):
        query = """SELECT b.*, t.issue_date, t.due_date 
                   FROM books b 
                   JOIN transactions t ON b.id = t.book_id 
                   WHERE t.user_id = %s AND t.return_date IS NULL"""
        return self.db.fetch_query(query, (user_id,))