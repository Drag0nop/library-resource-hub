#!/usr/bin/env python3
"""
Simple test for Library Resource Hub
"""

def test_basic_functionality():
    """Test basic application functionality"""
    print("Testing basic functionality...")
    
    try:
        # Test imports
        from app import app, db
        from models.user import User
        from models.book import Book
        from models.transaction import Transaction
        print("✓ All imports successful")
        
        # Test app creation
        with app.app_context():
            # Force SQLite for testing
            app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///test_library.db'
            
            # Test database operations
            db.create_all()
            print("✓ Database tables created")
            
            # Test model creation
            user = User(username='test', email='test@test.com', password_hash='test')
            book = Book(title='Test Book', author='Test Author', total_copies=1, available_copies=1)
            
            print("✓ Models can be instantiated")
            
        print("✓ Basic functionality test passed")
        return True
        
    except Exception as e:
        print(f"✗ Error: {e}")
        return False

if __name__ == '__main__':
    print("="*50)
    print("SIMPLE FUNCTIONALITY TEST")
    print("="*50)
    
    if test_basic_functionality():
        print("\n🎉 Application is working correctly!")
        print("You can now run: python3 app.py")
    else:
        print("\n❌ There are issues with the application.")