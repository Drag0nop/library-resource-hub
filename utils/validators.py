# utils/validators.py - Helper Functions
import re
from datetime import datetime

def validate_email(email):
    pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    return re.match(pattern, email) is not None

def validate_phone(phone):
    pattern = r'^\+?[\d\s\-\(\)]{10,}$'
    return re.match(pattern, phone) is not None

def validate_isbn(isbn):
    # Basic ISBN validation (10 or 13 digits)
    isbn = isbn.replace('-', '').replace(' ', '')
    return len(isbn) in [10, 13] and isbn.isdigit()

def calculate_fine(due_date, return_date=None):
    if return_date is None:
        return_date = datetime.now().date()
    
    if isinstance(due_date, str):
        due_date = datetime.strptime(due_date, '%Y-%m-%d').date()
    
    if return_date > due_date:
        overdue_days = (return_date - due_date).days
        return overdue_days * 1.0  # $1 per day fine
    return 0.0