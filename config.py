# config.py - Configuration
import os
from datetime import timedelta

class Config:
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'your-secret-key-here'
    DATABASE_PATH = 'library.db'
    PERMANENT_SESSION_LIFETIME = timedelta(hours=2)