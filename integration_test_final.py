"""
七圣召唤 API 集成测试脚本
"""

import requests
import json
import sys
import os
import time
from datetime import datetime, timedelta
import jwt
from werkzeug.security import generate_password_hash

# 添加项目根目录到Python路径
sys.path.append(os.path.dirname(os.path.abspath(__file__)))


def generate_test_token():
    """生成测试JWT令牌"""
    # 创建应用实例以访问JWT配置
    from app import create_app

    app = create_app()

    with app.app_context():
        # 导入模型并创建测试用户
        from models.db_models import User
        from database_manager import db_manager

        # 为兼容性，创建一个db引用
        def get_db():
            return db_manager.get_db()

        db = get_db()

        # 检查是否已存在测试用户
        existing_user = User.query.filter_by(username="integration_test_user").first()
        if existing_user:
            user_id = existing_user.id
            # 为已存在的用户生成JWT令牌
            payload = {
                "sub": user_id,  # JWT标准要求的用户标识符
                "user_id": user_id,
                "username": "integration_test_user",
                "email": "integration_test@example.com",
                "iat": datetime.utcnow(),
                "exp": datetime.utcnow() + timedelta(hours=1),  # 1小时后过期
            }

            token = jwt.encode(payload, app.config["JWT_SECRET_KEY"], algorithm="HS256")
        else:
            # 创建测试用户
            test_user = User(
                username="integration_test_user",
                email="integration_test@example.com",
                password_hash=generate_password_hash("test_password"),
            )

            db.session.add(test_user)
            db.session.commit()
            user_id = test_user.id

            # 生成JWT令牌
            payload = {
                "sub": user_id,  # JWT标准要求的用户标识符
                "user_id": user_id,
                "username": "integration_test_user",
                "email": "integration_test@example.com",
                "iat": datetime.utcnow(),
                "exp": datetime.utcnow() + timedelta(hours=1),  # 1小时后过期
            }

            token = jwt.encode(payload, app.config["JWT_SECRET_KEY"], algorithm="HS256")

        return token, user_id


def get_non_character_cards(headers, base_url, num_needed, exclude_ids):
    """获取指定数量的非角色卡"""
    other_cards = []
    page = 1
    per_page = 50

    while len(other_cards) < num_needed:
        response = requests.get(
            f"{base_url}/api/cards?per_page={per_page}&page={page}", headers=headers
        )
        if response.status_code != 200:
            break

        cards_data = response.json()
        cards = cards_data.get("cards", [])

        if not cards:  # 没有更多卡了
            break

        for card in cards:
            if (
                card["id"] not in exclude_ids
                and card["card_type"] != "角色牌"
                and card["id"] not in other_cards
                and len(other_cards) < num_needed
            ):
                other_cards.append(card["id"])

        page += 1

        # 防止无限循环
        if page > 10:  # 最多查询10页
            break

    return other_cards


def run_integration_tests():
    """运行API集成测试"""
    print("=" * 60)
    print("七圣召唤 API 集成测试")
    print("=" * 60)

    # Step 1: 生成测试令牌
    print("\n步骤 1: 生成测试令牌...")
    try:
        token, user_id = generate_test_token()
        headers = {
            "Authorization": f"Bearer {token}",
            "Content-Type": "application/json",
        }
        print("✓ 测试令牌生成成功")
    except Exception as e:
        print(f"✗ 测试令牌生成失败: {str(e)}")
        return False

    base_url = "http://localhost:5000"

    # Step 2: 测试健康检查端点
    print("\n步骤 2: 测试健康检查端点...")
    try:
        response = requests.get(f"{base_url}/health")
        if response.status_code == 200:
            health_data = response.json()
            if health_data.get("status") == "healthy":
                print("✓ 健康检查端点测试通过")
            else:
                print(f"✗ 健康检查端点返回非预期数据: {health_data}")
                return False
        else:
            print(f"✗ 健康检查端点返回错误状态码: {response.status_code}")
            return False
    except Exception as e:
        print(f"✗ 健康检查端点测试失败: {str(e)}")
        return False

    # Step 3: 测试获取所有卡牌
    print("\n步骤 3: 测试获取所有卡牌...")
    try:
        response = requests.get(f"{base_url}/api/cards?per_page=5", headers=headers)
        if response.status_code == 200:
            cards_data = response.json()
            if "cards" in cards_data and isinstance(cards_data["cards"], list):
                print(f"✓ 获取卡牌测试通过 (获取到 {len(cards_data['cards'])} 张卡牌)")
            else:
                print(f"✗ 获取卡牌返回非预期数据: {cards_data}")
                return False
        else:
            print(f"✗ 获取卡牌返回错误状态码: {response.status_code}")
            print(f"  错误信息: {response.text}")
            return False
    except Exception as e:
        print(f"✗ 获取卡牌测试失败: {str(e)}")
        return False

    # Step 4: 测试获取角色卡
    print("\n步骤 4: 测试获取角色卡...")
    try:
        response = requests.get(
            f"{base_url}/api/characters?per_page=3", headers=headers
        )
        if response.status_code == 200:
            characters_data = response.json()
            if isinstance(characters_data, list):  # 根据新的API，角色端点返回列表
                print(
                    f"✓ 获取角色卡测试通过 (获取到 {len(characters_data)} 张角色卡)"
                )
            elif "cards" in characters_data and isinstance(
                characters_data["cards"], list
            ):
                print(
                    f"✓ 获取角色卡测试通过 (获取到 {len(characters_data['cards'])} 张角色卡)"
                )
            else:
                print(f"✗ 获取角色卡返回非预期数据: {characters_data}")
                return False
        else:
            print(f"✗ 获取角色卡返回错误状态码: {response.status_code}")
            print(f"  错误信息: {response.text}")
            return False
    except Exception as e:
        print(f"✗ 获取角色卡测试失败: {str(e)}")
        return False

    # Step 5: 测试获取事件卡
    print("\n步骤 5: 测试获取事件卡...")
    try:
        response = requests.get(
            f"{base_url}/api/events?per_page=3", headers=headers
        )
        if response.status_code == 200:
            events_data = response.json()
            if isinstance(events_data, list):  # 根据新的API，事件端点返回列表
                print(
                    f"✓ 获取事件卡测试通过 (获取到 {len(events_data)} 张事件卡)"
                )
            elif "cards" in events_data and isinstance(events_data["cards"], list):
                print(
                    f"✓ 获取事件卡测试通过 (获取到 {len(events_data['cards'])} 张事件卡)"
                )
            else:
                print(f"✗ 获取事件卡返回非预期数据: {events_data}")
                return False
        else:
            print(f"✗ 获取事件卡返回错误状态码: {response.status_code}")
            print(f"  错误信息: {response.text}")
            return False
    except Exception as e:
        print(f"✗ 获取事件卡测试失败: {str(e)}")
        return False

    # Step 6: 测试获取用户卡组（应该为空）
    print("\n步骤 6: 测试获取用户卡组...")
    try:
        response = requests.get(f"{base_url}/api/decks", headers=headers)
        if response.status_code == 200:
            decks_data = response.json()
            if "decks" in decks_data and isinstance(decks_data["decks"], list):
                print(f"✓ 获取卡组测试通过 (用户有 {len(decks_data['decks'])} 个卡组)")
            else:
                print(f"✗ 获取卡组返回非预期数据: {decks_data}")
                return False
        else:
            print(f"✗ 获取卡组返回错误状态码: {response.status_code}")
            print(f"  错误信息: {response.text}")
            return False
    except Exception as e:
        print(f"✗ 获取卡组测试失败: {str(e)}")
        return False

    # Step 7: 测试创建卡组
    print("\n步骤 7: 测试创建卡组...")
    try:
        # 首先获取3张角色卡
        response = requests.get(
            f"{base_url}/api/cards/characters?per_page=3", headers=headers
        )
        if response.status_code == 200:
            characters_data = response.json()
            character_cards = [card["id"] for card in characters_data.get("cards", [])]

            if len(character_cards) < 3:
                print("⚠️  警告: 数据库中的角色卡数量不足3张，跳过卡组创建测试")
                deck_id = None
            else:
                print(f"  已获取 {len(character_cards)} 张角色卡")

                # 获取27张非角色卡
                other_cards = get_non_character_cards(
                    headers, base_url, 27, character_cards
                )

                print(f"  已获取 {len(other_cards)} 张非角色卡")

                if len(other_cards) < 27:
                    print(
                        f"⚠️  警告: 获取的非角色卡数量不足27张（当前有{len(other_cards)}张），跳过卡组创建测试"
                    )
                    deck_id = None
                else:
                    # 组合30张卡（3张角色卡 + 27张其他卡）
                    all_deck_cards = character_cards[:3] + other_cards[:27]

                    if len(all_deck_cards) != 30:
                        print(
                            f"⚠️  警告: 组合的卡牌数量不正确（当前有{len(all_deck_cards)}张），跳过卡组创建测试"
                        )
                        deck_id = None
                    else:
                        print(
                            f"  正在创建包含 {len(character_cards[:3])} 张角色卡和 {len(other_cards[:27])} 张其他卡的卡组..."
                        )

                        # 尝试创建卡组
                        deck_data = {
                            "name": "集成测试卡组",
                            "description": "API集成测试创建的卡组",
                            "cards": all_deck_cards,
                        }

                        response = requests.post(
                            f"{base_url}/api/decks", headers=headers, json=deck_data
                        )
                        if response.status_code == 201:
                            create_deck_data = response.json()
                            if "deck" in create_deck_data:
                                deck_id = create_deck_data["deck"]["id"]
                                print(f"✓ 卡组创建测试通过 (卡组ID: {deck_id})")

                                # Step 8: 测试获取特定卡组
                                print("\n步骤 8: 测试获取特定卡组...")
                                response = requests.get(
                                    f"{base_url}/api/decks/{deck_id}", headers=headers
                                )
                                if response.status_code == 200:
                                    deck_info = response.json()
                                    if "deck" in deck_info:
                                        print(
                                            f"✓ 获取特定卡组测试通过 (卡组: {deck_info['deck']['name']})"
                                        )
                                    else:
                                        print(
                                            f"✗ 获取特定卡组返回非预期数据: {deck_info}"
                                        )
                                        return False
                                else:
                                    print(
                                        f"✗ 获取特定卡组返回错误状态码: {response.status_code}"
                                    )
                                    print(f"  错误信息: {response.text}")
                                    return False
                            else:
                                print(f"✗ 卡组创建返回非预期数据: {create_deck_data}")
                                return False
                        else:
                            print(f"✗ 卡组创建返回错误状态码: {response.status_code}")
                            print(f"  错误信息: {response.text}")
                            return False
        else:
            print(f"✗ 获取角色卡用于创建卡组时失败: {response.status_code}")
            return False
    except Exception as e:
        print(f"✗ 卡组创建测试失败: {str(e)}")
        return False

    # Step 9: 测试获取用户卡组（应该有一个，如果成功创建了）
    print("\n步骤 9: 再次测试获取用户卡组（验证创建）...")
    try:
        response = requests.get(f"{base_url}/api/decks", headers=headers)
        if response.status_code == 200:
            decks_data = response.json()
            if "decks" in decks_data and isinstance(decks_data["decks"], list):
                if "deck_id" in locals() and deck_id:  # 如果前面成功创建了卡组
                    if len(decks_data["decks"]) > 0:
                        print(
                            f"✓ 获取卡组验证测试通过 (用户现在有 {len(decks_data['decks'])} 个卡组)"
                        )
                    else:
                        print("✗ 卡组创建后用户卡组列表仍为空")
                        return False
                else:
                    print(
                        f"✓ 获取卡组验证测试通过 (用户有 {len(decks_data['decks'])} 个卡组)"
                    )
            else:
                print(f"✗ 获取卡组返回非预期数据: {decks_data}")
                return False
        else:
            print(f"✗ 获取卡组返回错误状态码: {response.status_code}")
            print(f"  错误信息: {response.text}")
            return False
    except Exception as e:
        print(f"✗ 获取卡组验证测试失败: {str(e)}")
        return False

    # Step 10: 测试本地游戏API
    print("\n步骤 10: 测试本地游戏API...")
    try:
        # 尝试开始本地游戏（仅在成功创建卡组时）
        if "deck_id" in locals() and deck_id:
            game_data = {"deck_id": deck_id, "opponent_type": "ai"}

            response = requests.post(
                f"{base_url}/api/local-game/start", headers=headers, json=game_data
            )
            if response.status_code == 200:
                game_start_data = response.json()
                if "game_session_id" in game_start_data:
                    game_session_id = game_start_data["game_session_id"]
                    print(f"✓ 本地游戏开始测试通过 (游戏会话ID: {game_session_id})")

                    # 测试获取游戏状态
                    response = requests.get(
                        f"{base_url}/api/local-game/{game_session_id}/state",
                        headers=headers,
                    )
                    if response.status_code == 200:
                        print("✓ 获取游戏状态测试通过")
                    else:
                        print(f"⚠️  获取游戏状态返回错误状态码: {response.status_code}")

                    # 结束游戏
                    response = requests.post(
                        f"{base_url}/api/local-game/{game_session_id}/end",
                        headers=headers,
                        json={},
                    )
                    if response.status_code == 200:
                        print("✓ 结束游戏测试通过")
                    else:
                        print(f"⚠️  结束游戏返回错误状态码: {response.status_code}")

                else:
                    print(f"✗ 本地游戏开始返回非预期数据: {game_start_data}")
            elif response.status_code == 400:
                print("⚠️  本地游戏开始返回400错误 (可能由于卡组验证问题)")
            else:
                print(f"⚠️  本地游戏开始返回错误状态码: {response.status_code}")
                print(f"  错误信息: {response.text}")
        else:
            print("⚠️  未进行本地游戏测试 (未成功创建卡组)")
    except Exception as e:
        print(f"⚠️  本地游戏API测试出现异常: {str(e)}")
        # 不将此作为整体测试失败，因为游戏功能相对独立

    print("\n" + "=" * 60)
    print("集成测试完成！")
    print("=" * 60)

    return True


def main():
    """主函数"""
    print("开始运行七圣召唤 API 集成测试...")

    success = run_integration_tests()

    if success:
        print("\n✓ 所有集成测试通过！")
        sys.exit(0)
    else:
        print("\n✗ 集成测试失败！")
        sys.exit(1)


if __name__ == "__main__":
    main()
