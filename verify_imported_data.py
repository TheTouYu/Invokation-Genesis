"""
验证导入的卡牌数据
"""
import requests
import json

def verify_imported_cards():
    """验证导入的卡牌数据"""
    print("验证导入的卡牌数据...")
    
    # 获取测试令牌
    from app import create_app
    from models.db_models import db
    app = create_app()
    
    with app.app_context():
        from models.db_models import User
        from werkzeug.security import generate_password_hash
        from models.db_models import _initialized, init_models_db
        _initialized = False  # 重置初始化标记
        init_models_db(db)  # 重新初始化模型
        
        # 检查是否存在测试用户，如不存在则创建
        existing_user = User.query.filter_by(username='test_user').first()
        if not existing_user:
            test_user = User(
                username='test_user',
                email='test@example.com',
                password_hash=generate_password_hash('test_password')
            )
            db.session.add(test_user)
            db.session.commit()
            user_id = test_user.id
        else:
            user_id = existing_user.id
        
        # 生成JWT令牌
        import jwt
        from datetime import datetime, timedelta
        payload = {
            'sub': user_id,
            'user_id': user_id,
            'username': 'test_user',
            'email': 'test@example.com',
            'iat': datetime.utcnow(),
            'exp': datetime.utcnow() + timedelta(days=1)
        }
        
        token = jwt.encode(
            payload, 
            app.config['JWT_SECRET_KEY'], 
            algorithm='HS256'
        )
    
    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json"
    }
    
    base_url = "http://localhost:5000"
    
    print("\n1. 获取所有卡牌（前5张）:")
    try:
        response = requests.get(f"{base_url}/api/cards?per_page=5", headers=headers)
        if response.status_code == 200:
            data = response.json()
            for i, card in enumerate(data.get('cards', [])[:5]):
                print(f"  {i+1}. {card['name']} (类型: {card['card_type']})")
                if 'element_type' in card and card['element_type']:
                    print(f"     元素类型: {card['element_type']}")
        else:
            print(f"  获取卡牌失败: {response.status_code}")
    except Exception as e:
        print(f"  获取卡牌异常: {str(e)}")
    
    print("\n2. 获取角色卡（前5张）:")
    try:
        response = requests.get(f"{base_url}/api/cards/characters?per_page=5", headers=headers)
        if response.status_code == 200:
            data = response.json()
            for i, card in enumerate(data.get('cards', [])[:5]):
                print(f"  {i+1}. {card['name']} (元素: {card.get('element_type', 'N/A')})")
                if 'health' in card:
                    print(f"     生命值: {card['health']}, 技能数: {len(card.get('skills', []))}")
        else:
            print(f"  获取角色卡失败: {response.status_code}")
    except Exception as e:
        print(f"  获取角色卡异常: {str(e)}")
    
    print("\n3. 获取事件卡（前5张）:")
    try:
        response = requests.get(f"{base_url}/api/cards/events?per_page=5", headers=headers)
        if response.status_code == 200:
            data = response.json()
            for i, card in enumerate(data.get('cards', [])[:5]):
                print(f"  {i+1}. {card['name']}")
                if 'cost' in card:
                    print(f"     成本: {card['cost']}")
        else:
            print(f"  获取事件卡失败: {response.status_code}")
    except Exception as e:
        print(f"  获取事件卡异常: {str(e)}")
    
    print(f"\n数据验证完成！")

if __name__ == "__main__":
    verify_imported_cards()