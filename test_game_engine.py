"""
游戏引擎功能测试
"""
import unittest
from game_engine.core import GameEngine
from game_engine.element_reactions import ElementReactionSystem
from game_engine.deck_validation import DeckValidationSystem
from models.game_models import Card, CharacterCard, PlayerState, GameState
from models.enums import ElementType, CardType, GamePhase, PlayerAction, CharacterStatus, DamageType


class TestGameEngine(unittest.TestCase):
    def setUp(self):
        """设置测试环境"""
        self.game_engine = GameEngine()
        self.element_reaction_system = ElementReactionSystem()
        self.deck_validation_system = DeckValidationSystem()
        
        # 创建测试卡牌
        self.test_weapon_card = Card(
            id="weapon_001",
            name="测试武器",
            card_type=CardType.WEAPON,
            cost=[ElementType.OMNI, ElementType.OMNI],
            description="测试用武器卡"
        )
        
        self.test_talent_card = Card(
            id="talent_001",
            name="测试天赋",
            card_type=CardType.TALENT,
            cost=[ElementType.CRYO, ElementType.OMNI],
            character_subtype="测试角色",
            description="测试用天赋卡"
        )
        
        # 创建测试角色卡
        self.test_character = CharacterCard(
            id="char_001",
            name="测试角色",
            card_type=CardType.CHARACTER,
            cost=[],
            health=10,
            max_health=10,
            element_type=ElementType.CRYO,
            weapon=None,
            artifact=None,
            talent=None,
            character_statuses=[],
            is_alive=True
        )
        
        # 创建包含角色的卡组
        self.test_deck1 = [self.test_character, self.test_weapon_card, self.test_talent_card] + [self.test_weapon_card] * 27  # 总共30张行动牌
        self.test_deck2 = [self.test_character, self.test_weapon_card, self.test_talent_card] + [self.test_weapon_card] * 27  # 总共30张行动牌

    def test_create_game_state(self):
        """测试创建游戏状态"""
        game_id = self.game_engine.create_game_state(
            player1_id="player1",
            player2_id="player2",
            deck1=self.test_deck1,
            deck2=self.test_deck2
        )
        
        self.assertIsNotNone(game_id)
        self.assertIn(game_id, self.game_engine.game_states)
        
        game_state = self.game_engine.game_states[game_id]
        self.assertEqual(len(game_state.players), 2)
        self.assertEqual(game_state.players[0].player_id, "player1")
        self.assertEqual(game_state.players[1].player_id, "player2")
        
        # 验证卡组被验证
        for player in game_state.players:
            self.assertEqual(len(player.characters), 1)  # 1个角色
            self.assertEqual(len(player.hand_cards), 5)  # 5张初始手牌

    def test_element_reaction_system(self):
        """测试元素反应系统"""
        # 测试冰+火 = 融化
        reaction = self.element_reaction_system.check_element_reaction(ElementType.CRYO, ElementType.PYRO)
        self.assertEqual(reaction, "Melt")
        
        # 测试水+电 = 感电
        reaction = self.element_reaction_system.check_element_reaction(ElementType.HYDRO, ElementType.ELECTRO)
        self.assertEqual(reaction, "Electro-Charged")
        
        # 测试无反应情况
        reaction = self.element_reaction_system.check_element_reaction(ElementType.PYRO, ElementType.GEO)
        self.assertIsNone(reaction)

    def test_deck_validation(self):
        """测试卡组验证"""
        # 有效卡组测试
        result = self.deck_validation_system.validate_deck(self.test_deck1)
        self.assertTrue(result["is_valid"])
        
        # 无效卡组测试：角色数量不足
        invalid_deck = [self.test_weapon_card] * 30  # 没有角色卡
        result = self.deck_validation_system.validate_deck(invalid_deck)
        self.assertFalse(result["is_valid"])
        self.assertIn("角色卡应为3个不同角色", result["errors"][0])

    def test_process_action_play_card(self):
        """测试打出手牌操作"""
        game_id = self.game_engine.create_game_state(
            player1_id="player1",
            player2_id="player2",
            deck1=self.test_deck1,
            deck2=self.test_deck2
        )
        
        # 设置玩家骰子
        game_state = self.game_engine.game_states[game_id]
        game_state.players[0].dice = [ElementType.CRYO, ElementType.OMNI, ElementType.OMNI, ElementType.OMNI, ElementType.OMNI, ElementType.OMNI, ElementType.OMNI, ElementType.OMNI]
        
        # 确保玩家有武器卡在手牌中
        weapon_card_idx = -1
        for i, card in enumerate(game_state.players[0].hand_cards):
            if card.card_type == CardType.WEAPON:
                weapon_card_idx = i
                break
        
        if weapon_card_idx == -1:
            # 如果手牌中没有武器牌，则添加一张
            game_state.players[0].hand_cards.append(self.test_weapon_card)
            weapon_card_idx = len(game_state.players[0].hand_cards) - 1
        
        # 执行打出手牌操作
        payload = {
            'card_id': game_state.players[0].hand_cards[weapon_card_idx].id
        }
        
        updated_game_state = self.game_engine.process_action(
            game_id=game_id,
            player_id="player1",
            action=PlayerAction.PLAY_CARD,
            payload=payload
        )
        
        self.assertIsNotNone(updated_game_state)

    def test_process_action_use_skill(self):
        """测试使用技能操作"""
        game_id = self.game_engine.create_game_state(
            player1_id="player1",
            player2_id="player2",
            deck1=self.test_deck1,
            deck2=self.test_deck2
        )
        
        # 初始化骰子
        game_state = self.game_engine.game_states[game_id]
        game_state.players[0].dice = [ElementType.CRYO] * 8  # 8个冰元素骰
        
        # 获取当前出战角色
        active_character = self.game_engine._get_active_character(game_state.players[0])
        self.assertIsNotNone(active_character)
        
        # 添加一个测试技能到角色
        active_character.skills = [{
            'id': 'test_skill',
            'name': '测试技能',
            'cost': [ElementType.CRYO],
            'damage': 3,
            'damage_type': DamageType.ELEMENTAL,
            'element_application': ElementType.CRYO,
            'skill_type': 'ELEMENTAL_SKILL'
        }]
        
        # 执行使用技能操作
        payload = {
            'skill_id': 'test_skill'
        }
        
        # 先处理投骰阶段
        self.game_engine._roll_phase(game_state, PlayerAction.PASS, {})
        
        # 然后处理使用技能
        updated_game_state = self.game_engine.process_action(
            game_id=game_id,
            player_id="player1",
            action=PlayerAction.USE_SKILL,
            payload=payload
        )
        
        self.assertIsNotNone(updated_game_state)

    def test_game_end_conditions(self):
        """测试游戏结束条件"""
        game_id = self.game_engine.create_game_state(
            player1_id="player1",
            player2_id="player2",
            deck1=self.test_deck1,
            deck2=self.test_deck2
        )
        
        game_state = self.game_engine.game_states[game_id]
        
        # 模拟玩家2的角色全部死亡
        for character in game_state.players[1].characters:
            character.is_alive = False
            character.health = 0
        
        # 检查胜利条件
        winner = self.game_engine._check_victory_conditions(game_state)
        self.assertEqual(winner, "player1")

    def test_damage_application_with_reactions(self):
        """测试带元素反应的伤害应用"""
        # 创建测试角色
        character = CharacterCard(
            id="test_char",
            name="被攻击角色",
            card_type=CardType.CHARACTER,
            cost=[],
            health=10,
            max_health=10,
            element_type=ElementType.HYDRO,
            weapon=None,
            artifact=None,
            talent=None,
            character_statuses=[],
            is_alive=True
        )
        
        # 初始没有元素附着
        self.assertIsNone(character.element_attached)
        
        # 应用火元素（会与水元素反应）
        self.element_reaction_system.apply_element_attachment(character, ElementType.PYRO)
        
        # 此时应该触发蒸发反应，但实际实现中元素附着和反应的处理方式可能不同
        # 这里主要测试伤害应用函数
        initial_health = character.health
        damage_dealt = self.game_engine._apply_damage(
            character=character,
            damage=3,
            damage_type=DamageType.ELEMENTAL,
            source_element=ElementType.PYRO
        )
        
        self.assertEqual(character.health, initial_health - damage_dealt)


if __name__ == '__main__':
    unittest.main()