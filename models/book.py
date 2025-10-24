from datetime import datetime
from app import db

class Book(db.Model):
    __tablename__ = 'books'
    
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(200), nullable=False)
    author = db.Column(db.String(200), nullable=False)
    isbn = db.Column(db.String(20), unique=True)
    category = db.Column(db.String(100))
    description = db.Column(db.Text)
    total_copies = db.Column(db.Integer, default=1)
    available_copies = db.Column(db.Integer, default=1)
    published_year = db.Column(db.Integer)
    publisher = db.Column(db.String(200))
    language = db.Column(db.String(50), default='English')
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    transactions = db.relationship('Transaction', backref='book', lazy=True)
    
    def __repr__(self):
        return f'<Book {self.title}>'
    
    def to_dict(self):
        return {
            'id': self.id,
            'title': self.title,
            'author': self.author,
            'isbn': self.isbn,
            'category': self.category,
            'description': self.description,
            'total_copies': self.total_copies,
            'available_copies': self.available_copies,
            'published_year': self.published_year,
            'publisher': self.publisher,
            'language': self.language,
            'created_at': self.created_at.isoformat() if self.created_at else None
        }
    
    @property
    def is_available(self):
        return self.available_copies > 0