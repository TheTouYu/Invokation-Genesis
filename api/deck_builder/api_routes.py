"""
标准化的卡牌构建器API路由
使用数据库作为统一数据源，替代原有的文件读取方式
"""

from flask import Blueprint, jsonify, request, g
import json
from utils.deck_validator import validate_deck_composition
from utils.card_data_processor import (
    load_card_data_from_db,
    extract_country_from_region,
    extract_weapon_type_from_region,
)
from flask_jwt_extended import jwt_required, get_jwt_identity
from dal import db_dal
from utils.logger import get_logger, log_api_call

deck_builder_api = Blueprint("deck_builder_api", __name__)


def load_card_data():
    """从数据库加载所有卡牌数据（使用统一的处理器）"""
    return load_card_data_from_db()


def extract_element_from_character(character):
    """从角色技能费用中提取元素信息"""
    if "skills" in character and len(character["skills"]) > 0:
        first_skill = character["skills"][0]
        if "cost" in first_skill:
            costs = first_skill["cost"]
            for cost in costs:
                if isinstance(cost, dict) and "type" in cost:
                    cost_type = cost["type"]
                    # 检查是否为元素类型
                    elements = ["火", "水", "雷", "草", "风", "岩", "冰", "物理"]
                    if cost_type in elements:
                        return cost_type
                    # 检查始基力类型
                    if "始基力" in cost_type:
                        if "荒性" in cost_type:
                            return "荒性"
                        elif "芒性" in cost_type:
                            return "芒性"

    # 如果从技能费用中无法提取，尝试从其他字段中获取
    element = character.get("element", "")
    if element:
        return element

    return "物理"


def extract_element_from_region(region):
    """从region字段中提取元素信息"""
    if not region:
        return "未知"

    # 常见元素列表，包括始基力类型
    elements = ["火", "水", "雷", "草", "风", "岩", "冰", "物理"]

    # 检查是否包含始基力类型
    if "始基力：荒性" in region:
        return "荒性"
    elif "始基力：芒性" in region:
        return "芒性"

    # 检查常规元素
    for element in elements:
        if element in region:
            return element

    return "物理"


@deck_builder_api.route("/api/deck/validate", methods=["POST"])
@log_api_call
def validate_deck_api():
    """验证一个卡组组成基于游戏规则"""
    logger = get_logger(__name__)
    request_id = getattr(g, 'request_id', 'N/A')
    logger.info(f"Deck validation request, Request-ID: {request_id}")
    
    try:
        data = request.get_json()
        character_ids = data.get("characters", [])
        card_ids = data.get("cards", [])

        logger.info(f"Validating deck with {len(character_ids)} characters and {len(card_ids)} cards, Request-ID: {request_id}")

        # 转换为验证器期望的格式
        deck_data = {
            "name": data.get("deck_name", "Test Deck"),
            "character_ids": character_ids,
            "card_ids": card_ids,
        }

        # 使用现有的验证函数
        validation_result = validate_deck_composition(deck_data)
        
        logger.info(f"Deck validation completed with result: {validation_result['is_valid']}, Request-ID: {request_id}")

        return jsonify(
            {
                "valid": validation_result["is_valid"],
                "rules": {
                    "character_count": validation_result["rules"]
                    .get("character_count", {})
                    .get("valid", False),
                    "character_count_msg": validation_result["rules"]
                    .get("character_count", {})
                    .get("message", ""),
                    "deck_size": validation_result["rules"]
                    .get("deck_size", {})
                    .get("valid", False),
                    "deck_size_msg": validation_result["rules"]
                    .get("deck_size", {})
                    .get("message", ""),
                    "character_limit": validation_result["rules"]
                    .get("character_limit", {})
                    .get("valid", False),
                    "character_limit_msg": validation_result["rules"]
                    .get("character_limit", {})
                    .get("message", ""),
                    "card_limit": validation_result["rules"]
                    .get("card_limit", {})
                    .get("valid", False),
                    "card_limit_msg": validation_result["rules"]
                    .get("card_limit", {})
                    .get("message", ""),
                    "elemental_synergy": validation_result["rules"]
                    .get("elemental_synergy", {})
                    .get("valid", False),
                    "elemental_synergy_msg": validation_result["rules"]
                    .get("elemental_synergy", {})
                    .get("message", ""),
                },
                "errors": validation_result["errors"],
                "suggestions": validation_result["suggestions"],
            }
        )

    except Exception as e:
        logger.error(f"Deck validation failed with error: {str(e)}, Request-ID: {request_id}")
        return jsonify(
            {
                "valid": False,
                "rules": {},
                "errors": [f"验证过程中出现错误: {str(e)}"],
                "suggestions": [],
            }
        ), 400


@deck_builder_api.route("/api/deck", methods=["POST"])
@jwt_required()
def create_deck():
    """为当前用户创建一个新卡组"""
    try:
        current_user_id = get_jwt_identity()
        data = request.get_json()

        name = data.get("name")
        card_ids = data.get("card_ids", [])
        character_card_ids = data.get("character_card_ids", [])
        description = data.get("description", "")

        # 验证必要参数
        if not name:
            return jsonify({"message": "卡组名称是必需的"}), 400

        if not card_ids or not character_card_ids:
            return jsonify({"message": "卡组必须包含卡牌和角色"}), 400

        # 验证卡组是否符合规则
        deck_data = {
            "name": name,
            "character_ids": character_card_ids,
            "card_ids": card_ids,
        }
        validation_result = validate_deck_composition(deck_data)

        if not validation_result["is_valid"]:
            return jsonify(
                {"message": "卡组不符合规则", "errors": validation_result["errors"]}
            ), 400

        # 合并普通卡牌和角色卡牌到一个列表中
        all_cards = character_card_ids + card_ids
        # 使用DAL创建卡组
        deck = db_dal.decks.create_deck(
            user_id=current_user_id, name=name, cards=all_cards, description=description
        )

        return jsonify(
            {"message": "卡组创建成功", "deck_id": deck.id, "deck_name": deck.name}
        ), 201

    except Exception as e:
        return jsonify({"message": "创建卡组失败", "error": str(e)}), 500


@deck_builder_api.route("/api/deck", methods=["PUT"])
@jwt_required()
def update_deck():
    """更新指定卡组"""
    try:
        current_user_id = get_jwt_identity()
        data = request.get_json()

        deck_id = data.get("deck_id")
        name = data.get("name")
        card_ids = data.get("card_ids", [])
        description = data.get("description", "")

        # 验证参数
        if not deck_id:
            return jsonify({"message": "卡组ID是必需的"}), 400

        # 验证卡组是否属于当前用户
        deck = db_dal.decks.get_deck_by_id(deck_id)
        if not deck or deck.user_id != current_user_id:
            return jsonify({"message": "无权限访问此卡组"}), 403

        # 更新卡组
        update_data = {}
        if name:
            update_data["name"] = name
        if card_ids:
            update_data["cards"] = card_ids
        if description is not None:
            update_data["description"] = description

        success = db_dal.decks.update_deck(deck_id, **update_data)
        if success:
            return jsonify({"message": "卡组更新成功"}), 200
        else:
            return jsonify({"message": "更新卡组失败"}), 500

    except Exception as e:
        return jsonify({"message": "更新卡组失败", "error": str(e)}), 500


@deck_builder_api.route("/api/user/<user_id>/decks", methods=["GET"])
@jwt_required()
def get_user_decks(user_id):
    """获取指定用户的所有卡组"""
    try:
        current_user_id = get_jwt_identity()

        # 检查权限 - 用户只能查看自己的卡组，除非是管理员
        if current_user_id != user_id:
            # 检查是否是管理员权限（这里简化处理，实际应用中需要具体实现）
            # 暂时只允许用户查看自己的卡组
            return jsonify({"message": "无权限访问此用户卡组"}), 403

        page = request.args.get("page", 1, type=int)
        per_page = request.args.get("per_page", 10, type=int)
        per_page = min(per_page, 100)  # 限制最大每页数量

        offset = (page - 1) * per_page

        decks = db_dal.decks.get_decks_by_user(user_id, limit=per_page, offset=offset)

        # 计算总数
        all_user_decks = db_dal.decks.get_decks_by_user(user_id, limit=None, offset=0)
        total_count = len(all_user_decks)

        deck_list = []
        for deck in decks:
            deck_list.append(
                {
                    "id": deck.id,
                    "name": deck.name,
                    "description": deck.description,
                    "cards": deck.cards,
                    "created_at": deck.created_at.isoformat()
                    if deck.created_at
                    else None,
                    "updated_at": deck.updated_at.isoformat()
                    if deck.updated_at
                    else None,
                }
            )

        return jsonify(
            {
                "decks": deck_list,
                "pagination": {
                    "page": page,
                    "per_page": per_page,
                    "total": total_count,
                    "pages": (total_count + per_page - 1) // per_page,
                },
            }
        ), 200

    except Exception as e:
        return jsonify({"message": "获取卡组列表失败", "error": str(e)}), 500
