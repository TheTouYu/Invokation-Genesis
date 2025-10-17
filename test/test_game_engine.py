"""
测试游戏引擎核心功能
"""
from game_engine.core import GameEngine
from models.game_models import Card, CharacterCard
from models.enums import ElementType, CardType, PlayerAction
import random

def create_test_deck(player_id: str) -> list:
    """创建测试卡组"""
    # 创建一些测试卡牌
    test_cards = []
    
    # 添加一些角色卡
    from models.enums import CardType
    for i in range(3):
        char_card = CharacterCard(
            id=f"char_{player_id}_{i}",
            name=f"角色_{i}",
            card_type=CardType.CHARACTER,
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
    
    # 添加一些事件卡
    for i in range(5):
        event_card = Card(
            id=f"event_{player_id}_{i}",
            name=f"事件_{i}",
            card_type=CardType.EVENT,
            cost=[ElementType.OMNI] if i % 2 == 0 else [ElementType.PYRO],  # 交替使用万能和火元素
            description=f"测试事件卡 {i}"
        )
        test_cards.append(event_card)
    
    # 添加一些支援卡
    for i in range(5):
        support_card = Card(
            id=f"support_{player_id}_{i}",
            name=f"支援_{i}",
            card_type=CardType.SUPPORT,
            cost=[ElementType.CRYSTAL, ElementType.CRYSTAL],  # 2个任意元素
            description=f"测试支援卡 {i}"
        )
        test_cards.append(support_card)
    
    return test_cards

def test_game_engine():
    """测试游戏引擎"""
    print("开始测试游戏引擎...")
    
    # 创建游戏引擎实例
    engine = GameEngine()
    
    # 创建测试卡组
    deck1 = create_test_deck("player1")
    deck2 = create_test_deck("player2")
    
    # 创建游戏
    game_id = engine.create_game_state("player1", "player2", deck1, deck2)
    print(f"创建游戏: {game_id}")
    
    # 获取游戏状态
    game_state = engine.get_game_state(game_id)
    if game_state:
        print(f"游戏状态: 回合 {game_state.round_number}, 阶段 {game_state.phase.value}")
        print(f"玩家1手牌数: {len(game_state.players[0].hand_cards)}")
        print(f"玩家2手牌数: {len(game_state.players[1].hand_cards)}")
    
    # 尝试处理一个行动 - 这会从投骰阶段开始
    action_result = engine.process_action(
        game_id, 
        "player1", 
        PlayerAction.PLAY_CARD, 
        {"card_id": deck1[0].id if deck1 else ""}
    )
    
    if action_result:
        print(f"行动后状态: 阶段 {action_result.phase.value}")
    
    # 测试切换到行动阶段后使用技能
    # 先手动设置游戏进入行动阶段
    if game_state:
        from models.enums import GamePhase
        game_state.phase = GamePhase.ACTION_PHASE
        print("手动设置游戏进入行动阶段")
    
    print("游戏引擎测试完成")

if __name__ == "__main__":
    test_game_engine()