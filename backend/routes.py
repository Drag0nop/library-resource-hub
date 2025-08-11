from flask import Blueprint, request, jsonify
from models import User, Book, Transaction
import jwt
import datetime

api = Blueprint('api', __name__)
SECRET_KEY = 'your_secret_key_here'  # Change this in production

def generate_token(user_data):
    payload = {
        'user_id': user_data['id'],
        'username': user_data['username'],
        'role': user_data['role'],
        'exp': datetime.datetime.utcnow() + datetime.timedelta(hours=24)
    }
    return jwt.encode(payload, SECRET_KEY, algorithm='HS256')

def verify_token(token):
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=['HS256'])
        return payload
    except jwt.ExpiredSignatureError:
        return None
    except jwt.InvalidTokenError:
        return None

@api.route('/register', methods=['POST'])
def register():
    data = request.get_json()
    username = data.get('username')
    password = data.get('password')
    role = data.get('role', 'member')
    
    if not username or not password:
        return jsonify({'success': False, 'message': 'Username and password required'}), 400
    
    user_model = User()
    success, message = user_model.create_user(username, password, role)
    
    return jsonify({'success': success, 'message': message})

@api.route('/login', methods=['POST'])
def login():
    data = request.get_json()
    username = data.get('username')
    password = data.get('password')
    
    if not username or not password:
        return jsonify({'success': False, 'message': 'Username and password required'}), 400
    
    user_model = User()
    success, user_data = user_model.authenticate_user(username, password)
    
    if success:
        token = generate_token(user_data)
        return jsonify({
            'success': True,
            'token': token,
            'user': {
                'id': user_data['id'],
                'username': user_data['username'],
                'role': user_data['role']
            }
        })
    
    return jsonify({'success': False, 'message': 'Invalid credentials'}), 401

@api.route('/books', methods=['GET'])
def get_books():
    book_model = Book()
    search_term = request.args.get('search', '')
    
    if search_term:
        books = book_model.search_books(search_term)
    else:
        books = book_model.get_all_books()
    
    return jsonify({'success': True, 'books': books})

@api.route('/books', methods=['POST'])
def add_book():
    token = request.headers.get('Authorization', '').replace('Bearer ', '')
    user_data = verify_token(token)
    
    if not user_data or user_data['role'] != 'admin':
        return jsonify({'success': False, 'message': 'Admin access required'}), 403
    
    data = request.get_json()
    book_model = Book()
    
    success = book_model.add_book(
        data['title'], data['author'], data['isbn'], 
        data['category'], data['copies']
    )
    
    return jsonify({'success': success})

@api.route('/books/<int:book_id>', methods=['PUT'])
def update_book(book_id):
    token = request.headers.get('Authorization', '').replace('Bearer ', '')
    user_data = verify_token(token)
    
    if not user_data or user_data['role'] != 'admin':
        return jsonify({'success': False, 'message': 'Admin access required'}), 403
    
    data = request.get_json()
    book_model = Book()
    
    success = book_model.update_book(
        book_id, data['title'], data['author'], 
        data['isbn'], data['category'], data['copies']
    )
    
    return jsonify({'success': success})

@api.route('/issue-book', methods=['POST'])
def issue_book():
    token = request.headers.get('Authorization', '').replace('Bearer ', '')
    user_data = verify_token(token)
    
    if not user_data:
        return jsonify({'success': False, 'message': 'Authentication required'}), 401
    
    data = request.get_json()
    transaction_model = Transaction()
    
    success, message = transaction_model.issue_book(user_data['user_id'], data['book_id'])
    
    return jsonify({'success': success, 'message': message})

@api.route('/return-book', methods=['POST'])
def return_book():
    token = request.headers.get('Authorization', '').replace('Bearer ', '')
    user_data = verify_token(token)
    
    if not user_data:
        return jsonify({'success': False, 'message': 'Authentication required'}), 401
    
    data = request.get_json()
    transaction_model = Transaction()
    
    success, message = transaction_model.return_book(user_data['user_id'], data['book_id'])
    
    return jsonify({'success': success, 'message': message})

@api.route('/my-books', methods=['GET'])
def get_my_books():
    token = request.headers.get('Authorization', '').replace('Bearer ', '')
    user_data = verify_token(token)
    
    if not user_data:
        return jsonify({'success': False, 'message': 'Authentication required'}), 401
    
    transaction_model = Transaction()
    books = transaction_model.get_user_books(user_data['user_id'])
    
    return jsonify({'success': True, 'books': books})