from flask import Blueprint, render_template, request, redirect, url_for, flash, session
import sqlite3
from models.database import get_db_connection
from utils.validators import validate_email, validate_phone

members_bp = Blueprint('members', __name__)

def require_login():
    if 'user_id' not in session:
        flash('Please log in to access this page.', 'error')
        return redirect(url_for('auth.login'))
    return None

@members_bp.route('/')
def list_members():
    redirect_response = require_login()
    if redirect_response:
        return redirect_response
    
    conn = get_db_connection()
    members = conn.execute('SELECT * FROM members ORDER BY name').fetchall()
    conn.close()
    return render_template('members/list.html', members=members)

@members_bp.route('/add', methods=['GET', 'POST'])
def add_member():
    redirect_response = require_login()
    if redirect_response:
        return redirect_response
    
    if request.method == 'POST':
        name = request.form['name']
        email = request.form['email']
        phone = request.form['phone']
        address = request.form['address']
        
        if not validate_email(email):
            flash('Invalid email format!', 'error')
            return render_template('members/add.html')
        
        if phone and not validate_phone(phone):
            flash('Invalid phone format!', 'error')
            return render_template('members/add.html')
        
        conn = get_db_connection()
        try:
            conn.execute(
                'INSERT INTO members (name, email, phone, address) VALUES (?, ?, ?, ?)',
                (name, email, phone, address)
            )
            conn.commit()
            flash('Member added successfully!', 'success')
            return redirect(url_for('members.list_members'))
        except sqlite3.IntegrityError:
            flash('Email already exists!', 'error')
        finally:
            conn.close()
    
    return render_template('members/add.html')

@members_bp.route('/edit/<int:member_id>', methods=['GET', 'POST'])
def edit_member(member_id):
    redirect_response = require_login()
    if redirect_response:
        return redirect_response
    
    conn = get_db_connection()
    
    if request.method == 'POST':
        name = request.form['name']
        email = request.form['email']
        phone = request.form['phone']
        address = request.form['address']
        is_active = 1 if 'is_active' in request.form else 0
        
        if not validate_email(email):
            flash('Invalid email format!', 'error')
        elif phone and not validate_phone(phone):
            flash('Invalid phone format!', 'error')
        else:
            try:
                conn.execute('''
                    UPDATE members SET name = ?, email = ?, phone = ?, 
                                     address = ?, is_active = ?
                    WHERE id = ?
                ''', (name, email, phone, address, is_active, member_id))
                conn.commit()
                flash('Member updated successfully!', 'success')
                return redirect(url_for('members.list_members'))
            except sqlite3.IntegrityError:
                flash('Email already exists!', 'error')
    
    member = conn.execute('SELECT * FROM members WHERE id = ?', (member_id,)).fetchone()
    conn.close()
    return render_template('members/edit.html', member=member)

@members_bp.route('/delete/<int:member_id>')
def delete_member(member_id):
    redirect_response = require_login()
    if redirect_response:
        return redirect_response
    
    conn = get_db_connection()
    
    # Check if member has active transactions
    active_transactions = conn.execute(
        'SELECT COUNT(*) as count FROM transactions WHERE member_id = ? AND status = "issued"',
        (member_id,)
    ).fetchone()
    
    if active_transactions['count'] > 0:
        flash('Cannot delete member with active transactions!', 'error')
    else:
        conn.execute('DELETE FROM members WHERE id = ?', (member_id,))
        conn.commit()
        flash('Member deleted successfully!', 'success')
    
    conn.close()
    return redirect(url_for('members.list_members'))