"""
开发工具：生成测试用JWT令牌
"""
import os
import sys
import jwt
from datetime import datetime, timedelta

# 添加项目根目录到Python路径
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app import create_app
from database_manager import db_manager

# 为兼容性，创建一个db引用
def get_db():
    return db_manager.get_db()

db = get_db()

def generate_test_token(user_id="test_user_1", username="test_user", email="test@example.com"):
    """
    生成一个测试用的JWT令牌
    """
    # 获取应用实例以访问JWT配置
    app = create_app()
    
    # 生成一个简单的载荷
    payload = {
        'sub': user_id,  # JWT标准要求的用户标识符
        'user_id': user_id,
        'username': username,
        'email': email,
        'iat': datetime.utcnow(),
        'exp': datetime.utcnow() + timedelta(days=1)  # 1天后过期
    }
    
    # 使用应用配置的JWT密钥编码
    with app.app_context():
        token = jwt.encode(
            payload, 
            app.config['JWT_SECRET_KEY'], 
            algorithm='HS256'
        )
    
    return token

def create_test_user():
    """
    在数据库中创建一个测试用户
    """
    app = create_app()
    
    with app.app_context():
        # 现在可以从db获取User模型
        from models.db_models import User
        
        # 检查是否已存在测试用户
        existing_user = User.query.filter_by(username='test_user').first()
        if existing_user:
            print(f"测试用户已存在: ID={existing_user.id}")
            return existing_user.id
        
        # 创建测试用户
        from werkzeug.security import generate_password_hash
        test_user = User(
            username='test_user',
            email='test@example.com',
            password_hash=generate_password_hash('test_password')
        )
        
        db.session.add(test_user)
        db.session.commit()
        
        print(f"创建测试用户: ID={test_user.id}")
        return test_user.id

if __name__ == "__main__":
    print("七圣召唤开发工具 - 生成测试令牌")
    print("=" * 50)
    
    # 创建测试用户
    user_id = create_test_user()
    
    # 生成令牌
    token = generate_test_token(user_id=user_id)
    
    print(f"\n生成的测试JWT令牌:")
    print(f"Bearer {token}")
    print("\n使用方法:")
    print("在API请求的Authorization头中使用此令牌:")
    print(f"Authorization: Bearer {token}")
    print("\n例如使用curl:")
    print(f'curl -H "Authorization: Bearer {token}" http://localhost:5000/api/decks')
    
    print("\n注意: 此令牌仅在开发环境中使用，生产环境中应使用真实的认证流程。")