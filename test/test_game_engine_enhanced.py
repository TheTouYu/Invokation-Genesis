"""
游戏引擎测试套件
测试所有新添加的功能
"""
import unittest
from game_engine.core import GameEngine
from game_engine.element_reactions import ElementReactionSystem
from game_engine.deck_validation import DeckValidationSystem
from models.game_models import Card, CharacterCard, GameState, PlayerState
from models.enums import ElementType, CardType, CharacterStatus, DamageType, GamePhase
from typing import List


class TestElementReactionSystem(unittest.TestCase):
    """测试元素反应系统"""
    
    def setUp(self):
        self.reaction_system = ElementReactionSystem()
    
    def test_vaporize_reaction(self):
        """测试蒸发反应"""
        # 水元素攻击火附着角色
        reaction = self.reaction_system.check_element_reaction(ElementType.PYRO, ElementType.HYDRO)
        self.assertEqual(reaction, "Vaporize")
        
        # 火元素攻击水附着角色
        reaction = self.reaction_system.check_element_reaction(ElementType.HYDRO, ElementType.PYRO)
        self.assertEqual(reaction, "Vaporize")
    
    def test_melt_reaction(self):
        """测试融化反应"""
        # 火元素攻击冰附着角色
        reaction = self.reaction_system.check_element_reaction(ElementType.CRYO, ElementType.PYRO)
        self.assertEqual(reaction, "Melt")
        
        # 冰元素攻击火附着角色
        reaction = self.reaction_system.check_element_reaction(ElementType.PYRO, ElementType.CRYO)
        self.assertEqual(reaction, "Melt")
    
    def test_damage_calculation(self):
        """测试伤害计算"""
        # 测试蒸发反应（2倍伤害）
        final_damage, effect_info = self.reaction_system.calculate_reaction_damage(3, "Vaporize")
        self.assertEqual(final_damage, 6)  # 3 * 2 = 6
        self.assertTrue(effect_info["is_amplifying"])
        
        # 测试非反应伤害
        final_damage, effect_info = self.reaction_system.calculate_reaction_damage(3, "None")
        self.assertEqual(final_damage, 3)


class TestDeckValidationSystem(unittest.TestCase):
    """测试卡组验证系统"""
    
    def setUp(self):
        self.validator = DeckValidationSystem()
    
    def create_test_deck(self, num_characters=3, num_action_cards=30):
        """创建测试卡组"""
        deck = []
        
        # 添加角色卡
        for i in range(num_characters):
            char_card = CharacterCard(
                id=f"char_{i}",
                name=f"角色{i}",
                card_type=CardType.CHARACTER,
                cost=[],
                element_type=ElementType.PYRO,
                health=10,
                max_health=10,
                energy=0,
                max_energy=3,
                skills=[]
            )
            deck.append(char_card)
        
        # 添加行动卡
        for i in range(num_action_cards):
            action_card = Card(
                id=f"action_{i}",
                name=f"行动卡{i}",
                card_type=CardType.EVENT if i % 3 == 0 else CardType.WEAPON if i % 3 == 1 else CardType.SUPPORT,
                cost=[ElementType.OMNI]
            )
            deck.append(action_card)
        
        return deck
    
    def test_valid_deck(self):
        """测试有效卡组"""
        deck = self.create_test_deck(3, 30)  # 3角色+30行动=33张
        result = self.validator.validate_deck(deck)
        self.assertTrue(result["is_valid"])
    
    def test_invalid_character_count(self):
        """测试无效角色数量"""
        deck = self.create_test_deck(2, 31)  # 2角色+31行动=33张，但角色数不对
        result = self.validator.validate_deck(deck)
        self.assertFalse(result["is_valid"])
        self.assertIn("角色卡应为3张", result["errors"][0])
    
    def test_excessive_same_card_count(self):
        """测试同名卡牌数量超限"""
        deck = []
        
        # 添加3张角色卡
        for i in range(3):
            char_card = CharacterCard(
                id=f"char_{i}",
                name=f"角色{i}",
                card_type=CardType.CHARACTER,
                cost=[],
                element_type=ElementType.PYRO,
                health=10,
                max_health=10,
                energy=0,
                max_energy=3,
                skills=[]
            )
            deck.append(char_card)
        
        # 添加超过2张同名行动卡
        for i in range(5):
            action_card = Card(
                id=f"action_{i}",
                name="同名行动卡",  # 同名
                card_type=CardType.EVENT,
                cost=[ElementType.OMNI]
            )
            deck.append(action_card)
        
        result = self.validator.validate_deck(deck)
        self.assertFalse(result["is_valid"])
        self.assertTrue(any("超过2张限制" in error for error in result["errors"]))


class TestGameEngineEnhancements(unittest.TestCase):
    """测试游戏引擎增强功能"""
    
    def setUp(self):
        self.engine = GameEngine()
    
    def create_test_deck(self) -> List[Card]:
        """创建测试卡组"""
        deck = []
        
        # 添加角色卡 (3张)
        for i in range(3):
            char_card = CharacterCard(
                id=f"char_{i}",
                name=f"角色_{i}",
                card_type=CardType.CHARACTER,
                cost=[ElementType.OMNI, ElementType.OMNI],
                health=10,
                max_health=10,
                energy=0,
                max_energy=3,
                element_type=ElementType.PYRO if i % 3 == 0 else ElementType.HYDRO if i % 3 == 1 else ElementType.CRYO,
                skills=[
                    {
                        "id": f"skill_{i}_1",
                        "name": f"技能1_{i}",
                        "cost": [ElementType.SAME, ElementType.SAME],
                        "damage": 1,
                        "skill_type": "NORMAL_ATTACK",
                        "damage_type": DamageType.ELEMENTAL,
                        "element_application": ElementType.PYRO if i % 3 == 0 else ElementType.HYDRO
                    }
                ]
            )
            deck.append(char_card)
        
        # 添加行动卡 (30张: 25张事件卡 + 5张支援卡 = 30张)
        # 添加事件卡
        for i in range(25):  # 增加到25张事件卡
            event_card = Card(
                id=f"event_{i}",
                name=f"事件_{i}",
                card_type=CardType.EVENT,
                cost=[ElementType.OMNI] if i % 2 == 0 else [ElementType.PYRO],
                description="测试事件卡"
            )
            deck.append(event_card)
        
        # 添加支援卡
        for i in range(5):  # 5张支援卡
            support_card = Card(
                id=f"support_{i}",
                name=f"支援_{i}",
                card_type=CardType.SUPPORT,
                cost=[ElementType.CRYSTAL, ElementType.CRYSTAL],
                description="测试支援卡"
            )
            deck.append(support_card)
        
        assert len(deck) == 33  # 确保总数是33张 (3+25+5)
        return deck
    
    def test_deck_validation_in_game_creation(self):
        """测试游戏创建时的卡组验证"""
        deck1 = self.create_test_deck()
        deck2 = self.create_test_deck()
        
        # 这应该成功，因为卡组是有效的
        game_id = self.engine.create_game_state("player1", "player2", deck1, deck2)
        self.assertIsNotNone(game_id)
        
        # 创建无效卡组（只有1张角色卡）
        invalid_deck = []
        # 添加1张角色卡
        char_card = CharacterCard(
            id="char_0",
            name="角色_0",
            card_type=CardType.CHARACTER,
            cost=[],
            health=10,
            max_health=10,
            energy=0,
            max_energy=3,
            element_type=ElementType.PYRO,
            skills=[]
        )
        invalid_deck.append(char_card)
        
        # 尝试用无效卡组创建游戏
        invalid_game_id = self.engine.create_game_state("player1", "player2", invalid_deck, deck2)
        self.assertIsNone(invalid_game_id)
    
    def test_element_attachment_and_reaction(self):
        """测试元素附着和反应"""
        # 这个测试需要检查伤害计算和元素反应
        # 创建游戏
        deck1 = self.create_test_deck()
        deck2 = self.create_test_deck()
        game_id = self.engine.create_game_state("player1", "player2", deck1, deck2)
        
        # 获取游戏状态
        game_state = self.engine.get_game_state(game_id)
        self.assertIsNotNone(game_state)
        
        # 确保游戏状态不为None
        if game_state:
            # 获取玩家2的出战角色并应用元素附着
            target_player = game_state.players[1]  # 玩家2
            target_character = self.engine._get_active_character(target_player)
            
            if target_character:
                # 应用火元素附着
                self.engine.element_reaction_system.apply_element_attachment(target_character, ElementType.PYRO)
                self.assertEqual(target_character.element_attached, ElementType.PYRO)
                
                # 现在用水元素攻击，应该触发蒸发反应
                original_health = target_character.health
                actual_damage = self.engine._apply_damage(
                    target_character, 
                    2,  # 基础伤害
                    DamageType.ELEMENTAL, 
                    ElementType.HYDRO  # 水元素攻击
                )
                
                # 蒸发反应应该造成双倍伤害
                expected_damage = 4  # 2 (基础) * 2 (蒸发) = 4
                expected_health = original_health - expected_damage
                self.assertEqual(target_character.health, expected_health)
    
    def test_character_knockout(self):
        """测试角色击倒机制"""
        # 创建游戏
        deck1 = self.create_test_deck()
        deck2 = self.create_test_deck()
        game_id = self.engine.create_game_state("player1", "player2", deck1, deck2)
        
        game_state = self.engine.get_game_state(game_id)
        if game_state:
            # 获取玩家2的出战角色
            target_player = game_state.players[1]
            target_character = self.engine._get_active_character(target_player)
            
            if target_character:
                # 将角色生命值设置为较低值, then cause enough damage to kill it
                original_health = target_character.health
                target_character.health = 2  # Set to a low value
                
                # Cause 3 points of damage which should be enough to kill it
                self.engine._apply_damage(target_character, 3, DamageType.ELEMENTAL)
                
                # Check that the character is knocked out
                self.assertFalse(target_character.is_alive)
                self.assertEqual(target_character.status, CharacterStatus.DEAD)
    
    def test_survive_mechanic(self):
        """测试免于被击倒机制"""
        # 创建游戏
        deck1 = self.create_test_deck()
        deck2 = self.create_test_deck()
        game_id = self.engine.create_game_state("player1", "player2", deck1, deck2)
        
        game_state = self.engine.get_game_state(game_id)
        if game_state:
            # 获取玩家2的出战角色
            target_player = game_state.players[1]
            target_character = self.engine._get_active_character(target_player)
            
            if target_character:
                # 设置健康值，然后启用"免于被击倒"机制
                target_character.health = 5  # Set to a normal value
                target_character.survive_at_hp = True  # Enable the survive mechanism
                
                # Cause enough damage to reduce health to 0 or below
                original_health = target_character.health
                self.engine._apply_damage(target_character, original_health + 2, DamageType.ELEMENTAL)
                
                # Due to the survive mechanism, the character should still be alive with 1 HP
                self.assertTrue(target_character.is_alive)
                self.assertEqual(target_character.health, 1)
                self.assertFalse(target_character.survive_at_hp)  # Mechanism should be consumed
    
    def test_quick_vs_combat_actions(self):
        """测试快速行动与战斗行动"""
        # 创建游戏
        deck1 = self.create_test_deck()
        deck2 = self.create_test_deck()
        game_id = self.engine.create_game_state("player1", "player2", deck1, deck2)
        
        game_state = self.engine.get_game_state(game_id)
        if game_state:
            # 测试打出支援牌（应该是快速行动）
            player = game_state.players[0]  # 玩家1
            active_character = self.engine._get_active_character(player)
            
            # 添加一些骰子 so the player can pay for cards
            player.dice = [ElementType.OMNI, ElementType.OMNI, ElementType.PYRO, ElementType.HYDRO]
            
            # 添加一张支援卡到手牌
            support_card = Card(
                id="support_test",
                name="测试支援牌",
                card_type=CardType.SUPPORT,
                cost=[ElementType.CRYSTAL, ElementType.CRYSTAL]  # 这需要任意元素骰
            )
            player.hand_cards.append(support_card)
            
            # 模拟玩家打出支援牌
            old_action_count = game_state.round_actions
            old_player_index = game_state.current_player_index
            game_state = self.engine._process_play_card_action(
                game_state,
                {"card_id": "support_test"}
            )
            
            # 支援牌是快速行动，不应该切换玩家
            # 注意：支援牌虽然本身是快速行动，但在当前实现中，打出手牌会增加round_actions
            self.assertEqual(game_state.current_player_index, old_player_index)  # 应该还是原来的玩家
            self.assertEqual(game_state.round_actions, old_action_count + 1)


class TestGameMechanics(unittest.TestCase):
    """测试特殊游戏机制"""
    
    def setUp(self):
        self.engine = GameEngine()
    
    def create_test_deck(self) -> List[Card]:
        """创建测试卡组"""
        deck = []
        
        # 添加角色卡
        for i in range(3):
            char_card = CharacterCard(
                id=f"char_{i}",
                name=f"角色_{i}",
                card_type=CardType.CHARACTER,
                cost=[ElementType.OMNI, ElementType.OMNI],
                health=10,
                max_health=10,
                energy=0,
                max_energy=3,
                element_type=ElementType.PYRO if i % 3 == 0 else ElementType.HYDRO if i % 3 == 1 else ElementType.CRYO,
                skills=[
                    {
                        "id": f"skill_{i}_1",
                        "name": f"技能1_{i}",
                        "cost": [ElementType.SAME, ElementType.SAME],
                        "damage": 1,
                        "skill_type": "NORMAL_ATTACK" if i % 2 == 0 else "ELEMENTAL_SKILL",
                        "damage_type": DamageType.ELEMENTAL
                    }
                ]
            )
            deck.append(char_card)
        
        # 添加事件卡
        for i in range(10):
            event_card = Card(
                id=f"event_{i}",
                name=f"料理_{i}" if i < 5 else f"事件_{i}",
                card_type=CardType.EVENT,
                cost=[ElementType.OMNI],
                description="料理效果" if i < 5 else "普通事件"
            )
            deck.append(event_card)
        
        return deck
    
    def test_heavy_attack_mechanic(self):
        """测试重击机制"""
        deck1 = self.create_test_deck()
        deck2 = self.create_test_deck()
        game_id = self.engine.create_game_state("player1", "player2", deck1, deck2)
        
        game_state = self.engine.get_game_state(game_id)
        if game_state:
            # 设置玩家有偶数个骰子，触发重击
            current_player = game_state.players[game_state.current_player_index]
            current_player.dice = [ElementType.PYRO, ElementType.HYDRO]  # 2个骰子（偶数）
            
            # 获取出战角色和技能
            active_character = self.engine._get_active_character(current_player)
            if active_character and active_character.skills:
                skill = active_character.skills[0]
                skill_id = skill['id']
                
                # 记录目标角色原始生命值
                target_player = game_state.players[1]
                target_character = self.engine._get_active_character(target_player)
                if target_character:
                    original_health = target_character.health
                    
                    # 使用技能攻击
                    game_state = self.engine._process_use_skill_action(
                        game_state,
                        {"skill_id": skill_id}
                    )
                    
                    # 由于是偶数骰子，触发重击，伤害应为原伤害+1
                    expected_damage = skill.get('damage', 1) + 1  # 基础伤害+重击加成
                    self.assertEqual(target_character.health, original_health - expected_damage)
    
    def test_elemental_tuning(self):
        """测试元素调和"""
        deck1 = self.create_test_deck()
        deck2 = self.create_test_deck()
        game_id = self.engine.create_game_state("player1", "player2", deck1, deck2)
        
        game_state = self.engine.get_game_state(game_id)
        if game_state:
            current_player = game_state.players[game_state.current_player_index]
            active_character = self.engine._get_active_character(current_player)
            
            # 确保玩家有手牌和骰子
            if current_player.hand_cards and current_player.dice:
                original_dice_count = len(current_player.dice)
                
                # 使用元素调和
                game_state = self.engine._process_elemental_tuning_action(
                    game_state,
                    {"card_index": 0}  # 丢弃第一张手牌
                )
                
                # 检查元素调和是否成功
                self.assertTrue(current_player.has_used_elemental_tuning)


if __name__ == '__main__':
    # 运行测试
    unittest.main()