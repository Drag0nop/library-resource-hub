#!/usr/bin/env python3
"""
Database initialization script for Library Resource Hub
"""

from app import app, db
from models.user import User
from models.book import Book
from models.transaction import Transaction
from werkzeug.security import generate_password_hash
from datetime import datetime

def init_database():
    """Initialize the database with tables and sample data"""
    with app.app_context():
        # Create all tables
        db.create_all()
        print("✓ Database tables created")
        
        # Check if admin user exists
        admin = User.query.filter_by(email='admin@library.com').first()
        if not admin:
            admin = User(
                username='admin',
                email='admin@library.com',
                password_hash=generate_password_hash('admin123'),
                role='admin'
            )
            db.session.add(admin)
            print("✓ Admin user created (admin@library.com / admin123)")
        
        # Check if regular user exists
        user = User.query.filter_by(email='user@library.com').first()
        if not user:
            user = User(
                username='testuser',
                email='user@library.com',
                password_hash=generate_password_hash('user123'),
                role='user'
            )
            db.session.add(user)
            print("✓ Test user created (user@library.com / user123)")
        
        # Add sample books if none exist
        if Book.query.count() == 0:
            sample_books = [
                {
                    'title': 'The Great Gatsby',
                    'author': 'F. Scott Fitzgerald',
                    'isbn': '9780743273565',
                    'category': 'Literature',
                    'description': 'A classic American novel set in the Jazz Age.',
                    'total_copies': 3,
                    'available_copies': 3,
                    'published_year': 1925,
                    'publisher': 'Scribner',
                    'language': 'English'
                },
                {
                    'title': 'To Kill a Mockingbird',
                    'author': 'Harper Lee',
                    'isbn': '9780061120084',
                    'category': 'Literature',
                    'description': 'A gripping tale of racial injustice and childhood innocence.',
                    'total_copies': 2,
                    'available_copies': 2,
                    'published_year': 1960,
                    'publisher': 'J.B. Lippincott & Co.',
                    'language': 'English'
                },
                {
                    'title': '1984',
                    'author': 'George Orwell',
                    'isbn': '9780451524935',
                    'category': 'Fiction',
                    'description': 'A dystopian social science fiction novel.',
                    'total_copies': 4,
                    'available_copies': 4,
                    'published_year': 1949,
                    'publisher': 'Secker & Warburg',
                    'language': 'English'
                },
                {
                    'title': 'Pride and Prejudice',
                    'author': 'Jane Austen',
                    'isbn': '9780141439518',
                    'category': 'Literature',
                    'description': 'A romantic novel of manners written by Jane Austen.',
                    'total_copies': 2,
                    'available_copies': 2,
                    'published_year': 1813,
                    'publisher': 'T. Egerton, Whitehall',
                    'language': 'English'
                },
                {
                    'title': 'The Catcher in the Rye',
                    'author': 'J.D. Salinger',
                    'isbn': '9780316769174',
                    'category': 'Literature',
                    'description': 'A coming-of-age story about teenage rebellion.',
                    'total_copies': 3,
                    'available_copies': 3,
                    'published_year': 1951,
                    'publisher': 'Little, Brown and Company',
                    'language': 'English'
                },
                {
                    'title': 'Sapiens: A Brief History of Humankind',
                    'author': 'Yuval Noah Harari',
                    'isbn': '9780062316097',
                    'category': 'History',
                    'description': 'An exploration of how Homo sapiens came to dominate the world.',
                    'total_copies': 2,
                    'available_copies': 2,
                    'published_year': 2011,
                    'publisher': 'Harper',
                    'language': 'English'
                },
                {
                    'title': 'The Selfish Gene',
                    'author': 'Richard Dawkins',
                    'isbn': '9780192860927',
                    'category': 'Science',
                    'description': 'A book on evolution by natural selection.',
                    'total_copies': 2,
                    'available_copies': 2,
                    'published_year': 1976,
                    'publisher': 'Oxford University Press',
                    'language': 'English'
                },
                {
                    'title': 'Clean Code',
                    'author': 'Robert C. Martin',
                    'isbn': '9780132350884',
                    'category': 'Technology',
                    'description': 'A handbook of agile software craftsmanship.',
                    'total_copies': 3,
                    'available_copies': 3,
                    'published_year': 2008,
                    'publisher': 'Prentice Hall',
                    'language': 'English'
                }
            ]
            
            for book_data in sample_books:
                book = Book(**book_data)
                db.session.add(book)
            
            print(f"✓ Added {len(sample_books)} sample books")
        
        # Commit all changes
        db.session.commit()
        print("✓ Database initialization completed successfully!")
        print("\n" + "="*50)
        print("LIBRARY RESOURCE HUB - READY TO USE")
        print("="*50)
        print("Admin Login: admin@library.com / admin123")
        print("User Login:  user@library.com / user123")
        print("="*50)

if __name__ == '__main__':
    init_database()