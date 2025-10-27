from flask import Blueprint, request, jsonify, g
from flask_jwt_extended import create_access_token, jwt_required, get_jwt_identity
from werkzeug.security import generate_password_hash, check_password_hash
from dal import db_dal
from utils.logger import get_logger, log_api_call

auth_bp = Blueprint('auth', __name__)

@auth_bp.route('/register', methods=['POST'])
@log_api_call
def register():
    logger = get_logger(__name__)
    request_id = getattr(g, 'request_id', 'N/A')
    
    data = request.get_json()
    username = data.get('username')
    password = data.get('password')
    email = data.get('email', f"{username}@example.com")  # 使用默认邮箱，或从请求中获取
    
    logger.info(f"Registration attempt for username: {username}, Request-ID: {request_id}")
    
    if not username or not password:
        logger.warning(f"Registration failed: Missing username or password, Request-ID: {request_id}")
        return jsonify({'message': 'Username and password are required.'}), 400
    
    # Check if user already exists
    existing_user = db_dal.users.get_user_by_username(username)
    if existing_user:
        logger.warning(f"Registration failed: Username {username} already exists, Request-ID: {request_id}")
        return jsonify({'message': 'Username already exists.'}), 400
    
    hashed_password = generate_password_hash(password)
    
    try:
        new_user = db_dal.users.create_user(
            username=username, 
            email=email, 
            password_hash=hashed_password
        )
        
        logger.info(f"User {username} registered successfully with ID {new_user.id}, Request-ID: {request_id}")
        return jsonify({'message': 'User registered successfully.', 'user_id': new_user.id}), 201
    except Exception as e:
        logger.error(f"Registration failed with error: {str(e)}, Request-ID: {request_id}")
        return jsonify({'message': 'Registration failed.', 'error': str(e)}), 500

@auth_bp.route('/login', methods=['POST'])
@log_api_call
def login():
    logger = get_logger(__name__)
    request_id = getattr(g, 'request_id', 'N/A')
    
    data = request.get_json()
    username = data.get('username')
    password = data.get('password')
    
    logger.info(f"Login attempt for username: {username}, Request-ID: {request_id}")
    
    if not username or not password:
        logger.warning(f"Login failed: Missing username or password, Request-ID: {request_id}")
        return jsonify({'message': 'Username and password are required.'}), 400
    
    user = db_dal.users.get_user_by_username(username)
    
    if not user or not check_password_hash(user.password_hash, password):
        logger.warning(f"Login failed: Invalid credentials for username: {username}, Request-ID: {request_id}")
        return jsonify({'message': 'Invalid credentials.'}), 401
    
    access_token = create_access_token(identity=user.id)
    logger.info(f"User {username} logged in successfully, Request-ID: {request_id}")
    return jsonify({'access_token': access_token}), 200

@auth_bp.route('/profile', methods=['GET'])
@jwt_required()
@log_api_call
def get_profile():
    logger = get_logger(__name__)
    request_id = getattr(g, 'request_id', 'N/A')
    
    current_user_id = get_jwt_identity()
    logger.info(f"Fetching profile for user ID: {current_user_id}, Request-ID: {request_id}")
    
    user = db_dal.users.get_user_by_id(current_user_id)
    
    if not user:
        logger.warning(f"Profile request failed: User {current_user_id} not found, Request-ID: {request_id}")
        return jsonify({'message': 'User not found.'}), 404
    
    logger.info(f"Profile fetched successfully for user {user.username}, Request-ID: {request_id}")
    return jsonify({
        'id': user.id,
        'username': user.username
    }), 200