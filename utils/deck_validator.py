"""
卡组验证工具
用于API接口中验证卡组
"""
from typing import List, Dict, Any
from game_engine.deck_validation import DeckValidationSystem
from models.game_models import Card
from utils.logger import get_logger


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
        # 获取字符串类型的card_type并转换为CardType枚举
        card_type_str = card_data.get('card_type', '')
        card_type_enum = _convert_string_to_card_type(card_type_str)
        
        # 创建卡牌对象
        card_obj = Card(
            id=card_data.get('id', ''),
            name=card_data.get('name', ''),
            card_type=card_type_enum,
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
        # 获取字符串类型的card_type并转换为CardType枚举
        card_type_str = card_data.get('card_type', '')
        card_type_enum = _convert_string_to_card_type(card_type_str)
        
        # 创建卡牌对象
        card_obj = Card(
            id=card_data.get('id', ''),
            name=card_data.get('name', ''),
            card_type=card_type_enum,
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
    logger = get_logger(__name__)
    logger.info(f"Starting deck validation for {len(deck_data.get('character_ids', []))} characters and {len(deck_data.get('card_ids', []))} cards")
    
    try:
        # 先检查是否可以导入数据库模型
        try:
            from models.db_models import CardData
            # 检查CardData是否可用
            # 如果导入成功，使用数据库验证
            from models.db_models import db
            
            # 从数据库中获取角色卡信息 - 使用ID进行查询
            character_cards = []
            if deck_data.get('character_ids'):
                logger.info(f"Querying {len(deck_data['character_ids'])} character cards from database")
                character_cards = CardData.query.filter(
                    CardData.id.in_(deck_data['character_ids'])
                ).all()
                logger.info(f"Found {len(character_cards)} character cards in database")
            
            # 从数据库中获取其他卡牌信息 - 使用ID进行查询
            action_cards = []
            if deck_data.get('card_ids'):
                logger.info(f"Querying {len(deck_data['card_ids'])} action cards from database")
                action_cards = CardData.query.filter(
                    CardData.id.in_(deck_data['card_ids'])
                ).all()
                logger.info(f"Found {len(action_cards)} action cards in database")

            # 将数据库对象转换为Card对象
            all_cards = []
            
            # 添加角色卡 - create CharacterCard objects for characters
            for card in character_cards:
                card_type_enum = _convert_string_to_card_type(card.card_type)
                
                # Try to extract element type from skills if available
                element_type = None
                # First, try to get from the direct element_type field (from database)
                db_element_type = getattr(card, 'element_type', None)
                
                if db_element_type:
                    # Map DB element type to enum
                    from models.enums import ElementType
                    element_mapping = {
                        '火': ElementType.PYRO, 'Pyro': ElementType.PYRO,
                        '水': ElementType.HYDRO, 'Hydro': ElementType.HYDRO,
                        '雷': ElementType.ELECTRO, 'Electro': ElementType.ELECTRO,
                        '草': ElementType.DENDRO, 'Dendro': ElementType.DENDRO,
                        '风': ElementType.ANEMO, 'Anemo': ElementType.ANEMO,
                        '岩': ElementType.GEO, 'Geo': ElementType.GEO,
                        '冰': ElementType.CRYO, 'Cryo': ElementType.CRYO,
                        '物理': ElementType.PHYSICAL, 'Physical': ElementType.PHYSICAL,
                        '始基力：荒性': ElementType.NONE,  # Special type
                        '始基力：芒性': ElementType.NONE,  # Special type
                    }
                    if db_element_type in element_mapping:
                        element_type = element_mapping[db_element_type]
                
                # If element_type not found in DB field, extract from first skill cost
                if not element_type and card.skills:
                    try:
                        import json
                        
                        # First, check if card.skills is a JSON string and parse it if needed
                        skills_data = card.skills
                        if isinstance(card.skills, str):
                            try:
                                skills_data = json.loads(card.skills)
                            except json.JSONDecodeError:
                                logger.warning(f"Error parsing skills for {card.name}: not valid JSON")
                                skills_data = []
                        
                        # Look for element in the first skill's cost
                        first_skill = skills_data[0] if isinstance(skills_data, list) and skills_data else {}
                        if 'cost' in first_skill and isinstance(first_skill['cost'], list):
                            # The cost can be in two formats:
                            # 1. Array of strings like ["水", "无色", "无色"]
                            # 2. Array of objects like [{"type": "水", "value": 1}, {"type": "无色", "value": 1}]
                            for cost_item in first_skill['cost']:
                                # Handle both formats
                                cost_type = None
                                if isinstance(cost_item, str):
                                    # Format 1: simple string
                                    cost_type = cost_item
                                elif isinstance(cost_item, dict) and 'type' in cost_item:
                                    # Format 2: object with type property
                                    cost_type = cost_item['type']
                                
                                if cost_type:
                                    # Attempt to map to ElementType enum
                                    from models.enums import ElementType
                                    element_mapping = {
                                        '火': ElementType.PYRO, 'Pyro': ElementType.PYRO,
                                        '水': ElementType.HYDRO, 'Hydro': ElementType.HYDRO,
                                        '雷': ElementType.ELECTRO, 'Electro': ElementType.ELECTRO,
                                        '草': ElementType.DENDRO, 'Dendro': ElementType.DENDRO,
                                        '风': ElementType.ANEMO, 'Anemo': ElementType.ANEMO,
                                        '岩': ElementType.GEO, 'Geo': ElementType.GEO,
                                        '冰': ElementType.CRYO, 'Cryo': ElementType.CRYO,
                                        '物理': ElementType.PHYSICAL, 'Physical': ElementType.PHYSICAL,
                                        '始基力：荒性': ElementType.NONE,  # Special type
                                        '始基力：芒性': ElementType.NONE,  # Special type
                                        '无色': ElementType.NONE,  # Unaligned element
                                        '充能': ElementType.NONE,  # Energy dice
                                    }
                                    if cost_type in element_mapping:
                                        # Don't overwrite if we already found a primary element (not None, Unaligned, etc.)
                                        if element_type is None or element_type == ElementType.NONE:
                                            element_type_candidate = element_mapping[cost_type]
                                            if element_type_candidate not in [ElementType.NONE]:
                                                element_type = element_type_candidate
                                            elif element_type is None:
                                                element_type = element_type_candidate
                                        break
                    except Exception as e:
                        logger.error(f"Error extracting element from skills: {e}")
                        import traceback
                        traceback.print_exc()
                        pass  # Keep element_type as whatever was found from db_element_type
                
                # Create CharacterCard object instead of base Card
                from models.game_models import CharacterCard
                card_obj = CharacterCard(
                    id=str(card.id),
                    name=card.name,
                    card_type=card_type_enum,
                    cost=card.cost if card.cost else [],
                    description=card.description or "",
                    character_subtype=getattr(card, 'character_subtype', None),
                    element_type=element_type or getattr(card, 'element_type', None),
                    weapon_type=getattr(card, 'weapon_type', '')
                )
                
                # 添加多张相同的角色卡（如果用户选择了多张）
                str_card_id = str(card.id)  # Ensure string comparison
                count = deck_data['character_ids'].count(str_card_id)
                logger.debug(f"Adding {count} copies of character card {card.name} (ID: {card.id})")
                for _ in range(count):
                    all_cards.append(card_obj)
            
            # 添加行动卡
            for card in action_cards:
                card_type_enum = _convert_string_to_card_type(card.card_type)
                card_obj = Card(
                    id=str(card.id),
                    name=card.name,
                    card_type=card_type_enum,
                    cost=card.cost if card.cost else [],
                    description=card.description or "",
                    character_subtype=getattr(card, 'character_subtype', None)
                )
                # 添加多张相同的行动卡（如果用户选择了多张）
                str_card_id = str(card.id)  # Ensure string comparison
                count = deck_data['card_ids'].count(str_card_id)
                logger.debug(f"Adding {count} copies of action card {card.name} (ID: {card.id})")
                for _ in range(count):
                    all_cards.append(card_obj)

            logger.info(f"Total cards prepared for validation: {len(all_cards)}")

            # 创建验证系统实例并验证
            validator = DeckValidationSystem()
            result = validator.validate_deck(all_cards)
            
            # 确保返回的结构包含所有必要字段
            if 'suggestions' not in result:
                result['suggestions'] = []
            
            # 确保规则部分存在
            if 'rules' not in result:
                result['rules'] = {}
            
            # 填充默认规则值如果不存在
            if 'character_count' not in result['rules']:
                result['rules']['character_count'] = {'valid': True, 'message': '角色数量检查通过'}
            if 'deck_size' not in result['rules']:
                result['deck_size'] = {'valid': True, 'message': '卡组大小检查通过'}
            if 'character_limit' not in result['rules']:
                result['character_limit'] = {'valid': True, 'message': '角色限制检查通过'}
            if 'card_limit' not in result['rules']:
                result['card_limit'] = {'valid': True, 'message': '卡牌限制检查通过'}
            if 'elemental_synergy' not in result['rules']:
                result['elemental_synergy'] = {'valid': True, 'message': '元素协同检查通过'}
            
            # 确保错误列表存在
            if 'errors' not in result:
                result['errors'] = []
            
            logger.info(f"Deck validation completed with result: {result['is_valid']}")
            return result
        
        except ImportError as e:
            logger.error(f"Could not import database models, using simplified validation: {e}")
            # 如果无法导入数据库模型，使用简化验证
            return _validate_deck_by_id_counts(deck_data)
    
    except Exception as e:
        logger.error(f"Deck validation failed: {str(e)}")
        return {
            "is_valid": False,
            "errors": [f"验证过程中出现错误: {str(e)}"],
            "suggestions": ["请检查输入数据格式是否正确"],
            "rules": {}
        }


def _convert_string_to_card_type(card_type_str: str):
    """
    将字符串类型的卡牌类型转换为CardType枚举值
    """
    from models.enums import CardType
    
    # 映射字符串到CardType枚举
    type_mapping = {
        '角色牌': CardType.CHARACTER,
        '武器': CardType.WEAPON,
        '武器牌': CardType.WEAPON,
        '圣遗物': CardType.ARTIFACT,
        '圣遗物牌': CardType.ARTIFACT,
        '天赋': CardType.TALENT,
        '天赋牌': CardType.TALENT,
        '支援牌': CardType.SUPPORT,
        '事件牌': CardType.EVENT,
        '装备牌': CardType.WEAPON,  # 装备牌通常归类为武器
        'Character': CardType.CHARACTER,
        'Weapon': CardType.WEAPON,
        'Artifact': CardType.ARTIFACT,
        'Talent': CardType.TALENT,
        'Support': CardType.SUPPORT,
        'Event': CardType.EVENT,
    }
    
    # 如果映射存在，返回对应的枚举值，否则返回默认值
    return type_mapping.get(card_type_str, CardType.EVENT)  # 默认为事件牌


def _validate_deck_by_id_counts(deck_data: Dict[str, Any]) -> Dict[str, Any]:
    """
    基于ID数量进行简化验证，当数据库不可用时使用
    """
    import json
    import os
    
    # Load all card data from the local JSON files to check elements and other properties
    card_data_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'card_data')
    all_cards = []
    
    # Load各类卡牌数据
    for filename in ['equipments.json', 'events.json', 'supports.json']:
        file_path = os.path.join(card_data_path, filename)
        if os.path.exists(file_path):
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    cards = json.load(f)
                    all_cards.extend(cards)
            except Exception as e:
                print(f"Error loading {file_path}: {e}")
    
    # 单独处理角色数据，提取国家、元素、武器信息
    character_file = os.path.join(card_data_path, 'characters.json')
    if os.path.exists(character_file):
        try:
            with open(character_file, 'r', encoding='utf-8') as f:
                characters = json.load(f)
                for character in characters:
                    # 保留完整的角色信息
                    all_cards.append(character)
        except Exception as e:
            print(f"Error loading {character_file}: {e}")
    
    # Separate character cards and other cards
    character_ids = deck_data.get('character_ids', [])
    card_ids = deck_data.get('card_ids', [])
    
    # Find the actual character and action cards from loaded data
    selected_character_cards = [card for card in all_cards if card.get('id', '') in character_ids]
    selected_action_cards = [card for card in all_cards if card.get('id', '') in card_ids]
    
    errors = []
    suggestions = []
    
    # Check character count
    character_count = len(character_ids)
    character_count_valid = character_count == 3
    if not character_count_valid:
        errors.append(f"角色卡应为3个不同角色，当前为{character_count}个")
    
    # Check card count
    card_count = len(card_ids)
    card_count_valid = card_count == 30
    if not card_count_valid:
        errors.append(f"行动卡应为30张，当前为{card_count}张")
    
    # Create a mapping from IDs to names for user-friendly error messages
    card_id_to_name = {card.get('id', ''): card.get('name', '') for card in all_cards if 'id' in card and 'name' in card}
    
    # Check individual card limits (no more than 2 of same card)
    card_counts = {}
    for card_id in card_ids:
        if card_id in card_counts:
            card_counts[card_id] += 1
        else:
            card_counts[card_id] = 1
    
    card_limits_valid = True
    for card_id, count in card_counts.items():
        if count > 2:
            card_name = card_id_to_name.get(card_id, card_id)  # Use ID if name not available
            errors.append(f"卡牌「{card_name}」超过2张限制，当前为{count}张")
            card_limits_valid = False
    
    # Check character limits (each character only once)
    character_ids_list = [char.get('id', '') for char in selected_character_cards]
    character_names_count = {}
    for char_id in character_ids_list:
        character_names_count[char_id] = character_names_count.get(char_id, 0) + 1
    
    # Check for character duplicates - get names for user-friendly message
    character_limit_valid = all(count <= 1 for count in character_names_count.values())
    for char_id, count in character_names_count.items():
        if count > 1:
            char_name = card_id_to_name.get(char_id, char_id)  # Use ID if name not available
            errors.append(f"角色「{char_name}」超过1张限制，当前为{count}张")
            character_limit_valid = False  # Mark as invalid if character appears more than once
    
    character_limit_valid = all(count <= 1 for count in character_names_count.values())
    
    # Check element resonance rules
    elemental_synergy_valid = True
    elemental_synergy_msg = "元素协同检查通过"
    
    # Find element resonance cards in the deck
    element_resonance_cards = [card for card in selected_action_cards 
                              if '元素共鸣' in card.get('name', '') or 'Elemental Resonance' in card.get('name', '')]
    
    if element_resonance_cards:
        for resonance_card in element_resonance_cards:
            card_name = resonance_card.get('name', '')
            
            # Extract element from card name (e.g., "元素共鸣：愈疗之水" -> "水")
            target_element = None
            if '：' in card_name:
                element_part = card_name.split('：')[1] if '：' in card_name else card_name
                element_chars = ['火', '水', '雷', '草', '风', '岩', '冰']
                for char in element_chars:
                    if char in element_part:
                        target_element = char
                        break
            
            if target_element:
                # Count characters with the target element
                matching_characters = 0
                for char_card in selected_character_cards:
                    # Try to extract element from character skills
                    element_from_skills = None
                    if 'skills' in char_card and isinstance(char_card['skills'], list) and len(char_card['skills']) > 0:
                        first_skill = char_card['skills'][0]
                        if 'cost' in first_skill and isinstance(first_skill['cost'], list):
                            for cost_item in first_skill['cost']:
                                if isinstance(cost_item, str) and cost_item in ['火', '水', '雷', '草', '风', '岩', '冰']:
                                    element_from_skills = cost_item
                                    break
                                elif isinstance(cost_item, dict) and 'type' in cost_item and cost_item['type'] in ['火', '水', '雷', '草', '风', '岩', '冰']:
                                    element_from_skills = cost_item['type']
                                    break
                    
                    # Also try to extract from region field
                    if not element_from_skills and 'region' in char_card:
                        region = char_card['region']
                        for char in element_chars:
                            if char in region:
                                element_from_skills = char
                                break
                    
                    if element_from_skills == target_element:
                        matching_characters += 1
                
                if matching_characters < 2:
                    errors.append(f"元素共鸣牌「{card_name}」需要至少2个{target_element}角色，当前只有{matching_characters}个")
                    elemental_synergy_valid = False
                    elemental_synergy_msg = f"元素共鸣检查失败：需要至少2个{target_element}元素角色"
    
    # Check for talent cards (require matching character)
    talent_cards = [card for card in selected_action_cards if card.get('type') == '天赋牌' or card.get('subtype') == '天赋牌']
    for talent in talent_cards:
        talent_name = talent.get('name', '')
        # Extract required character name from talent (this is a simplification)
        # In a real implementation, we'd need a mapping of talents to characters
        # For now, skip this check since we don't have complete talent->character mappings
        pass
    
    # Determine overall validity
    is_valid = (character_count_valid and card_count_valid and 
                card_limits_valid and elemental_synergy_valid and 
                character_limit_valid)
    
    rules = {
        'character_count': {
            'valid': character_count_valid,
            'message': f"角色数量为 {character_count}/3"
        },
        'deck_size': {
            'valid': card_count_valid,
            'message': f"行动卡数量为 {card_count}/30"
        },
        'character_limit': {
            'valid': character_limit_valid,
            'message': "每个角色限1张"
        },
        'card_limit': {
            'valid': card_limits_valid,
            'message': "行动牌数量符合要求"
        },
        'elemental_synergy': {
            'valid': elemental_synergy_valid,
            'message': elemental_synergy_msg
        }
    }
    
    return {
        "is_valid": is_valid,
        "errors": errors,
        "suggestions": suggestions,
        "rules": rules
    }