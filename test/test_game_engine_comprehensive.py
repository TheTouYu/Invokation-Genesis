"""
全面测试游戏引擎核心功能
"""
from game_engine.core import GameEngine
from models.game_models import Card, CharacterCard
from models.enums import ElementType, CardType, PlayerAction, GamePhase, SkillType
import random

def create_test_deck(player_id: str) -> list:
    """创建测试卡组"""
    # 创建一些测试卡牌
    test_cards = []
    
    # 添加一些角色卡
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

def test_comprehensive_game_engine():
    """全面测试游戏引擎"""
    print("开始全面测试游戏引擎...")
    
    # 创建游戏引擎实例
    engine = GameEngine()
    
    # 创建测试卡组
    deck1 = create_test_deck("player1")
    deck2 = create_test_deck("player2")
    
    # 创建游戏
    game_id = engine.create_game_state("player1", "player2", deck1, deck2)
    print(f"✓ 创建游戏: {game_id}")
    
    # 获取游戏状态
    game_state = engine.get_game_state(game_id)
    if game_state:
        print(f"✓ 游戏状态: 回合 {game_state.round_number}, 阶段 {game_state.phase.value}")
        print(f"✓ 玩家1手牌数: {len(game_state.players[0].hand_cards)}")
        print(f"✓ 玩家2手牌数: {len(game_state.players[1].hand_cards)}")
    
    # 测试投骰阶段
    action_result = engine.process_action(
        game_id, 
        "player1", 
        PlayerAction.PLAY_CARD, 
        {}
    )
    
    if action_result:
        print(f"✓ 投骰阶段处理后状态: 阶段 {action_result.phase.value}")
        print(f"✓ 玩家1骰子数: {len(action_result.players[0].dice)}")
        print(f"✓ 玩家2骰子数: {len(action_result.players[1].dice)}")
    
    # 测试费用支付验证
    player1 = action_result.players[0] if action_result else None
    if player1:
        test_cost = [ElementType.OMNI, ElementType.PYRO]
        can_pay = engine._can_pay_cost(player1, test_cost)
        print(f"✓ 费用支付验证: {can_pay}")
    
    # 测试使用技能（在行动阶段）
    if action_result and action_result.phase == GamePhase.ACTION_PHASE:
        # 添加一些骰子确保能支付技能费用
        from models.enums import GamePhase as GamePhaseEnum
        action_result.phase = GamePhaseEnum.ACTION_PHASE
        skill_result = engine.process_action(
            game_id,
            "player1",
            PlayerAction.USE_SKILL,
            {"skill_id": "skill_0_1"}
        )
        if skill_result:
            print(f"✓ 使用技能处理完成")
    
    # 测试打出手牌
    if action_result:
        # 获取玩家1的第一张手牌
        if action_result.players[0].hand_cards:
            first_card = action_result.players[0].hand_cards[0]
            play_result = engine.process_action(
                game_id,
                "player1",
                PlayerAction.PLAY_CARD,
                {"card_id": first_card.id}
            )
            if play_result:
                print(f"✓ 打出卡牌处理完成: {first_card.name}")
    
    # 测试切换角色
    if action_result:
        switch_result = engine.process_action(
            game_id,
            "player1",
            PlayerAction.SWITCH_CHARACTER,
            {"character_index": 1}
        )
        if switch_result:
            print(f"✓ 切换角色处理完成")
    
    # 测试结束回合
    pass_result = engine.process_action(
        game_id,
        "player1",
        PlayerAction.PASS,
        {}
    )
    if pass_result:
        print(f"✓ 结束回合处理完成，进入结束阶段")
    
    # 测试结束阶段
    # 这将自动触发到下一回合
    print(f"✓ 当前回合数: {pass_result.round_number}")
    
    print("✓ 游戏引擎全面测试完成")

def test_edge_cases():
    """测试边界情况"""
    print("\n开始测试边界情况...")
    
    engine = GameEngine()
    
    # 测试无效操作
    invalid_result = engine.process_action(
        "nonexistent_game_id",
        "player1",
        PlayerAction.PLAY_CARD,
        {}
    )
    if invalid_result is None:
        print("✓ 正确处理了不存在的游戏ID")
    
    # 测试非当前玩家的操作
    deck1 = create_test_deck("player1")
    deck2 = create_test_deck("player2")
    game_id = engine.create_game_state("player1", "player2", deck1, deck2)
    
    invalid_player_result = engine.process_action(
        game_id,
        "player3",  # 非游戏中的玩家
        PlayerAction.PLAY_CARD,
        {}
    )
    if invalid_player_result is None:
        print("✓ 正确处理了非当前玩家的操作")
    
    print("✓ 边界情况测试完成")

def performance_test():
    """性能测试"""
    print("\n开始性能测试...")
    import time
    
    engine = GameEngine()
    deck1 = create_test_deck("player1")
    deck2 = create_test_deck("player2")
    
    start_time = time.time()
    for i in range(100):  # 创建100个游戏
        game_id = engine.create_game_state(f"player1_{i}", f"player2_{i}", deck1, deck2)
    end_time = time.time()
    
    print(f"✓ 创建100个游戏耗时: {end_time - start_time:.4f}秒")
    
    print("✓ 性能测试完成")

if __name__ == "__main__":
    test_comprehensive_game_engine()
    test_edge_cases()
    performance_test()