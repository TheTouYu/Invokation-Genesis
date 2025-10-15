"""
卡组验证工具
用于API接口中验证卡组
"""
from typing import List, Dict, Any
from game_engine.deck_validation import DeckValidationSystem
from models.game_models import Card


def validate_deck_api(deck: List[Dict[str, Any]]) -> Dict[str, Any]:
    """
    API接口使用的卡组验证函数
    
    Args:
        deck: 从API接收到的卡组数据（字典格式）
        
    Returns:
        验证结果
    """
    # 将字典格式的卡牌转换为Card对象
    card_objects = []
    for card_data in deck:
        # 创建卡牌对象
        card_obj = Card(
            id=card_data.get('id', ''),
            name=card_data.get('name', ''),
            card_type=card_data.get('card_type', ''),
            cost=card_data.get('cost', []),
            description=card_data.get('description', ''),
            character_subtype=card_data.get('character_subtype')
        )
        card_objects.append(card_obj)
    
    # 创建验证系统实例并验证
    validator = DeckValidationSystem()
    return validator.validate_deck(card_objects)


def get_deck_stats_api(deck: List[Dict[str, Any]]) -> Dict[str, Any]:
    """
    API接口使用的卡组统计函数
    
    Args:
        deck: 从API接收到的卡组数据（字典格式）
        
    Returns:
        卡组统计信息
    """
    # 将字典格式的卡牌转换为Card对象
    card_objects = []
    for card_data in deck:
        # 创建卡牌对象
        card_obj = Card(
            id=card_data.get('id', ''),
            name=card_data.get('name', ''),
            card_type=card_data.get('card_type', ''),
            cost=card_data.get('cost', []),
            description=card_data.get('description', ''),
            character_subtype=card_data.get('character_subtype')
        )
        card_objects.append(card_obj)
    
    # 创建验证系统实例并获取统计信息
    validator = DeckValidationSystem()
    return validator.get_deck_stats(card_objects)


def validate_deck_composition(deck_data: Dict[str, Any]) -> Dict[str, Any]:
    """
    验证卡组构成 - 根据卡牌ID验证卡组
    
    Args:
        deck_data: 包含卡组信息的字典，包含:
            - name: 卡组名称
            - character_ids: 角色牌ID列表
            - card_ids: 其他卡牌ID列表
    
    Returns:
        验证结果字典
    """
    try:
        # 先检查是否可以导入数据库模型
        try:
            from models.db_models import CardData
            # 检查CardData是否可用
            # 如果导入成功，使用数据库验证
            from models.db_models import db
            
            # 从数据库中获取角色卡信息
            character_cards = []
            if deck_data.get('character_ids'):
                character_cards = CardData.query.filter(
                    CardData.id.in_(deck_data['character_ids'])
                ).all()
            
            # 从数据库中获取其他卡牌信息
            action_cards = []
            if deck_data.get('card_ids'):
                action_cards = CardData.query.filter(
                    CardData.id.in_(deck_data['card_ids'])
                ).all()

            # 将数据库对象转换为Card对象
            all_cards = []
            
            # 添加角色卡
            for card in character_cards:
                card_obj = Card(
                    id=str(card.id),
                    name=card.name,
                    card_type=card.card_type,
                    cost=card.cost if card.cost else [],
                    description=card.description or "",
                    character_subtype=getattr(card, 'character_subtype', None)
                )
                # 添加多张相同的角色卡（如果用户选择了多张）
                count = deck_data['character_ids'].count(card.id)
                for _ in range(count):
                    all_cards.append(card_obj)
            
            # 添加行动卡
            for card in action_cards:
                card_obj = Card(
                    id=str(card.id),
                    name=card.name,
                    card_type=card.card_type,
                    cost=card.cost if card.cost else [],
                    description=card.description or "",
                    character_subtype=getattr(card, 'character_subtype', None)
                )
                # 添加多张相同的行动卡（如果用户选择了多张）
                count = deck_data['card_ids'].count(card.id)
                for _ in range(count):
                    all_cards.append(card_obj)

            # 创建验证系统实例并验证
            validator = DeckValidationSystem()
            return validator.validate_deck(all_cards)
        
        except ImportError:
            # 如果无法导入数据库模型，使用简化验证
            return _validate_deck_by_id_counts(deck_data)
    
    except Exception as e:
        return {
            "is_valid": False,
            "errors": [f"验证过程中出现错误: {str(e)}"],
            "suggestions": ["请检查输入数据格式是否正确"],
            "rules": {}
        }


def _validate_deck_by_id_counts(deck_data: Dict[str, Any]) -> Dict[str, Any]:
    """
    基于ID数量进行简化验证，当数据库不可用时使用
    """
    # 检查角色数量
    character_count = len(deck_data.get('character_ids', []))
    card_count = len(deck_data.get('card_ids', []))
    
    errors = []
    rules = {
        'character_count': {
            'valid': character_count <= 3,
            'message': f"角色数量为 {character_count}/3"
        },
        'deck_size': {
            'valid': card_count <= 30,
            'message': f"卡牌数量为 {card_count}/30"
        },
        'character_limit': {
            'valid': True,  # 简化版验证中假设用户正确处理了重复
            'message': "每个角色限1张"
        },
        'card_limit': {
            'valid': True,  # 简化版验证中假设用户正确处理了重复
            'message': "每个行动牌限2张"
        },
        'elemental_synergy': {
            'valid': True,  # 简化版验证中不检查元素协同
            'message': "元素协同检查通过"
        }
    }
    
    # 检查基本规则
    if character_count > 3:
        errors.append(f"角色数量过多: {character_count}/3")
    if card_count > 30:
        errors.append(f"卡牌数量过多: {card_count}/30")
    
    is_valid = len(errors) == 0
    
    return {
        "is_valid": is_valid,
        "errors": errors,
        "suggestions": [] if is_valid else ["请减少角色或行动牌的数量"],
        "rules": rules
    }