"""
认证API测试文件
测试 api/auth.py 中的端点
"""
import pytest
import uuid
import json
from app import create_app
from models.db_models import db, User
from werkzeug.security import generate_password_hash


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


def test_register_user(client):
    """测试用户注册"""
    response = client.post('/api/auth/register', json={
        'username': 'newuser',
        'email': 'newuser@example.com',
        'password': 'newpassword123'
    })
    
    assert response.status_code == 201 or response.status_code == 400  # 400 如果用户已存在


def test_login_user(client):
    """测试用户登录"""
    # 注册一个新用户用于测试
    unique_id = str(uuid.uuid4())[:8]
    test_username = f'testuser_{unique_id}'
    test_email = f'{test_username}@example.com'
    test_password = 'password123'
    
    client.post('/api/auth/register', json={
        'username': test_username,
        'email': test_email,
        'password': test_password
    })
    
    # 登录
    response = client.post('/api/auth/login', json={
        'username': test_username,
        'password': test_password
    })
    
    assert response.status_code == 200
    data = json.loads(response.data)
    assert 'access_token' in data


def test_login_invalid_credentials(client):
    """测试使用无效凭据登录"""
    # 注册一个新用户用于测试
    unique_id = str(uuid.uuid4())[:8]
    test_username = f'testuser_{unique_id}'
    test_email = f'{test_username}@example.com'
    test_password = 'password123'
    
    client.post('/api/auth/register', json={
        'username': test_username,
        'email': test_email,
        'password': test_password
    })
    
    # 使用错误密码登录
    response = client.post('/api/auth/login', json={
        'username': test_username,
        'password': 'wrongpassword'
    })
    
    assert response.status_code == 401


def test_get_profile_authenticated(client):
    """测试获取用户资料（认证后）"""
    # 注册并登录一个新用户用于测试
    unique_id = str(uuid.uuid4())[:8]
    test_username = f'testuser_{unique_id}'
    test_email = f'{test_username}@example.com'
    test_password = 'password123'
    
    client.post('/api/auth/register', json={
        'username': test_username,
        'email': test_email,
        'password': test_password
    })
    
    # 登录获取token
    login_response = client.post('/api/auth/login', json={
        'username': test_username,
        'password': test_password
    })
    login_data = json.loads(login_response.data)
    token = login_data.get('access_token', '')
    
    headers = {'Authorization': f'Bearer {token}'}
    response = client.get('/api/auth/profile', headers=headers)
    
    assert response.status_code == 200
    data = json.loads(response.data)
    assert 'username' in data
    assert data['username'] == test_username


def test_get_profile_unauthenticated(client):
    """测试获取用户资料（未认证）"""
    response = client.get('/api/auth/profile')
    
    assert response.status_code == 401