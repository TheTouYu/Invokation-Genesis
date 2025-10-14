"""
七圣召唤游戏引擎核心实现
"""
from typing import Dict, List, Optional, Any
from models.game_models import GameState, PlayerState, Card, CharacterCard
from models.enums import GamePhase, PlayerAction
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
        # 创建玩家状态
        player1_state = PlayerState(
            player_id=player1_id,
            deck=deck1.copy(),
            hand_cards=[],
            characters=[],
            dice=[],
            supports=[],
            summons=[]
        )
        
        player2_state = PlayerState(
            player_id=player2_id,
            deck=deck2.copy(),
            hand_cards=[],
            characters=[],
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
        # 在实际实现中，这里会处理重投骰子等逻辑
        # 简单示例：直接进入行动阶段
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
        # 简单示例：切换到下一回合
        game_state.round_number += 1
        game_state.current_player_index = 1 - game_state.current_player_index  # 切换玩家
        game_state.phase = GamePhase.ROLL_PHASE
        game_state.game_log.append(f"回合 {game_state.round_number} 开始")
        
        return game_state

    def _process_use_skill_action(self, game_state: GameState, payload: Dict[str, Any]) -> GameState:
        """
        处理使用技能操作
        """
        # 这里是简化实现，实际需要处理技能费用、效果等
        skill_id = payload.get('skill_id')
        player_index = game_state.current_player_index
        player = game_state.players[player_index]
        
        # 记录到游戏日志
        game_state.game_log.append(f"玩家 {player.player_id} 使用了技能 {skill_id}")
        
        # 增加行动次数
        game_state.round_actions += 1
        
        return game_state

    def _process_play_card_action(self, game_state: GameState, payload: Dict[str, Any]) -> GameState:
        """
        处理打出手牌操作
        """
        card_id = payload.get('card_id')
        player_index = game_state.current_player_index
        player = game_state.players[player_index]
        
        # 查找并移除手牌中的卡牌
        card_to_play = None
        for i, card in enumerate(player.hand_cards):
            if card.id == card_id:
                card_to_play = card
                break
        
        if card_to_play:
            player.hand_cards.pop(i)
            # 记录到游戏日志
            game_state.game_log.append(f"玩家 {player.player_id} 打出了卡牌 {card_to_play.name}")
            
            # 增加行动次数
            game_state.round_actions += 1
        else:
            self.logger.warning(f"Card {card_id} not found in player's hand")
        
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

    def _can_pay_cost(self, player: PlayerState, cost: List[Any]) -> bool:
        """
        检查玩家是否能支付费用
        """
        # 这里需要实现费用检查逻辑
        # 简单示例：假设总是能支付
        return True

    def _pay_cost(self, player: PlayerState, cost: List[Any]) -> bool:
        """
        支付费用
        """
        # 这里需要实现费用支付逻辑
        # 简单示例：假设总是能支付
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