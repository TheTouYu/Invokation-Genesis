"""
七圣召唤游戏引擎核心实现 - 改进版
"""
from typing import Dict, List, Optional, Any
from models.game_models import GameState, PlayerState, Card, CharacterCard
from models.enums import GamePhase, PlayerAction, ElementType, CharacterStatus, DamageType
from game_engine.element_reactions import ElementReactionSystem
from game_engine.deck_validation import DeckValidationSystem
import logging


class GameEngine:
    """
    游戏引擎核心类，处理游戏逻辑和状态变更
    """
    
    def __init__(self):
        self.game_states: Dict[str, GameState] = {}  # 存储游戏会话状态
        self.element_reaction_system = ElementReactionSystem()  # 元素反应系统
        self.deck_validation_system = DeckValidationSystem()  # 卡组验证系统
        logging.basicConfig(level=logging.INFO)
        self.logger = logging.getLogger(__name__)

    def create_game_state(self, player1_id: str, player2_id: str, deck1: List[Card], deck2: List[Card]) -> str:
        """
        创建新的游戏状态，包含初始手牌和初始手牌替换机制
        """
        # 首先验证卡组
        validation_result1 = self.deck_validation_system.validate_deck(deck1)
        validation_result2 = self.deck_validation_system.validate_deck(deck2)
        
        if not validation_result1["is_valid"]:
            self.logger.error(f"Player {player1_id} deck validation failed: {validation_result1['errors']}")
            return None  # 返回None表示创建失败
        
        if not validation_result2["is_valid"]:
            self.logger.error(f"Player {player2_id} deck validation failed: {validation_result2['errors']}")
            return None  # 返回None表示创建失败
        
        import random
        
        # 初始化玩家手牌（每个玩家抽5张）
        player1_deck = deck1.copy()
        player2_deck = deck2.copy()
        
        # 分离角色卡和非角色卡
        player1_character_cards = [card for card in player1_deck if isinstance(card, CharacterCard)]
        player1_non_character_cards = [card for card in player1_deck if not isinstance(card, CharacterCard)]
        
        player2_character_cards = [card for card in player2_deck if isinstance(card, CharacterCard)]
        player2_non_character_cards = [card for card in player2_deck if not isinstance(card, CharacterCard)]
        
        # 随机抽取初始手牌（从非角色卡中抽取）
        player1_hand = []
        for _ in range(5):
            if player1_non_character_cards:
                card = random.choice(player1_non_character_cards)
                player1_hand.append(card)
                player1_non_character_cards.remove(card)
        
        player2_hand = []
        for _ in range(5):
            if player2_non_character_cards:
                card = random.choice(player2_non_character_cards)
                player2_hand.append(card)
                player2_non_character_cards.remove(card)
        
        # 使用剩余的非角色卡更新玩家牌库
        player1_remaining_deck = player1_character_cards + player1_non_character_cards
        player2_remaining_deck = player2_character_cards + player2_non_character_cards
        
        # 创建玩家状态
        player1_state = PlayerState(
            player_id=player1_id,
            deck=player1_remaining_deck,
            hand_cards=player1_hand,
            characters=player1_character_cards,  # 添加角色
            dice=[],
            supports=[],
            summons=[],
            has_card_replace_option_used=False  # 标记未使用手牌替换
        )
        
        player2_state = PlayerState(
            player_id=player2_id,
            deck=player2_remaining_deck,
            hand_cards=player2_hand,
            characters=player2_character_cards,  # 添加角色
            dice=[],
            supports=[],
            summons=[],
            has_card_replace_option_used=False  # 标记未使用手牌替换
        )
        
        # 创建游戏状态
        game_state = GameState(
            players=[player1_state, player2_state],
            current_player_index=0,  # 默认玩家1先手
            first_player_index=0,  # 记录先手玩家
            phase=GamePhase.ROLL_PHASE,
            can_replace_initial_cards=True  # 允许替换初始手牌
        )
        
        # 生成唯一的游戏ID
        import uuid
        game_id = str(uuid.uuid4())
        self.game_states[game_id] = game_state
        
        self.logger.info(f"Created new game with ID: {game_id}")
        return game_id

    def process_action(self, game_id: str, player_id: str, action: PlayerAction, payload: Dict[str, Any]) -> Optional[GameState]:
        """
        处理玩家操作
        """
        if game_id not in self.game_states:
            self.logger.error(f"Game with ID {game_id} does not exist")
            return None
            
        game_state = self.game_states[game_id]
        
        # 验证操作是否来自当前行动玩家
        current_player = game_state.players[game_state.current_player_index]
        if current_player.player_id != player_id:
            self.logger.error(f"Player {player_id} is not the current player")
            return None
        
        # 特殊处理：初始手牌替换
        if game_state.can_replace_initial_cards and action == PlayerAction.REPLACE_CARDS:
            return self._replace_initial_cards(game_state, payload)
        
        # 根据当前阶段处理操作
        if game_state.phase == GamePhase.ROLL_PHASE:
            return self._roll_phase(game_state, action, payload)
        elif game_state.phase == GamePhase.ACTION_PHASE:
            return self._action_phase(game_state, action, payload)
        elif game_state.phase == GamePhase.END_PHASE:
            return self._end_phase(game_state, action, payload)
        
        return game_state

    def _replace_initial_cards(self, game_state: GameState, payload: Dict[str, Any]) -> GameState:
        """
        处理初始手牌替换
        """
        player_index = game_state.current_player_index
        player = game_state.players[player_index]
        
        # 获取要替换的卡牌ID
        card_ids_to_replace = payload.get('card_ids', [])
        
        # 从手牌中找到要替换的卡牌并放回牌库顶部
        cards_to_return = []
        for card_id in card_ids_to_replace:
            for i, card in enumerate(player.hand_cards):
                if card.id == card_id:
                    cards_to_return.append((i, card))
                    break
        
        # 将卡牌放回牌库顶部
        for _, card in reversed(cards_to_return):
            player.deck.insert(0, card)
        
        # 从牌库中抽取相同数量的新卡牌
        for _ in card_ids_to_replace:
            if player.deck:
                new_card = player.deck.pop(0)
                player.hand_cards.append(new_card)
        
        # 标记该玩家已完成手牌替换
        player.has_card_replace_option_used = True
        
        # 检查是否两个玩家都完成了手牌替换
        all_players_replaced = all(p.has_card_replace_option_used for p in game_state.players)
        if all_players_replaced:
            game_state.can_replace_initial_cards = False
            # 开始投骰阶段
            game_state.phase = GamePhase.ROLL_PHASE
            self.logger.info("Both players have replaced cards, starting roll phase")
        
        # 如果还有玩家未替换，继续让当前玩家替换或切换到下一个玩家
        elif player_index < len(game_state.players) - 1:
            # 切换到下一个玩家继续替换手牌
            game_state.current_player_index += 1
        else:
            # 所有玩家已经有机会替换，但有人选择不替换，开始投骰阶段
            game_state.can_replace_initial_cards = False
            game_state.phase = GamePhase.ROLL_PHASE
        
        # 记录到游戏日志
        game_state.game_log.append(f"玩家 {player.player_id} 替换了 {len(card_ids_to_replace)} 张手牌")
        
        return game_state

    def _roll_phase(self, game_state: GameState, action: PlayerAction, payload: Dict[str, Any]) -> GameState:
        """
        处理投骰阶段的逻辑
        """
        if action == PlayerAction.REROLL_DICE:
            # 处理重投骰子
            player_index = game_state.current_player_index
            player = game_state.players[player_index]
            
            # 重投指定索引的骰子
            indices_to_reroll = payload.get('dice_indices', [])
            dice_types = [ElementType.ANEMO, ElementType.GEO, ElementType.ELECTRO, 
                          ElementType.DENDRO, ElementType.HYDRO, ElementType.PYRO, 
                          ElementType.CRYO, ElementType.OMNI]  # 包含万能元素
            
            for i in indices_to_reroll:
                if 0 <= i < len(player.dice):
                    # 随机选择一个新的骰子类型
                    import random
                    player.dice[i] = random.choice(dice_types)
            
            # 标记已使用重投选项
            player.has_reroll_option_used = True
            
            # 记录到游戏日志
            game_state.game_log.append(f"玩家 {player.player_id} 重投了骰子")
        else:
            # 初始化每个玩家的骰子（每个玩家8个骰子）
            for i, player in enumerate(game_state.players):
                # 每个玩家获得8个随机骰子
                dice_types = [ElementType.ANEMO, ElementType.GEO, ElementType.ELECTRO, 
                              ElementType.DENDRO, ElementType.HYDRO, ElementType.PYRO, 
                              ElementType.CRYO]
                
                # 随机生成8个骰子
                player.dice = []
                for _ in range(8):
                    import random
                    # 8%概率生成万能元素骰
                    if random.random() < 0.08:
                        player.dice.append(ElementType.OMNI)
                    else:
                        player.dice.append(random.choice(dice_types))
            
            # 记录到游戏日志
            game_state.game_log.append(f"投骰阶段 - 回合 {game_state.round_number}")
            
            # 简单版本：直接进入行动阶段
            game_state.phase = GamePhase.ACTION_PHASE
            game_state.game_log.append(f"进入行动阶段 - 回合 {game_state.round_number}")
        
        return game_state

    def _action_phase(self, game_state: GameState, action: PlayerAction, payload: Dict[str, Any]) -> GameState:
        """
        处理行动阶段的逻辑
        """
        if action == PlayerAction.USE_SKILL:
            result = self._process_use_skill_action(game_state, payload)
            # 使用技能是战斗行动，切换到对方玩家
            self._switch_current_player(game_state)
            return result
        elif action == PlayerAction.PLAY_CARD:
            result = self._process_play_card_action(game_state, payload)
            # 判断是快速行动还是战斗行动
            card_id = payload.get('card_id')
            card = self._find_card_by_id(game_state.players[game_state.current_player_index].hand_cards, card_id)
            if card and card.card_type in ['SUPPORT', 'EVENT']:
                # 支援牌和事件牌是快速行动，可以继续行动
                game_state.quick_action_available = True
                return result
            else:
                # 其他卡牌（如装备牌）是战斗行动
                self._switch_current_player(game_state)
                return result
        elif action == PlayerAction.SWITCH_CHARACTER:
            result = self._process_switch_action(game_state, payload)
            # 切换角色是战斗行动，切换到对方玩家
            self._switch_current_player(game_state)
            return result
        elif action == PlayerAction.ELEMENTAL_TUNING:
            result = self._process_elemental_tuning_action(game_state, payload)
            # 元素调和是快速行动，可以继续行动
            game_state.quick_action_available = True
            return result
        elif action == PlayerAction.PASS:
            return self._process_pass_action(game_state)
        
        return game_state

    def _end_phase(self, game_state: GameState, action: PlayerAction, payload: Dict[str, Any]) -> GameState:
        """
        处理结束阶段的逻辑
        """
        # 处理结束阶段触发的卡牌效果（从先手牌手开始）
        # 先处理当前先手玩家的效果
        first_player = game_state.players[game_state.first_player_index]
        # 应用先手玩家的结束阶段效果（如某些卡牌效果）
        self._apply_end_phase_effects(first_player, game_state)
        
        # 再处理后手玩家的效果
        second_player_index = 1 - game_state.first_player_index
        second_player = game_state.players[second_player_index]
        # 应用后手玩家的结束阶段效果
        self._apply_end_phase_effects(second_player, game_state)
        
        # 应用状态效果（如燃烧、绽放等持续效果）
        self._apply_status_effects(game_state)
        
        # 每位牌手从自己的牌堆中抓2张牌
        for player in game_state.players:
            # 抓2张牌
            for _ in range(2):
                if player.deck:
                    card = player.deck.pop(0)  # 从牌堆顶部抽牌
                    if len(player.hand_cards) < player.max_hand_size:  # 检查手牌上限
                        player.hand_cards.append(card)
                        game_state.game_log.append(f"玩家 {player.player_id} 抓到 {card.name}")
                    else:
                        # 如果手牌已满，丢弃这张牌
                        game_state.game_log.append(f"玩家 {player.player_id} 手牌已满，丢弃了 {card.name}")
        
        # 清空本轮行动次数
        game_state.round_actions = 0
        game_state.quick_action_available = True  # 重置快速行动可用状态
        
        # 切换到下一回合
        game_state.round_number += 1
        
        # 检查回合数上限（七圣召唤中，第15回合开始时如果仍未分出胜负，则双方都输）
        if game_state.round_number >= 15:
            game_state.is_game_over = True
            game_state.winner = None  # 平局
            game_state.game_log.append(f"达到回合数上限，游戏平局")
            return game_state
        
        # 检查获胜条件（是否有玩家所有角色都被击倒）
        winner = self._check_victory_conditions(game_state)
        if winner is not None:
            game_state.is_game_over = True
            game_state.winner = winner
            game_state.game_log.append(f"游戏结束，获胜者: {winner}")
            return game_state
        
        # 切换先手玩家（在实际规则中，上回合最后行动的玩家成为下回合的先手）
        # 记录当前回合最后行动的玩家作为下回合先手
        # 当前game_state.current_player_index在行动阶段结束时是行动过的玩家
        game_state.first_player_index = game_state.current_player_index
        game_state.current_player_index = game_state.first_player_index
        
        # 重置玩家的回合状态
        for player in game_state.players:
            player.round_passed = False
            player.has_used_elemental_tuning = False  # 重置元素调和使用状态
            player.has_reroll_option_used = False  # 重置重投选项使用状态
        
        # 进入下一回合的投骰阶段
        game_state.phase = GamePhase.ROLL_PHASE
        game_state.game_log.append(f"回合 {game_state.round_number} 开始")
        
        return game_state

    def _apply_end_phase_effects(self, player: PlayerState, game_state: GameState):
        """
        应用玩家在结束阶段的效果
        """
        # 检查角色的结束阶段效果
        for i, character in enumerate(player.characters):
            if not character.is_alive:
                continue
                
            # 检查角色状态效果的结束阶段处理
            for status in character.character_statuses:
                if status.get('name') == 'HealRegen':  # 持续治疗状态
                    heal_amount = status.get('effect', {}).get('heal_amount', 0)
                    character.health = min(character.health + heal_amount, character.max_health)
                    game_state.game_log.append(f"角色 {character.name} 在结束阶段恢复了 {heal_amount} 点生命值")
        
        # 检查支援牌的结束阶段效果
        for i, support in enumerate(player.supports):
            # 一些支援牌在结束阶段有特殊效果
            if support.get('name') == '田铁嘴':
                # 田铁嘴在结束阶段可能有费用返还效果
                pass

    def _process_use_skill_action(self, game_state: GameState, payload: Dict[str, Any]) -> GameState:
        """
        处理使用技能操作
        """
        skill_id = payload.get('skill_id')
        player_index = game_state.current_player_index
        player = game_state.players[player_index]
        active_character = self._get_active_character(player)
        
        if not active_character:
            self.logger.error(f"Player {player.player_id} has no active character")
            return game_state
        
        # 查找技能
        skill = None
        for s in active_character.skills:
            if s.get('id') == skill_id:
                skill = s
                break
        
        if not skill:
            self.logger.error(f"Skill {skill_id} not found for character {active_character.name}")
            return game_state

        # 检查技能费用
        skill_cost = skill.get('cost', [])
        if not skill_cost:
            # 有些技能可能没有费用
            skill_cost = []

        if not self._can_pay_cost(player, skill_cost):
            self.logger.error(f"Player {player.player_id} cannot pay cost for skill {skill_id}")
            return game_state

        # 支付费用
        if not self._pay_cost(player, skill_cost):
            self.logger.error(f"Failed to pay cost for skill {skill_id}")
            return game_state

        # 检查出战角色是否被冻结、眩晕等状态影响，无法使用技能
        for status in active_character.character_statuses:
            if status.get('name') in ['Frozen', 'Stun']:  # 冻结、眩晕状态
                self.logger.error(f"Character {active_character.name} is in status {status.get('name')} and cannot use skill")
                return game_state

        # 记录到游戏日志
        game_state.game_log.append(f"玩家 {player.player_id} 使用了技能 {skill.get('name', skill_id)}")
        
        # 增加行动次数
        game_state.round_actions += 1

        # 增加角色充能（使用普通攻击或元素战技后获得1点充能）
        skill_type = skill.get('skill_type', '')
        if skill_type in ['NORMAL_ATTACK', 'ELEMENTAL_SKILL']:
            active_character.energy = min(active_character.energy + 1, active_character.max_energy)

        # 检查是否为重击（当前骰子数为偶数时，普通攻击变为重击）
        is_heavy_attack = False
        if len(player.dice) % 2 == 0 and skill_type == 'NORMAL_ATTACK':
            is_heavy_attack = True
            game_state.game_log.append(f"触发重击效果！")

        # 处理技能效果（简化处理，实际需要实现完整的伤害计算）
        damage = skill.get('damage', 0)
        damage_type = skill.get('damage_type', None)
        element_application = skill.get('element_application', None)
        
        if damage > 0 and damage_type:
            target_player_index = 1 - player_index  # 攻击对方
            target_player = game_state.players[target_player_index]
            target_character = self._get_active_character(target_player)
            
            if target_character and target_character.is_alive:
                # 应用元素附着
                if element_application:
                    self.element_reaction_system.apply_element_attachment(target_character, element_application)
                
                # 如果是重击，增加伤害
                if is_heavy_attack:
                    damage = damage + 1  # 重击增加1点伤害
                
                # 应用伤害
                actual_damage = self._apply_damage(target_character, damage, damage_type, element_application)
                
                # 检查是否击倒角色
                if target_character.health <= 0:
                    self._knock_out_character(game_state, target_player_index)
                    game_state.game_log.append(f"角色 {target_character.name} 被击倒！")
                
                game_state.game_log.append(f"对角色 {target_character.name} 造成了 {actual_damage} 点{damage_type.value}伤害")
        
        return game_state

    def _process_play_card_action(self, game_state: GameState, payload: Dict[str, Any]) -> GameState:
        """
        处理打出手牌操作
        """
        card_id = payload.get('card_id')
        player_index = game_state.current_player_index
        player = game_state.players[player_index]
        
        # 查找手牌中的卡牌
        card_to_play = None
        card_index = -1
        for i, card in enumerate(player.hand_cards):
            if card.id == card_id:
                card_to_play = card
                card_index = i
                break
        
        if not card_to_play:
            self.logger.warning(f"Card {card_id} not found in player's hand")
            return game_state

        # 检查是否为秘传卡，每场对局只能使用一张
        if '秘传' in card_to_play.name or 'Legacy' in card_to_play.name:
            if not hasattr(player, 'used_legacy_card'):
                player.used_legacy_card = False
            if player.used_legacy_card:
                self.logger.error(f"Player {player.player_id} has already used a Legacy card this game")
                return game_state
            # 标记已使用秘传卡
            player.used_legacy_card = True

        # 检查卡牌费用
        if not self._can_pay_cost(player, card_to_play.cost):
            self.logger.error(f"Player {player.player_id} cannot pay cost for card {card_id}")
            return game_state

        # 支付费用
        if not self._pay_cost(player, card_to_play.cost):
            self.logger.error(f"Failed to pay cost for card {card_id}")
            return game_state

        # 从手牌中移除卡牌
        player.hand_cards.pop(card_index)
        
        # 处理卡牌效果
        if card_to_play.card_type == 'WEAPON':
            # 装备武器
            active_character = self._get_active_character(player)
            if active_character:
                active_character.weapon = card_to_play
                game_state.game_log.append(f"角色 {active_character.name} 装备了 {card_to_play.name}")
        elif card_to_play.card_type == 'ARTIFACT':
            # 装备圣遗物
            active_character = self._get_active_character(player)
            if active_character:
                active_character.artifact = card_to_play
                game_state.game_log.append(f"角色 {active_character.name} 装备了 {card_to_play.name}")
        elif card_to_play.card_type == 'TALENT':
            # 装备天赋
            active_character = self._get_active_character(player)
            if active_character and self._character_match(active_character, card_to_play):
                active_character.talent = card_to_play
                game_state.game_log.append(f"角色 {active_character.name} 装备了天赋 {card_to_play.name}")
        elif card_to_play.card_type == 'SUPPORT':
            # 放置支援牌
            if len(player.supports) < player.max_support_size:
                player.supports.append({
                    'id': card_to_play.id,
                    'name': card_to_play.name,
                    'card_type': card_to_play.card_type,
                    'effect': card_to_play.description
                })
                game_state.game_log.append(f"玩家 {player.player_id} 放置了支援牌 {card_to_play.name}")
            else:
                # 按规则需要先选择一张支援牌弃置
                game_state.game_log.append(f"支援区已满，无法放置新的支援牌")
                game_state.game_log.append(f"请选择一张支援牌进行弃置")
                # 将卡牌返回手牌
                player.hand_cards.append(card_to_play)
                return game_state
        elif card_to_play.card_type == 'EVENT':
            # 处理事件卡效果
            game_state.game_log.append(f"玩家 {player.player_id} 打出了事件卡 {card_to_play.name}")
            
            # 检查是否有复苏效果的料理，一回合内只能打出一张
            if '复苏' in card_to_play.description:
                if not hasattr(player, 'used_recharge_food_this_round'):
                    player.used_recharge_food_this_round = False
                if player.used_recharge_food_this_round:
                    game_state.game_log.append(f"本回合已使用过复苏效果的料理，无法再次使用")
                    # 将卡牌返回手牌
                    player.hand_cards.append(card_to_play)
                    return game_state
                else:
                    player.used_recharge_food_this_round = True
            
            # 处理特定的事件卡效果（如料理、治疗、护盾等）
            if '料理' in card_to_play.description or '治疗' in card_to_play.description:
                # 找到出战角色并治疗
                active_character = self._get_active_character(player)
                if active_character:
                    # 检查角色是否处于饱腹状态（如果是料理卡）
                    if '料理' in card_to_play.description and hasattr(active_character, 'has_full_stomach') and active_character.has_full_stomach:
                        game_state.game_log.append(f"角色 {active_character.name} 已处于饱腹状态，料理无效")
                    else:
                        # 通常料理或治疗卡会恢复生命值
                        heal_amount = 2  # 通常料理恢复2点生命值
                        original_health = active_character.health
                        active_character.health = min(active_character.health + heal_amount, active_character.max_health)
                        actual_heal = active_character.health - original_health
                        game_state.game_log.append(f"角色 {active_character.name} 恢复了 {actual_heal} 点生命值")
                        
                        # 标记角色进入饱腹状态（如果是料理卡）
                        if '料理' in card_to_play.description:
                            active_character.has_full_stomach = True
            
            # 处理生成护盾的事件卡
            elif '护盾' in card_to_play.description:
                active_character = self._get_active_character(player)
                if active_character:
                    # 通常护盾卡会提供1-2点护盾
                    shield_amount = 2  # 示例值
                    current_max_shield = getattr(active_character, 'max_shield', 2)  # 默认最大护盾为2
                    active_character.shield = min(active_character.shield + shield_amount, current_max_shield)
                    game_state.game_log.append(f"角色 {active_character.name} 获得了 {shield_amount} 点护盾")
            
            # 添加其他事件卡效果处理...
        else:
            # 其他类型的卡牌处理
            game_state.game_log.append(f"玩家 {player.player_id} 打出了卡牌 {card_to_play.name}")
        
        # 记录到游戏日志
        game_state.game_log.append(f"玩家 {player.player_id} 打出了卡牌 {card_to_play.name}")
        
        # 增加行动次数
        game_state.round_actions += 1
        
        return game_state

    def _process_switch_action(self, game_state: GameState, payload: Dict[str, Any]) -> GameState:
        """
        处理切换角色操作
        """
        new_character_index = payload.get('character_index')
        player_index = game_state.current_player_index
        player = game_state.players[player_index]
        
        if 0 <= new_character_index < len(player.characters):
            old_index = player.active_character_index
            old_character = player.characters[old_index] if old_index < len(player.characters) else None
            
            # 检查是否可以切换角色
            if not player.can_change_active_character:
                self.logger.error(f"Player {player.player_id} cannot switch character due to status effect")
                return game_state

            # 切换角色需要支付1个任意元素骰
            switch_cost = [ElementType.CRYSTAL]  # 任意元素骰

            if not self._can_pay_cost(player, switch_cost):
                self.logger.error(f"Player {player.player_id} cannot pay cost for switching character")
                return game_state

            # 支付切换费用
            if not self._pay_cost(player, switch_cost):
                self.logger.error(f"Failed to pay cost for switching character")
                return game_state

            player.active_character_index = new_character_index
            
            # 记录到游戏日志
            old_char_name = old_character.name if old_character else "unknown"
            new_char = player.characters[new_character_index]
            game_state.game_log.append(f"玩家 {player.player_id} 从角色 {old_char_name} 切换到角色 {new_char.name}")
            
            # 增加行动次数
            game_state.round_actions += 1
            
            # 标记下落攻击可用（切换角色后下一次近战攻击变为下落攻击）
            # 这里我们用一个标志来表示
            if not hasattr(player, 'plunge_attack_available'):
                player.plunge_attack_available = True
            else:
                player.plunge_attack_available = True
        else:
            self.logger.warning(f"Invalid character index {new_character_index}")
        
        return game_state

    def _process_elemental_tuning_action(self, game_state: GameState, payload: Dict[str, Any]) -> GameState:
        """
        处理元素调和操作
        """
        player_index = game_state.current_player_index
        player = game_state.players[player_index]
        
        # 检查是否已经使用过元素调和
        if player.has_used_elemental_tuning:
            self.logger.error(f"Player {player.player_id} has already used elemental tuning this round")
            return game_state
        
        # 获取要丢弃的手牌索引
        card_index_to_discard = payload.get('card_index')
        if card_index_to_discard is None or card_index_to_discard < 0 or card_index_to_discard >= len(player.hand_cards):
            self.logger.error(f"Invalid card index to discard: {card_index_to_discard}")
            return game_state
        
        # 获取当前出战角色
        active_character = self._get_active_character(player)
        if not active_character:
            self.logger.error(f"Player {player.player_id} has no active character")
            return game_state
        
        # 检查是否有骰子可以转换
        if not player.dice:
            self.logger.error(f"Player {player.player_id} has no dice to convert")
            return game_state
        
        # 找到第一个骰子并转换为当前角色的元素类型
        dice_to_convert_idx = 0  # 可以扩展为选择任意骰子
        original_dice = player.dice[dice_to_convert_idx]
        player.dice[dice_to_convert_idx] = active_character.element_type
        
        # 丢弃手牌
        discarded_card = player.hand_cards.pop(card_index_to_discard)
        
        # 标记已使用元素调和
        player.has_used_elemental_tuning = True
        
        # 记录到游戏日志
        game_state.game_log.append(f"玩家 {player.player_id} 使用元素调和，丢弃了 {discarded_card.name} 并将一个骰子转换为 {active_character.element_type.value}")
        
        # 增加行动次数
        game_state.round_actions += 1
        
        return game_state

    def _process_pass_action(self, game_state: GameState) -> GameState:
        """
        处理结束回合操作
        """
        current_player = game_state.players[game_state.current_player_index]
        game_state.game_log.append(f"玩家 {current_player.player_id} 结束了回合")
        
        # 标记当前玩家已结束回合
        current_player.round_passed = True
        
        # 检查是否两个玩家都结束了回合
        all_players_passed = all(p.round_passed for p in game_state.players)
        if all_players_passed:
            # 都结束回合，进入结束阶段
            game_state.phase = GamePhase.END_PHASE
        else:
            # 只有一个玩家结束回合，切换到另一个玩家
            game_state.current_player_index = 1 - game_state.current_player_index
        
        return game_state

    def _get_active_character(self, player: PlayerState) -> Optional[CharacterCard]:
        """
        获取玩家当前出战的角色
        """
        if 0 <= player.active_character_index < len(player.characters):
            character = player.characters[player.active_character_index]
            if character.is_alive:  # 只有存活的角色才能是出战角色
                return character
            else:
                # 如果当前出战角色已死亡，查找下一个存活的角色
                for i, char in enumerate(player.characters):
                    if char.is_alive:
                        player.active_character_index = i
                        return char
        return None

    def _can_pay_cost(self, player: PlayerState, cost: List[Any]) -> bool:
        """
        检查玩家是否能支付费用
        """
        # 创建一个骰子副本进行模拟支付
        dice_counts = {}
        for die in player.dice:
            dice_counts[die] = dice_counts.get(die, 0) + 1
        
        # 万能骰子数量
        omni_count = dice_counts.get(ElementType.OMNI, 0)
        
        # 获取当前出战角色
        active_character = self._get_active_character(player)
        if not active_character:
            return False  # 没有有效角色，无法支付
        
        # 对每种需要的费用进行检查
        for required_element in cost:
            if required_element == ElementType.OMNI:
                # 万能元素费用：必须用万能骰子支付
                if dice_counts.get(ElementType.OMNI, 0) > 0:
                    dice_counts[ElementType.OMNI] -= 1
                else:
                    return False
            elif required_element == ElementType.SAME:
                # SAME类型：需要相同元素类型的骰子
                matched = False
                for die_type, count in dice_counts.items():
                    if count > 0 and die_type == active_character.element_type:
                        dice_counts[die_type] -= 1
                        matched = True
                        break
                if not matched and omni_count > 0:
                    # 如果没有对应元素的骰子，可以用万能骰子
                    dice_counts[ElementType.OMNI] -= 1
                    omni_count -= 1
                elif not matched:
                    return False
            elif required_element == ElementType.CRYSTAL:
                # 晶体元素：可以是任意元素或万能骰子
                matched = False
                for die_type, count in dice_counts.items():
                    if count > 0 and die_type != ElementType.PHYSICAL and die_type != ElementType.OMNI:
                        dice_counts[die_type] -= 1
                        matched = True
                        break
                if not matched and omni_count > 0:
                    # 如果没有晶体元素骰子，可以用万能骰子
                    dice_counts[ElementType.OMNI] -= 1
                    omni_count -= 1
                elif not matched:
                    return False
            else:
                # 需要特定元素骰子
                if dice_counts.get(required_element, 0) > 0:
                    dice_counts[required_element] -= 1
                elif omni_count > 0:
                    # 使用万能骰子代替
                    dice_counts[ElementType.OMNI] -= 1
                    omni_count -= 1
                else:
                    return False
        
        return True

    def _pay_cost(self, player: PlayerState, cost: List[Any]) -> bool:
        """
        支付费用
        """
        # 检查是否能支付
        if not self._can_pay_cost(player, cost):
            return False
        
        # 获取当前出战角色
        active_character = self._get_active_character(player)
        if not active_character:
            return False  # 没有有效角色，无法支付
        
        # 实际支付
        for required_element in cost:
            if required_element == ElementType.OMNI:
                # 万能元素费用：必须用万能骰子支付
                if ElementType.OMNI in player.dice:
                    player.dice.remove(ElementType.OMNI)
                else:
                    return False  # 无法支付
            elif required_element == ElementType.SAME:
                # SAME类型：需要相同元素类型的骰子
                paid = False
                for i, die in enumerate(player.dice):
                    if die == active_character.element_type:
                        player.dice.pop(i)
                        paid = True
                        break
                if not paid:
                    # 用万能骰子支付
                    if ElementType.OMNI in player.dice:
                        player.dice.remove(ElementType.OMNI)
                    else:
                        return False  # 无法支付
            elif required_element == ElementType.CRYSTAL:
                # 晶体元素：可以是任意元素或万能骰子
                paid = False
                for i, die in enumerate(player.dice):
                    if die != ElementType.PHYSICAL and die != ElementType.OMNI:
                        player.dice.pop(i)
                        paid = True
                        break
                if not paid:
                    # 用万能骰子支付
                    if ElementType.OMNI in player.dice:
                        player.dice.remove(ElementType.OMNI)
                    else:
                        return False  # 无法支付
            else:
                # 需要特定元素骰子
                if required_element in player.dice:
                    player.dice.remove(required_element)
                elif ElementType.OMNI in player.dice:
                    # 用万能骰子代替
                    player.dice.remove(ElementType.OMNI)
                else:
                    return False  # 无法支付
        
        return True

    def _apply_damage(self, character: CharacterCard, damage: int, damage_type: DamageType, source_element: Optional[ElementType] = None, is_physical_hit: bool = False) -> int:
        """
        应用伤害到角色，支持元素反应计算
        返回实际造成的伤害
        """
        if damage_type == DamageType.HEAL:
            # 治疗效果
            character.health = min(character.health + abs(damage), character.max_health)
            return abs(damage)
        else:
            # 检查角色是否有护盾
            shield_absorption = min(damage, getattr(character, 'shield', 0))
            remaining_damage = damage - shield_absorption
            
            # 如果有护盾，先扣除护盾
            if shield_absorption > 0:
                character.shield -= shield_absorption
            
            # 如果伤害被完全抵消，直接返回
            if remaining_damage <= 0:
                return 0
            
            # 计算元素反应
            actual_damage = remaining_damage
            if source_element and source_element != ElementType.PHYSICAL:
                # 检查是否与角色身上的元素产生反应
                reaction_type, effect_info = self.element_reaction_system.handle_element_attachment(character, source_element)
                if reaction_type:
                    actual_damage, reaction_effects = self.element_reaction_system.calculate_reaction_damage(remaining_damage, reaction_type)
                    # 应用额外效果
                    if reaction_effects.get("additional_effect") == "force_character_switch":
                        # 超载反应强制切换角色，这里简化处理
                        pass
                    elif reaction_effects.get("additional_effect") == "spread_damage_to_other_enemies":
                        # 扩散伤害反应，对其他敌人造成伤害
                        spread_damage = reaction_effects.get("spread_damage", 0)
                        # 对其他角色造成扩散伤害
                        self._apply_spread_damage(character, spread_damage)
                    elif reaction_effects.get("additional_effect") == "create_status":
                        # 创建状态效果，如燃烧、绽放等
                        status_name = reaction_effects.get("status_name")
                        duration = reaction_effects.get("duration", 1)
                        # 添加到角色的状态列表中
                        character.character_statuses.append({
                            'name': status_name,
                            'duration': duration,
                            'effect': reaction_effects  # 保存效果参数
                        })
            else:
                # 物理伤害或其他情况
                # 特殊情况：冻结角色受到物理或火元素伤害时，伤害增加2点并移除冻结状态
                if character.element_attached == ElementType.CRYO and (source_element == ElementType.PHYSICAL or source_element == ElementType.PYRO):
                    actual_damage = remaining_damage + 2
                    # 移除冻结状态，这里我们简单处理为移除元素附着
                    self.element_reaction_system.remove_element_attachment(character)
            
            # 应用穿透伤害（忽略护盾和减伤）
            if damage_type == DamageType.PIERCING:
                character.health -= remaining_damage
                actual_damage = remaining_damage  # Update actual damage for piercing
            else:
                # 应用最终伤害
                character.health -= actual_damage
            
            # 检查是否触发免于被击倒机制
            if character.health <= 0:
                if hasattr(character, 'survive_at_hp') and character.survive_at_hp:
                    # 角色免于被击倒，恢复到1生命值
                    character.health = 1
                    character.survive_at_hp = False
                else:
                    # 角色被击倒，但此时我们不切换角色，只是设置状态
                    # 角色被击倒的完整处理应该在其他地方进行
                    character.is_alive = False
                    character.status = CharacterStatus.DEAD
            
            return actual_damage

    def _apply_spread_damage(self, source_character: CharacterCard, spread_damage: int) -> None:
        """
        对其他敌人造成扩散伤害
        """
        # 遍历所有角色，对非同一队伍的角色造成扩散伤害
        for player in self.game_states.values():
            for character in player.characters:
                # 假设source_character和character不在同一队伍
                if character != source_character and character.is_alive:
                    # 对角色造成扩散伤害，不触发元素反应
                    character.health -= spread_damage
                    if character.health <= 0:
                        # 检查免于被击倒机制
                        if hasattr(character, 'survive_at_hp') and character.survive_at_hp:
                            character.health = 1
                            character.survive_at_hp = False
                        else:
                            character.is_alive = False
                            character.status = CharacterStatus.DEAD
    
    def _apply_status_effects(self, game_state: GameState) -> None:
        """
        应用状态效果，如燃烧烈焰、草原核等
        """
        for player in game_state.players:
            for i, character in enumerate(player.characters):
                # 处理角色身上的状态效果
                for status in character.character_statuses[:]:  # 使用副本，因为可能要移除状态
                    if 'effect' in status:
                        effect = status['effect']
                        effect_type = effect.get('additional_effect')
                        
                        # 持续伤害类状态（如燃烧）
                        if effect_type == 'create_status' and effect.get('damage_per_turn', 0) > 0:
                            damage_per_turn = effect.get('damage_per_turn', 0)
                            # 对角色造成持续伤害
                            self._apply_damage(character, damage_per_turn, DamageType.ELEMENTAL)
                            
                            # 检查是否击倒角色
                            if character.health <= 0:
                                self._knock_out_character(game_state, game_state.players.index(player))
                                game_state.game_log.append(f"角色 {character.name} 因状态效果被击倒！")
                        
                        # 更新状态的持续时间
                        status['duration'] -= 1
                        
                        # 如果持续时间为0，移除状态
                        if status['duration'] <= 0:
                            character.character_statuses.remove(status)
                
                # 处理出战角色的特殊状态
                if i == player.active_character_index:
                    # 这里可以处理出战角色的特殊效果
                    pass

    def _knock_out_character(self, game_state: GameState, player_index: int) -> None:
        """
        击倒玩家的角色
        """
        player = game_state.players[player_index]
        active_character = self._get_active_character(player)
        
        if active_character:
            # 检查是否有"免于被击倒"机制（例如某些角色的天赋或效果）
            if hasattr(active_character, 'survive_at_hp') and active_character.survive_at_hp and active_character.health <= 0:
                # 角色免于被击倒，恢复到特定生命值
                active_character.health = 1  # 或者其他指定的生命值
                # 移除免于被击倒标记
                active_character.survive_at_hp = False
                game_state.game_log.append(f"角色 {active_character.name} 免于被击倒！")
                return  # 不执行击倒逻辑
            
            # 标记角色死亡
            active_character.is_alive = False
            active_character.status = CharacterStatus.DEAD
            
            # 移除角色上的装备
            active_character.weapon = None
            active_character.artifact = None
            active_character.talent = None
            active_character.character_statuses = []
            
            # 清空充能
            active_character.energy = 0
            
            # 检查是否还有存活角色
            alive_characters = [char for char in player.characters if char.is_alive]
            if len(alive_characters) > 0:
                # 需要选择新角色作为出战角色
                # 这里简化处理，选择第一个存活的角色
                for i, char in enumerate(player.characters):
                    if char.is_alive:
                        player.active_character_index = i
                        break
            else:
                # 该玩家所有角色都被击倒
                pass  # 胜负判定在_end_phase中处理

    def _check_victory_conditions(self, game_state: GameState) -> Optional[str]:
        """
        检查胜利条件
        """
        # 检查玩家1是否获胜（玩家2所有角色被击倒）
        player2_alive_count = sum(1 for char in game_state.players[1].characters if char.is_alive)
        if player2_alive_count == 0:
            return game_state.players[0].player_id
        
        # 检查玩家2是否获胜（玩家1所有角色被击倒）
        player1_alive_count = sum(1 for char in game_state.players[0].characters if char.is_alive)
        if player1_alive_count == 0:
            return game_state.players[1].player_id
        
        return None

    def _switch_current_player(self, game_state: GameState) -> None:
        """
        切换当前行动玩家
        """
        game_state.current_player_index = 1 - game_state.current_player_index

    def _find_card_by_id(self, cards: List[Card], card_id: str) -> Optional[Card]:
        """
        根据ID查找卡牌
        """
        for card in cards:
            if card.id == card_id:
                return card
        return None

    def _character_match(self, character: CharacterCard, card: Card) -> bool:
        """
        检查卡牌是否适用于角色（如天赋牌）
        """
        if card.character_subtype:
            return card.character_subtype == character.name
        return True

    def get_game_state(self, game_id: str) -> Optional[GameState]:
        """
        获取游戏状态
        """
        return self.game_states.get(game_id)

    def end_game(self, game_id: str, winner_id: str) -> None:
        """
        结束游戏
        """
        if game_id in self.game_states:
            game_state = self.game_states[game_id]
            game_state.is_game_over = True
            game_state.winner = winner_id
            game_state.game_log.append(f"游戏结束，获胜者: {winner_id}")
            
            self.logger.info(f"Game {game_id} ended. Winner: {winner_id}")
        else:
            self.logger.error(f"Cannot end game {game_id}: game does not exist")