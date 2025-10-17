"""
标准化的卡牌构建器API路由
使用数据库作为统一数据源，替代原有的文件读取方式
"""
from flask import Blueprint, jsonify, request
import json
from utils.deck_validator import validate_deck_composition
from utils.card_data_processor import load_card_data_from_db, extract_country_from_region, extract_weapon_type_from_region

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
def validate_deck_api():
    """验证一个卡组组成基于游戏规则"""
    try:
        data = request.get_json()
        character_ids = data.get("characters", [])
        card_ids = data.get("cards", [])

        # 转换为验证器期望的格式
        deck_data = {
            "name": data.get("deck_name", "Test Deck"),
            "character_ids": character_ids,
            "card_ids": card_ids,
        }

        # 使用现有的验证函数
        validation_result = validate_deck_composition(deck_data)

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
        return jsonify(
            {
                "valid": False,
                "rules": {},
                "errors": [f"验证过程中出现错误: {str(e)}"],
                "suggestions": [],
            }
        ), 400











