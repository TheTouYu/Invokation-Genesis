"""
游戏会话API
"""
from flask import Blueprint, request, jsonify
from game_engine.core import GameEngine
from game_engine.deck_validation import DeckValidationSystem
from dal import db_dal
from utils.decorators import token_required
from models.game_models import Card
import uuid
from utils.logger import get_logger

local_game_bp = Blueprint('local_game', __name__)

# 创建全局游戏引擎实例
game_engine = GameEngine()

# 创建卡组验证系统实例
deck_validation = DeckValidationSystem()

logger = get_logger(__name__)


@local_game_bp.route('/api/game_sessions', methods=['POST'])
@token_required
def create_game_session(current_user):
    """
    创建游戏会话
    """
    try:
        data = request.get_json()
        
        # 获取玩家和卡组信息
        player1_id = current_user.id  # 当前用户作为玩家1
        player2_id = data.get('player2_id')  # 对手ID，如果是AI对战则为AI标识
        deck1_id = data.get('deck1_id')
        deck2_id = data.get('deck2_id')  # 在AI对战中这可能为空
        
        if not deck1_id:
            return jsonify({'error': '必须提供玩家1的卡组ID'}), 400
        
        # 获取玩家1的卡组
        deck1 = db_dal.decks.get_deck_by_id(deck1_id)
        if not deck1 or deck1.user_id != player1_id:
            return jsonify({'error': '无效的卡组ID或无权访问该卡组'}), 400
        
        # 验证玩家1的卡组
        # 从数据库中获取卡牌详细信息
        card_ids1 = deck1.cards  # 这里需要根据实际数据结构调整
        deck1_cards = []
        for card_id in card_ids1:
            card_data = db_dal.cards.get_card_by_id(card_id)
            if card_data:
                # 转换为Card对象
                card = Card(
                    id=card_data.id,
                    name=card_data.name,
                    card_type=card_data.card_type,
                    cost=card_data.cost,  # 需要转换为ElementType
                    description=card_data.description
                )
                deck1_cards.append(card)
        
        # 模拟获取玩家2的卡组（如果是AI对战则随机生成或使用预设卡组）
        deck2_cards = []
        if deck2_id:
            deck2 = db_dal.decks.get_deck_by_id(deck2_id)
            if not deck2:
                return jsonify({'error': '无效的玩家2卡组ID'}), 400
            
            card_ids2 = deck2.cards  # 这里需要根据实际数据结构调整
            for card_id in card_ids2:
                card_data = db_dal.cards.get_card_by_id(card_id)
                if card_data:
                    card = Card(
                        id=card_data.id,
                        name=card_data.name,
                        card_type=card_data.card_type,
                        cost=card_data.cost,  # 需要转换为ElementType
                        description=card_data.description
                    )
                    deck2_cards.append(card)
        else:
            # 如果没有提供deck2_id，可能是AI对战，使用预设卡组
            # 这里应该有AI卡组的逻辑，暂时用模拟数据
            pass
        
        # 创建游戏状态
        game_id = game_engine.create_game_state(
            player1_id=player1_id,
            player2_id=player2_id or f"AI_{uuid.uuid4()}",  # 如果没有对手ID，则创建AI标识
            deck1=deck1_cards,
            deck2=deck2_cards
        )
        
        if not game_id:
            return jsonify({'error': '创建游戏会话失败，卡组验证未通过'}), 400
        
        # 记录游戏历史
        game_history = db_dal.game_history.create_game_history(
            player1_id=player1_id,
            player2_id=player2_id or "AI",
            game_data={'game_id': game_id},
            game_result='ongoing'
        )
        
        return jsonify({
            'message': '游戏会话创建成功',
            'game_id': game_id,
            'game_history_id': game_history.id
        }), 201
    except Exception as e:
        logger.error(f"创建游戏会话时发生错误: {e}")
        return jsonify({'error': '服务器内部错误'}), 500


@local_game_bp.route('/api/game_sessions/<game_session_id>', methods=['GET'])
@token_required
def get_game_state(current_user, game_session_id):
    """
    获取游戏状态
    """
    try:
        game_state = game_engine.get_game_state(game_session_id)
        if not game_state:
            return jsonify({'error': '游戏会话不存在'}), 404
        
        # 检查当前用户是否有权查看此游戏状态
        if not any(player.player_id == current_user.id for player in game_state.players):
            return jsonify({'error': '无权查看此游戏状态'}), 403
        
        # 返回游戏状态（根据用户角色过滤信息）
        # 在观战模式中可能需要过滤某些信息
        return jsonify({
            'game_id': game_session_id,
            'game_state': game_state.__dict__  # 序列化游戏状态
        })
    except Exception as e:
        logger.error(f"获取游戏状态时发生错误: {e}")
        return jsonify({'error': '服务器内部错误'}), 500


@local_game_bp.route('/api/game_sessions/<game_session_id>/actions', methods=['POST'])
@token_required
def submit_action(current_user, game_session_id):
    """
    提交玩家操作
    """
    try:
        data = request.get_json()
        action = data.get('action')
        payload = data.get('payload', {})
        
        if not action:
            return jsonify({'error': '必须提供操作类型'}), 400
        
        # 处理玩家操作
        updated_game_state = game_engine.process_action(
            game_id=game_session_id,
            player_id=current_user.id,
            action=action,
            payload=payload
        )
        
        if not updated_game_state:
            return jsonify({'error': '处理操作失败'}), 400
        
        # 记录操作日志
        try:
            db_dal.game_action_log.create_action_log(
                game_id=game_session_id,
                player_id=current_user.id,
                action_type=action,
                action_payload=payload,
                turn_number=updated_game_state.round_number,
                action_number=updated_game_state.round_actions,
                game_phase=updated_game_state.phase.value if hasattr(updated_game_state.phase, 'value') else updated_game_state.phase
            )
        except Exception as e:
            logger.error(f"记录操作日志时发生错误: {e}")
        
        return jsonify({
            'message': '操作提交成功',
            'game_state': updated_game_state.__dict__
        })
    except Exception as e:
        logger.error(f"提交操作时发生错误: {e}")
        return jsonify({'error': '服务器内部错误'}), 500


@local_game_bp.route('/api/game_sessions/<game_session_id>/end', methods=['POST'])
@token_required
def end_game(current_user, game_session_id):
    """
    结束游戏
    """
    try:
        # 获取游戏状态以确定获胜者
        game_state = game_engine.get_game_state(game_session_id)
        if not game_state:
            return jsonify({'error': '游戏会话不存在'}), 404
        
        # 确定获胜者，通常由游戏引擎内部逻辑确定
        winner_id = game_state.winner
        
        # 结束游戏
        game_engine.end_game(game_session_id, winner_id)
        
        # 更新游戏历史记录
        game_histories = db_dal.game_history.get_games_by_user(current_user.id)
        for history in game_histories:
            if history.game_data.get('game_id') == game_session_id:
                db_dal.game_history.update_game_history(
                    history.id,
                    winner_id=winner_id,
                    game_result='completed',
                    duration=game_state.round_number * 60  # 简化的时长计算
                )
                break
        
        # 创建回放数据
        try:
            replay_data = {
                'game_id': game_session_id,
                'final_state': game_state.__dict__,
                'actions': db_dal.game_action_log.get_action_logs_by_game(game_session_id)
            }
            
            db_dal.replay_data.create_replay_data(
                game_id=game_session_id,
                replay_data=replay_data,
                duration=game_state.round_number * 60  # 简化的时长计算
            )
        except Exception as e:
            logger.error(f"创建回放数据时发生错误: {e}")
        
        return jsonify({
            'message': '游戏结束',
            'winner_id': winner_id
        })
    except Exception as e:
        logger.error(f"结束游戏时发生错误: {e}")
        return jsonify({'error': '服务器内部错误'}), 500


@local_game_bp.route('/api/replays', methods=['GET'])
@token_required
def get_replay_list(current_user):
    """
    获取回放列表
    """
    try:
        # 获取用户参与的游戏历史
        game_histories = db_dal.game_history.get_games_by_user(current_user.id)
        
        replays = []
        for history in game_histories:
            replay = db_dal.replay_data.get_replay_by_game_id(history.id)
            if replay:
                replays.append({
                    'replay_id': replay.id,
                    'game_id': replay.game_id,
                    'created_at': replay.creation_time,
                    'duration': replay.duration
                })
        
        return jsonify({
            'replays': replays,
            'count': len(replays)
        })
    except Exception as e:
        logger.error(f"获取回放列表时发生错误: {e}")
        return jsonify({'error': '服务器内部错误'}), 500


@local_game_bp.route('/api/replays/<replay_id>', methods=['GET'])
@token_required
def get_replay(current_user, replay_id):
    """
    获取特定回放
    """
    try:
        replay = db_dal.replay_data.get_replay_by_id(replay_id)
        if not replay:
            return jsonify({'error': '回放不存在'}), 404
        
        # 检查用户是否有权查看此回放
        game_history = db_dal.game_history.get_game_history_by_id(replay.game_id)
        if not game_history or (game_history.player1_id != current_user.id and game_history.player2_id != current_user.id):
            return jsonify({'error': '无权查看此回放'}), 403
        
        return jsonify({
            'replay_id': replay.id,
            'game_id': replay.game_id,
            'replay_data': replay.replay_data,
            'created_at': replay.creation_time,
            'duration': replay.duration
        })
    except Exception as e:
        logger.error(f"获取回放时发生错误: {e}")
        return jsonify({'error': '服务器内部错误'}), 500


@local_game_bp.route('/api/spectator/<game_session_id>/join', methods=['POST'])
@token_required
def join_spectate(current_user, game_session_id):
    """
    加入观战
    """
    try:
        # 获取游戏状态
        game_state = game_engine.get_game_state(game_session_id)
        if not game_state:
            return jsonify({'error': '游戏会话不存在'}), 404
        
        # 观战者可以加入任何正在进行的游戏
        # 这里可以添加额外的权限检查，如仅观战公开游戏等
        
        return jsonify({
            'message': '成功加入观战',
            'game_id': game_session_id,
            'spectator_id': current_user.id
        })
    except Exception as e:
        logger.error(f"加入观战时发生错误: {e}")
        return jsonify({'error': '服务器内部错误'}), 500


@local_game_bp.route('/api/spectator/active_games', methods=['GET'])
@token_required
def get_active_games_for_spectator(current_user):
    """
    获取可观看的游戏
    """
    try:
        # 获取所有正在进行的游戏（未结束的游戏）
        recent_games = db_dal.game_history.get_recent_games(limit=20)
        active_games = []
        
        for game in recent_games:
            if game.game_result != 'completed' and game.game_result != 'ongoing':
                game_state = game_engine.get_game_state(game.id)
                if game_state and not game_state.is_game_over:
                    active_games.append({
                        'game_id': game.id,
                        'player1_id': game.player1_id,
                        'player2_id': game.player2_id,
                        'start_time': game.created_at,
                        'current_round': game_state.round_number if game_state else 1
                    })
        
        return jsonify({
            'active_games': active_games,
            'count': len(active_games)
        })
    except Exception as e:
        logger.error(f"获取可观看游戏时发生错误: {e}")
        return jsonify({'error': '服务器内部错误'}), 500