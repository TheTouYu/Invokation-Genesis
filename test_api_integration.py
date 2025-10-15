"""
API集成测试脚本
"""
import sys
import os
import json
import unittest
from unittest.mock import patch, MagicMock

# 添加项目根目录到Python路径
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from models.game_models import Card, CharacterCard
from models.enums import ElementType, CardType as GameCardType
from models.db_models import init_models_db
from flask_sqlalchemy import SQLAlchemy

# 初始化数据库模型
db = SQLAlchemy()
init_models_db(db)

# 现在可以安全地导入模型
from models.db_models import CardData, Deck
from api.local_game import convert_db_cards_to_game_cards, determine_winner, serialize_game_state

class TestCardsAPI(unittest.TestCase):
    """测试卡牌API"""
    
    def setUp(self):
        """设置测试环境"""
        self.card_data = MagicMock(spec=CardData)
        self.card_data.id = "test_card_1"
        self.card_data.name = "测试卡牌"
        self.card_data.card_type = "角色牌"
        self.card_data.element_type = "火"
        self.card_data.rarity = 5
        self.card_data.cost = json.dumps([ElementType.OMNI.value, ElementType.PYRO.value])
        self.card_data.description = "这是一个测试卡牌"
        self.card_data.character_subtype = "角色子类型"
        self.card_data.health = 10
        self.card_data.max_health = 10
        self.card_data.energy = 0
        self.card_data.max_energy = 3
        self.card_data.weapon_type = "武器"
        self.card_data.skills = json.dumps([{
            "id": "skill_1",
            "name": "技能1",
            "cost": [ElementType.SAME.value, ElementType.SAME.value],
            "damage": 1
        }])
        self.card_data.image_url = "http://example.com/card.jpg"
        
    def test_convert_db_cards_to_game_cards_character(self):
        """测试将数据库角色卡转换为游戏卡"""
        
        # 测试角色卡转换
        game_cards = convert_db_cards_to_game_cards([self.card_data])
        
        self.assertEqual(len(game_cards), 1)
        game_card = game_cards[0]
        
        # 检查是否为CharacterCard实例
        self.assertIsInstance(game_card, CharacterCard)
        self.assertEqual(game_card.id, self.card_data.id)
        self.assertEqual(game_card.name, self.card_data.name)
        self.assertEqual(game_card.health, self.card_data.health)
        self.assertEqual(len(game_card.skills), 1)
        
    def test_convert_db_cards_to_game_cards_non_character(self):
        """测试将数据库非角色卡转换为游戏卡"""
        
        # 修改为非角色卡
        non_char_card = MagicMock(spec=CardData)
        non_char_card.id = "test_event_1"
        non_char_card.name = "测试事件"
        non_char_card.card_type = "事件牌"
        non_char_card.element_type = None
        non_char_card.rarity = 3
        non_char_card.cost = json.dumps([ElementType.OMNI.value])
        non_char_card.description = "这是一个测试事件"
        non_char_card.character_subtype = "角色子类型"
        
        game_cards = convert_db_cards_to_game_cards([non_char_card])
        
        self.assertEqual(len(game_cards), 1)
        game_card = game_cards[0]
        
        # 检查是否为Card实例而非CharacterCard
        self.assertIsInstance(game_card, Card)
        self.assertNotIsInstance(game_card, CharacterCard)
        self.assertEqual(game_card.id, non_char_card.id)
        self.assertEqual(game_card.name, non_char_card.name)


class TestLocalGameAPI(unittest.TestCase):
    """测试本地游戏API"""
    
    def test_determine_winner(self):
        """测试胜负判断功能"""
        from models.game_models import GameState, PlayerState
        from models.enums import GamePhase
        import uuid
        
        # 创建测试游戏状态
        player1_state = PlayerState(
            player_id="player1",
            characters=[],  # 无角色，应判负
        )
        player2_state = PlayerState(
            player_id="player2",
            characters=[],  # 无角色，应判负
        )
        game_state = GameState(
            players=[player1_state, player2_state],
            current_player_index=0,
            phase=GamePhase.ACTION_PHASE
        )
        
        # 在这种情况下，应该返回当前玩家
        winner = determine_winner(game_state)
        self.assertEqual(winner, "player1")
    
    def test_serialize_game_state(self):
        """测试游戏状态序列化"""
        from models.game_models import GameState, PlayerState, CharacterCard
        from models.enums import GamePhase, ElementType
        import uuid
        
        # 创建测试数据
        test_character = CharacterCard(
            id="char1",
            name="测试角色",
            card_type=GameCardType.CHARACTER,
            cost=[ElementType.OMNI],
            health=10,
            max_health=10,
            energy=0,
            max_energy=3,
            element_type=ElementType.PYRO,
            weapon_type="剑",
            skills=[]
        )
        
        player_state = PlayerState(
            player_id="player1",
            characters=[test_character],
            active_character_index=0
        )
        
        game_state = GameState(
            players=[player_state],
            current_player_index=0,
            phase=GamePhase.ACTION_PHASE,
            game_log=["游戏开始"]
        )
        
        serialized = serialize_game_state(game_state)
        
        # 检查序列化结果
        self.assertIsNotNone(serialized)
        self.assertIn('players', serialized)
        self.assertIn('current_player_index', serialized)
        self.assertIn('phase', serialized)
        
        # 检查角色信息是否正确序列化
        player_data = serialized['players'][0]
        self.assertEqual(len(player_data['characters']), 1)
        self.assertEqual(player_data['characters'][0]['name'], '测试角色')


def run_tests():
    """运行所有测试"""
    print("开始运行API测试...")
    
    # 创建测试套件
    suite = unittest.TestSuite()
    
    # 添加测试用例
    suite.addTest(unittest.makeSuite(TestCardsAPI))
    suite.addTest(unittest.makeSuite(TestLocalGameAPI))
    
    # 运行测试
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)
    
    print(f"\n测试完成: {result.testsRun} 个测试, {len(result.errors)} 个错误, {len(result.failures)} 个失败")
    
    return result.wasSuccessful()


if __name__ == "__main__":
    success = run_tests()
    sys.exit(0 if success else 1)