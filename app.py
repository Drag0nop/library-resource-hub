from flask import Flask, render_template, request, jsonify, session, redirect, url_for, flash
from flask_mysqldb import MySQL
from werkzeug.security import generate_password_hash, check_password_hash
import MySQLdb.cursors
import re
from datetime import datetime, timedelta
import secrets
import os
from functools import wraps

app = Flask(__name__)

# Configuration
app.config['SECRET_KEY'] = secrets.token_hex(16)  # Generate a random secret key
app.config['MYSQL_HOST'] = 'localhost'
app.config['MYSQL_USER'] = 'root'  # Change to your MySQL username
app.config['MYSQL_PASSWORD'] = 'kn@g@rk0ti'  # Change to your MySQL password
app.config['MYSQL_DB'] = 'login_app'
app.config['MYSQL_CURSORCLASS'] = 'DictCursor'

# Initialize MySQL
mysql = MySQL(app)

# Database setup function
def init_db():
    """Initialize the database with required tables"""
    try:
        cursor = mysql.connection.cursor()
        
        # Create users table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS users (
                id INT AUTO_INCREMENT PRIMARY KEY,
                username VARCHAR(50) UNIQUE NOT NULL,
                email VARCHAR(100) UNIQUE NOT NULL,
                password_hash VARCHAR(255) NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                last_login TIMESTAMP NULL,
                is_active BOOLEAN DEFAULT TRUE,
                remember_token VARCHAR(255) NULL
            )
        ''')
        
        # Create login_attempts table for security
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS login_attempts (
                id INT AUTO_INCREMENT PRIMARY KEY,
                email VARCHAR(100) NOT NULL,
                ip_address VARCHAR(45) NOT NULL,
                attempt_time TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                success BOOLEAN DEFAULT FALSE
            )
        ''')
        
        mysql.connection.commit()
        cursor.close()
        print("Database tables created successfully!")
        
    except Exception as e:
        print(f"Error creating database tables: {e}")

# Decorator for login required
def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_id' not in session:
            return redirect(url_for('login'))
        return f(*args, **kwargs)
    return decorated_function

# Helper functions
def validate_email(email):
    """Validate email format"""
    pattern = r'^[^\s@]+@[^\s@]+\.[^\s@]+$'
    return re.match(pattern, email) is not None

def validate_password(password):
    """Validate password strength"""
    if len(password) < 6:
        return False, "Password must be at least 6 characters long"
    if not re.search(r'[A-Za-z]', password):
        return False, "Password must contain at least one letter"
    if not re.search(r'\d', password):
        return False, "Password must contain at least one number"
    return True, "Valid password"

def check_login_attempts(email, ip_address):
    """Check if too many failed login attempts"""
    cursor = mysql.connection.cursor()
    
    # Check attempts in last 15 minutes
    time_limit = datetime.now() - timedelta(minutes=15)
    cursor.execute('''
        SELECT COUNT(*) as attempts FROM login_attempts 
        WHERE email = %s AND ip_address = %s AND attempt_time > %s AND success = FALSE
    ''', (email, ip_address, time_limit))
    
    result = cursor.fetchone()
    cursor.close()
    
    return result['attempts'] >= 5  # Max 5 attempts in 15 minutes

def log_login_attempt(email, ip_address, success):
    """Log login attempt"""
    try:
        cursor = mysql.connection.cursor()
        cursor.execute('''
            INSERT INTO login_attempts (email, ip_address, success) 
            VALUES (%s, %s, %s)
        ''', (email, ip_address, success))
        mysql.connection.commit()
        cursor.close()
    except Exception as e:
        print(f"Error logging login attempt: {e}")

# Routes
@app.route('/')
def index():
    """Home page - redirect to login if not authenticated"""
    if 'user_id' in session:
        return redirect(url_for('dashboard'))
    return redirect(url_for('login'))

@app.route('/login', methods=['GET', 'POST'])
def login():
    """Login page and authentication"""
    if request.method == 'GET':
        # If already logged in, redirect to dashboard
        if 'user_id' in session:
            return redirect(url_for('dashboard'))
        return render_template('login.html')
    
    elif request.method == 'POST':
        # Handle AJAX login request
        data = request.get_json()
        email = data.get('email', '').strip().lower()
        password = data.get('password', '')
        remember_me = data.get('remember', False)
        
        # Validation
        if not email or not password:
            return jsonify({
                'success': False,
                'message': 'Email and password are required'
            }), 400
        
        if not validate_email(email):
            return jsonify({
                'success': False,
                'message': 'Invalid email format'
            }), 400
        
        # Check for too many failed attempts
        ip_address = request.environ.get('HTTP_X_REAL_IP', request.remote_addr)
        if check_login_attempts(email, ip_address):
            return jsonify({
                'success': False,
                'message': 'Too many failed login attempts. Please try again later.'
            }), 429
        
        try:
            cursor = mysql.connection.cursor()
            cursor.execute('SELECT * FROM users WHERE email = %s AND is_active = TRUE', (email,))
            user = cursor.fetchone()
            
            if user and check_password_hash(user['password_hash'], password):
                # Successful login
                session['user_id'] = user['id']
                session['username'] = user['username']
                session['email'] = user['email']
                session.permanent = remember_me
                
                # Update last login
                cursor.execute('UPDATE users SET last_login = NOW() WHERE id = %s', (user['id'],))
                mysql.connection.commit()
                
                # Log successful attempt
                log_login_attempt(email, ip_address, True)
                
                cursor.close()
                
                return jsonify({
                    'success': True,
                    'message': 'Login successful',
                    'redirect': url_for('dashboard')
                })
            else:
                # Failed login
                log_login_attempt(email, ip_address, False)
                cursor.close()
                
                return jsonify({
                    'success': False,
                    'message': 'Invalid email or password'
                }), 401
                
        except Exception as e:
            return jsonify({
                'success': False,
                'message': 'Database error occurred'
            }), 500

@app.route('/register', methods=['GET', 'POST'])
def register():
    """User registration"""
    if request.method == 'GET':
        return render_template('register.html')
    
    elif request.method == 'POST':
        data = request.get_json()
        username = data.get('username', '').strip()
        email = data.get('email', '').strip().lower()
        password = data.get('password', '')
        confirm_password = data.get('confirm_password', '')
        
        # Validation
        if not all([username, email, password, confirm_password]):
            return jsonify({
                'success': False,
                'message': 'All fields are required'
            }), 400
        
        if not validate_email(email):
            return jsonify({
                'success': False,
                'message': 'Invalid email format'
            }), 400
        
        if password != confirm_password:
            return jsonify({
                'success': False,
                'message': 'Passwords do not match'
            }), 400
        
        is_valid, message = validate_password(password)
        if not is_valid:
            return jsonify({
                'success': False,
                'message': message
            }), 400
        
        try:
            cursor = mysql.connection.cursor()
            
            # Check if user already exists
            cursor.execute('SELECT id FROM users WHERE email = %s OR username = %s', (email, username))
            existing_user = cursor.fetchone()
            
            if existing_user:
                cursor.close()
                return jsonify({
                    'success': False,
                    'message': 'User with this email or username already exists'
                }), 409
            
            # Create new user
            password_hash = generate_password_hash(password)
            cursor.execute('''
                INSERT INTO users (username, email, password_hash) 
                VALUES (%s, %s, %s)
            ''', (username, email, password_hash))
            
            mysql.connection.commit()
            cursor.close()
            
            return jsonify({
                'success': True,
                'message': 'Registration successful! You can now login.',
                'redirect': url_for('login')
            })
            
        except Exception as e:
            return jsonify({
                'success': False,
                'message': 'Registration failed. Please try again.'
            }), 500

@app.route('/dashboard')
@login_required
def dashboard():
    """User dashboard"""
    try:
        cursor = mysql.connection.cursor()
        cursor.execute('''
            SELECT username, email, created_at, last_login 
            FROM users WHERE id = %s
        ''', (session['user_id'],))
        user_info = cursor.fetchone()
        cursor.close()
        
        return render_template('dashboard.html', user=user_info)
    except Exception as e:
        flash('Error loading dashboard')
        return redirect(url_for('login'))

@app.route('/logout')
def logout():
    """User logout"""
    session.clear()
    flash('You have been logged out successfully')
    return redirect(url_for('login'))

@app.route('/forgot-password', methods=['GET', 'POST'])
def forgot_password():
    """Forgot password functionality"""
    if request.method == 'GET':
        return render_template('forgot_password.html')
    
    elif request.method == 'POST':
        data = request.get_json()
        email = data.get('email', '').strip().lower()
        
        if not validate_email(email):
            return jsonify({
                'success': False,
                'message': 'Invalid email format'
            }), 400
        
        try:
            cursor = mysql.connection.cursor()
            cursor.execute('SELECT id FROM users WHERE email = %s', (email,))
            user = cursor.fetchone()
            cursor.close()
            
            if user:
                # In a real application, you would send a password reset email here
                # For demo purposes, we'll just return a success message
                return jsonify({
                    'success': True,
                    'message': 'If an account with this email exists, a password reset link has been sent.'
                })
            else:
                # Return the same message for security (don't reveal if email exists)
                return jsonify({
                    'success': True,
                    'message': 'If an account with this email exists, a password reset link has been sent.'
                })
                
        except Exception as e:
            return jsonify({
                'success': False,
                'message': 'Error processing request'
            }), 500

@app.route('/profile')
@login_required
def profile():
    """User profile page"""
    try:
        cursor = mysql.connection.cursor()
        cursor.execute('''
            SELECT username, email, created_at, last_login 
            FROM users WHERE id = %s
        ''', (session['user_id'],))
        user_info = cursor.fetchone()
        cursor.close()
        
        return render_template('profile.html', user=user_info)
    except Exception as e:
        flash('Error loading profile')
        return redirect(url_for('dashboard'))

@app.route('/api/user-stats')
@login_required
def user_stats():
    """API endpoint for user statistics"""
    try:
        cursor = mysql.connection.cursor()
        
        # Get user info
        cursor.execute('''
            SELECT created_at, last_login 
            FROM users WHERE id = %s
        ''', (session['user_id'],))
        user_info = cursor.fetchone()
        
        # Get login attempts count
        cursor.execute('''
            SELECT COUNT(*) as total_attempts 
            FROM login_attempts WHERE email = %s
        ''', (session['email'],))
        attempts = cursor.fetchone()
        
        cursor.close()
        
        return jsonify({
            'success': True,
            'data': {
                'member_since': user_info['created_at'].strftime('%B %Y'),
                'last_login': user_info['last_login'].strftime('%Y-%m-%d %H:%M:%S') if user_info['last_login'] else 'Never',
                'total_login_attempts': attempts['total_attempts']
            }
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'message': 'Error fetching user statistics'
        }), 500

# Error handlers
@app.errorhandler(404)
def not_found_error(error):
    return render_template('404.html'), 404

@app.errorhandler(500)
def internal_error(error):
    return render_template('500.html'), 500

# Database initialization
@app.before_request
def create_tables():
    init_db()

if __name__ == '__main__':
    # Set session lifetime
    app.permanent_session_lifetime = timedelta(days=7)
    
    # Run the application
    app.run(debug=True, host='0.0.0.0', port=5000)