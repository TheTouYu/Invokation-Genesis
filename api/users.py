"""
用户管理API
"""
from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required
from dal import db_dal

users_bp = Blueprint('users', __name__)

@users_bp.route('/users', methods=['GET'])
@jwt_required()
def get_users():
    """
    获取用户列表（分页）
    """
    try:
        page = request.args.get('page', 1, type=int)
        per_page = request.args.get('per_page', 10, type=int)
        
        # 限制每页数量
        per_page = min(per_page, 100)
        
        # 计算偏移量
        offset = (page - 1) * per_page
        
        # 获取用户列表
        # 注意：目前DAL可能没有get_all_users方法，我们使用get_users_with_pagination
        try:
            # 尝试使用DAL的get_all_users方法
            users = db_dal.users.get_all_users(limit=per_page, offset=offset)
        except AttributeError:
            # 如果DAL没有get_all_users方法，则直接使用模型查询
            from models.db_models import model_container
            User = model_container.User
            users = User.query.offset(offset).limit(per_page).all()
        
        # 计算总数
        try:
            total_count = db_dal.users.get_all_users_count()
        except AttributeError:
            # 如果没有计数方法，则使用模型查询
            from models.db_models import model_container
            User = model_container.User
            total_count = User.query.count()
        
        user_list = []
        for user in users:
            user_list.append({
                'id': user.id,
                'username': user.username,
                'email': user.email,
                'created_at': user.created_at.isoformat() if user.created_at else None
            })
        
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
        return jsonify({'message': '获取用户列表失败', 'error': str(e)}), 500