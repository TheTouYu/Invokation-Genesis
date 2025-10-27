"""
用户管理API
"""
from flask import Blueprint, request, jsonify, g
from flask_jwt_extended import jwt_required
from dal import db_dal
from utils.logger import get_logger, log_api_call

users_bp = Blueprint('users', __name__)

@users_bp.route('/users', methods=['GET'])
@jwt_required()
@log_api_call
def get_users():
    """
    获取用户列表（分页）
    """
    logger = get_logger(__name__)
    request_id = getattr(g, 'request_id', 'N/A')
    
    logger.info(f"Fetch users request, Request-ID: {request_id}")
    
    try:
        page = request.args.get('page', 1, type=int)
        per_page = request.args.get('per_page', 10, type=int)
        
        # 限制每页数量
        per_page = min(per_page, 100)
        
        logger.info(f"Fetching users with page: {page}, per_page: {per_page}, Request-ID: {request_id}")
        
        # 计算偏移量
        offset = (page - 1) * per_page
        
        # 获取用户列表
        # 注意：目前DAL可能没有get_all_users方法，我们使用get_users_with_pagination
        try:
            # 尝试使用DAL的get_all_users方法
            users = db_dal.users.get_all_users(limit=per_page, offset=offset)
            logger.debug(f"Fetched {len(users)} users using DAL, Request-ID: {request_id}")
        except AttributeError:
            # 如果DAL没有get_all_users方法，则直接使用模型查询
            from models.db_models import model_container
            User = model_container.User
            users = User.query.offset(offset).limit(per_page).all()
            logger.debug(f"Fetched {len(users)} users using direct query, Request-ID: {request_id}")
        
        # 计算总数
        try:
            total_count = db_dal.users.get_all_users_count()
            logger.debug(f"Total user count from DAL: {total_count}, Request-ID: {request_id}")
        except AttributeError:
            # 如果没有计数方法，则使用模型查询
            from models.db_models import model_container
            User = model_container.User
            total_count = User.query.count()
            logger.debug(f"Total user count from direct query: {total_count}, Request-ID: {request_id}")
        
        user_list = []
        for user in users:
            user_list.append({
                'id': user.id,
                'username': user.username,
                'email': user.email,
                'created_at': user.created_at.isoformat() if user.created_at else None
            })
        
        logger.info(f"Successfully fetched {len(user_list)} users, Request-ID: {request_id}")
        
        return jsonify({
            'users': user_list,
            'pagination': {
                'page': page,
                'per_page': per_page,
                'total': total_count,
                'pages': (total_count + per_page - 1) // per_page
            }
        }), 200
    except Exception as e:
        logger.error(f"Failed to fetch users: {str(e)}, Request-ID: {request_id}")
        return jsonify({'message': '获取用户列表失败', 'error': str(e)}), 500