"""
卡牌API路由
"""
from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from models.db_models import CardData, Deck, db
from models.game_models import Card, CharacterCard
from typing import List, Dict, Any
import json

cards_bp = Blueprint('cards', __name__)

@cards_bp.route('/cards', methods=['GET'])
@jwt_required()
def get_all_cards():
    """
    获取所有卡牌数据
    """
    try:
        # 获取查询参数
        card_type = request.args.get('type')
        element = request.args.get('element')
        page = request.args.get('page', 1, type=int)
        per_page = request.args.get('per_page', 20, type=int)
        
        # 构建查询
        query = CardData.query
        
        if card_type:
            query = query.filter(CardData.card_type == card_type)
        if element:
            query = query.filter(CardData.element_type == element)
        
        # 分页
        cards = query.paginate(page=page, per_page=per_page, error_out=False)
        
        result = []
        for card in cards.items:
            result.append({
                'id': card.id,
                'name': card.name,
                'card_type': card.card_type,
                'element_type': card.element_type,
                'rarity': card.rarity,
                'cost': json.loads(card.cost) if card.cost else [],
                'description': card.description,
                'character_subtype': card.character_subtype,
                'image_url': card.image_url
            })
        
        return jsonify({
            'cards': result,
            'total': cards.total,
            'pages': cards.pages,
            'current_page': page
        }), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@cards_bp.route('/cards/characters', methods=['GET'])
@jwt_required()
def get_character_cards():
    """
    获取所有角色卡牌数据
    """
    try:
        # 获取查询参数
        element = request.args.get('element')
        page = request.args.get('page', 1, type=int)
        per_page = request.args.get('per_page', 20, type=int)
        
        # 查询角色卡牌
        query = CardData.query.filter(CardData.card_type == '角色牌')
        
        if element:
            query = query.filter(CardData.element_type == element)
        
        cards = query.paginate(page=page, per_page=per_page, error_out=False)
        
        result = []
        for card in cards.items:
            result.append({
                'id': card.id,
                'name': card.name,
                'card_type': card.card_type,
                'element_type': card.element_type,
                'rarity': card.rarity,
                'cost': json.loads(card.cost) if card.cost else [],
                'description': card.description,
                'character_subtype': card.character_subtype,
                'image_url': card.image_url,
                # 角色卡的特殊属性
                'health': card.health,
                'energy': card.energy,
                'weapon_type': card.weapon_type,
                'skills': json.loads(card.skills) if card.skills else []
            })
        
        return jsonify({
            'cards': result,
            'total': cards.total,
            'pages': cards.pages,
            'current_page': page
        }), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@cards_bp.route('/cards/events', methods=['GET'])
@jwt_required()
def get_event_cards():
    """
    获取所有事件卡牌数据
    """
    try:
        # 获取查询参数
        page = request.args.get('page', 1, type=int)
        per_page = request.args.get('per_page', 20, type=int)
        
        # 查询事件卡牌
        query = CardData.query.filter(CardData.card_type == '事件牌')
        cards = query.paginate(page=page, per_page=per_page, error_out=False)
        
        result = []
        for card in cards.items:
            result.append({
                'id': card.id,
                'name': card.name,
                'card_type': card.card_type,
                'rarity': card.rarity,
                'cost': json.loads(card.cost) if card.cost else [],
                'description': card.description,
                'image_url': card.image_url
            })
        
        return jsonify({
            'cards': result,
            'total': cards.total,
            'pages': cards.pages,
            'current_page': page
        }), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@cards_bp.route('/decks', methods=['GET'])
@jwt_required()
def get_user_decks():
    """
    获取当前用户的所有卡组
    """
    try:
        current_user_id = get_jwt_identity()
        
        decks = Deck.query.filter_by(user_id=current_user_id).all()
        
        result = []
        for deck in decks:
            result.append({
                'id': deck.id,
                'name': deck.name,
                'description': deck.description,
                'cards': json.loads(deck.cards) if deck.cards else [],
                'created_at': deck.created_at.isoformat(),
                'updated_at': deck.updated_at.isoformat()
            })
        
        return jsonify({'decks': result}), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@cards_bp.route('/decks', methods=['POST'])
@jwt_required()
def create_deck():
    """
    创建新的卡组
    """
    try:
        current_user_id = get_jwt_identity()
        data = request.get_json()
        
        name = data.get('name')
        description = data.get('description', '')
        card_list = data.get('cards', [])
        
        if not name:
            return jsonify({'error': '卡组名称不能为空'}), 400
        
        # 使用新的验证系统验证卡组
        # 首先，通过card_ids获取完整卡牌信息
        cards_from_db = CardData.query.filter(CardData.id.in_(card_list)).all()
        
        # 将数据库中的卡牌数据转换为卡片对象用于验证
        from utils.deck_validator import validate_deck_api
        # 将数据库中的卡片转换为API验证函数需要的格式
        card_data_for_validation = []
        for card in cards_from_db:
            card_data = {
                'id': card.id,
                'name': card.name,
                'card_type': card.card_type,
                'cost': json.loads(card.cost) if card.cost else [],
                'description': card.description,
                'character_subtype': card.character_subtype
            }
            card_data_for_validation.append(card_data)
        
        # 进行详细验证
        validation_result = validate_deck_api(card_data_for_validation)
        if not validation_result['is_valid']:
            return jsonify({'error': '卡组验证失败', 'details': validation_result['errors']}), 400
        
        # 创建卡组
        deck = Deck(
            user_id=current_user_id,
            name=name,
            description=description,
            cards=json.dumps(card_list)
        )
        
        db.session.add(deck)
        db.session.commit()
        
        return jsonify({
            'message': '卡组创建成功',
            'deck': {
                'id': deck.id,
                'name': deck.name,
                'description': deck.description,
                'cards': card_list,
                'created_at': deck.created_at.isoformat()
            }
        }), 201
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500


@cards_bp.route('/decks/<deck_id>', methods=['PUT'])
@jwt_required()
def update_deck(deck_id):
    """
    更新卡组
    """
    try:
        current_user_id = get_jwt_identity()
        data = request.get_json()
        
        deck = Deck.query.filter_by(id=deck_id, user_id=current_user_id).first()
        if not deck:
            return jsonify({'error': '卡组不存在或无权限访问'}), 404
        
        name = data.get('name', deck.name)
        description = data.get('description', deck.description)
        card_list = data.get('cards', json.loads(deck.cards) if deck.cards else [])
        
        # 使用新的验证系统验证卡组
        # 首先，通过card_ids获取完整卡牌信息
        cards_from_db = CardData.query.filter(CardData.id.in_(card_list)).all()
        
        # 将数据库中的卡牌数据转换为卡片对象用于验证
        from utils.deck_validator import validate_deck_api
        # 将数据库中的卡片转换为API验证函数需要的格式
        card_data_for_validation = []
        for card in cards_from_db:
            card_data = {
                'id': card.id,
                'name': card.name,
                'card_type': card.card_type,
                'cost': json.loads(card.cost) if card.cost else [],
                'description': card.description,
                'character_subtype': card.character_subtype
            }
            card_data_for_validation.append(card_data)
        
        # 进行详细验证
        validation_result = validate_deck_api(card_data_for_validation)
        if not validation_result['is_valid']:
            return jsonify({'error': '卡组验证失败', 'details': validation_result['errors']}), 400
        
        # 更新卡组
        deck.name = name
        deck.description = description
        deck.cards = json.dumps(card_list)
        
        db.session.commit()
        
        return jsonify({
            'message': '卡组更新成功',
            'deck': {
                'id': deck.id,
                'name': deck.name,
                'description': deck.description,
                'cards': card_list,
                'updated_at': deck.updated_at.isoformat()
            }
        }), 200
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500


@cards_bp.route('/decks/<deck_id>', methods=['DELETE'])
@jwt_required()
def delete_deck(deck_id):
    """
    删除卡组
    """
    try:
        current_user_id = get_jwt_identity()
        
        deck = Deck.query.filter_by(id=deck_id, user_id=current_user_id).first()
        if not deck:
            return jsonify({'error': '卡组不存在或无权限访问'}), 404
        
        db.session.delete(deck)
        db.session.commit()
        
        return jsonify({'message': '卡组删除成功'}), 200
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500


@cards_bp.route('/decks/<deck_id>', methods=['GET'])
@jwt_required()
def get_deck(deck_id):
    """
    获取特定卡组详情
    """
    try:
        current_user_id = get_jwt_identity()
        
        deck = Deck.query.filter_by(id=deck_id, user_id=current_user_id).first()
        if not deck:
            return jsonify({'error': '卡组不存在或无权限访问'}), 404
        
        # 获取卡组中的卡牌详情
        card_list = json.loads(deck.cards) if deck.cards else []
        
        # 根据卡ID获取完整的卡牌信息
        cards = CardData.query.filter(CardData.id.in_(card_list)).all()
        card_details = []
        for card in cards:
            card_details.append({
                'id': card.id,
                'name': card.name,
                'card_type': card.card_type,
                'element_type': card.element_type,
                'rarity': card.rarity,
                'cost': json.loads(card.cost) if card.cost else [],
                'description': card.description,
                'character_subtype': card.character_subtype,
                'image_url': card.image_url
            })
        
        return jsonify({
            'deck': {
                'id': deck.id,
                'name': deck.name,
                'description': deck.description,
                'cards': card_details,
                'created_at': deck.created_at.isoformat(),
                'updated_at': deck.updated_at.isoformat()
            }
        }), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@cards_bp.route('/decks/validate', methods=['POST'])
@jwt_required()
def validate_deck():
    """
    验证卡组是否符合规则
    """
    try:
        data = request.get_json()
        card_list = data.get('cards', [])
        
        # 通过card_ids获取完整卡牌信息
        cards_from_db = CardData.query.filter(CardData.id.in_(card_list)).all()
        
        # 将数据库中的卡牌数据转换为卡片对象用于验证
        from utils.deck_validator import validate_deck_api
        # 将数据库中的卡片转换为API验证函数需要的格式
        card_data_for_validation = []
        for card in cards_from_db:
            card_data = {
                'id': card.id,
                'name': card.name,
                'card_type': card.card_type,
                'cost': json.loads(card.cost) if card.cost else [],
                'description': card.description,
                'character_subtype': card.character_subtype
            }
            card_data_for_validation.append(card_data)
        
        # 进行详细验证
        validation_result = validate_deck_api(card_data_for_validation)
        
        return jsonify(validation_result), 200
    except Exception as e:
        return jsonify({'error': str(e), 'is_valid': False, 'errors': ['验证过程中发生错误']}), 500