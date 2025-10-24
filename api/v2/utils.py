"""
API v2模块的通用工具函数
"""
import json
from flask import jsonify
from sqlalchemy import or_
from typing import Dict, Any
from models.db_models import model_container


def get_models():
    """获取数据库模型"""
    return model_container.CardData, model_container.Deck


def extract_card_info(card) -> Dict[str, Any]:
    """
    从CardData对象中提取标准化的卡牌信息
    统一处理所有卡牌类型的数据格式
    """
    # 处理cost字段 - 优先从技能中提取，否则使用card.cost
    card_cost = card.cost if card.cost else []
    # If card.cost is a string (from legacy storage), parse it; otherwise it's already a Python object from JSON field
    if isinstance(card_cost, str):
        try:
            card_cost = (json.loads(card.cost) if card.cost and isinstance(card.cost, str) else (card.cost if card.cost else []))
        except json.JSONDecodeError:
            card_cost = []
    elif card_cost is None:
        card_cost = []

    # 对于非角色牌，尝试从技能中获取cost和description
    card_description = card.description or ""
    if card.card_type != "角色牌" and card.skills:
        try:
            # card.skills from JSON field is already a Python object, not a string
            skills_data = card.skills if isinstance(card.skills, list) else (json.loads(card.skills) if isinstance(card.skills, str) else [])
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
                # card.skills from JSON field is already a Python object, not a string
                skills_data = card.skills if isinstance(card.skills, list) else (json.loads(card.skills) if isinstance(card.skills, str) else [])
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
            except (json.JSONDecodeError, TypeError):
                pass

    # 提取武器类型和国家信息需要region_info
    # For character cards, character_subtype often contains element/country info, so check that first
    character_subtype_val = getattr(card, "character_subtype", "") or ""
    weapon_type_val = getattr(card, "weapon_type", "") or ""
    
    # Use character_subtype first, then weapon_type as fallback
    region_info = character_subtype_val or weapon_type_val
    
    # 提取国家信息 - now using the stored country field
    country = getattr(card, "country", "") or ""

    # 从技能中提取元素信息
    element = card.element_type or ""
    if not element and card.skills:
        try:
            # card.skills from JSON field is already a Python object, not a string
            skills_data = card.skills if isinstance(card.skills, list) else (json.loads(card.skills) if isinstance(card.skills, str) else [])
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

    # 提取武器类型 - now using the stored weapon_type field
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
        "skills": card.skills if card.skills else [],
        "title": region_info if isinstance(region_info, str) else "",
    }

    # 为角色牌添加额外属性
    if card.card_type == "角色牌":
        card_data.update(
            {
                "health": getattr(card, "health", None),
                "energy": getattr(card, "energy", None),
                "health_max": getattr(card, "health_max", None),
                "energy_max": getattr(card, "energy_max", None),
            }
        )

    return card_data


def apply_filters(query, filters: Dict[str, Any], CardData):
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
    energy_cost = filters.get("energy_cost")  # 元素费用过滤

    # 应用基础过滤条件
    if card_type:
        if card_type == "非角色牌":
            query = query.filter(CardData.card_type != "角色牌")
        elif card_type == "行动牌":
            # 行动牌通常指非角色牌，在这里我们将其视为非角色牌的别名
            query = query.filter(CardData.card_type != "角色牌")
        else:
            query = query.filter(CardData.card_type == card_type)

    if element:
        query = query.filter(CardData.element_type == element)

    if character_subtype:
        query = query.filter(CardData.character_subtype == character_subtype)

    if rarity is not None:
        query = query.filter(CardData.rarity == int(rarity))

    # 应用国家过滤 - 现在直接使用country字段
    if country:
        query = query.filter(CardData.country == country)

    # 应用武器类型过滤
    if weapon_type:
        query = query.filter(CardData.weapon_type == weapon_type)

    # 应用标签过滤功能  
    if tags:
        for tag in tags:
            # 由于skills是JSON字段，将其转换为TEXT进行搜索
            from database_manager import db_manager
            db = db_manager.get_db()
            query = query.filter(
                or_(
                    CardData.card_type.contains(tag),
                    CardData.character_subtype.contains(tag),
                    CardData.description.contains(tag),
                    db.cast(CardData.skills, db.Text).contains(tag)  # 将JSON字段转换为文本进行搜索
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

    # 应用元素费用过滤 - 根据技能中的cost字段过滤
    if energy_cost is not None:
        # 将能量费用转换为整数
        try:
            energy_value = int(energy_cost)
            from database_manager import db_manager
            db = db_manager.get_db()
            
            # 更智能地搜索技能中的费用信息
            if energy_value >= 0 and energy_value <= 3:
                # 查找需要特定数量充能的卡牌
                # 我们需要在JSON字段中搜索特定的费用值
                query = query.filter(
                    db.cast(CardData.skills, db.Text).like(f'%"{energy_value}"%')
                )
            elif energy_cost == "其他":
                # 查找非标准费用的卡牌
                query = query.filter(
                    or_(
                        db.cast(CardData.skills, db.Text).notlike('%"value": 0%'),
                        db.cast(CardData.skills, db.Text).notlike('%"value": 1%'),
                        db.cast(CardData.skills, db.Text).notlike('%"value": 2%'),
                        db.cast(CardData.skills, db.Text).notlike('%"value": 3%')
                    )
                )
        except ValueError:
            # 如果不是数字，则按文本搜索
            if energy_cost == "充能":
                from database_manager import db_manager
                db = db_manager.get_db()
                query = query.filter(
                    db.cast(CardData.skills, db.Text).like('%充能%')
                )
            pass  # 忽略无效的能量费用值

    return query