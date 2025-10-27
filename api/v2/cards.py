"""
API v2 - 主要卡牌功能
"""
import json
import random
from flask import Blueprint, request, jsonify, g
from flask_jwt_extended import jwt_required
from .utils import get_models, extract_card_info, apply_filters
from utils.logger import get_logger, log_api_call


cards_bp = Blueprint("standardized_cards_v2", __name__)


@cards_bp.route("/cards", methods=["GET"])
@jwt_required()
@log_api_call
def get_all_cards():
    """
    获取卡牌数据 - 支持多种过滤条件和分页
    查询参数:
    - type: 卡牌类型 (角色牌, 事件牌, 武器, 圣遗物, 支援牌, 非角色牌, 行动牌)
    - element: 元素类型
    - country: 国家 (蒙德, 璃月, 稻妻, etc.)
    - weapon_type: 武器类型 (单手剑, 双手剑, etc.)
    - character_subtype: 角色子类型
    - rarity: 稀有度
    - tag: 卡牌标签 (场地, 武器, 圣遗物等，详见 /cards/tags 接口)
    - energy_cost: 元素费用 (0, 1, 2, 3, 其他)
    - search: 搜索关键词 (在名称、描述、类型、子类型、技能中搜索)
    - page: 页码 (默认 1)
    - per_page: 每页数量 (默认 20, 最大 100)
    """
    logger = get_logger(__name__)
    request_id = getattr(g, 'request_id', 'N/A')
    
    logger.info(f"Fetch cards request with filters: {dict(request.args)}, Request-ID: {request_id}")
    
    try:
        # 获取查询参数
        filters = {
            "type": request.args.get("type"),
            "element": request.args.get("element"),
            "country": request.args.get("country"),
            "weapon_type": request.args.get("weapon_type"),
            "character_subtype": request.args.get("character_subtype"),
            "rarity": request.args.get("rarity"),
            "energy_cost": request.args.get("energy_cost"),  # 元素费用过滤
            "search": request.args.get("search"),
            "tags": request.args.getlist("tag"),  # 支持多个标签
        }

        page = request.args.get("page", 1, type=int)
        per_page = min(
            request.args.get("per_page", 20, type=int), 100
        )  # 限制最大每页数量

        logger.info(f"Fetching cards with page: {page}, per_page: {per_page}, Request-ID: {request_id}")

        # 构建查询
        CardData, Deck = get_models()
        query = CardData.query.filter(CardData.is_active == True)

        # 应用过滤条件
        query = apply_filters(query, filters, CardData)

        # 分页
        cards = query.paginate(page=page, per_page=per_page, error_out=False)

        # 转换为标准化格式
        result = [extract_card_info(card) for card in cards.items]
        
        logger.info(f"Successfully fetched {len(result)} cards, Request-ID: {request_id}")

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
        logger.error(f"Failed to fetch cards: {str(e)}, Request-ID: {request_id}")
        return jsonify({"error": str(e)}), 500


@cards_bp.route("/cards/<card_id>", methods=["GET"])
@jwt_required()
@log_api_call
def get_card_by_id(card_id):
    """
    根据ID获取特定卡牌信息
    """
    logger = get_logger(__name__)
    request_id = getattr(g, 'request_id', 'N/A')
    
    logger.info(f"Fetch card by ID: {card_id}, Request-ID: {request_id}")
    
    try:
        CardData, Deck = get_models()
        card = CardData.query.filter_by(id=card_id, is_active=True).first()
        if not card:
            logger.warning(f"Card with ID {card_id} not found, Request-ID: {request_id}")
            return jsonify({"error": "卡牌不存在"}), 404

        card_data = extract_card_info(card)
        logger.info(f"Successfully fetched card: {card.name}, Request-ID: {request_id}")
        return jsonify({"card": card_data}), 200
    except Exception as e:
        logger.error(f"Failed to fetch card {card_id}: {str(e)}, Request-ID: {request_id}")
        return jsonify({"error": str(e)}), 500


@cards_bp.route("/cards/types", methods=["GET"])
@jwt_required()
@log_api_call
def get_card_types():
    """
    获取所有卡牌类型列表
    """
    logger = get_logger(__name__)
    request_id = getattr(g, 'request_id', 'N/A')
    
    logger.info(f"Fetch card types request, Request-ID: {request_id}")
    
    try:
        CardData, Deck = get_models()
        from database_manager import db_manager

        db = db_manager.get_db()
        types = (
            db.session.query(CardData.card_type)
            .filter(CardData.is_active == True)
            .distinct(CardData.card_type)
            .all()
        )
        type_list = [t[0] for t in types if t[0]]
        logger.info(f"Successfully fetched {len(type_list)} card types, Request-ID: {request_id}")
        return jsonify({"types": type_list}), 200
    except Exception as e:
        logger.error(f"Failed to fetch card types: {str(e)}, Request-ID: {request_id}")
        return jsonify({"error": str(e)}), 500


@cards_bp.route("/cards/elements", methods=["GET"])
@jwt_required()
@log_api_call
def get_card_elements():
    """
    获取所有元素类型列表
    """
    logger = get_logger(__name__)
    request_id = getattr(g, 'request_id', 'N/A')
    
    logger.info(f"Fetch card elements request, Request-ID: {request_id}")
    
    try:
        CardData, Deck = get_models()
        from database_manager import db_manager

        db = db_manager.get_db()
        elements = (
            db.session.query(CardData.element_type)
            .filter(CardData.is_active == True)
            .distinct(CardData.element_type)
            .all()
        )
        element_list = [e[0] for e in elements if e[0]]
        logger.info(f"Successfully fetched {len(element_list)} card elements, Request-ID: {request_id}")
        return jsonify({"elements": element_list}), 200
    except Exception as e:
        logger.error(f"Failed to fetch card elements: {str(e)}, Request-ID: {request_id}")
        return jsonify({"error": str(e)}), 500


@cards_bp.route("/cards/countries", methods=["GET"])
@jwt_required()
@log_api_call
def get_card_countries():
    """
    获取所有国家列表
    """
    logger = get_logger(__name__)
    request_id = getattr(g, 'request_id', 'N/A')
    
    logger.info(f"Fetch card countries request, Request-ID: {request_id}")
    
    try:
        CardData, Deck = get_models()
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

        logger.info(f"Successfully fetched {len(countries)} card countries, Request-ID: {request_id}")
        return jsonify({"countries": sorted(list(countries))}), 200
    except Exception as e:
        logger.error(f"Failed to fetch card countries: {str(e)}, Request-ID: {request_id}")
        return jsonify({"error": str(e)}), 500


@cards_bp.route("/cards/weapon_types", methods=["GET"])
@jwt_required()
@log_api_call
def get_weapon_types():
    """
    获取所有武器类型列表
    """
    logger = get_logger(__name__)
    request_id = getattr(g, 'request_id', 'N/A')
    
    logger.info(f"Fetch weapon types request, Request-ID: {request_id}")
    
    try:
        CardData, Deck = get_models()
        from database_manager import db_manager

        db = db_manager.get_db()
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

        logger.info(f"Successfully fetched {len(valid_weapons)} weapon types, Request-ID: {request_id}")
        return jsonify({"weapon_types": sorted(valid_weapons)}), 200
    except Exception as e:
        logger.error(f"Failed to fetch weapon types: {str(e)}, Request-ID: {request_id}")
        return jsonify({"error": str(e)}), 500


@cards_bp.route("/cards/tags", methods=["GET"])
@jwt_required()
@log_api_call
def get_card_tags():
    """
    获取所有卡牌标签 - 用于过滤和搜索
    """
    logger = get_logger(__name__)
    request_id = getattr(g, 'request_id', 'N/A')
    
    logger.info(f"Fetch card tags request, Request-ID: {request_id}")
    
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
                        else (json.loads(card.skills) if isinstance(card.skills, str) else card.skills)
                    )
                    for skill in skills_data:
                        if "description" in skill:
                            desc = skill["description"]
                            for tag in valid_tags:
                                if tag in desc:
                                    tags.add(tag)
                except (json.JSONDecodeError, TypeError):
                    pass

        logger.info(f"Successfully fetched {len(tags)} card tags, Request-ID: {request_id}")
        return jsonify({"tags": sorted(list(tags))}), 200
    except Exception as e:
        logger.error(f"Failed to fetch card tags: {str(e)}, Request-ID: {request_id}")
        return jsonify({"error": str(e)}), 500


@cards_bp.route("/cards/random", methods=["GET"])
@jwt_required()
@log_api_call
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
    logger = get_logger(__name__)
    request_id = getattr(g, 'request_id', 'N/A')
    
    logger.info(f"Fetch random cards request with filters: {dict(request.args)}, Request-ID: {request_id}")
    
    try:
        CardData, Deck = get_models()
        # 获取查询参数
        filters = {
            "type": request.args.get("type"),
            "element": request.args.get("element"),
            "country": request.args.get("country"),
            "weapon_type": request.args.get("weapon_type"),
        }

        count = int(request.args.get("count", 1))
        logger.info(f"Randomly selecting {count} cards, Request-ID: {request_id}")

        # 构建查询
        query = CardData.query.filter(CardData.is_active == True)

        # 应用过滤条件
        query = apply_filters(query, filters, CardData)

        # 获取符合条件的所有卡牌
        all_matching_cards = query.all()

        # 随机选择指定数量的卡牌
        selected_cards = random.sample(
            all_matching_cards, min(count, len(all_matching_cards))
        )

        # 转换为标准化格式
        result = [extract_card_info(card) for card in selected_cards]

        logger.info(f"Successfully fetched {len(result)} random cards, Request-ID: {request_id}")
        return jsonify({"cards": result, "total": len(result)}), 200
    except Exception as e:
        logger.error(f"Failed to fetch random cards: {str(e)}, Request-ID: {request_id}")
        return jsonify({"error": str(e)}), 500


@cards_bp.route("/characters/filters", methods=["GET"])
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
                        else (json.loads(character.skills) if isinstance(character.skills, str) else character.skills)
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
        CardData, Deck = get_models()
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

        # 分页参数
        page = request.args.get("page", 1, type=int)
        per_page = min(request.args.get("per_page", 12, type=int), 100)  # 限制最大每页数量

        # 构建查询
        query = CardData.query.filter(CardData.is_active == True)

        # 应用过滤条件
        query = apply_filters(query, filters, CardData)

        # 分页查询
        paginated_cards = query.paginate(page=page, per_page=per_page, error_out=False)
        result = [extract_card_info(card) for card in paginated_cards.items]

        return jsonify({
            "cards": result,
            "total": paginated_cards.total,
            "pages": paginated_cards.pages,
            "current_page": page
        }), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500