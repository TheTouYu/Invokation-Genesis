"""
更新的卡牌和本地游戏API测试文件
适应数据库重构：ID类型从整数改为字符串
"""
import requests
import json
import sys
import os
import uuid

# 添加项目根目录到Python路径
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

def test_api_endpoints():
    """测试API端点"""
    base_url = "http://localhost:5000/api"
    
    print("开始测试卡牌和本地游戏API...")
    
    # 测试前需要一个有效的JWT令牌，这里我们假设已经通过认证API获得了令牌
    # 由于我们无法直接获取令牌，我们将在测试环境中模拟
    
    # 首先测试健康检查
    try:
        response = requests.get("http://localhost:5000/health")
        if response.status_code == 200:
            print(f"✓ 健康检查: {response.json()}")
        else:
            print(f"✗ 健康检查失败: {response.status_code}")
    except Exception as e:
        print(f"✗ 健康检查异常: {str(e)}")
    
    # 模拟JWT令牌（用于测试，实际使用时需要先登录获取）
    # 注意：在实际测试中，您需要先调用认证API获取JWT令牌
    jwt_token = "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9.eyJmcmVzaCI6ZmFsc2UsImlhdCI6MTUxNjIzOTAyMiwianRpIjoiZGVmYXVsdF90b2tlbl9pZCIsImlkZW50aXR5IjoiMSIsIm5iZiI6MTUxNjIzOTAyMiwicm9sZXMiOiJ1c2VyIiwic2NvcGVzIjpbInVzZXIiXX0.default_encoded_token"
    
    headers = {
        "Authorization": f"Bearer {jwt_token}",
        "Content-Type": "application/json"
    }
    
    print("\n测试卡牌API (需要有效的JWT令牌)...")
    print("注意：以下测试需要有效的JWT令牌，否则将返回401错误")
    
    # 测试获取所有卡牌
    try:
        response = requests.get(f"{base_url}/cards", headers=headers)
        print(f"获取卡牌: 状态码 {response.status_code}")
        if response.status_code == 200:
            data = response.json()
            print(f"  - 返回 {len(data.get('cards', []))} 张卡牌")
        elif response.status_code == 422:
            print("  - 预期：需要有效的JWT令牌")
        else:
            print(f"  - 错误: {response.json()}")
    except Exception as e:
        print(f"获取卡牌异常: {str(e)}")
    
    # 测试获取角色卡牌
    try:
        response = requests.get(f"{base_url}/cards/characters", headers=headers)
        print(f"获取角色卡牌: 状态码 {response.status_code}")
        if response.status_code == 200:
            data = response.json()
            print(f"  - 返回 {len(data.get('cards', []))} 张角色卡牌")
        elif response.status_code == 422:
            print("  - 预期：需要有效的JWT令牌")
        else:
            print(f"  - 错误: {response.json()}")
    except Exception as e:
        print(f"获取角色卡牌异常: {str(e)}")
    
    # 测试获取事件卡牌
    try:
        response = requests.get(f"{base_url}/cards/events", headers=headers)
        print(f"获取事件卡牌: 状态码 {response.status_code}")
        if response.status_code == 200:
            data = response.json()
            print(f"  - 返回 {len(data.get('cards', []))} 张事件卡牌")
        elif response.status_code == 422:
            print("  - 预期：需要有效的JWT令牌")
        else:
            print(f"  - 错误: {response.json()}")
    except Exception as e:
        print(f"获取事件卡牌异常: {str(e)}")
    
    # 测试获取用户卡组
    try:
        response = requests.get(f"{base_url}/decks", headers=headers)
        print(f"获取用户卡组: 状态码 {response.status_code}")
        if response.status_code == 200:
            data = response.json()
            print(f"  - 返回 {len(data.get('decks', []))} 个卡组")
        elif response.status_code == 422:
            print("  - 预期：需要有效的JWT令牌")
        else:
            print(f"  - 错误: {response.json()}")
    except Exception as e:
        print(f"获取用户卡组异常: {str(e)}")
    
    print("\n测试本地游戏API (需要有效的JWT令牌)...")
    
    # 使用UUID生成字符串格式的卡组ID
    unique_deck_id = str(uuid.uuid4())
    
    # 测试开始本地游戏（需要先创建卡组）
    start_game_payload = {
        "deck_id": unique_deck_id,  # 使用字符串格式的ID
        "opponent_type": "ai"
    }
    
    try:
        response = requests.post(f"{base_url}/local-game/start", 
                                headers=headers, 
                                json=start_game_payload)
        print(f"开始本地游戏: 状态码 {response.status_code}")
        if response.status_code == 200:
            print("  - 游戏开始成功")
        elif response.status_code == 401 or response.status_code == 422:
            print("  - 预期：需要有效的JWT令牌")
        elif response.status_code == 400:
            print("  - 卡组不存在或无效")
        else:
            print(f"  - 错误: {response.json()}")
    except Exception as e:
        print(f"开始本地游戏异常: {str(e)}")
    
    print("\nAPI测试完成")
    print("\n要进行完整的API测试，请:")
    print("1. 启动Flask应用: uv run python app.py")
    print("2. 通过/api/auth/register注册用户")
    print("3. 通过/api/auth/login获取JWT令牌")
    print("4. 使用获取的令牌测试上述API端点")
    print("\n注意：由于数据库重构，所有ID现在使用字符串格式（基于UUID）")

if __name__ == "__main__":
    test_api_endpoints()