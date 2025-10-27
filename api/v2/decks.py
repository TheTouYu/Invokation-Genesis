"""
API v2 - 卡组功能
"""
import json
from flask import Blueprint, request, jsonify, g
from flask_jwt_extended import jwt_required, get_jwt_identity
from dal import db_dal
from .utils import get_models, extract_card_info
from utils.logger import get_logger, log_api_call


decks_bp = Blueprint("decks_v2", __name__)


@decks_bp.route("/decks", methods=["GET"])
@jwt_required()
@log_api_call
def get_user_decks():
    """
    获取当前用户的所有卡组
    """
    logger = get_logger(__name__)
    request_id = getattr(g, 'request_id', 'N/A')
    
    logger.info(f"Fetching user decks request, Request-ID: {request_id}")
    
    try:
        current_user_id = get_jwt_identity()

        decks = db_dal.decks.get_decks_by_user(current_user_id)

        result = []
        for deck in decks:
            result.append(
                {
                    "id": deck.id,
                    "name": deck.name,
                    "description": deck.description,
                    "cards": deck.cards if deck.cards else [],
                    "created_at": deck.created_at.isoformat(),
                    "updated_at": deck.updated_at.isoformat(),
                }
            )
        
        logger.info(f"Successfully fetched {len(result)} decks for user {current_user_id}, Request-ID: {request_id}")

        return jsonify({"decks": result}), 200
    except Exception as e:
        logger.error(f"Failed to fetch user decks: {str(e)}, Request-ID: {request_id}")
        return jsonify({"error": str(e)}), 500


@decks_bp.route("/decks", methods=["POST"])
@jwt_required()
@log_api_call
def create_deck():
    """
    创建新的卡组
    """
    logger = get_logger(__name__)
    request_id = getattr(g, 'request_id', 'N/A')
    
    logger.info(f"Create deck request, Request-ID: {request_id}")
    
    try:
        CardData, Deck = get_models()
        current_user_id = get_jwt_identity()
        data = request.get_json()

        name = data.get("name")
        description = data.get("description", "")
        card_list = data.get("cards", [])

        if not name:
            logger.warning(f"Create deck request missing name, Request-ID: {request_id}")
            return jsonify({"error": "卡组名称不能为空"}), 400

        # 使用新的验证系统验证卡组
        # 首先，通过card_ids获取完整卡牌信息
        # Note: For now, we'll continue using direct query for card validation to avoid breaking existing validation logic
        cards_from_db = CardData.query.filter(CardData.id.in_(card_list)).all()

        # 将数据库中的卡牌数据转换为卡片对象用于验证
        from utils.deck_validator import validate_deck_api

        # 将数据库中的卡片转换为API验证函数需要的格式
        card_data_for_validation = []
        for card in cards_from_db:
            # 根据卡牌类型来决定cost和description的来源
            card_cost = (json.loads(card.cost) if card.cost and isinstance(card.cost, str) else (card.cost if card.cost else []))
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

        logger.info(f"Validating deck with {len(card_list)} cards, Request-ID: {request_id}")
        
        # 进行详细验证
        validation_result = validate_deck_api(card_data_for_validation)
        if not validation_result["is_valid"]:
            logger.warning(f"Deck validation failed: {validation_result['errors']}, Request-ID: {request_id}")
            return jsonify(
                {"error": "卡组验证失败", "details": validation_result["errors"]}
            ), 400

        # 创建卡组 using the data access layer
        try:
            deck = db_dal.decks.create_deck(
                name=name,
                user_id=current_user_id,
                cards=card_list,
                description=description,
            )

            logger.info(f"Successfully created deck {deck.id} for user {current_user_id}, Request-ID: {request_id}")
            
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
            logger.error(f"Failed to create deck: {str(e)}, Request-ID: {request_id}")
            return jsonify({"error": f"创建卡组失败: {str(e)}"}), 500

    except Exception as e:
        logger.error(f"Create deck request failed with error: {str(e)}, Request-ID: {request_id}")
        return jsonify({"error": str(e)}), 500


@decks_bp.route("/decks/<string:deck_id>", methods=["PUT"])
@jwt_required()
@log_api_call
def update_deck(deck_id):
    """
    更新卡组
    """
    logger = get_logger(__name__)
    request_id = getattr(g, 'request_id', 'N/A')
    
    logger.info(f"Update deck request for deck {deck_id}, Request-ID: {request_id}")
    
    try:
        CardData, Deck = get_models()
        current_user_id = get_jwt_identity()
        data = request.get_json()

        deck = db_dal.decks.get_deck_by_id(deck_id)
        if not deck or deck.user_id != current_user_id:
            logger.warning(f"Attempt to update non-existent or unauthorized deck {deck_id}, Request-ID: {request_id}")
            return jsonify({"error": "卡组不存在或无权限访问"}), 404

        name = data.get("name", deck.name)
        description = data.get("description", deck.description)
        card_list = data.get(
            "cards", (json.loads(deck.cards) if deck.cards and isinstance(deck.cards, str) else (deck.cards if deck.cards else []))
        )

        # 使用新的验证系统验证卡组
        # 首先，通过card_ids获取完整卡牌信息
        cards_from_db = CardData.query.filter(
            CardData.id.in_(card_list)
        ).all()  # Still using direct query for validation

        # 将数据库中的卡牌数据转换为卡片对象用于验证
        from utils.deck_validator import validate_deck_api

        # 将数据库中的卡片转换为API验证函数需要的格式
        card_data_for_validation = []
        for card in cards_from_db:
            # 根据卡牌类型来决定cost和description的来源
            card_cost = (json.loads(card.cost) if card.cost and isinstance(card.cost, str) else (card.cost if card.cost else []))
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

        logger.info(f"Validating deck with {len(card_list)} cards for update, Request-ID: {request_id}")
        
        # 进行详细验证
        validation_result = validate_deck_api(card_data_for_validation)
        if not validation_result["is_valid"]:
            logger.warning(f"Deck validation failed for update: {validation_result['errors']}, Request-ID: {request_id}")
            return jsonify(
                {"error": "卡组验证失败", "details": validation_result["errors"]}
            ), 400

        # 更新卡组 using data access layer
        success = db_dal.decks.update_deck(
            deck_id=deck_id, name=name, description=description, card_ids=card_list
        )

        if not success:
            logger.error(f"Failed to update deck {deck_id}, Request-ID: {request_id}")
            return jsonify({"error": "更新卡组失败"}), 500

        updated_deck = db_dal.decks.get_deck_by_id(deck_id)
        
        logger.info(f"Successfully updated deck {deck_id}, Request-ID: {request_id}")
        
        return jsonify(
            {
                "message": "卡组更新成功",
                "deck": {
                    "id": updated_deck.id,
                    "name": updated_deck.name,
                    "description": updated_deck.description,
                    "cards": json.loads(updated_deck.cards) if updated_deck.cards and isinstance(updated_deck.cards, str) else (updated_deck.cards if updated_deck.cards else [])
                    if updated_deck.cards
                    else [],
                    "created_at": updated_deck.created_at.isoformat(),
                    "updated_at": updated_deck.updated_at.isoformat(),
                },
            }
        ), 200
    except Exception as e:
        logger.error(f"Update deck request failed with error: {str(e)}, Request-ID: {request_id}")
        return jsonify({"error": str(e)}), 500


@decks_bp.route("/decks/<string:deck_id>", methods=["DELETE"])
@jwt_required()
@log_api_call
def delete_deck(deck_id):
    """
    删除卡组
    """
    logger = get_logger(__name__)
    request_id = getattr(g, 'request_id', 'N/A')
    
    logger.info(f"Delete deck request for deck {deck_id}, Request-ID: {request_id}")
    
    try:
        current_user_id = get_jwt_identity()

        deck = db_dal.decks.get_deck_by_id(deck_id)
        if not deck or deck.user_id != current_user_id:
            logger.warning(f"Attempt to delete non-existent or unauthorized deck {deck_id}, Request-ID: {request_id}")
            return jsonify({"error": "卡组不存在或无权限访问"}), 404

        success = db_dal.decks.delete_deck(deck_id)

        if not success:
            logger.error(f"Failed to delete deck {deck_id}, Request-ID: {request_id}")
            return jsonify({"error": "删除卡组失败"}), 500

        logger.info(f"Successfully deleted deck {deck_id}, Request-ID: {request_id}")
        
        return jsonify({"message": "卡组删除成功"}), 200
    except Exception as e:
        logger.error(f"Delete deck request failed with error: {str(e)}, Request-ID: {request_id}")
        return jsonify({"error": str(e)}), 500


@decks_bp.route("/decks/<string:deck_id>", methods=["GET"])
@jwt_required()
@log_api_call
def get_deck_by_id(deck_id):
    """
    获取特定卡组详情
    """
    logger = get_logger(__name__)
    request_id = getattr(g, 'request_id', 'N/A')
    
    logger.info(f"Fetch specific deck request for deck {deck_id}, Request-ID: {request_id}")
    
    try:
        CardData, Deck = get_models()
        current_user_id = get_jwt_identity()

        deck = db_dal.decks.get_deck_by_id(deck_id)
        if not deck or deck.user_id != current_user_id:
            logger.warning(f"Attempt to access non-existent or unauthorized deck {deck_id}, Request-ID: {request_id}")
            return jsonify({"error": "卡组不存在或无权限访问"}), 404

        # 获取卡组中的卡牌详情
        card_list = (json.loads(deck.cards) if deck.cards and isinstance(deck.cards, str) else (deck.cards if deck.cards else []))

        # 根据卡ID获取完整的卡牌信息
        cards_query = CardData.query.filter(CardData.id.in_(card_list)).all()
        card_details = []
        for card in (
            cards_query
        ):  # Note: This still uses direct query to avoid changing too much at once
            # 根据卡牌类型来决定cost和description的来源
            card_cost = (json.loads(card.cost) if card.cost and isinstance(card.cost, str) else (card.cost if card.cost else []))
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
                "skills": card.skills if card.skills else [],
                "title": region_info,
            }

            # 如果是角色卡，添加角色特定的属性
            if card.card_type == "角色牌":
                # 添加角色特定的字段
                result_card["health"] = getattr(card, "health", None)
                result_card["energy"] = getattr(card, "energy", None)

            card_details.append(result_card)

        logger.info(f"Successfully fetched deck {deck_id} with {len(card_details)} cards, Request-ID: {request_id}")
        
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
        logger.error(f"Fetch specific deck request failed with error: {str(e)}, Request-ID: {request_id}")
        return jsonify({"error": str(e)}), 500


@decks_bp.route("/decks/validate", methods=["POST"])
@jwt_required()
@log_api_call
def validate_deck():
    """
    验证卡组是否符合规则
    """
    logger = get_logger(__name__)
    request_id = getattr(g, 'request_id', 'N/A')
    
    logger.info(f"Validate deck request with {len(request.get_json().get('cards', []))} cards, Request-ID: {request_id}")
    
    try:
        CardData, Deck = get_models()
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
            card_cost = (json.loads(card.cost) if card.cost and isinstance(card.cost, str) else (card.cost if card.cost else []))
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

        logger.info(f"Validating deck with {len(card_list)} cards, Request-ID: {request_id}")
        
        # 进行详细验证
        validation_result = validate_deck_api(card_data_for_validation)

        logger.info(f"Deck validation completed with result: {validation_result['is_valid']}, Request-ID: {request_id}")
        
        return jsonify(validation_result), 200
    except Exception as e:
        logger.error(f"Deck validation failed with error: {str(e)}, Request-ID: {request_id}")
        return jsonify(
            {"error": str(e), "is_valid": False, "errors": ["验证过程中发生错误"]}
        ), 500