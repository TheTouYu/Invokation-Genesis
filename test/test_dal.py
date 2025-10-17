"""
测试数据访问层(DAL)功能
"""
import pytest
from app import create_app
from dal import db_dal
from werkzeug.security import generate_password_hash


@pytest.fixture
def app():
    """创建测试应用"""
    app = create_app()
    app.config['TESTING'] = True
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///:memory:'
    app.config['JWT_SECRET_KEY'] = 'test-secret-key'
    return app


@pytest.fixture
def client(app):
    """创建测试客户端"""
    with app.app_context():
        from models.db_models import db
        db.create_all()

    with app.test_client() as client:
        yield client


@pytest.fixture
def db_session(app):
    """提供数据库会话"""
    with app.app_context():
        yield app


def test_user_dal_operations(client, app):
    """测试用户数据访问层操作"""
    import uuid
    unique_id = str(uuid.uuid4())[:8]
    
    with app.app_context():
        # 测试创建用户
        user = db_dal.users.create_user(
            username=f'testuser_{unique_id}',
            email=f'test_{unique_id}@example.com',
            password_hash=generate_password_hash('password123')
        )
        
        assert user is not None
        assert user.username == f'testuser_{unique_id}'
        assert isinstance(user.id, str)  # ID 应该是字符串类型
        
        # 测试通过ID获取用户
        retrieved_user = db_dal.users.get_user_by_id(user.id)
        assert retrieved_user is not None
        assert retrieved_user.id == user.id
        
        # 测试通过用户名获取用户
        retrieved_by_username = db_dal.users.get_user_by_username(f'testuser_{unique_id}')
        assert retrieved_by_username is not None
        assert retrieved_by_username.id == user.id
        
        # 测试通过邮箱获取用户
        retrieved_by_email = db_dal.users.get_user_by_email(f'test_{unique_id}@example.com')
        assert retrieved_by_email is not None
        assert retrieved_by_email.id == user.id
        
        # 测试更新用户
        success = db_dal.users.update_user(user.id, is_active=False)
        assert success is True
        
        updated_user = db_dal.users.get_user_by_id(user.id)
        assert updated_user.is_active is False
        
        # 测试删除用户
        success = db_dal.users.delete_user(user.id)
        assert success is True
        
        deleted_user = db_dal.users.get_user_by_id(user.id)
        assert deleted_user is None


def test_card_dal_operations(client, app):
    """测试卡牌数据访问层操作"""
    import uuid
    unique_id = str(uuid.uuid4())[:8]
    
    with app.app_context():
        # 测试创建卡牌
        card = db_dal.cards.create_card(
            name=f'测试卡牌_{unique_id}',
            card_type='事件牌',
            description='测试用卡牌',
            cost='[{"type": "万能", "value": 1}]'
        )
        
        assert card is not None
        assert card.name == f'测试卡牌_{unique_id}'
        assert isinstance(card.id, str)  # ID 应该是字符串类型
        
        # 测试通过ID获取卡牌
        retrieved_card = db_dal.cards.get_card_by_id(card.id)
        assert retrieved_card is not None
        assert retrieved_card.id == card.id
        
        # 测试通过类型获取卡牌
        cards_by_type = db_dal.cards.get_cards_by_type('事件牌')
        assert len(cards_by_type) >= 1
        assert any(c.id == card.id for c in cards_by_type)
        
        # 测试通过稀有度获取卡牌
        cards_by_rarity = db_dal.cards.get_cards_by_rarity(1)
        # 注意：新创建的卡牌可能没有设置稀有度，默认为None，所以这里可能为空
        
        # 测试搜索卡牌
        search_results = db_dal.cards.search_cards(f'测试卡牌_{unique_id}')
        assert len(search_results) >= 1
        assert any(c.id == card.id for c in search_results)
        
        # 测试更新卡牌
        success = db_dal.cards.update_card(card.id, name=f'更新的卡牌_{unique_id}')
        assert success is True
        
        updated_card = db_dal.cards.get_card_by_id(card.id)
        assert updated_card.name == f'更新的卡牌_{unique_id}'


def test_deck_dal_operations(client, app):
    """测试卡组数据访问层操作"""
    import uuid
    unique_id = str(uuid.uuid4())[:8]
    
    with app.app_context():
        # 首先创建一个用户
        user = db_dal.users.create_user(
            username=f'deck_test_user_{unique_id}',
            email=f'deck_test_{unique_id}@example.com',
            password_hash=generate_password_hash('password123')
        )
        
        # 测试创建卡组
        deck = db_dal.decks.create_deck(
            name=f'测试卡组_{unique_id}',
            user_id=user.id,
            cards=[f'card1_{unique_id}', f'card2_{unique_id}', f'card3_{unique_id}'],
            description='测试描述'
        )
        
        assert deck is not None
        assert deck.name == f'测试卡组_{unique_id}'
        assert isinstance(deck.id, str)  # ID 应该是字符串类型
        assert deck.user_id == user.id
        
        # 测试获取用户卡组
        user_decks = db_dal.decks.get_decks_by_user(user.id)
        assert len(user_decks) >= 1
        assert any(d.id == deck.id for d in user_decks)
        
        # 测试通过ID获取卡组
        retrieved_deck = db_dal.decks.get_deck_by_id(deck.id)
        assert retrieved_deck is not None
        assert retrieved_deck.id == deck.id
        
        # 测试更新卡组
        success = db_dal.decks.update_deck(deck.id, name=f'更新的卡组_{unique_id}')
        assert success is True
        
        updated_deck = db_dal.decks.get_deck_by_id(deck.id)
        assert updated_deck.name == f'更新的卡组_{unique_id}'
        
        # 测试删除卡组
        success = db_dal.decks.delete_deck(deck.id)
        assert success is True
        
        deleted_deck = db_dal.decks.get_deck_by_id(deck.id)
        assert deleted_deck is None