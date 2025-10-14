"""
本地游戏API端点
"""
from flask import Blueprint, jsonify, request
from game_engine.core import GameEngine
from models.db_models import CardData
from models.game_models import Card
from typing import List
import logging

local_game_bp = Blueprint('local_game', __name__)
game_engine = GameEngine()

@local_game_bp.route('/start', methods=['POST'])
def start_local_game():
    """开始本地游戏"""
    try:
        data = request.get_json()
        player1_id = data.get('player1_id', 'player1')
        player2_id = data.get('player2_id', 'player2')
        deck1_ids = data.get('deck1', [])
        deck2_ids = data.get('deck2', [])
        
        # 从数据库获取卡牌数据
        deck1 = get_cards_by_ids(deck1_ids)
        deck2 = get_cards_by_ids(deck2_ids)
        
        # 创建游戏
        game_id = game_engine.create_game_state(player1_id, player2_id, deck1, deck2)
        
        return jsonify({
            "game_id": game_id,
            "message": "游戏开始成功"
        }), 200
    except Exception as e:
        logging.exception("Error starting local game")
        return jsonify({"error": str(e)}), 500

@local_game_bp.route('/<session_id>/action', methods=['POST'])
def process_game_action(session_id):
    """处理游戏操作"""
    try:
        data = request.get_json()
        player_id = data.get('player_id')
        action_type = data.get('action_type')
        payload = data.get('payload', {})
        
        # 使用游戏引擎处理操作
        result = game_engine.process_action(session_id, player_id, action_type, payload)
        
        if result is None:
            return jsonify({"error": "Invalid game or player"}), 400
            
        return jsonify({
            "game_state": serialize_game_state(result),
            "message": "操作处理成功"
        }), 200
    except Exception as e:
        logging.exception("Error processing game action")
        return jsonify({"error": str(e)}), 500

@local_game_bp.route('/<session_id>/state', methods=['GET'])
def get_game_state(session_id):
    """获取游戏状态"""
    try:
        game_state = game_engine.get_game_state(session_id)
        
        if game_state is None:
            return jsonify({"error": "Game not found"}), 404
            
        return jsonify({
            "game_state": serialize_game_state(game_state)
        }), 200
    except Exception as e:
        logging.exception("Error getting game state")
        return jsonify({"error": str(e)}), 500

def get_cards_by_ids(card_ids: List[str]) -> List[Card]:
    """根据ID列表获取卡牌对象"""
    cards = []
    for card_id in card_ids:
        db_card = CardData.query.get(card_id)
        if db_card:
            # 这里需要根据实际的数据库模型转换为游戏模型
            # 简单实现，实际需要更复杂的转换逻辑
            card = Card(
                id=db_card.id,
                name=db_card.name,
                card_type=db_card.card_type,
                cost=[],  # 实际应用中需要从数据库获取费用信息
                description=db_card.description
            )
            cards.append(card)
    return cards

def serialize_game_state(game_state):
    """序列化游戏状态以便返回给前端"""
    # 这里需要实现游戏状态的序列化逻辑
    # 简单实现，实际应用中需要完整序列化
    return {
        "current_player_index": game_state.current_player_index,
        "round_number": game_state.round_number,
        "phase": game_state.phase.value,
        "players": [
            {
                "player_id": p.player_id,
                "hand_cards": [c.name for c in p.hand_cards],
                "dice": [d.value for d in p.dice],
            } for p in game_state.players
        ],
        "game_log": game_state.game_log,
        "is_game_over": game_state.is_game_over,
        "winner": game_state.winner
    }