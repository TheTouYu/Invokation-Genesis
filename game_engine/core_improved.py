"""
七圣召唤游戏引擎核心实现 - 改进版
"""
from typing import Dict, List, Optional, Any
from models.game_models import GameState, PlayerState, Card, CharacterCard
from models.enums import GamePhase, PlayerAction, ElementType, CharacterStatus, DamageType
import logging


class GameEngine:
    """
    游戏引擎核心类，处理游戏逻辑和状态变更
    """
    
    def __init__(self):
        self.game_states: Dict[str, GameState] = {}  # 存储游戏会话状态
        logging.basicConfig(level=logging.INFO)
        self.logger = logging.getLogger(__name__)

    def create_game_state(self, player1_id: str, player2_id: str, deck1: List[Card], deck2: List[Card]) -> str:
        """
        创建新的游戏状态，包含初始手牌和初始手牌替换机制
        """
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
        # 每位牌手从自己的牌堆中抓2张牌
        for player in game_state.players:
            # 抓2张牌
            for _ in range(2):
                if player.deck:
                    card = player.deck.pop(0)  # 从牌堆顶部抽牌
                    if len(player.hand_cards) < player.max_hand_size:  # 检查手牌上限
                        player.hand_cards.append(card)
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
        game_state.current_player_index = game_state.first_player_index
        game_state.first_player_index = 1 - game_state.first_player_index  # 切换先手玩家
        
        # 重置玩家的回合状态
        for player in game_state.players:
            player.round_passed = False
            player.has_used_elemental_tuning = False  # 重置元素调和使用状态
        
        # 进入下一回合的投骰阶段
        game_state.phase = GamePhase.ROLL_PHASE
        game_state.game_log.append(f"回合 {game_state.round_number} 开始")
        
        return game_state

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

        # 记录到游戏日志
        game_state.game_log.append(f"玩家 {player.player_id} 使用了技能 {skill.get('name', skill_id)}")
        
        # 增加行动次数
        game_state.round_actions += 1

        # 增加角色充能（使用普通攻击或元素战技后获得1点充能）
        skill_type = skill.get('skill_type', '')
        if skill_type in ['NORMAL_ATTACK', 'ELEMENTAL_SKILL']:
            active_character.energy = min(active_character.energy + 1, active_character.max_energy)

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
                    target_character.element_attached = element_application
                
                # 应用伤害
                self._apply_damage(target_character, damage, damage_type)
                
                # 检查是否击倒角色
                if target_character.health <= 0:
                    self._knock_out_character(game_state, target_player_index)
                    game_state.game_log.append(f"角色 {target_character.name} 被击倒！")
                
                game_state.game_log.append(f"对角色 {target_character.name} 造成了 {damage} 点{damage_type.value}伤害")
        
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
                # 将卡牌返回手牌
                player.hand_cards.append(card_to_play)
                return game_state
        elif card_to_play.card_type == 'EVENT':
            # 处理事件卡效果
            game_state.game_log.append(f"玩家 {player.player_id} 打出了事件卡 {card_to_play.name}")
            # 实现事件卡效果...
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
            
            # 如果是下落攻击（切换角色后第一次普通攻击）
            # 这里我们标记当前玩家可以执行下落攻击，实际实现需要更复杂的逻辑
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

    def _apply_damage(self, character: CharacterCard, damage: int, damage_type: DamageType) -> None:
        """
        应用伤害到角色
        """
        if damage_type == DamageType.HEAL:
            # 治疗效果
            character.health = min(character.health + abs(damage), character.max_health)
        else:
            # 伤害效果
            character.health -= damage

    def _knock_out_character(self, game_state: GameState, player_index: int) -> None:
        """
        击倒玩家的角色
        """
        player = game_state.players[player_index]
        active_character = self._get_active_character(player)
        
        if active_character:
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