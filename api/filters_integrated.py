"""
Integrated filters API for both character and card tags/filters
"""

from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required
import json
from dal import db_dal

filters_bp = Blueprint("filters", __name__)


def get_models():
    from models.db_models import model_container

    return model_container.CardData, model_container.Deck


@filters_bp.route("/filters", methods=["GET"])
@jwt_required()
def get_all_filters():
    """
    获取所有卡牌的过滤选项 - 统一接口，返回所有可能的过滤选项
    包括标签和角色过滤选项
    """
    try:
        CardData, Deck = get_models()

        # 获取所有卡牌用于提取标签
        cards = CardData.query.filter(CardData.is_active == True).all()

        # 初始化所有过滤选项
        card_types = set()
        card_tags = set()
        countries = set()
        elements = set()
        weapon_types = set()

        # 定义有意义的标签类别
        valid_tags = {
            "事件牌",
            "装备牌",
            "支援牌",
            "角色牌",
            "元素共鸣",
            "武器",
            "圣遗物",
            "天赋",
            "特技",
            "秘传",
            "伙伴",
            "料理",
            "道具",
            "场地",
            "战斗行动",
        }

        card_types.add("非角色牌")
        card_types.add("行动牌")
        # 提取所有过滤选项
        for card in cards:
            # 卡牌类型
            card_types.add(card.card_type)

            # 基础类型标签
            if card.card_type in valid_tags:
                card_tags.add(card.card_type)

            # 检查character_subtype中是否包含标签
            if card.character_subtype:
                for tag in valid_tags:
                    if tag in card.character_subtype:
                        card_tags.add(tag)

            # 检查技能描述中是否包含特殊标签
            if card.skills:
                try:
                    skills_data = (
                        card.skills
                        if isinstance(card.skills, list)
                        else (
                            json.loads(card.skills)
                            if isinstance(card.skills, str)
                            else card.skills
                        )
                    )
                    for skill in skills_data:
                        if "description" in skill:
                            desc = skill["description"]
                            for tag in valid_tags:
                                if tag in desc:
                                    card_tags.add(tag)
                except (json.JSONDecodeError, TypeError):
                    pass

            # 如果是角色牌，提取角色特定的过滤选项
            if card.card_type == "角色牌":
                # 提取国家
                # For country detection, we should prioritize character_subtype which contains country/element info
                character_subtype_val = getattr(card, "character_subtype", "") or ""
                weapon_type_val = getattr(card, "weapon_type", "") or ""

                # Use character_subtype first for country detection since it contains element/country info
                region_info = character_subtype_val or weapon_type_val

                country_keywords = [
                    "蒙德",
                    "璃月",
                    "稻妻",
                    "须弥",
                    "枫丹",
                    "纳塔",
                    "至冬",
                    "魔物",
                    "愚人众",
                    "丘丘人",
                ]
                country = next(
                    (c for c in country_keywords if c in region_info), "未知"
                )
                countries.add(country)

                # 提取元素
                element = getattr(card, "element_type", "") or ""
                if not element and card.skills:
                    try:
                        skills_data = (
                            card.skills
                            if isinstance(card.skills, list)
                            else (
                                json.loads(card.skills)
                                if isinstance(card.skills, str)
                                else card.skills
                            )
                        )
                        if (
                            skills_data
                            and isinstance(skills_data, list)
                            and len(skills_data) > 0
                        ):
                            first_skill = skills_data[0]
                            if "cost" in first_skill:
                                costs = first_skill["cost"]
                                elements_list = [
                                    "火",
                                    "水",
                                    "雷",
                                    "草",
                                    "风",
                                    "岩",
                                    "冰",
                                    "物理",
                                ]
                                for cost in costs:
                                    if isinstance(cost, dict) and "type" in cost:
                                        cost_type = cost["type"]
                                        if cost_type in elements_list:
                                            element = cost_type
                                            break
                                        if "始基力" in cost_type:
                                            if "荒性" in cost_type:
                                                element = "荒性"
                                            elif "芒性" in cost_type:
                                                element = "芒性"
                                    elif (
                                        isinstance(cost, str) and cost in elements_list
                                    ):
                                        element = cost
                                        break
                    except (json.JSONDecodeError, TypeError):
                        pass
                elements.add(element if element else "未知")

                # 提取武器类型
                weapon_type = getattr(card, "weapon_type", "") or "未知"
                weapon_type_keywords = [
                    "单手剑",
                    "双手剑",
                    "长柄武器",
                    "弓",
                    "法器",
                    "其他武器",
                ]
                if not any(keyword in weapon_type for keyword in weapon_type_keywords):
                    weapon_type = "未知"
                weapon_types.add(weapon_type)

        # 移除'未知'选项，如果存在其他选项
        if len(countries) > 1:
            countries.discard("未知")
        if len(elements) > 1:
            elements.discard("未知")
        if len(weapon_types) > 1:
            weapon_types.discard("未知")

        # 构建响应
        result = {
            # 通用过滤选项
            "card_types": sorted(list(card_types)),
            "tags": sorted(list(card_tags)),
            # 角色特定过滤选项
            "countries": sorted(list(countries)),
            "elements": sorted(list(elements)),
            "weapon_types": sorted(list(weapon_types)),
        }

        return jsonify(result), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@filters_bp.route("/filters/character", methods=["GET"])
@jwt_required()
def get_character_filters():
    """
    获取角色的过滤选项（国家、元素、武器类型）
    专为角色选择界面设计
    """
    try:
        CardData, Deck = get_models()
        # 只查询角色牌
        characters = CardData.query.filter(
            CardData.card_type == "角色牌", CardData.is_active == True
        ).all()

        countries = set()
        elements = set()
        weapon_types = set()

        for character in characters:
            # 提取国家
            # For country detection, we should prioritize character_subtype which contains country/element info
            character_subtype_val = getattr(character, "character_subtype", "") or ""
            weapon_type_val = getattr(character, "weapon_type", "") or ""

            # Use character_subtype first for country detection since it contains element/country info
            region_info = character_subtype_val or weapon_type_val

            country_keywords = [
                "蒙德",
                "璃月",
                "稻妻",
                "须弥",
                "枫丹",
                "纳塔",
                "至冬",
                "魔物",
                "愚人众",
                "丘丘人",
            ]
            country = next((c for c in country_keywords if c in region_info), "未知")
            countries.add(country)

            # 提取元素
            element = getattr(character, "element_type", "") or ""
            if not element and character.skills:
                try:
                    skills_data = (
                        character.skills
                        if isinstance(character.skills, list)
                        else (
                            json.loads(character.skills)
                            if isinstance(character.skills, str)
                            else character.skills
                        )
                    )
                    if (
                        skills_data
                        and isinstance(skills_data, list)
                        and len(skills_data) > 0
                    ):
                        first_skill = skills_data[0]
                        if "cost" in first_skill:
                            costs = first_skill["cost"]
                            elements_list = [
                                "火",
                                "水",
                                "雷",
                                "草",
                                "风",
                                "岩",
                                "冰",
                                "物理",
                            ]
                            for cost in costs:
                                if isinstance(cost, dict) and "type" in cost:
                                    cost_type = cost["type"]
                                    if cost_type in elements_list:
                                        element = cost_type
                                        break
                                    if "始基力" in cost_type:
                                        if "荒性" in cost_type:
                                            element = "荒性"
                                        elif "芒性" in cost_type:
                                            element = "芒性"
                                elif isinstance(cost, str) and cost in elements_list:
                                    element = cost
                                    break
                except (json.JSONDecodeError, TypeError):
                    pass
            elements.add(element if element else "未知")

            # 提取武器类型
            weapon_type = getattr(character, "weapon_type", "") or "未知"
            weapon_type_keywords = [
                "单手剑",
                "双手剑",
                "长柄武器",
                "弓",
                "法器",
                "其他武器",
            ]
            if not any(keyword in weapon_type for keyword in weapon_type_keywords):
                weapon_type = "未知"
            weapon_types.add(weapon_type)

        # 移除'未知'选项，如果存在其他选项
        if len(countries) > 1:
            countries.discard("未知")
        if len(elements) > 1:
            elements.discard("未知")
        if len(weapon_types) > 1:
            weapon_types.discard("未知")

        return jsonify(
            {
                "countries": sorted(list(countries)),
                "elements": sorted(list(elements)),
                "weapon_types": sorted(list(weapon_types)),
            }
        ), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@filters_bp.route("/filters/tags", methods=["GET"])
@jwt_required()
def get_card_tags():
    """
    获取所有卡牌标签 - 用于过滤和搜索
    """
    try:
        CardData, Deck = get_models()
        cards = CardData.query.filter(CardData.is_active == True).all()
        tags = set()

        # 定义有意义的标签类别
        valid_tags = {
            "事件牌",
            "装备牌",
            "支援牌",
            "角色牌",
            "元素共鸣",
            "武器",
            "圣遗物",
            "天赋",
            "特技",
            "秘传",
            "伙伴",
            "料理",
            "道具",
            "场地",
            "战斗行动",
        }

        for card in cards:
            # 添加基础类型标签
            if card.card_type in valid_tags:
                tags.add(card.card_type)

            # 检查character_subtype中是否包含标签
            if card.character_subtype:
                for tag in valid_tags:
                    if tag in card.character_subtype:
                        tags.add(tag)

            # 检查技能描述中是否包含特殊标签
            if card.skills:
                try:
                    skills_data = (
                        card.skills
                        if isinstance(card.skills, list)
                        else (
                            json.loads(card.skills)
                            if isinstance(card.skills, str)
                            else card.skills
                        )
                    )
                    for skill in skills_data:
                        if "description" in skill:
                            desc = skill["description"]
                            for tag in valid_tags:
                                if tag in desc:
                                    tags.add(tag)
                except (json.JSONDecodeError, TypeError):
                    pass

        return jsonify({"tags": sorted(list(tags))}), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500

