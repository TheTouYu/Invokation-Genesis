"""
标准化的卡牌API路由
统一所有卡牌数据访问接口，全部使用数据库作为数据源
"""

import json
from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from models.db_models import CardData, Deck, db
from sqlalchemy import or_, and_
from typing import Dict, Any, List
import random
from utils.card_data_processor import load_card_data_from_db

cards_bp = Blueprint("standardized_cards", __name__)


def extract_card_info(card: CardData) -> Dict[str, Any]:
    """
    从CardData对象中提取标准化的卡牌信息
    统一处理所有卡牌类型的数据格式
    """
    # 处理cost字段 - 优先从技能中提取，否则使用card.cost
    card_cost = card.cost if card.cost else []
    if isinstance(card_cost, str):
        try:
            card_cost = json.loads(card_cost) if card_cost else []
        except json.JSONDecodeError:
            card_cost = []

    # 对于非角色牌，尝试从技能中获取cost和description
    card_description = card.description or ""
    if card.card_type != "角色牌" and card.skills:
        try:
            skills_data = (
                card.skills
                if isinstance(card.skills, list)
                else json.loads(card.skills)
            )
            if skills_data and isinstance(skills_data, list) and len(skills_data) > 0:
                first_skill = skills_data[0]
                if "cost" in first_skill:
                    card_cost = first_skill["cost"]
                if "description" in first_skill:
                    card_description = first_skill["description"]
        except (json.JSONDecodeError, TypeError):
            pass
    elif card.card_type == "角色牌":
        # 对于角色牌，技能中也可能包含cost和description信息
        if card.skills:
            try:
                skills_data = (
                    card.skills
                    if isinstance(card.skills, list)
                    else json.loads(card.skills)
                )
                if (
                    skills_data
                    and isinstance(skills_data, list)
                    and len(skills_data) > 0
                ):
                    first_skill = skills_data[0]
                    if "cost" in first_skill:
                        card_cost = first_skill["cost"]
                    if "description" in first_skill:
                        card_description = first_skill["description"]
            except (json.JSONDecodeError, TypeError):
                pass

    # 提取国家信息
    region_info = (
        getattr(card, "weapon_type", "") or getattr(card, "character_subtype", "") or ""
    )

    countries = [
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
    country = next((c for c in countries if c in region_info), "")

    # 从技能中提取元素信息
    element = card.element_type or ""
    if not element and card.skills:
        try:
            skills_data = (
                card.skills
                if isinstance(card.skills, list)
                else json.loads(card.skills)
            )
            if skills_data and isinstance(skills_data, list) and len(skills_data) > 0:
                first_skill = skills_data[0]
                if "cost" in first_skill:
                    costs = first_skill["cost"]
                    elements = ["火", "水", "雷", "草", "风", "岩", "冰", "物理"]
                    for cost in costs:
                        if isinstance(cost, dict) and "type" in cost:
                            cost_type = cost["type"]
                            if cost_type in elements:
                                element = cost_type
                                break
                            if "始基力" in cost_type:
                                if "荒性" in cost_type:
                                    element = "荒性"
                                elif "芒性" in cost_type:
                                    element = "芒性"
                        elif isinstance(cost, str) and cost in elements:
                            element = cost
                            break
        except (json.JSONDecodeError, TypeError):
            pass

    # 提取武器类型
    weapon_type = getattr(card, "weapon_type", "") or ""
    weapon_types = ["单手剑", "双手剑", "长柄武器", "弓", "法器", "其他武器"]
    if not weapon_type:
        for wt in weapon_types:
            if wt in region_info:
                weapon_type = wt
                break

    # 构建基础卡牌数据
    card_data = {
        "id": card.id,
        "name": card.name,
        "type": card.card_type,
        "description": card_description,
        "cost": card_cost,
        "rarity": getattr(card, "rarity", None),
        "element_type": getattr(card, "element_type", None),
        "character_subtype": getattr(card, "character_subtype", None),
        "image_url": getattr(card, "image_url", None),
        "country": country,
        "element": element,
        "weapon_type": weapon_type,
        "skills": json.loads(card.skills) if card.skills else [],
        "title": region_info if isinstance(region_info, str) else "",
    }

    # 为角色牌添加额外属性
    if card.card_type == "角色牌":
        card_data.update(
            {
                "health": getattr(card, "health", None),
                "energy": getattr(card, "energy", None),
                "max_health": getattr(card, "max_health", None),
                "max_energy": getattr(card, "max_energy", None),
            }
        )

    return card_data


def apply_filters(query, filters: Dict[str, Any]):
    """
    应用过滤条件到SQLAlchemy查询对象
    """
    card_type = filters.get("type")
    element = filters.get("element")
    country = filters.get("country")
    weapon_type = filters.get("weapon_type")
    character_subtype = filters.get("character_subtype")
    rarity = filters.get("rarity")
    search = filters.get("search")
    tags = filters.get("tags", [])

    # 应用基础过滤条件
    if card_type:
        if card_type == "非角色牌":
            query = query.filter(CardData.card_type != "角色牌")
        else:
            query = query.filter(CardData.card_type == card_type)

    if element:
        query = query.filter(CardData.element_type == element)

    if character_subtype:
        query = query.filter(CardData.character_subtype == character_subtype)

    if rarity is not None:
        query = query.filter(CardData.rarity == int(rarity))

    # 应用国家过滤 - 在数据库中可能存储在不同的字段
    if country:
        query = query.filter(
            or_(
                CardData.weapon_type.contains(country),
                CardData.character_subtype.contains(country),
            )
        )

    # 应用武器类型过滤
    if weapon_type:
        query = query.filter(CardData.weapon_type == weapon_type)

    # 应用标签过滤功能
    if tags:
        for tag in tags:
            query = query.filter(
                or_(
                    CardData.card_type.contains(tag),
                    CardData.character_subtype.contains(tag),
                    CardData.description.contains(tag),
                    CardData.skills.contains(tag),
                )
            )

    # 应用搜索过滤
    if search:
        # 将搜索词按空格分割成多个关键字
        search_terms = [term.strip() for term in search.split() if term.strip()]
        if search_terms:
            for term in search_terms:
                search_pattern = f"%{term}%"
                query = query.filter(
                    or_(
                        CardData.name.ilike(search_pattern),
                        CardData.description.ilike(search_pattern),
                        CardData.card_type.ilike(search_pattern),
                        CardData.character_subtype.ilike(search_pattern),
                        CardData.skills.ilike(search_pattern),  # 在技能中搜索
                    )
                )

    return query


@cards_bp.route("/cards", methods=["GET"])
@jwt_required()
def get_all_cards():
    """
    获取卡牌数据 - 支持多种过滤条件和分页
    查询参数:
    - type: 卡牌类型 (角色牌, 事件牌, 武器, 圣遗物, 支援牌, 非角色牌)
    - element: 元素类型
    - country: 国家 (蒙德, 璃月, 稻妻, etc.)
    - weapon_type: 武器类型 (单手剑, 双手剑, etc.)
    - character_subtype: 角色子类型
    - rarity: 稀有度
    - search: 搜索关键词 (在名称、描述、类型、子类型、技能中搜索)
    - page: 页码 (默认 1)
    - per_page: 每页数量 (默认 20, 最大 100)
    """
    try:
        # 获取查询参数
        filters = {
            "type": request.args.get("type"),
            "element": request.args.get("element"),
            "country": request.args.get("country"),
            "weapon_type": request.args.get("weapon_type"),
            "character_subtype": request.args.get("character_subtype"),
            "rarity": request.args.get("rarity"),
            "search": request.args.get("search"),
            "tags": request.args.getlist("tag"),  # 支持多个标签
        }

        page = request.args.get("page", 1, type=int)
        per_page = min(
            request.args.get("per_page", 20, type=int), 100
        )  # 限制最大每页数量

        # 构建查询
        query = CardData.query.filter(CardData.is_active == True)

        # 应用过滤条件
        query = apply_filters(query, filters)

        # 分页
        cards = query.paginate(page=page, per_page=per_page, error_out=False)

        # 转换为标准化格式
        result = [extract_card_info(card) for card in cards.items]

        return jsonify(
            {
                "cards": result,
                "total": cards.total,
                "pages": cards.pages,
                "current_page": page,
                "per_page": per_page,
                "has_next": cards.has_next,
                "has_prev": cards.has_prev,
            }
        ), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@cards_bp.route("/cards/<card_id>", methods=["GET"])
@jwt_required()
def get_card_by_id(card_id):
    """
    根据ID获取特定卡牌信息
    """
    try:
        card = CardData.query.filter_by(id=card_id, is_active=True).first()
        if not card:
            return jsonify({"error": "卡牌不存在"}), 404

        card_data = extract_card_info(card)
        return jsonify({"card": card_data}), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@cards_bp.route("/cards/types", methods=["GET"])
@jwt_required()
def get_card_types():
    """
    获取所有卡牌类型列表
    """
    try:
        types = (
            db.session.query(CardData.card_type)
            .filter(CardData.is_active == True)
            .distinct(CardData.card_type)
            .all()
        )
        type_list = [t[0] for t in types if t[0]]
        return jsonify({"types": type_list}), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@cards_bp.route("/cards/elements", methods=["GET"])
@jwt_required()
def get_card_elements():
    """
    获取所有元素类型列表
    """
    try:
        elements = (
            db.session.query(CardData.element_type)
            .filter(CardData.is_active == True)
            .distinct(CardData.element_type)
            .all()
        )
        element_list = [e[0] for e in elements if e[0]]
        return jsonify({"elements": element_list}), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@cards_bp.route("/cards/countries", methods=["GET"])
@jwt_required()
def get_card_countries():
    """
    获取所有国家列表
    """
    try:
        # 从weapon_type和character_subtype字段中提取国家信息
        cards = CardData.query.filter(CardData.is_active == True).all()
        countries = set()

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

        for card in cards:
            # 检查weapon_type
            if card.weapon_type:
                for country in country_keywords:
                    if country in card.weapon_type:
                        countries.add(country)
            # 检查character_subtype
            if card.character_subtype:
                for country in country_keywords:
                    if country in card.character_subtype:
                        countries.add(country)

        return jsonify({"countries": sorted(list(countries))}), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@cards_bp.route("/cards/weapon_types", methods=["GET"])
@jwt_required()
def get_weapon_types():
    """
    获取所有武器类型列表
    """
    try:
        # 从weapon_type字段中提取武器类型
        weapon_types = (
            db.session.query(CardData.weapon_type)
            .filter(CardData.is_active == True, CardData.weapon_type.isnot(None))
            .distinct(CardData.weapon_type)
            .all()
        )

        weapon_type_list = [wt[0] for wt in weapon_types if wt[0]]
        weapon_type_keywords = [
            "单手剑",
            "双手剑",
            "长柄武器",
            "弓",
            "法器",
            "其他武器",
        ]

        # 过滤出有效的武器类型
        valid_weapons = [
            wt
            for wt in weapon_type_list
            if any(keyword in wt for keyword in weapon_type_keywords)
        ]

        return jsonify({"weapon_types": sorted(valid_weapons)}), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@cards_bp.route("/cards/tags", methods=["GET"])
@jwt_required()
def get_card_tags():
    """
    获取所有卡牌标签 - 用于过滤和搜索
    """
    try:
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
                        else json.loads(card.skills)
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


@cards_bp.route("/cards/random", methods=["GET"])
@jwt_required()
def get_random_cards():
    """
    获取随机卡牌，支持过滤条件
    查询参数:
    - type: 卡牌类型
    - country: 国家
    - element: 元素类型
    - weapon_type: 武器类型
    - count: 获取数量 (默认 1)
    """
    try:
        # 获取查询参数
        filters = {
            "type": request.args.get("type"),
            "element": request.args.get("element"),
            "country": request.args.get("country"),
            "weapon_type": request.args.get("weapon_type"),
        }

        count = int(request.args.get("count", 1))

        # 构建查询
        query = CardData.query.filter(CardData.is_active == True)

        # 应用过滤条件
        query = apply_filters(query, filters)

        # 获取符合条件的所有卡牌
        all_matching_cards = query.all()

        # 随机选择指定数量的卡牌
        selected_cards = random.sample(
            all_matching_cards, min(count, len(all_matching_cards))
        )

        # 转换为标准化格式
        result = [extract_card_info(card) for card in selected_cards]

        return jsonify({"cards": result, "total": len(result)}), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@cards_bp.route("/characters/filters", methods=["GET"])
@jwt_required()
def get_character_filters():
    """
    获取角色的过滤选项（国家、元素、武器类型）
    专为角色选择界面设计
    """
    try:
        # 只查询角色牌
        characters = CardData.query.filter(
            CardData.card_type == "角色牌", CardData.is_active == True
        ).all()

        countries = set()
        elements = set()
        weapon_types = set()

        for character in characters:
            # 提取国家
            region_info = (
                getattr(character, "weapon_type", "")
                or getattr(character, "character_subtype", "")
                or ""
            )
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
                        else json.loads(character.skills)
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
        )
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@cards_bp.route("/cards/search", methods=["GET"])
@jwt_required()
def search_cards():
    """
    搜索卡牌 (保留此路由作为别名，实际功能在 /cards 中已实现)
    """
    return get_all_cards()


@cards_bp.route("/cards/filter", methods=["GET"])
@jwt_required()
def filter_cards_endpoint():
    """
    使用统一过滤参数过滤卡牌
    此接口兼容原有的deck_builder过滤方式，但使用数据库作为数据源
    """
    try:
        # 获取查询参数 (兼容原有接口参数)
        filters = {
            "type": request.args.get("type"),
            "element": request.args.get("element"),
            "country": request.args.get("country"),
            "weapon_type": request.args.get("weapon_type"),
            "character_subtype": request.args.get("character_subtype"),
            "rarity": request.args.get("rarity"),
            "search": request.args.get(
                "search", request.args.get("q", "")
            ),  # 兼容search和q参数
            "tags": request.args.getlist("tag"),  # 支持多个标签
        }

        # 构建查询
        query = CardData.query.filter(CardData.is_active == True)

        # 应用过滤条件
        query = apply_filters(query, filters)

        # 获取所有符合条件的卡牌
        cards = query.all()

        # 转换为标准化格式
        result = [extract_card_info(card) for card in cards]

        return jsonify({"cards": result, "total": len(result)}), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500


# 以下是兼容原deck_builder功能的API端点
@cards_bp.route("/characters", methods=["GET"])
def get_characters():
    """
    兼容原API端点：获取角色牌数据
    """
    try:
        # 查询角色牌
        query = CardData.query.filter(
            CardData.card_type == "角色牌", CardData.is_active == True
        )

        # 分页参数
        page = request.args.get("page", 1, type=int)
        per_page = min(request.args.get("per_page", 20, type=int), 100)

        cards = query.paginate(page=page, per_page=per_page, error_out=False)
        result = [extract_card_info(card) for card in cards.items]

        return jsonify(result), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@cards_bp.route("/equipments", methods=["GET"])
def get_equipments():
    """
    兼容原API端点：获取装备牌数据
    """
    try:
        # 查询装备牌（在数据库中存储为"武器"）
        query = CardData.query.filter(
            CardData.card_type == "武器", CardData.is_active == True
        )

        # 分页参数
        page = request.args.get("page", 1, type=int)
        per_page = min(request.args.get("per_page", 20, type=int), 100)

        cards = query.paginate(page=page, per_page=per_page, error_out=False)
        result = [extract_card_info(card) for card in cards.items]

        return jsonify(result), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@cards_bp.route("/supports", methods=["GET"])
def get_supports():
    """
    兼容原API端点：获取支援牌数据
    """
    try:
        # 查询支援牌
        query = CardData.query.filter(
            CardData.card_type == "支援牌", CardData.is_active == True
        )

        # 分页参数
        page = request.args.get("page", 1, type=int)
        per_page = min(request.args.get("per_page", 20, type=int), 100)

        cards = query.paginate(page=page, per_page=per_page, error_out=False)
        result = [extract_card_info(card) for card in cards.items]

        return jsonify(result), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@cards_bp.route("/events", methods=["GET"])
def get_events():
    """
    兼容原API端点：获取事件牌数据
    """
    try:
        # 查询事件牌
        query = CardData.query.filter(
            CardData.card_type == "事件牌", CardData.is_active == True
        )

        # 分页参数
        page = request.args.get("page", 1, type=int)
        per_page = min(request.args.get("per_page", 20, type=int), 100)

        cards = query.paginate(page=page, per_page=per_page, error_out=False)
        result = [extract_card_info(card) for card in cards.items]

        return jsonify(result), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@cards_bp.route("/decks", methods=["GET"])
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
            result.append(
                {
                    "id": deck.id,
                    "name": deck.name,
                    "description": deck.description,
                    "cards": json.loads(deck.cards) if deck.cards else [],
                    "created_at": deck.created_at.isoformat(),
                    "updated_at": deck.updated_at.isoformat(),
                }
            )

        return jsonify({"decks": result}), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@cards_bp.route("/decks", methods=["POST"])
@jwt_required()
def create_deck():
    """
    创建新的卡组
    """
    try:
        current_user_id = get_jwt_identity()
        data = request.get_json()

        name = data.get("name")
        description = data.get("description", "")
        card_list = data.get("cards", [])

        if not name:
            return jsonify({"error": "卡组名称不能为空"}), 400

        # 使用新的验证系统验证卡组
        # 首先，通过card_ids获取完整卡牌信息
        cards_from_db = CardData.query.filter(CardData.id.in_(card_list)).all()

        # 将数据库中的卡牌数据转换为卡片对象用于验证
        from utils.deck_validator import validate_deck_api

        # 将数据库中的卡片转换为API验证函数需要的格式
        card_data_for_validation = []
        for card in cards_from_db:
            # 根据卡牌类型来决定cost和description的来源
            card_cost = json.loads(card.cost) if card.cost else []
            card_description = card.description or ""

            # 对于非角色牌，尝试从技能中获取cost和description
            if card.card_type != "角色牌":
                if card.skills:
                    try:
                        # 解析skills JSON字符串
                        skills_data = (
                            json.loads(card.skills)
                            if isinstance(card.skills, str)
                            else card.skills
                        )
                        if (
                            skills_data
                            and isinstance(skills_data, list)
                            and len(skills_data) > 0
                        ):
                            first_skill = skills_data[0]
                            if "cost" in first_skill:
                                card_cost = first_skill["cost"]
                            if "description" in first_skill:
                                card_description = first_skill["description"]
                    except (json.JSONDecodeError, TypeError):
                        # 如果解析失败，使用原来的数据
                        pass

            card_data = {
                "id": card.id,
                "name": card.name,
                "card_type": card.card_type,
                "cost": card_cost,
                "description": card_description,
                "character_subtype": card.character_subtype,
            }
            card_data_for_validation.append(card_data)

        # 进行详细验证
        validation_result = validate_deck_api(card_data_for_validation)
        if not validation_result["is_valid"]:
            return jsonify(
                {"error": "卡组验证失败", "details": validation_result["errors"]}
            ), 400

        # 创建卡组
        deck = Deck(
            user_id=current_user_id,
            name=name,
            description=description,
            cards=json.dumps(card_list),
        )

        db.session.add(deck)
        db.session.commit()

        return jsonify(
            {
                "message": "卡组创建成功",
                "deck": {
                    "id": deck.id,
                    "name": deck.name,
                    "description": deck.description,
                    "cards": card_list,
                    "created_at": deck.created_at.isoformat(),
                },
            }
        ), 201
    except Exception as e:
        db.session.rollback()
        return jsonify({"error": str(e)}), 500


@cards_bp.route("/decks/<int:deck_id>", methods=["PUT"])
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
            return jsonify({"error": "卡组不存在或无权限访问"}), 404

        name = data.get("name", deck.name)
        description = data.get("description", deck.description)
        card_list = data.get("cards", json.loads(deck.cards) if deck.cards else [])

        # 使用新的验证系统验证卡组
        # 首先，通过card_ids获取完整卡牌信息
        cards_from_db = CardData.query.filter(CardData.id.in_(card_list)).all()

        # 将数据库中的卡牌数据转换为卡片对象用于验证
        from utils.deck_validator import validate_deck_api

        # 将数据库中的卡片转换为API验证函数需要的格式
        card_data_for_validation = []
        for card in cards_from_db:
            # 根据卡牌类型来决定cost和description的来源
            card_cost = json.loads(card.cost) if card.cost else []
            card_description = card.description or ""

            # 对于非角色牌，尝试从技能中获取cost和description
            if card.card_type != "角色牌":
                if card.skills:
                    try:
                        # 解析skills JSON字符串
                        skills_data = (
                            json.loads(card.skills)
                            if isinstance(card.skills, str)
                            else card.skills
                        )
                        if (
                            skills_data
                            and isinstance(skills_data, list)
                            and len(skills_data) > 0
                        ):
                            first_skill = skills_data[0]
                            if "cost" in first_skill:
                                card_cost = first_skill["cost"]
                            if "description" in first_skill:
                                card_description = first_skill["description"]
                    except (json.JSONDecodeError, TypeError):
                        # 如果解析失败，使用原来的数据
                        pass

            card_data = {
                "id": card.id,
                "name": card.name,
                "card_type": card.card_type,
                "cost": card_cost,
                "description": card_description,
                "character_subtype": card.character_subtype,
            }
            card_data_for_validation.append(card_data)

        # 进行详细验证
        validation_result = validate_deck_api(card_data_for_validation)
        if not validation_result["is_valid"]:
            return jsonify(
                {"error": "卡组验证失败", "details": validation_result["errors"]}
            ), 400

        # 更新卡组
        deck.name = name
        deck.description = description
        deck.cards = json.dumps(card_list)

        db.session.commit()

        return jsonify(
            {
                "message": "卡组更新成功",
                "deck": {
                    "id": deck.id,
                    "name": deck.name,
                    "description": deck.description,
                    "cards": card_list,
                    "updated_at": deck.updated_at.isoformat(),
                },
            }
        ), 200
    except Exception as e:
        db.session.rollback()
        return jsonify({"error": str(e)}), 500


@cards_bp.route("/decks/<int:deck_id>", methods=["DELETE"])
@jwt_required()
def delete_deck(deck_id):
    """
    删除卡组
    """
    try:
        current_user_id = get_jwt_identity()

        deck = Deck.query.filter_by(id=deck_id, user_id=current_user_id).first()
        if not deck:
            return jsonify({"error": "卡组不存在或无权限访问"}), 404

        db.session.delete(deck)
        db.session.commit()

        return jsonify({"message": "卡组删除成功"}), 200
    except Exception as e:
        db.session.rollback()
        return jsonify({"error": str(e)}), 500


@cards_bp.route("/decks/<int:deck_id>", methods=["GET"])
@jwt_required()
def get_deck_by_id(deck_id):
    """
    获取特定卡组详情
    """
    try:
        current_user_id = get_jwt_identity()

        deck = Deck.query.filter_by(id=deck_id, user_id=current_user_id).first()
        if not deck:
            return jsonify({"error": "卡组不存在或无权限访问"}), 404

        # 获取卡组中的卡牌详情
        card_list = json.loads(deck.cards) if deck.cards else []

        # 根据卡ID获取完整的卡牌信息
        cards = CardData.query.filter(CardData.id.in_(card_list)).all()
        card_details = []
        for card in cards:
            # 根据卡牌类型来决定cost和description的来源
            card_cost = json.loads(card.cost) if card.cost else []
            card_description = card.description or ""

            # 对于非角色牌，尝试从技能中获取cost和description
            if card.card_type != "角色牌":
                if card.skills:
                    try:
                        # 解析skills JSON字符串
                        skills_data = (
                            json.loads(card.skills)
                            if isinstance(card.skills, str)
                            else card.skills
                        )
                        if (
                            skills_data
                            and isinstance(skills_data, list)
                            and len(skills_data) > 0
                        ):
                            first_skill = skills_data[0]
                            if "cost" in first_skill:
                                card_cost = first_skill["cost"]
                            if "description" in first_skill:
                                card_description = first_skill["description"]
                    except (json.JSONDecodeError, TypeError):
                        # 如果解析失败，使用原来的数据
                        pass

            # 从技能中提取角色信息，模仿deck_builder中的逻辑
            region_info = (
                getattr(card, "weapon_type", "")
                or getattr(card, "character_subtype", "")
                or ""
            )

            # 从region字段提取国家信息
            country = ""
            countries = [
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
            for c in countries:
                if c in region_info:
                    country = c
                    break

            # 从技能中提取元素信息
            element = ""
            if card.skills:
                try:
                    skills_data = (
                        json.loads(card.skills)
                        if isinstance(card.skills, str)
                        else card.skills
                    )
                    if (
                        skills_data
                        and isinstance(skills_data, list)
                        and len(skills_data) > 0
                    ):
                        first_skill = skills_data[0]
                        if "cost" in first_skill:
                            costs = first_skill["cost"]
                            for cost in costs:
                                if isinstance(cost, dict) and "type" in cost:
                                    cost_type = cost["type"]
                                    elements = [
                                        "火",
                                        "水",
                                        "雷",
                                        "草",
                                        "风",
                                        "岩",
                                        "冰",
                                        "物理",
                                    ]
                                    if cost_type in elements:
                                        element = cost_type
                                        break
                                    if "始基力" in cost_type:
                                        if "荒性" in cost_type:
                                            element = "荒性"
                                        elif "芒性" in cost_type:
                                            element = "芒性"
                                elif isinstance(cost, str):
                                    elements = [
                                        "火",
                                        "水",
                                        "雷",
                                        "草",
                                        "风",
                                        "岩",
                                        "冰",
                                        "物理",
                                    ]
                                    if cost in elements:
                                        element = cost
                                        break
                except (json.JSONDecodeError, TypeError):
                    pass

            # 从region字段提取武器类型
            weapon_type = getattr(card, "weapon_type", "") or ""
            weapon_types = ["单手剑", "双手剑", "长柄武器", "弓", "法器", "其他武器"]
            for wt in weapon_types:
                if wt in region_info:
                    weapon_type = wt
                    break

            # 使用与deck_builder一致的结构
            result_card = {
                "id": card.id,
                "name": card.name,
                "type": card.card_type,
                "description": card_description,
                "cost": card_cost,
                "rarity": getattr(card, "rarity", None),
                "element_type": getattr(card, "element_type", None),
                "character_subtype": getattr(card, "character_subtype", None),
                "image_url": getattr(card, "image_url", None),
                "country": country,
                "element": element,
                "weapon_type": weapon_type,
                "skills": json.loads(card.skills) if card.skills else [],
                "title": region_info,
            }

            # 如果是角色卡，添加角色特定的属性
            if card.card_type == "角色牌":
                # 添加角色特定的字段
                result_card["health"] = getattr(card, "health", None)
                result_card["energy"] = getattr(card, "energy", None)

            card_details.append(result_card)

        return jsonify(
            {
                "deck": {
                    "id": deck.id,
                    "name": deck.name,
                    "description": deck.description,
                    "cards": card_details,
                    "created_at": deck.created_at.isoformat(),
                    "updated_at": deck.updated_at.isoformat(),
                }
            }
        ), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@cards_bp.route("/decks/validate", methods=["POST"])
@jwt_required()
def validate_deck():
    """
    验证卡组是否符合规则
    """
    try:
        data = request.get_json()
        card_list = data.get("cards", [])

        # 通过card_ids获取完整卡牌信息
        cards_from_db = CardData.query.filter(CardData.id.in_(card_list)).all()

        # 将数据库中的卡牌数据转换为卡片对象用于验证
        from utils.deck_validator import validate_deck_api

        # 将数据库中的卡片转换为API验证函数需要的格式
        card_data_for_validation = []
        for card in cards_from_db:
            # 根据卡牌类型来决定cost和description的来源
            card_cost = json.loads(card.cost) if card.cost else []
            card_description = card.description or ""

            # 对于非角色牌，尝试从技能中获取cost和description
            if card.card_type != "角色牌":
                if card.skills:
                    try:
                        # 解析skills JSON字符串
                        skills_data = (
                            json.loads(card.skills)
                            if isinstance(card.skills, str)
                            else card.skills
                        )
                        if (
                            skills_data
                            and isinstance(skills_data, list)
                            and len(skills_data) > 0
                        ):
                            first_skill = skills_data[0]
                            if "cost" in first_skill:
                                card_cost = first_skill["cost"]
                            if "description" in first_skill:
                                card_description = first_skill["description"]
                    except (json.JSONDecodeError, TypeError):
                        # 如果解析失败，使用原来的数据
                        pass

            card_data = {
                "id": card.id,
                "name": card.name,
                "card_type": card.card_type,
                "cost": card_cost,
                "description": card_description,
                "character_subtype": card.character_subtype,
            }
            card_data_for_validation.append(card_data)

        # 进行详细验证
        validation_result = validate_deck_api(card_data_for_validation)

        return jsonify(validation_result), 200
    except Exception as e:
        return jsonify(
            {"error": str(e), "is_valid": False, "errors": ["验证过程中发生错误"]}
        ), 500

