"""
测试卡牌转换功能
"""
import sys
import os
import json

# 添加项目根目录到Python路径
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from models.game_models import Card, CharacterCard
from models.enums import ElementType, CardType as GameCardType


def test_convert_db_cards_to_game_cards():
    """测试数据库卡牌转换功能"""
    print("测试数据库卡牌转换功能...")
    
    # 模拟数据库卡牌数据
    class MockCardData:
        def __init__(self, **kwargs):
            for k, v in kwargs.items():
                setattr(self, k, v)
    
    # 创建一个角色卡数据
    char_card_data = MockCardData(
        id="char_001",
        name="测试角色",
        card_type="角色牌",
        element_type="火",
        cost=json.dumps([ElementType.OMNI.value, ElementType.PYRO.value]),
        description="测试角色描述",
        character_subtype="角色子类型",
        health=10,
        max_health=10,
        energy=0,
        max_energy=3,
        weapon_type="剑",
        skills=json.dumps([{
            "id": "skill_1",
            "name": "测试技能",
            "cost": [ElementType.SAME.value, ElementType.SAME.value],
            "damage": 2
        }]),
        image_url="http://example.com/image.jpg"
    )
    
    # 创建一个事件卡数据
    event_card_data = MockCardData(
        id="event_001",
        name="测试事件",
        card_type="事件牌",
        element_type=None,
        cost=json.dumps([ElementType.OMNI.value]),
        description="测试事件描述",
        character_subtype="角色子类型",
        health=None,
        max_health=None,
        energy=None,
        max_energy=None,
        weapon_type=None,
        skills=None,
        image_url=None
    )
    
    from api.local_game import convert_db_cards_to_game_cards
    
    # 测试转换角色卡
    game_cards = convert_db_cards_to_game_cards([char_card_data, event_card_data])
    
    print(f"转换了 {len(game_cards)} 张卡牌")
    
    # 检查第一张卡（角色卡）
    char_card = game_cards[0]
    print(f"角色卡: {char_card.name}, 类型: {type(char_card).__name__}")
    assert isinstance(char_card, CharacterCard), "第一张卡应该是CharacterCard类型"
    assert char_card.name == "测试角色", "角色卡名称不匹配"
    assert char_card.health == 10, "角色卡生命值不匹配"
    assert len(char_card.skills) == 1, "技能数量不匹配"
    
    # 检查第二张卡（事件卡）
    event_card = game_cards[1]
    print(f"事件卡: {event_card.name}, 类型: {type(event_card).__name__}")
    assert isinstance(event_card, Card), "第二张卡应该是Card类型"
    assert not isinstance(event_card, CharacterCard), "第二张卡不应该是CharacterCard类型"
    assert event_card.name == "测试事件", "事件卡名称不匹配"
    
    print("✓ 卡牌转换功能测试通过")


def test_game_state_serialization():
    """测试游戏状态序列化功能"""
    print("\n测试游戏状态序列化功能...")
    
    from models.game_models import GameState, PlayerState, CharacterCard
    from models.enums import GamePhase
    
    # 创建测试角色
    test_character = CharacterCard(
        id="char1",
        name="测试角色",
        card_type=GameCardType.CHARACTER,
        cost=[ElementType.OMNI],
        health=10,
        max_health=10,
        energy=2,
        max_energy=3,
        element_type=ElementType.PYRO,
        weapon_type="法器",
        skills=[{
            "id": "test_skill",
            "name": "测试技能",
            "cost": [ElementType.SAME, ElementType.SAME],
            "damage": 1
        }]
    )
    
    # 创建玩家状态
    player_state = PlayerState(
        player_id="player1",
        characters=[test_character],
        active_character_index=0,
        hand_cards=[Card(
            id="card1",
            name="测试手牌",
            card_type=GameCardType.EVENT,
            cost=[ElementType.OMNI],
            description="测试用的手牌"
        )],
        dice=[ElementType.PYRO, ElementType.HYDRO]
    )
    
    # 创建游戏状态
    game_state = GameState(
        players=[player_state, PlayerState(player_id="player2")],
        current_player_index=0,
        round_number=1,
        phase=GamePhase.ACTION_PHASE,
        game_log=["游戏开始"]
    )
    
    from api.local_game import serialize_game_state
    
    # 序列化游戏状态
    serialized = serialize_game_state(game_state)
    
    print(f"序列化成功: {serialized is not None}")
    print(f"玩家数量: {len(serialized['players'])}")
    print(f"当前回合: {serialized['round_number']}")
    print(f"游戏阶段: {serialized['phase']}")
    
    # 检查序列化结果
    assert serialized is not None, "序列化结果不应为None"
    assert 'players' in serialized, "序列化结果应包含players字段"
    assert 'current_player_index' in serialized, "序列化结果应包含current_player_index字段"
    
    # 检查玩家角色信息
    player_data = serialized['players'][0]
    assert len(player_data['characters']) == 1, "玩家应有1个角色"
    assert player_data['characters'][0]['name'] == '测试角色', "角色名称应正确序列化"
    assert player_data['dice'] == ['火', '水'], "骰子信息应正确序列化"
    
    print("✓ 游戏状态序列化功能测试通过")


def test_winner_determination():
    """测试胜负判断功能"""
    print("\n测试胜负判断功能...")
    
    from api.local_game import determine_winner
    from models.game_models import GameState, PlayerState, CharacterCard
    from models.enums import GamePhase
    
    # 创建有两个存活角色的玩家
    alive_char = CharacterCard(
        id="alive_char",
        name="存活角色",
        card_type=GameCardType.CHARACTER,
        cost=[],
        health=5,  # 生命值大于0，存活
        max_health=10
    )
    
    dead_char = CharacterCard(
        id="dead_char",
        name="死亡角色",
        card_type=GameCardType.CHARACTER,
        cost=[],
        health=0,  # 生命值为0，死亡
        max_health=10
    )
    
    # 玩家1有1个存活角色
    player1 = PlayerState(
        player_id="player1",
        characters=[alive_char, dead_char]
    )
    
    # 玩家2没有存活角色（所有角色都死亡）
    player2 = PlayerState(
        player_id="player2",
        characters=[dead_char]  # 只有死亡角色
    )
    
    game_state = GameState(
        players=[player1, player2],
        current_player_index=0,
        phase=GamePhase.ACTION_PHASE
    )
    
    winner = determine_winner(game_state)
    print(f"获胜者: {winner}")
    
    # 玩家1应该获胜，因为玩家2没有存活角色
    assert winner == "player1", f"预期获胜者是player1，实际是{winner}"
    
    print("✓ 胜负判断功能测试通过")


def run_all_tests():
    """运行所有测试"""
    print("开始运行卡牌与游戏API功能测试...\n")
    
    try:
        test_convert_db_cards_to_game_cards()
        test_game_state_serialization()
        test_winner_determination()
        
        print("\n✓ 所有测试通过！卡牌与游戏API核心功能正常工作")
        return True
    except Exception as e:
        print(f"\n✗ 测试失败: {str(e)}")
        import traceback
        traceback.print_exc()
        return False


if __name__ == "__main__":
    success = run_all_tests()
    sys.exit(0 if success else 1)