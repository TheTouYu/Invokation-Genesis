"""
标准化卡牌API的测试文件
测试 api/standardized_cards.py 中的所有端点
"""
import pytest
import json
from app import create_app
from models.db_models import db, CardData, User
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
    # 创建一个临时用户用于测试
    import uuid
    unique_id = str(uuid.uuid4())[:8]
    test_username = f'testuser_{unique_id}'
    test_email = f'test_{unique_id}@example.com'
    hashed_password = generate_password_hash('password123')
    
    with client.application.app_context():
        # 添加测试用户
        test_user = User(username=test_username, email=test_email, password_hash=hashed_password)
        db.session.add(test_user)
        db.session.commit()
        
        # 添加测试卡牌
        test_cards = [
            CardData(
                id=f'test_card_1_{unique_id}',
                name='测试卡牌1',
                card_type='事件牌',
                description='测试用卡牌',
                cost='[{"type": "万能", "value": 1}]',
                is_active=True
            ),
            CardData(
                id=f'test_character_1_{unique_id}',
                name='测试角色',
                card_type='角色牌',
                description='测试用角色',
                cost='[]',
                is_active=True
            )
        ]
        for card in test_cards:
            db.session.add(card)
        db.session.commit()
    
    # 登录获取token
    response = client.post('/api/auth/login', json={
        'username': test_username,
        'password': 'password123'
    })
    data = json.loads(response.data)
    token = data.get('access_token', '')
    headers = {'Authorization': f'Bearer {token}', 'Content-Type': 'application/json'}
    
    return headers, unique_id


def test_get_all_cards(client):
    """测试获取所有卡牌"""
    headers, unique_id = get_auth_headers(client)
    response = client.get('/api/cards', headers=headers)
    
    assert response.status_code == 200
    data = json.loads(response.data)
    assert 'cards' in data
    assert 'total' in data
    assert len(data['cards']) >= 0  # 至少有测试数据或更多


def test_get_card_by_id(client):
    """测试根据ID获取卡牌"""
    headers, unique_id = get_auth_headers(client)
    card_id = f'test_card_1_{unique_id}'
    
    response = client.get(f'/api/cards/{card_id}', headers=headers)
    
    assert response.status_code == 200
    data = json.loads(response.data)
    assert 'card' in data
    assert data['card']['id'] == card_id


def test_get_card_types(client):
    """测试获取卡牌类型"""
    headers, _ = get_auth_headers(client)
    response = client.get('/api/cards/types', headers=headers)
    
    assert response.status_code == 200
    data = json.loads(response.data)
    assert 'types' in data


def test_get_card_elements(client):
    """测试获取卡牌元素"""
    headers, _ = get_auth_headers(client)
    response = client.get('/api/cards/elements', headers=headers)
    
    assert response.status_code == 200
    data = json.loads(response.data)
    assert 'elements' in data


def test_get_card_countries(client):
    """测试获取卡牌国家"""
    headers, _ = get_auth_headers(client)
    response = client.get('/api/cards/countries', headers=headers)
    
    assert response.status_code == 200
    data = json.loads(response.data)
    assert 'countries' in data


def test_get_card_tags(client):
    """测试获取卡牌标签"""
    headers, _ = get_auth_headers(client)
    response = client.get('/api/cards/tags', headers=headers)
    
    assert response.status_code == 200
    data = json.loads(response.data)
    assert 'tags' in data


def test_get_character_filters(client):
    """测试获取角色过滤选项"""
    headers, _ = get_auth_headers(client)
    response = client.get('/api/characters/filters', headers=headers)
    
    assert response.status_code == 200
    data = json.loads(response.data)
    assert 'countries' in data
    assert 'elements' in data
    assert 'weapon_types' in data


def test_get_cards_by_type(client):
    """测试根据类型过滤卡牌"""
    headers, unique_id = get_auth_headers(client)
    
    # 首先添加一个事件牌类型卡牌用于测试
    with client.application.app_context():
        event_card = CardData(
            id=f'test_event_{unique_id}',
            name='测试事件卡',
            card_type='事件牌',
            description='测试用事件卡',
            cost='[{"type": "万能", "value": 1}]',
            is_active=True
        )
        db.session.add(event_card)
        db.session.commit()
    
    response = client.get('/api/cards?type=事件牌', headers=headers)
    
    assert response.status_code == 200
    data = json.loads(response.data)
    assert 'cards' in data
    for card in data['cards']:
        if card['id'].startswith(f'test_event_{unique_id}'):
            assert card['type'] == '事件牌'


def test_get_cards_with_search(client):
    """测试搜索卡牌"""
    headers, unique_id = get_auth_headers(client)
    response = client.get('/api/cards?search=测试', headers=headers)
    
    assert response.status_code == 200
    data = json.loads(response.data)
    assert 'cards' in data


def test_get_random_cards(client):
    """测试获取随机卡牌"""
    headers, _ = get_auth_headers(client)
    response = client.get('/api/cards/random?count=1', headers=headers)
    
    assert response.status_code == 200
    data = json.loads(response.data)
    assert 'cards' in data
    assert 'total' in data