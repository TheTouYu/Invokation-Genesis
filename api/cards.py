"""
卡牌API端点
"""
from flask import Blueprint, jsonify
from models.db_models import CardData

cards_bp = Blueprint('cards', __name__)

@cards_bp.route('/cards/characters', methods=['GET'])
def get_character_cards():
    """获取角色卡牌列表"""
    try:
        cards = CardData.query.filter_by(card_type='character').all()
        result = []
        for card in cards:
            result.append({
                'id': card.id,
                'name': card.name,
                'card_type': card.card_type,
                'rarity': card.rarity,
                'description': card.description,
                'character': card.character
            })
        return jsonify(result)
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@cards_bp.route('/cards/weapons', methods=['GET'])
def get_weapon_cards():
    """获取武器卡牌列表"""
    try:
        cards = CardData.query.filter_by(card_type='weapon').all()
        result = []
        for card in cards:
            result.append({
                'id': card.id,
                'name': card.name,
                'card_type': card.card_type,
                'rarity': card.rarity,
                'description': card.description,
                'character': card.character
            })
        return jsonify(result)
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@cards_bp.route('/cards/artifacts', methods=['GET'])
def get_artifact_cards():
    """获取圣遗物卡牌列表"""
    try:
        cards = CardData.query.filter_by(card_type='artifact').all()
        result = []
        for card in cards:
            result.append({
                'id': card.id,
                'name': card.name,
                'card_type': card.card_type,
                'rarity': card.rarity,
                'description': card.description,
                'character': card.character
            })
        return jsonify(result)
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@cards_bp.route('/cards/talents', methods=['GET'])
def get_talent_cards():
    """获取天赋卡牌列表"""
    try:
        cards = CardData.query.filter_by(card_type='talent').all()
        result = []
        for card in cards:
            result.append({
                'id': card.id,
                'name': card.name,
                'card_type': card.card_type,
                'rarity': card.rarity,
                'description': card.description,
                'character': card.character
            })
        return jsonify(result)
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@cards_bp.route('/cards/supports', methods=['GET'])
def get_support_cards():
    """获取支援卡牌列表"""
    try:
        cards = CardData.query.filter_by(card_type='support').all()
        result = []
        for card in cards:
            result.append({
                'id': card.id,
                'name': card.name,
                'card_type': card.card_type,
                'rarity': card.rarity,
                'description': card.description,
                'character': card.character
            })
        return jsonify(result)
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@cards_bp.route('/cards/events', methods=['GET'])
def get_event_cards():
    """获取事件卡牌列表"""
    try:
        cards = CardData.query.filter_by(card_type='event').all()
        result = []
        for card in cards:
            result.append({
                'id': card.id,
                'name': card.name,
                'card_type': card.card_type,
                'rarity': card.rarity,
                'description': card.description,
                'character': card.character
            })
        return jsonify(result)
    except Exception as e:
        return jsonify({"error": str(e)}), 500