"""
装饰器模块
"""
from functools import wraps
from flask import request, jsonify
from flask_jwt_extended import verify_jwt_in_request, get_jwt_identity
from models.db_models import model_container


def token_required(f):
    """
    JWT令牌验证装饰器
    """
    @wraps(f)
    def decorated_function(*args, **kwargs):
        try:
            # 验证JWT令牌
            verify_jwt_in_request()
            
            # 获取当前用户ID
            current_user_id = get_jwt_identity()
            
            # 通过DAL获取用户信息
            from dal import db_dal
            current_user = db_dal.users.get_user_by_id(current_user_id)
            
            if not current_user:
                return jsonify({'message': '用户不存在', 'error': 'user_not_found'}), 401
            
            # 将用户对象传递给被装饰的函数
            return f(current_user, *args, **kwargs)
        except Exception as e:
            return jsonify({'message': '访问被拒绝', 'error': str(e)}), 401
    
    return decorated_function