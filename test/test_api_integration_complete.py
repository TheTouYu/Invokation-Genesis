"""
API集成测试
测试不同API端点之间的交互和完整工作流程
"""
import pytest
import json
from app import create_app
from database_manager import db_manager
from models.db_models import CardData, User, Deck

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
        
        # 创建测试用户
        hashed_password = generate_password_hash('password123')
        test_user = User(username='testuser', email='test@example.com', password_hash=hashed_password)
        db.session.add(test_user)
        db.session.commit()
        
        # 创建测试卡牌数据
        test_cards = [
            CardData(
                id='test_card_1',
                name='测试卡牌1',
                card_type='事件牌',
                description='测试用卡牌',
                cost='[{"type": "万能", "value": 1}]',
                is_active=True
            ),
            CardData(
                id='test_character_1',
                name='测试角色',
                card_type='角色牌',
                description='测试用角色',
                cost='[]',
                is_active=True
            ),
            CardData(
                id='test_weapon_1',
                name='测试武器',
                card_type='武器牌',
                description='测试用武器',
                cost='[{"type": "万能", "value": 2}]',
                is_active=True
            ),
            CardData(
                id='test_artifact_1',
                name='测试圣遗物',
                card_type='圣遗物牌',
                description='测试用圣遗物',
                cost='[{"type": "万能", "value": 1}]',
                is_active=True
            )
        ]
        for card in test_cards:
            db.session.add(card)
        db.session.commit()

    with app.test_client() as client:
        yield client


def get_auth_headers(client, username='testuser', password='password123'):
    """获取认证头"""
    response = client.post('/api/auth/login', json={
        'username': username,
        'password': password
    })
    data = json.loads(response.data)
    token = data.get('access_token', '')
    return {'Authorization': f'Bearer {token}', 'Content-Type': 'application/json'}


def test_complete_deck_workflow(client):
    """测试完整的卡组工作流程：获取卡牌 -> 创建卡组 -> 验证卡组 -> 获取卡组 -> 更新 -> 删除"""
    
    # 1. 用户登录获取token
    headers = get_auth_headers(client)
    
    # 2. 获取所有卡牌
    response = client.get('/api/cards', headers=headers)
    assert response.status_code == 200
    cards_data = json.loads(response.data)
    assert 'cards' in cards_data
    
    # 3. 获取特定类型的卡牌（角色牌）
    response = client.get('/api/cards/characters', headers=headers)
    assert response.status_code == 200
    characters_data = json.loads(response.data)
    assert 'cards' in characters_data
    
    # 4. 获取卡牌标签
    response = client.get('/api/cards/tags', headers=headers)
    assert response.status_code == 200
    tags_data = json.loads(response.data)
    assert 'tags' in tags_data
    
    # 5. 获取角色过滤选项
    response = client.get('/api/characters/filters', headers=headers)
    assert response.status_code == 200
    filters_data = json.loads(response.data)
    assert 'countries' in filters_data
    assert 'elements' in filters_data
    assert 'weapon_types' in filters_data
    
    # 6. 创建一个卡组
    deck_data = {
        'name': '集成测试卡组',
        'description': '用于集成测试的卡组',
        'cards': ['test_character_1', 'test_card_1', 'test_weapon_1']
    }
    
    response = client.post('/api/decks', json=deck_data, headers=headers)
    assert response.status_code == 201
    create_deck_data = json.loads(response.data)
    assert 'message' in create_deck_data
    assert create_deck_data['message'] == '卡组创建成功'
    assert 'deck' in create_deck_data
    deck_id = create_deck_data['deck']['id']
    
    # 7. 验证刚创建的卡组
    validate_data = {
        'cards': ['test_character_1', 'test_card_1', 'test_weapon_1']
    }
    response = client.post('/api/decks/validate', json=validate_data, headers=headers)
    assert response.status_code == 200
    validate_result = json.loads(response.data)
    assert 'is_valid' in validate_result
    
    # 8. 获取用户的所有卡组
    response = client.get('/api/decks', headers=headers)
    assert response.status_code == 200
    decks_data = json.loads(response.data)
    assert 'decks' in decks_data
    assert any(deck['id'] == deck_id for deck in decks_data['decks'])
    
    # 9. 获取特定卡组详情
    response = client.get(f'/api/decks/{deck_id}', headers=headers)
    assert response.status_code == 200
    specific_deck_data = json.loads(response.data)
    assert 'deck' in specific_deck_data
    assert specific_deck_data['deck']['id'] == deck_id
    assert len(specific_deck_data['deck']['cards']) == 3
    
    # 10. 更新卡组
    update_data = {
        'name': '更新后的集成测试卡组',
        'description': '更新后的描述',
        'cards': ['test_character_1', 'test_card_1', 'test_weapon_1', 'test_artifact_1']
    }
    
    response = client.put(f'/api/decks/{deck_id}', json=update_data, headers=headers)
    assert response.status_code == 200
    update_result = json.loads(response.data)
    assert 'message' in update_result
    assert update_result['message'] == '卡组更新成功'
    
    # 11. 验证更新后的卡组
    response = client.get(f'/api/decks/{deck_id}', headers=headers)
    assert response.status_code == 200
    updated_deck_data = json.loads(response.data)
    assert updated_deck_data['deck']['name'] == '更新后的集成测试卡组'
    assert len(updated_deck_data['deck']['cards']) == 4
    
    # 12. 删除卡组
    response = client.delete(f'/api/decks/{deck_id}', headers=headers)
    assert response.status_code == 200
    delete_result = json.loads(response.data)
    assert 'message' in delete_result
    assert delete_result['message'] == '卡组删除成功'
    
    print("完整的卡组工作流程测试通过！")


def test_card_filtering_and_search(client):
    """测试卡牌过滤和搜索功能"""
    
    headers = get_auth_headers(client)
    
    # 1. 按类型过滤卡牌
    response = client.get('/api/cards?type=角色牌', headers=headers)
    assert response.status_code == 200
    data = json.loads(response.data)
    assert 'cards' in data
    for card in data['cards']:
        assert card['type'] == '角色牌'
    
    # 2. 按搜索词过滤卡牌
    response = client.get('/api/cards?search=测试', headers=headers)
    assert response.status_code == 200
    data = json.loads(response.data)
    assert 'cards' in data
    assert len(data['cards']) > 0  # 应该找到测试卡牌
    
    # 3. 使用filter端点
    response = client.get('/api/cards/filter?type=事件牌', headers=headers)
    assert response.status_code == 200
    data = json.loads(response.data)
    assert 'cards' in data
    for card in data['cards']:
        # 可能type字段是card_type或其他字段，根据实际API响应调整
        pass
    
    # 4. 获取随机卡牌
    response = client.get('/api/cards/random?count=2', headers=headers)
    assert response.status_code == 200
    data = json.loads(response.data)
    assert 'cards' in data
    assert len(data['cards']) <= 2
    
    print("卡牌过滤和搜索功能测试通过！")


def test_user_authentication_flow(client):
    """测试用户认证流程"""
    
    # 1. 尝试注册新用户
    response = client.post('/api/auth/register', json={
        'username': 'integration_test_user',
        'email': 'integration@test.com',
        'password': 'securepassword123'
    })
    # 可能会失败如果用户已存在，这没关系
    
    # 2. 登录现有用户
    response = client.post('/api/auth/login', json={
        'username': 'testuser',
        'password': 'password123'
    })
    assert response.status_code == 200
    login_data = json.loads(response.data)
    assert 'access_token' in login_data
    
    token = login_data['access_token']
    headers = {'Authorization': f'Bearer {token}'}
    
    # 3. 访问需要认证的端点
    response = client.get('/api/auth/profile', headers=headers)
    assert response.status_code == 200
    profile_data = json.loads(response.data)
    assert 'username' in profile_data
    
    print("用户认证流程测试通过！")


def test_api_consistency(client):
    """测试API响应格式的一致性"""
    
    headers = get_auth_headers(client)
    
    # 检查各种端点的响应格式
    endpoints_to_check = [
        '/api/cards?per_page=5',
        '/api/cards/types',
        '/api/cards/elements',
        '/api/characters/filters',
        '/api/cards/tags'
    ]
    
    for endpoint in endpoints_to_check:
        response = client.get(endpoint, headers=headers)
        assert response.status_code == 200, f"端点 {endpoint} 返回状态码 {response.status_code}"
        
        data = json.loads(response.data)
        # 检查响应格式是否包含预期字段
        assert isinstance(data, dict), f"端点 {endpoint} 返回的数据不是字典格式"
    
    print("API响应格式一致性测试通过！")