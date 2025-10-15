"""
七圣召唤游戏引擎核心实现
"""
from typing import Dict, List, Optional, Any
from models.game_models import GameState, PlayerState, Card, CharacterCard
from models.enums import GamePhase, PlayerAction, ElementType
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
        创建新的游戏状态
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
            summons=[]
        )
        
        player2_state = PlayerState(
            player_id=player2_id,
            deck=player2_remaining_deck,
            hand_cards=player2_hand,
            characters=player2_character_cards,  # 添加角色
            dice=[],
            supports=[],
            summons=[]
        )
        
        # 创建游戏状态
        game_state = GameState(
            players=[player1_state, player2_state],
            current_player_index=0,  # 默认玩家1先手
            phase=GamePhase.ROLL_PHASE
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
        
        # 根据当前阶段处理操作
        if game_state.phase == GamePhase.ROLL_PHASE:
            return self._roll_phase(game_state, action, payload)
        elif game_state.phase == GamePhase.ACTION_PHASE:
            return self._action_phase(game_state, action, payload)
        elif game_state.phase == GamePhase.END_PHASE:
            return self._end_phase(game_state, action, payload)
        
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
            return self._process_use_skill_action(game_state, payload)
        elif action == PlayerAction.PLAY_CARD:
            return self._process_play_card_action(game_state, payload)
        elif action == PlayerAction.SWITCH_CHARACTER:
            return self._process_switch_action(game_state, payload)
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
        
        # 切换到下一回合
        game_state.round_number += 1
        
        # 检查回合数上限（七圣召唤中，第15回合开始时如果仍未分出胜负，则双方都输）
        if game_state.round_number >= 15:
            game_state.is_game_over = True
            game_state.winner = None  # 平局
            game_state.game_log.append(f"达到回合数上限，游戏平局")
            return game_state
        
        # 切换先手玩家（在实际规则中，上回合最后行动的玩家成为下回合的先手）
        game_state.current_player_index = 1 - game_state.current_player_index
        
        # 重置玩家的回合状态
        for player in game_state.players:
            player.round_passed = False
        
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
        
        # 处理技能效果（简化处理）
        # ... 实际游戏中需要实现技能效果应用逻辑
        
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
        
        # 记录到游戏日志
        game_state.game_log.append(f"玩家 {player.player_id} 打出了卡牌 {card_to_play.name}")
        
        # 增加行动次数
        game_state.round_actions += 1
        
        # 处理卡牌效果（简化处理）
        # ... 实际游戏中需要实现卡牌效果应用逻辑
        
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
            old_char = player.characters[old_index].name if old_index < len(player.characters) else "unknown"
            new_char = player.characters[new_character_index].name
            game_state.game_log.append(f"玩家 {player.player_id} 从角色 {old_char} 切换到角色 {new_char}")
            
            # 增加行动次数
            game_state.round_actions += 1
        else:
            self.logger.warning(f"Invalid character index {new_character_index}")
        
        return game_state

    def _process_pass_action(self, game_state: GameState) -> GameState:
        """
        处理结束回合操作
        """
        current_player = game_state.players[game_state.current_player_index]
        game_state.game_log.append(f"玩家 {current_player.player_id} 结束了回合")
        
        # 切换到下一阶段
        game_state.phase = GamePhase.END_PHASE
        
        return game_state

    def _get_active_character(self, player: PlayerState) -> Optional[CharacterCard]:
        """
        获取玩家当前出战的角色
        """
        if 0 <= player.active_character_index < len(player.characters):
            return player.characters[player.active_character_index]
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