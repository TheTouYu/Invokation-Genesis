"""
测试游戏引擎核心功能 - 更新版本，包含角色初始化
"""
from game_engine.core import GameEngine
from models.game_models import Card, CharacterCard
from models.enums import ElementType, CardType, PlayerAction, GamePhase
import random

def create_test_deck_with_characters(player_id: str) -> list:
    """创建包含角色卡的测试卡组"""
    # 创建一些测试卡牌
    test_cards = []
    
    # 添加一些角色卡 (30张卡组中的3张角色)
    from models.enums import CardType as CardTypeEnum
    for i in range(3):
        char_card = CharacterCard(
            id=f"char_{player_id}_{i}",
            name=f"角色_{i}",
            card_type=CardTypeEnum.CHARACTER,
            cost=[ElementType.OMNI, ElementType.OMNI],  # 2个万能元素
            health=10,
            max_health=10,
            element_type=ElementType.PYRO if i % 3 == 0 else ElementType.HYDRO if i % 3 == 1 else ElementType.CRYO,
            skills=[
                {
                    "id": f"skill_{i}_1",
                    "name": f"技能1_{i}",
                    "cost": [ElementType.SAME, ElementType.SAME],  # 2个同色元素
                    "damage": 1
                },
                {
                    "id": f"skill_{i}_2", 
                    "name": f"技能2_{i}",
                    "cost": [ElementType.OMNI, ElementType.OMNI, ElementType.OMNI],  # 3个万能元素
                    "damage": 3
                }
            ]
        )
        test_cards.append(char_card)
    
    # 添加一些事件卡 (30张卡组中的27张其他卡)
    for i in range(27):
        event_card = Card(
            id=f"event_{player_id}_{i}",
            name=f"事件_{i}",
            card_type=CardType.EVENT,
            cost=[ElementType.OMNI] if i % 2 == 0 else [ElementType.PYRO],  # 交替使用万能和火元素
            description=f"测试事件卡 {i}"
        )
        test_cards.append(event_card)
    
    return test_cards

def test_game_with_characters():
    """测试包含角色卡的游戏"""
    print("开始测试包含角色的游戏引擎...")
    
    # 创建游戏引擎实例
    engine = GameEngine()
    
    # 创建包含角色卡的测试卡组
    deck1 = create_test_deck_with_characters("player1")
    deck2 = create_test_deck_with_characters("player2")
    
    # 创建游戏
    game_id = engine.create_game_state("player1", "player2", deck1, deck2)
    print(f"✓ 创建游戏: {game_id}")
    
    # 获取游戏状态
    game_state = engine.get_game_state(game_id)
    if game_state:
        print(f"✓ 游戏状态: 回合 {game_state.round_number}, 阶段 {game_state.phase.value}")
        print(f"✓ 玩家1手牌数: {len(game_state.players[0].hand_cards)}")
        print(f"✓ 玩家2手牌数: {len(game_state.players[1].hand_cards)}")
        print(f"✓ 玩家1角色数: {len(game_state.players[0].characters)}")
        print(f"✓ 玩家2角色数: {len(game_state.players[1].characters)}")
    
    # 测试投骰阶段
    action_result = engine.process_action(
        game_id, 
        "player1", 
        PlayerAction.PLAY_CARD,  # 这会触发投骰阶段，然后进入行动阶段
        {}
    )
    
    if action_result:
        print(f"✓ 投骰阶段处理后状态: 阶段 {action_result.phase.value}")
        print(f"✓ 玩家1骰子数: {len(action_result.players[0].dice)}")
        print(f"✓ 玩家2骰子数: {len(action_result.players[1].dice)}")
        
        # 设置玩家1的初始出战角色
        if action_result.players[0].characters:
            action_result.players[0].active_character_index = 0
            print(f"✓ 设置玩家1的初始出战角色为 {action_result.players[0].characters[0].name}")
        
        # 现在测试使用技能
        skill_result = engine.process_action(
            game_id,
            "player1",
            PlayerAction.USE_SKILL,
            {"skill_id": "skill_0_1"}
        )
        if skill_result:
            print(f"✓ 使用技能处理完成")
    
    print("✓ 包含角色的游戏测试完成")

def test_complete_game_flow():
    """测试完整的对局流程"""
    print("\n开始测试完整对局流程...")
    
    # 创建游戏引擎实例
    engine = GameEngine()
    
    # 创建包含角色卡的测试卡组
    deck1 = create_test_deck_with_characters("player1")
    deck2 = create_test_deck_with_characters("player2")
    
    # 创建游戏
    game_id = engine.create_game_state("player1", "player2", deck1, deck2)
    
    # 获取游戏状态
    game_state = engine.get_game_state(game_id)
    
    # 设置初始出战角色
    if game_state:
        game_state.players[0].active_character_index = 0
        game_state.players[1].active_character_index = 0
        print(f"✓ 设置双方初始出战角色")
    
    # 测试完整的回合流程
    print("测试回合流程:")
    
    # 行动阶段 - 使用技能
    if game_state and game_state.phase == GamePhase.ACTION_PHASE:
        # 使用技能
        skill_result = engine.process_action(
            game_id,
            "player1",
            PlayerAction.USE_SKILL,
            {"skill_id": "skill_0_1"}
        )
        if skill_result:
            print(f"  - 玩家1使用技能成功")
    
    # 结束回合，进入结束阶段
    pass_result = engine.process_action(
        game_id,
        "player1",
        PlayerAction.PASS,
        {}
    )
    if pass_result:
        print(f"  - 玩家1回合结束，进入结束阶段")
    
    # 进入下一回合
    print(f"  - 进入第{pass_result.round_number}回合")
    
    print("✓ 完整对局流程测试完成")

if __name__ == "__main__":
    test_game_with_characters()
    test_complete_game_flow()