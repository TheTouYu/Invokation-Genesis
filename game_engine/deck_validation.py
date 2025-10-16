"""
卡组构筑验证系统
"""
from typing import List, Dict, Any
from models.game_models import Card, CharacterCard
from models.enums import CardType
import logging


class DeckValidationSystem:
    """
    卡组构筑验证系统，确保卡组符合官方规则
    """
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
    
    def validate_deck(self, deck: List[Card]) -> Dict[str, Any]:
        """
        验证卡组是否符合规则
        
        Args:
            deck: 卡组列表
            
        Returns:
            验证结果字典，包含是否有效和错误信息
        """
        result = {
            "is_valid": True,
            "errors": [],
            "warnings": [],
            "rules": {
                "character_count": {"valid": True, "message": ""},
                "deck_size": {"valid": True, "message": ""},
                "character_limit": {"valid": True, "message": ""},
                "card_limit": {"valid": True, "message": ""},
                "elemental_synergy": {"valid": True, "message": ""}
            }
        }
        
        # 分类卡牌 - account for both CharacterCard instances and cards with CHARACTER type
        character_cards = [card for card in deck if isinstance(card, CharacterCard) or card.card_type == CardType.CHARACTER]
        action_cards = [card for card in deck if not isinstance(card, CharacterCard) and card.card_type != CardType.CHARACTER]
        
        # 验证角色卡数量 (3个不同角色，每个角色只能1张)
        unique_characters = set(c.id for c in character_cards)
        if len(unique_characters) != 3:  # 3个不同角色
            unique_count = len(unique_characters)
            result["errors"].append(f"角色卡应为3个不同角色，当前为{unique_count}个")
            result["is_valid"] = False
            result["rules"]["character_count"] = {"valid": False, "message": f"角色数量为 {unique_count}/3"}
        else:
            result["rules"]["character_count"] = {"valid": True, "message": "角色数量为 3/3"}
        
        # 验证行动卡数量 (总共30张行动牌)
        if len(action_cards) != 30:
            result["errors"].append(f"行动卡应为30张，当前为{len(action_cards)}张")
            result["is_valid"] = False
            result["rules"]["deck_size"] = {"valid": False, "message": f"行动卡数量为 {len(action_cards)}/30"}
        else:
            result["rules"]["deck_size"] = {"valid": True, "message": f"行动卡数量为 {len(action_cards)}/30"}
        
        # 验证同名卡牌数量限制（除秘传牌外，每种行动牌最多2张）
        card_counts = {}
        for card in action_cards:
            card_name = card.name
            if card_name in card_counts:
                card_counts[card_name] += 1
            else:
                card_counts[card_name] = 1
        
        for name, count in card_counts.items():
            if count > 2:
                # 检查是否为秘传牌（通常每种只允许1张）
                if '秘传' in name or 'Legacy' in name:
                    if count > 1:
                        result["errors"].append(f"秘传牌「{name}」超过1张限制，当前为{count}张")
                        result["is_valid"] = False
                else:
                    result["errors"].append(f"卡牌「{name}」超过2张限制，当前为{count}张")
                    result["is_valid"] = False
        
        # 检查角色数量限制规则
        if len(unique_characters) <= 3:
            result["rules"]["character_limit"] = {"valid": True, "message": "每个角色限1张"}
        else:
            result["rules"]["character_limit"] = {"valid": False, "message": f"角色数量超出限制: {len(unique_characters)}/3"}
        
        # 检查卡牌数量限制规则
        if len(action_cards) <= 30:
            result["rules"]["card_limit"] = {"valid": True, "message": "行动牌数量符合要求"}
        else:
            result["rules"]["card_limit"] = {"valid": False, "message": f"行动牌数量超出限制: {len(action_cards)}/30"}
        
        # 验证天赋牌规则：卡组中包含对应角色牌
        for card in action_cards:
            if card.card_type == CardType.TALENT:
                # 检查是否有对应的字符卡
                has_matching_character = any(
                    c.name == card.character_subtype for c in character_cards
                )
                if not has_matching_character:
                    result["errors"].append(f"天赋牌「{card.name}」缺少对应的「{card.character_subtype}」角色")
                    result["is_valid"] = False
        
        # 验证元素共鸣牌规则：牌组包含至少两个对应元素角色
        element_cards = [card for card in action_cards if '元素共鸣' in card.name or 'Elemental Resonance' in card.name]
        for card in element_cards:
            element_name = self._extract_element_from_card(card.name)
            if element_name:
                # Map Chinese element names to possible enum values
                element_to_enum = {
                    '火': ['火', 'Pyro'],
                    '水': ['水', 'Hydro'], 
                    '雷': ['雷', 'Electro'],
                    '草': ['草', 'Dendro'],
                    '风': ['风', 'Anemo'],
                    '岩': ['岩', 'Geo'],
                    '冰': ['冰', 'Cryo'],
                    '物理': ['物理', 'Physical']
                }
                
                # Get the expected element values based on the element name
                expected_values = element_to_enum.get(element_name, [element_name])
                
                matching_characters = [
                    c for c in character_cards 
                    if (hasattr(c, 'element_type') and 
                        (
                            # Check if element_type has value attribute (enum) that matches
                            (hasattr(c.element_type, 'value') and 
                             any(expected_val in str(c.element_type.value) for expected_val in expected_values)) or
                            # Check if element_type is a string that matches
                            (not hasattr(c.element_type, 'value') and 
                             any(expected_val in str(c.element_type) for expected_val in expected_values))
                        ) or 
                        element_name in c.name)
                ]
                if len(matching_characters) < 2:
                    result["errors"].append(f"元素共鸣牌「{card.name}」需要至少2个{element_name}角色，当前只有{len(matching_characters)}个")
                    result["is_valid"] = False
        
        # 验证国家牌规则：牌组包含至少两个对应国家角色
        nation_cards = [card for card in action_cards if '国家' in card.name or 'Nation' in card.name]
        for card in nation_cards:
            nation_name = self._extract_nation_from_card(card.name)
            if nation_name:
                matching_characters = [
                    c for c in character_cards 
                    if nation_name in c.name
                ]
                if len(matching_characters) < 2:
                    result["errors"].append(f"国家牌「{card.name}」需要至少2个{nation_name}角色，当前只有{len(matching_characters)}个")
                    result["is_valid"] = False
        
        # 检查元素协同规则
        element_cards = [card for card in action_cards if '元素共鸣' in card.name or 'Elemental Resonance' in card.name]
        nation_cards_check = [card for card in action_cards if '国家' in card.name or 'Nation' in card.name]
        
        if element_cards or nation_cards_check:
            result["rules"]["elemental_synergy"] = {"valid": True, "message": "元素协同检查通过"}
        else:
            result["rules"]["elemental_synergy"] = {"valid": True, "message": "无需要元素协同的卡牌"}
        
        return result
    
    def _extract_element_from_card(self, card_name: str) -> str:
        """
        从卡牌名称中提取元素名称
        """
        elements = ["火", "水", "雷", "草", "风", "岩", "冰", "Pyro", "Hydro", "Electro", "Dendro", "Anemo", "Geo", "Cryo"]
        for element in elements:
            if element in card_name:
                return element
        return ""
    
    def _extract_nation_from_card(self, card_name: str) -> str:
        """
        从卡牌名称中提取国家名称
        """
        nations = ["蒙德", "璃月", "稻妻", "须弥", "枫丹", "纳塔", "穆斯贝尔", "蒙德城", "Mondstadt", "Liyue", "Inazuma", "Sumeru", "Fontaine"]
        for nation in nations:
            if nation in card_name:
                return nation
        return ""
    
    def get_deck_stats(self, deck: List[Card]) -> Dict[str, Any]:
        """
        获取卡组统计信息
        
        Args:
            deck: 卡组列表
            
        Returns:
            卡组统计信息
        """
        character_cards = [card for card in deck if isinstance(card, CharacterCard)]
        action_cards = [card for card in deck if not isinstance(card, CharacterCard)]
        
        # 按类型统计行动卡
        action_type_counts = {}
        for card in action_cards:
            card_type = card.card_type.value
            if card_type in action_type_counts:
                action_type_counts[card_type] += 1
            else:
                action_type_counts[card_type] = 1
        
        # 按元素统计角色
        element_counts = {}
        for char in character_cards:
            if hasattr(char, 'element_type') and hasattr(char.element_type, 'value'):
                element = str(char.element_type.value)
            elif hasattr(char, 'element_type'):
                element = str(char.element_type)
            else:
                element = "未知"
            if element in element_counts:
                element_counts[element] += 1
            else:
                element_counts[element] = 1
        
        return {
            "total_cards": len(deck),
            "character_cards_count": len(character_cards),
            "action_cards_count": len(action_cards),
            "action_type_distribution": action_type_counts,
            "element_distribution": element_counts,
            "characters": [char.name for char in character_cards]
        }