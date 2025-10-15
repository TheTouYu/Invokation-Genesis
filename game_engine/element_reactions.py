"""
元素反应系统实现
"""
from typing import Dict, List, Optional, Tuple
from models.game_models import CharacterCard
from models.enums import ElementType, DamageType


class ElementReactionSystem:
    """
    元素反应系统，处理各种元素之间的相互作用
    """
    
    def __init__(self):
        # 定义元素反应映射
        self.reactions = {
            (ElementType.PYRO, ElementType.HYDRO): "Vaporize",  # 蒸发
            (ElementType.HYDRO, ElementType.PYRO): "Vaporize",  # 蒸发(reverse)
            (ElementType.PYRO, ElementType.CRYO): "Melt",       # 融化
            (ElementType.CRYO, ElementType.PYRO): "Melt",       # 融化(reverse)
            (ElementType.ELECTRO, ElementType.HYDRO): "Electro-Charged",  # 感电
            (ElementType.HYDRO, ElementType.ELECTRO): "Electro-Charged",  # 感电(reverse)
            (ElementType.ELECTRO, ElementType.CRYO): "Superconduct",      # 超导
            (ElementType.CRYO, ElementType.ELECTRO): "Superconduct",      # 超导(reverse)
            (ElementType.PYRO, ElementType.ELECTRO): "Overloaded",        # 超载
            (ElementType.ELECTRO, ElementType.PYRO): "Overloaded",        # 超载(reverse)
            (ElementType.PYRO, ElementType.DENDRO): "Burning",            # 燃烧
            (ElementType.DENDRO, ElementType.PYRO): "Burning",            # 燃烧(reverse)
            (ElementType.HYDRO, ElementType.DENDRO): "Bloom",            # 绽放
            (ElementType.DENDRO, ElementType.HYDRO): "Bloom",            # 绽放(reverse)
            (ElementType.ELECTRO, ElementType.DENDRO): "Catalyze",       # 催化
            (ElementType.DENDRO, ElementType.ELECTRO): "Catalyze",       # 催化(reverse)
        }
        
        # 定义反应效果
        self.reaction_effects = {
            "Vaporize": {
                "damage_multiplier": 2.0,  # 伤害翻倍
                "is_amplifying": True,     # 增幅反应
                "additional_effect": None
            },
            "Melt": {
                "damage_multiplier": 2.0,  # 伤害翻倍
                "is_amplifying": True,     # 增幅反应
                "additional_effect": None
            },
            "Electro-Charged": {
                "damage_multiplier": 1.0,
                "is_amplifying": False,    # 物化反应
                "additional_effect": "spread_damage_to_other_enemies",
                "spread_damage": 1
            },
            "Superconduct": {
                "damage_multiplier": 1.0,
                "is_amplifying": False,    # 物化反应
                "additional_effect": "spread_damage_to_other_enemies",
                "spread_damage": 1
            },
            "Overloaded": {
                "damage_multiplier": 2.0,
                "is_amplifying": False,    # 物化反应
                "additional_effect": "force_character_switch"
            },
            "Burning": {
                "damage_multiplier": 1.0,
                "is_amplifying": False,
                "additional_effect": "create_status",
                "status_name": "Burn",
                "damage_per_turn": 1,
                "duration": 2
            },
            "Bloom": {
                "damage_multiplier": 1.0,
                "is_amplifying": False,
                "additional_effect": "create_status",
                "status_name": "Bloom",
                "enhance_future_damage": 2
            },
            "Catalyze": {
                "damage_multiplier": 1.0,
                "is_amplifying": False,
                "additional_effect": "create_status",
                "status_name": "Catalyze",
                "enhance_future_damage": 1
            }
        }
    
    def check_element_reaction(self, existing_element: Optional[ElementType], incoming_element: ElementType) -> Optional[str]:
        """
        检查两个元素是否会产生反应
        
        Args:
            existing_element: 目标角色当前附着的元素
            incoming_element: 攻击的元素
            
        Returns:
            反应名称，如果没有反应则返回None
        """
        if existing_element is None or incoming_element is None:
            return None
            
        # 检查是否产生元素反应
        reaction = self.reactions.get((existing_element, incoming_element))
        if reaction:
            return reaction
        
        # 检查反向反应（有些反应是双向的）
        reverse_reaction = self.reactions.get((incoming_element, existing_element))
        if reverse_reaction:
            return reverse_reaction
            
        return None
    
    def calculate_reaction_damage(self, base_damage: int, reaction_type: str) -> Tuple[int, Dict[str, any]]:
        """
        计算元素反应后的伤害
        
        Args:
            base_damage: 基础伤害
            reaction_type: 反应类型
            
        Returns:
            (最终伤害, 反应效果字典)
        """
        reaction_info = self.reaction_effects.get(reaction_type, {})
        multiplier = reaction_info.get("damage_multiplier", 1.0)
        is_amplifying = reaction_info.get("is_amplifying", False)
        
        final_damage = int(base_damage * multiplier)
        
        # 反应效果
        effect_info = {
            "reaction_type": reaction_type,
            "is_amplifying": is_amplifying,
            "additional_effect": reaction_info.get("additional_effect"),
            "multiplier": multiplier,
            "spread_damage": reaction_info.get("spread_damage"),
            "status_name": reaction_info.get("status_name"),
            "duration": reaction_info.get("duration"),
            "enhance_value": reaction_info.get("enhance_future_damage", 0)
        }
        
        return final_damage, effect_info
    
    def apply_element_attachment(self, target_character: CharacterCard, element_type: ElementType) -> bool:
        """
        应用元素附着到角色
        
        Args:
            target_character: 目标角色
            element_type: 要附着的元素类型
            
        Returns:
            True 表示成功附着元素
        """
        # 某些元素无法附着（物理、万能元素）
        if element_type in [ElementType.PHYSICAL, ElementType.OMNI]:
            return False
            
        # 风和岩元素无法附着
        if element_type in [ElementType.ANEMO, ElementType.GEO]:
            return False
            
        # 应用元素附着
        target_character.element_attached = element_type
        return True
    
    def handle_element_attachment(self, target_character: CharacterCard, incoming_element: ElementType) -> Tuple[Optional[str], int]:
        """
        处理元素附着逻辑
        
        Args:
            target_character: 目标角色
            incoming_element: 传入的元素
            
        Returns:
            (反应类型, 附加伤害)
        """
        existing_element = target_character.element_attached
        reaction_type = self.check_element_reaction(existing_element, incoming_element)
        
        if reaction_type:
            # 如果发生反应，清除原元素附着
            if existing_element:
                target_character.element_attached = None
            return reaction_type, 0
        else:
            # 如果没有反应，但是是元素伤害且目标没有附着元素，则附着元素
            if incoming_element not in [ElementType.PHYSICAL, ElementType.OMNI]:
                if incoming_element not in [ElementType.ANEMO, ElementType.GEO]:
                    # 附着新元素
                    target_character.element_attached = incoming_element
            return None, 0
    
    def remove_element_attachment(self, target_character: CharacterCard) -> None:
        """
        移除角色的元素附着
        """
        target_character.element_attached = None