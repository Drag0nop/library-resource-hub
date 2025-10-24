#!/usr/bin/env python3
"""
Setup script for Library Resource Hub
"""

import subprocess
import sys
import os

def install_requirements():
    """Install Python requirements"""
    print("Installing Python requirements...")
    try:
        subprocess.check_call([sys.executable, "-m", "pip", "install", "-r", "requirements.txt"])
        print("✓ Requirements installed successfully")
        return True
    except subprocess.CalledProcessError as e:
        print(f"✗ Error installing requirements: {e}")
        return False

def setup_database():
    """Initialize the database"""
    print("Setting up database...")
    try:
        from init_db import init_database
        init_database()
        return True
    except Exception as e:
        print(f"✗ Error setting up database: {e}")
        return False

def main():
    """Main setup function"""
    print("="*60)
    print("LIBRARY RESOURCE HUB - SETUP")
    print("="*60)
    
    # Install requirements
    if not install_requirements():
        print("Setup failed. Please check the error messages above.")
        return False
    
    # Setup database
    if not setup_database():
        print("Setup failed. Please check the error messages above.")
        return False
    
    print("\n" + "="*60)
    print("SETUP COMPLETED SUCCESSFULLY!")
    print("="*60)
    print("To start the application, run:")
    print("  python app.py")
    print("\nThen open your browser and go to:")
    print("  http://localhost:5000")
    print("\nDefault login credentials:")
    print("  Admin: admin@library.com / admin123")
    print("  User:  user@library.com / user123")
    print("="*60)
    
    return True

if __name__ == '__main__':
    main()