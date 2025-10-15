"""
本地游戏API路由
"""
from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from game_engine.core import GameEngine
from models.db_models import User, Deck, CardData, db
from models.game_models import Card, CharacterCard
from models.enums import PlayerAction, ElementType, CardType
import json
import logging
from typing import Dict, Any

local_game_bp = Blueprint('local_game', __name__)

# 创建游戏引擎实例
game_engine = GameEngine()

# 用于存储本地游戏会话的字典
local_game_sessions: Dict[str, Any] = {}

@local_game_bp.route('/local-game/start', methods=['POST'])
@jwt_required()
def start_local_game():
    """
    开始本地游戏
    """
    try:
        current_user_id = get_jwt_identity()
        data = request.get_json()
        
        opponent_type = data.get('opponent_type', 'ai')  # 'ai' 或 'human'
        deck_id = data.get('deck_id')
        
        if not deck_id:
            return jsonify({'error': '必须选择一个卡组'}), 400
        
        # 获取用户和对手的卡组
        user_deck = Deck.query.filter_by(id=deck_id, user_id=current_user_id).first()
        if not user_deck:
            return jsonify({'error': '卡组不存在或无权限访问'}), 404
        
        # 获取对手卡组（如果是AI对手，使用系统提供的卡组）
        if opponent_type == 'ai':
            # 这里可以实现AI对手的逻辑，现在我们使用一个默认的卡组
            # 为了测试，我们创建一个简单的AI卡组
            ai_deck_data = [
                {
                    'id': 'ai_char_1',
                    'name': 'AI角色1',
                    'card_type': '角色牌',
                    'cost': [ElementType.OMNI.value, ElementType.OMNI.value],
                    'health': 10,
                    'max_health': 10,
                    'element_type': ElementType.PYRO.value,
                    'skills': [
                        {
                            'id': 'ai_skill_1',
                            'name': 'AI技能1',
                            'cost': [ElementType.SAME.value, ElementType.SAME.value],
                            'damage': 1
                        }
                    ]
                }
            ]
            # 这只是一个简单示例，实际应从数据库获取AI卡组
            ai_deck_cards = []
        else:
            # 如果是人对人，需要获取对手的卡组
            return jsonify({'error': '多人游戏尚未实现，请选择AI对手'}), 400
        
        # 解析用户卡组
        user_card_list = json.loads(user_deck.cards) if user_deck.cards else []
        user_cards_data = CardData.query.filter(CardData.id.in_(user_card_list)).all()
        
        # 将数据库数据转换为游戏引擎需要的格式
        user_cards = convert_db_cards_to_game_cards(user_cards_data)
        
        # 启动本地游戏
        game_session_id = game_engine.create_game_state(
            current_user_id,  # 玩家1 ID
            "ai_opponent",    # 玩家2 ID (AI)
            user_cards,       # 玩家卡组
            []               # AI卡组 (暂时为空，需要实现AI卡组)
        )
        
        # 保存游戏会话信息
        local_game_sessions[game_session_id] = {
            'player_id': current_user_id,
            'opponent_type': opponent_type,
            'game_started_at': db.func.now()
        }
        
        # 获取初始游戏状态
        game_state = game_engine.get_game_state(game_session_id)
        
        response_data = {
            'game_session_id': game_session_id,
            'message': '本地游戏已开始',
            'game_state': serialize_game_state(game_state)
        }
        
        return jsonify(response_data), 200
    except Exception as e:
        logging.error(f"Start local game error: {str(e)}")
        return jsonify({'error': str(e)}), 500


@local_game_bp.route('/local-game/<session_id>/action', methods=['POST'])
@jwt_required()
def process_game_action(session_id):
    """
    处理游戏中的行动
    """
    try:
        current_user_id = get_jwt_identity()
        data = request.get_json()
        
        # 验证会话是否存在
        if session_id not in local_game_sessions:
            return jsonify({'error': '游戏会话不存在'}), 404
        
        session_info = local_game_sessions[session_id]
        if session_info['player_id'] != current_user_id:
            return jsonify({'error': '无权访问此游戏会话'}), 403
        
        # 验证行动数据
        action_type = data.get('action_type')
        if not action_type:
            return jsonify({'error': '必须指定行动类型'}), 400
        
        # 处理行动
        payload = data.get('payload', {})
        action_enum = PlayerAction[action_type.upper()]
        
        game_state = game_engine.process_action(
            session_id,
            current_user_id,
            action_enum,
            payload
        )
        
        if game_state is None:
            return jsonify({'error': '处理行动失败'}), 400
        
        response_data = {
            'game_session_id': session_id,
            'message': '行动处理成功',
            'game_state': serialize_game_state(game_state)
        }
        
        return jsonify(response_data), 200
    except KeyError as e:
        logging.error(f"Invalid action type: {str(e)}")
        return jsonify({'error': f'无效的行动类型: {str(e)}'}), 400
    except Exception as e:
        logging.error(f"Process game action error: {str(e)}")
        return jsonify({'error': str(e)}), 500


@local_game_bp.route('/local-game/<session_id>/state', methods=['GET'])
@jwt_required()
def get_game_state(session_id):
    """
    获取游戏状态
    """
    try:
        current_user_id = get_jwt_identity()
        
        # 验证会话是否存在
        if session_id not in local_game_sessions:
            return jsonify({'error': '游戏会话不存在'}), 404
        
        session_info = local_game_sessions[session_id]
        if session_info['player_id'] != current_user_id:
            return jsonify({'error': '无权访问此游戏会话'}), 403
        
        game_state = game_engine.get_game_state(session_id)
        if game_state is None:
            return jsonify({'error': '游戏状态不存在'}), 404
        
        response_data = {
            'game_session_id': session_id,
            'game_state': serialize_game_state(game_state)
        }
        
        return jsonify(response_data), 200
    except Exception as e:
        logging.error(f"Get game state error: {str(e)}")
        return jsonify({'error': str(e)}), 500


@local_game_bp.route('/local-game/<session_id>/end', methods=['POST'])
@jwt_required()
def end_local_game(session_id):
    """
    结束本地游戏
    """
    try:
        current_user_id = get_jwt_identity()
        
        # 验证会话是否存在
        if session_id not in local_game_sessions:
            return jsonify({'error': '游戏会话不存在'}), 404
        
        session_info = local_game_sessions[session_id]
        if session_info['player_id'] != current_user_id:
            return jsonify({'error': '无权访问此游戏会话'}), 403
        
        # 结束游戏
        game_state = game_engine.get_game_state(session_id)
        if game_state:
            winner_id = determine_winner(game_state)  # 简单的胜负判断逻辑
            game_engine.end_game(session_id, winner_id)
        
        # 清理会话
        del local_game_sessions[session_id]
        
        return jsonify({'message': '本地游戏已结束'}), 200
    except Exception as e:
        logging.error(f"End local game error: {str(e)}")
        return jsonify({'error': str(e)}), 500


def convert_db_cards_to_game_cards(db_cards):
    """
    将数据库卡牌数据转换为游戏引擎需要的卡牌对象
    """
    from models.enums import ElementType as EType, CardType as CType
    game_cards = []
    
    for db_card in db_cards:
        card_data = json.loads(db_card.cost) if db_card.cost else []
        cost = []
        
        # 将字符串转换为ElementType枚举
        for cost_item in card_data:
            if cost_item == "万能":
                cost.append(EType.OMNI)
            elif cost_item == "火":
                cost.append(EType.PYRO)
            elif cost_item == "水":
                cost.append(EType.HYDRO)
            elif cost_item == "雷":
                cost.append(EType.ELECTRO)
            elif cost_item == "风":
                cost.append(EType.ANEMO)
            elif cost_item == "岩":
                cost.append(EType.GEO)
            elif cost_item == "草":
                cost.append(EType.DENDRO)
            elif cost_item == "冰":
                cost.append(EType.CRYO)
            elif cost_item == "物理":
                cost.append(EType.PHYSICAL)
            elif cost_item == "同色":
                cost.append(EType.SAME)
            elif cost_item == "晶体":
                cost.append(EType.CRYSTAL)
            else:
                cost.append(EType.NONE)
        
        # 根据卡牌类型创建相应对象
        if db_card.card_type == "角色牌":
            skills = json.loads(db_card.skills) if db_card.skills else []
            game_card = CharacterCard(
                id=db_card.id,
                name=db_card.name,
                card_type=CType.CHARACTER,
                cost=cost,
                health=db_card.health or 10,
                max_health=db_card.max_health or 10,
                energy=db_card.energy or 0,
                max_energy=db_card.max_energy or 3,
                skills=skills,
                element_type=getattr(EType, db_card.element_type, EType.NONE) if db_card.element_type else EType.NONE,
                weapon_type=db_card.weapon_type or "",
                description=db_card.description
            )
        else:
            game_card = Card(
                id=db_card.id,
                name=db_card.name,
                card_type=getattr(CType, db_card.card_type.replace('牌', '').upper(), CType.EVENT),
                cost=cost,
                description=db_card.description,
                character_subtype=db_card.character_subtype
            )
        
        game_cards.append(game_card)
    
    return game_cards


def serialize_game_state(game_state):
    """
    序列化游戏状态为JSON可序列化格式
    """
    if game_state is None:
        return None
    
    # 将游戏状态转换为字典格式
    serialized = {
        'players': [
            {
                'player_id': player.player_id,
                'characters': [
                    {
                        'id': char.id,
                        'name': char.name,
                        'health': char.health,
                        'max_health': char.max_health,
                        'energy': char.energy,
                        'max_energy': char.max_energy,
                        'element_type': char.element_type.value if hasattr(char.element_type, 'value') else str(char.element_type),
                        'weapon_type': char.weapon_type,
                        'status': char.status.value if hasattr(char.status, 'value') else str(char.status),
                        'skills': char.skills if hasattr(char, 'skills') else []
                    } for char in player.characters
                ],
                'active_character_index': player.active_character_index,
                'hand_cards': [
                    {
                        'id': card.id,
                        'name': card.name,
                        'card_type': card.card_type.value if hasattr(card.card_type, 'value') else str(card.card_type),
                        'cost': [cost.value if hasattr(cost, 'value') else str(cost) for cost in card.cost],
                        'description': card.description
                    } for card in player.hand_cards
                ],
                'dice': [
                    die.value if hasattr(die, 'value') else str(die) for die in player.dice
                ],
                'supports': player.supports,
                'summons': player.summons
            } for player in game_state.players
        ],
        'current_player_index': game_state.current_player_index,
        'round_number': game_state.round_number,
        'phase': game_state.phase.value if hasattr(game_state.phase, 'value') else str(game_state.phase),
        'round_actions': game_state.round_actions,
        'game_log': game_state.game_log,
        'is_game_over': game_state.is_game_over,
        'winner': game_state.winner
    }
    
    return serialized


def determine_winner(game_state):
    """
    简单的胜负判断逻辑
    """
    if not game_state.players:
        return None
    
    # 检查是否有玩家的所有角色都被击败
    for i, player in enumerate(game_state.players):
        alive_characters = [char for char in player.characters if char.health > 0]
        if len(alive_characters) == 0:
            # 如果当前玩家没有存活角色，则对方获胜
            opponent_index = 1 - i
            if opponent_index < len(game_state.players):
                return game_state.players[opponent_index].player_id
    
    # 如果没有玩家的所有角色都被击败，返回当前玩家ID（作为默认值）
    # 在实际游戏中，可能还有其他决定胜负的条件
    if game_state.players:
        return game_state.players[game_state.current_player_index].player_id
    
    return None