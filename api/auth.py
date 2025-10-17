from flask import Blueprint, request, jsonify
from flask_jwt_extended import create_access_token, jwt_required, get_jwt_identity
from werkzeug.security import generate_password_hash, check_password_hash
from dal import db_dal

auth_bp = Blueprint('auth', __name__)

@auth_bp.route('/register', methods=['POST'])
def register():
    data = request.get_json()
    username = data.get('username')
    password = data.get('password')
    email = data.get('email', f"{username}@example.com")  # 使用默认邮箱，或从请求中获取
    
    if not username or not password:
        return jsonify({'message': 'Username and password are required.'}), 400
    
    # Check if user already exists
    existing_user = db_dal.users.get_user_by_username(username)
    if existing_user:
        return jsonify({'message': 'Username already exists.'}), 400
    
    hashed_password = generate_password_hash(password)
    
    try:
        new_user = db_dal.users.create_user(
            username=username, 
            email=email, 
            password_hash=hashed_password
        )
        
        return jsonify({'message': 'User registered successfully.', 'user_id': new_user.id}), 201
    except Exception as e:
        return jsonify({'message': 'Registration failed.', 'error': str(e)}), 500

@auth_bp.route('/login', methods=['POST'])
def login():
    data = request.get_json()
    username = data.get('username')
    password = data.get('password')
    
    if not username or not password:
        return jsonify({'message': 'Username and password are required.'}), 400
    
    user = db_dal.users.get_user_by_username(username)
    
    if not user or not check_password_hash(user.password_hash, password):
        return jsonify({'message': 'Invalid credentials.'}), 401
    
    access_token = create_access_token(identity=user.id)
    return jsonify({'access_token': access_token}), 200

@auth_bp.route('/profile', methods=['GET'])
@jwt_required()
def get_profile():
    current_user_id = get_jwt_identity()
    user = db_dal.users.get_user_by_id(current_user_id)
    
    if not user:
        return jsonify({'message': 'User not found.'}), 404
    
    return jsonify({
        'id': user.id,
        'username': user.username
    }), 200