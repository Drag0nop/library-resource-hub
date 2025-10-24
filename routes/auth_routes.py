from flask import Blueprint, render_template, request, redirect, url_for, flash
from flask_login import login_user, logout_user, login_required, current_user
from werkzeug.security import generate_password_hash, check_password_hash
from app import db
from models.user import User
from models.book import Book
from models.transaction import Transaction

auth_bp = Blueprint('auth', __name__)

@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('dashboard'))
    
    if request.method == 'POST':
        data = request.get_json() if request.is_json else request.form
        email = data.get('email')
        password = data.get('password')
        
        user = User.query.filter_by(email=email).first()
        
        if user and check_password_hash(user.password_hash, password):
            if not user.is_active:
                flash('Your account has been deactivated. Please contact an administrator.', 'error')
                return redirect(url_for('auth.login'))
            
            login_user(user, remember=True)
            next_page = request.args.get('next')
            
            if request.is_json:
                return {'success': True, 'redirect': next_page or url_for('dashboard')}
            
            return redirect(next_page) if next_page else redirect(url_for('dashboard'))
        else:
            if request.is_json:
                return {'success': False, 'message': 'Invalid email or password'}
            flash('Invalid email or password', 'error')
    
    return render_template('login.html')

@auth_bp.route('/register', methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('dashboard'))
    
    if request.method == 'POST':
        data = request.get_json() if request.is_json else request.form
        username = data.get('username')
        email = data.get('email')
        password = data.get('password')
        confirm_password = data.get('confirm_password')
        
        # Validation
        if not username or not email or not password:
            if request.is_json:
                return {'success': False, 'message': 'All fields are required'}
            flash('All fields are required', 'error')
            return render_template('register.html')
        
        if password != confirm_password:
            if request.is_json:
                return {'success': False, 'message': 'Passwords do not match'}
            flash('Passwords do not match', 'error')
            return render_template('register.html')
        
        if len(password) < 6:
            if request.is_json:
                return {'success': False, 'message': 'Password must be at least 6 characters long'}
            flash('Password must be at least 6 characters long', 'error')
            return render_template('register.html')
        
        # Check if user already exists
        if User.query.filter_by(username=username).first():
            if request.is_json:
                return {'success': False, 'message': 'Username already exists'}
            flash('Username already exists', 'error')
            return render_template('register.html')
        
        if User.query.filter_by(email=email).first():
            if request.is_json:
                return {'success': False, 'message': 'Email already registered'}
            flash('Email already registered', 'error')
            return render_template('register.html')
        
        # Create new user
        user = User(
            username=username,
            email=email,
            password_hash=generate_password_hash(password)
        )
        
        db.session.add(user)
        db.session.commit()
        
        if request.is_json:
            return {'success': True, 'message': 'Registration successful! Please log in.'}
        
        flash('Registration successful! Please log in.', 'success')
        return redirect(url_for('auth.login'))
    
    return render_template('register.html')

@auth_bp.route('/logout')
@login_required
def logout():
    logout_user()
    flash('You have been logged out successfully.', 'info')
    return redirect(url_for('index'))