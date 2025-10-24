#!/usr/bin/env python3
"""
Test script for Library Resource Hub
"""

import sys
import os

def test_imports():
    """Test if all required modules can be imported"""
    print("Testing imports...")
    
    try:
        from app import app, db
        print("✓ Main app imports successful")
    except Exception as e:
        print(f"✗ Error importing main app: {e}")
        return False
    
    try:
        from models.user import User
        from models.book import Book
        from models.transaction import Transaction
        print("✓ Model imports successful")
    except Exception as e:
        print(f"✗ Error importing models: {e}")
        return False
    
    try:
        from routes.auth_routes import auth_bp
        from routes.book_routes import book_bp
        from routes.admin_routes import admin_bp
        print("✓ Route imports successful")
    except Exception as e:
        print(f"✗ Error importing routes: {e}")
        return False
    
    return True

def test_database_connection():
    """Test database connection and table creation"""
    print("Testing database connection...")
    
    try:
        from app import app, db
        # Force SQLite for testing
        app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///test_library.db'
        
        with app.app_context():
            # Test database connection
            with db.engine.connect() as connection:
                connection.execute(db.text('SELECT 1'))
            print("✓ Database connection successful")
            
            # Test table creation
            db.create_all()
            print("✓ Database tables created successfully")
            
            return True
    except Exception as e:
        print(f"✗ Database error: {e}")
        return False

def test_routes():
    """Test if routes are properly registered"""
    print("Testing route registration...")
    
    try:
        from app import app
        
        # Check if routes are registered
        routes = [str(rule) for rule in app.url_map.iter_rules()]
        
        expected_routes = [
            '/',
            '/login',
            '/register',
            '/dashboard',
            '/books',
            '/admin'
        ]
        
        for route in expected_routes:
            if any(route in r for r in routes):
                print(f"✓ Route {route} registered")
            else:
                print(f"✗ Route {route} not found")
                return False
        
        return True
    except Exception as e:
        print(f"✗ Route testing error: {e}")
        return False

def main():
    """Run all tests"""
    print("="*50)
    print("LIBRARY RESOURCE HUB - TEST SUITE")
    print("="*50)
    
    tests = [
        ("Import Test", test_imports),
        ("Database Test", test_database_connection),
        ("Route Test", test_routes)
    ]
    
    passed = 0
    total = len(tests)
    
    for test_name, test_func in tests:
        print(f"\n{test_name}:")
        if test_func():
            passed += 1
            print(f"✓ {test_name} PASSED")
        else:
            print(f"✗ {test_name} FAILED")
    
    print("\n" + "="*50)
    print(f"TEST RESULTS: {passed}/{total} tests passed")
    print("="*50)
    
    if passed == total:
        print("🎉 All tests passed! The application is ready to run.")
        print("\nTo start the application, run:")
        print("  python app.py")
        return True
    else:
        print("❌ Some tests failed. Please check the errors above.")
        return False

if __name__ == '__main__':
    success = main()
    sys.exit(0 if success else 1)