"""
API端点测试脚本（使用测试令牌）
"""
import os
import sys
import json
import requests

def get_test_token_and_user():
    """获取测试令牌和用户ID"""
    from app import create_app, db
    app = create_app()
    
    with app.app_context():
        # 导入User模型
        from models.db_models import User
        from werkzeug.security import generate_password_hash
        
        # 检查是否已存在测试用户
        existing_user = User.query.filter_by(username='test_user').first()
        if existing_user:
            user_id = existing_user.id
        else:
            # 创建测试用户
            test_user = User(
                username='test_user',
                email='test@example.com',
                password_hash=generate_password_hash('test_password')
            )
            
            db.session.add(test_user)
            db.session.commit()
            
            user_id = test_user.id
        
        # 生成令牌
        import jwt
        from datetime import datetime, timedelta
        payload = {
            'sub': user_id,  # JWT标准要求的用户标识符
            'user_id': user_id,
            'username': 'test_user',
            'email': 'test@example.com',
            'iat': datetime.utcnow(),
            'exp': datetime.utcnow() + timedelta(days=1)  # 1天后过期
        }
        
        token = jwt.encode(
            payload, 
            app.config['JWT_SECRET_KEY'], 
            algorithm='HS256'
        )
        
        return token, user_id

def test_api_endpoints():
    """使用测试令牌测试API端点"""
    # 生成测试令牌
    print("生成测试令牌...")
    token, user_id = get_test_token_and_user()
    
    base_url = "http://localhost:5000"
    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json"
    }
    
    print(f"使用令牌: {token[:20]}...")
    print(f"测试用户ID: {user_id}")
    print("\n开始测试API端点...")
    
    # 测试健康检查
    print("\n1. 测试健康检查端点...")
    try:
        response = requests.get(f"{base_url}/health")
        if response.status_code == 200:
            print(f"✓ 健康检查: {response.json()}")
        else:
            print(f"✗ 健康检查失败: {response.status_code}")
    except Exception as e:
        print(f"✗ 健康检查异常: {str(e)}")
    
    # 测试获取卡牌
    print("\n2. 测试获取卡牌端点...")
    try:
        response = requests.get(f"{base_url}/api/cards", headers=headers)
        if response.status_code == 200:
            data = response.json()
            print(f"✓ 获取卡牌: {len(data.get('cards', []))} 张卡牌")
        else:
            print(f"✗ 获取卡牌失败: {response.status_code} - {response.text}")
    except Exception as e:
        print(f"✗ 获取卡牌异常: {str(e)}")
    
    # 测试获取角色卡
    print("\n3. 测试获取角色卡端点...")
    try:
        response = requests.get(f"{base_url}/api/cards/characters", headers=headers)
        if response.status_code == 200:
            data = response.json()
            print(f"✓ 获取角色卡: {len(data.get('cards', []))} 张角色卡")
        else:
            print(f"✗ 获取角色卡失败: {response.status_code} - {response.text}")
    except Exception as e:
        print(f"✗ 获取角色卡异常: {str(e)}")
    
    # 测试获取用户卡组
    print("\n4. 测试获取用户卡组端点...")
    try:
        response = requests.get(f"{base_url}/api/decks", headers=headers)
        if response.status_code == 200:
            data = response.json()
            print(f"✓ 获取卡组: {len(data.get('decks', []))} 个卡组")
        else:
            print(f"✗ 获取卡组失败: {response.status_code} - {response.text}")
    except Exception as e:
        print(f"✗ 获取卡组异常: {str(e)}")
    
    # 尝试创建一个测试卡组
    print("\n5. 测试创建卡组端点...")
    try:
        # 注意：这里需要有效卡牌ID，由于我们没有预设数据，我们先获取现有卡牌
        cards_response = requests.get(f"{base_url}/api/cards", headers=headers)
        if cards_response.status_code == 200:
            cards_data = cards_response.json()
            card_list = [card['id'] for card in cards_data.get('cards', [])[:30]]  # 取前30张卡
            
            if len(card_list) >= 30:  # 只有在有足够的卡牌时才创建
                create_deck_data = {
                    "name": "测试卡组",
                    "description": "自动生成的测试卡组",
                    "cards": card_list
                }
                
                response = requests.post(
                    f"{base_url}/api/decks", 
                    headers=headers, 
                    json=create_deck_data
                )
                if response.status_code == 201:
                    print("✓ 创建卡组成功")
                else:
                    print(f"✗ 创建卡组失败: {response.status_code} - {response.text}")
            else:
                print("⚠ 卡牌数量不足，跳过创建卡组测试")
        else:
            print(f"⚠ 无法获取卡牌数据: {cards_response.status_code}")
    except Exception as e:
        print(f"✗ 创建卡组异常: {str(e)}")
    
    print("\n" + "="*50)
    print("API测试完成")
    print(f"\n要手动测试其他端点，可使用以下令牌:")
    print(f"Authorization: Bearer {token}")
    print("\n示例curl命令:")
    print(f'curl -H "Authorization: Bearer {token}" http://localhost:5000/api/decks')

if __name__ == "__main__":
    print("七圣召唤API测试工具")
    print("=" * 50)
    
    # 检查服务器是否运行
    try:
        response = requests.get("http://localhost:5000/health", timeout=5)
        if response.status_code == 200:
            print("✓ 服务器运行正常")
            test_api_endpoints()
        else:
            print("✗ 服务器未响应，请先启动服务器: uv run python app.py")
    except requests.exceptions.ConnectionError:
        print("✗ 无法连接到服务器，请先启动服务器: uv run python app.py")
    except requests.exceptions.Timeout:
        print("✗ 连接服务器超时，请先启动服务器: uv run python app.py")