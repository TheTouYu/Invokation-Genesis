"""
更新的卡牌和本地游戏API测试文件
使用Flask测试客户端和正确的测试实践
"""
import json
import pytest
from app import create_app
from database_manager import db_manager
from models.db_models import User, CardData, Deck

# 为兼容性，创建一个db引用
def get_db():
    return db_manager.get_db()

db = get_db()
from werkzeug.security import generate_password_hash
from flask_jwt_extended import create_access_token


@pytest.fixture
def client():
    """创建测试客户端"""
    app = create_app()
    app.config['TESTING'] = True
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///:memory:'
    app.config['JWT_SECRET_KEY'] = 'test-secret-key'

    with app.app_context():
        db.create_all()

    with app.test_client() as client:
        yield client


def get_auth_headers(client):
    """获取认证头"""
    import uuid
    unique_id = str(uuid.uuid4())[:8]
    test_username = f'testuser_{unique_id}'
    test_email = f'test_{unique_id}@example.com'
    hashed_password = generate_password_hash('password123')
    
    with client.application.app_context():
        # 添加测试用户
        test_user = User(
            username=test_username, 
            email=test_email, 
            password_hash=hashed_password
        )
        db.session.add(test_user)
        db.session.commit()
        
        # 添加测试卡牌
        test_card = CardData(
            id=f'test_card_1_{unique_id}',
            name='测试卡牌1',
            card_type='事件牌',
            description='测试用卡牌',
            cost='[{"type": "万能", "value": 1}]',
            is_active=True
        )
        db.session.add(test_card)
        db.session.commit()
    
    # 登录获取token
    response = client.post('/api/auth/login', json={
        'username': test_username,
        'password': 'password123'
    })
    data = json.loads(response.data)
    token = data.get('access_token', '')
    headers = {'Authorization': f'Bearer {token}', 'Content-Type': 'application/json'}
    
    return headers


def test_api_endpoints(client):
    """测试API端点"""
    headers = get_auth_headers(client)
    
    print("开始测试健康检查...")
    # 测试健康检查
    response = client.get('/health')
    assert response.status_code == 200
    data = json.loads(response.data)
    assert data['status'] == 'healthy'
    print("✓ 健康检查通过")

    print("\n测试卡牌API...")
    # 测试获取所有卡牌
    response = client.get('/api/cards', headers=headers)
    assert response.status_code == 200
    data = json.loads(response.data)
    assert 'cards' in data
    print(f"✓ 获取卡牌: 返回 {len(data.get('cards', []))} 张卡牌")

    # 测试获取角色卡牌
    response = client.get('/api/cards/characters', headers=headers)
    assert response.status_code == 200
    print("✓ 获取角色卡牌成功")

    # 测试获取事件卡牌
    response = client.get('/api/cards/events', headers=headers)
    assert response.status_code == 200
    print("✓ 获取事件卡牌成功")

    # 测试获取用户卡组
    response = client.get('/api/decks', headers=headers)
    assert response.status_code == 200
    data = json.loads(response.data)
    assert 'decks' in data
    print(f"✓ 获取用户卡组: 返回 {len(data.get('decks', []))} 个卡组")

    print("\nAPI测试完成")


if __name__ == "__main__":
    # 为直接运行提供一个简单版本
    import sys
    import os
    sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    
    app = create_app()
    app.config['TESTING'] = True
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///:memory:'
    app.config['JWT_SECRET_KEY'] = 'test-secret-key'

    with app.app_context():
        from models.db_models import db
        db.create_all()
        
        with app.test_client() as client:
            test_api_endpoints(client)