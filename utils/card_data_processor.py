"""
统一的卡牌数据处理模块
实现从原始数据到数据库存储的标准转换流程
"""
import json
import os
from utils.logger import get_logger
from typing import List, Dict, Any
from models.game_models import Card as GameCard
import uuid


class CardDataProcessor:
    """卡牌数据处理器，统一处理从源数据到数据库的转换"""
    
    def __init__(self):
        self.logger = get_logger(__name__)
        self.card_types_map = {
            "角色牌": "角色牌",
            "事件牌": "事件牌", 
            "装备牌": "武器",  # 在数据库中归类为武器
            "武器牌": "武器",
            "圣遗物牌": "圣遗物",
            "支援牌": "支援牌"
        }
        
        self.element_types = ["火", "水", "雷", "草", "风", "岩", "冰", "物理", "荒性", "芒性"]
        self.weapon_types = ["单手剑", "双手剑", "长柄武器", "弓", "法器", "其他武器"]
        self.countries = ["蒙德", "璃月", "稻妻", "须弥", "枫丹", "纳塔", "至冬", "魔物", "愚人众", "丘丘人"]
    
    def parse_cost_from_data(self, cost_data: List[Dict[str, Any]]) -> List[str]:
        """将原始成本数据转换为标准格式"""
        if not cost_data:
            return []
        
        # 将成本数据转换为元素类型列表
        cost_elements = []
        for cost_item in cost_data:
            cost_type = cost_item.get('type', '无')
            cost_value = cost_item.get('value', 1)
            
            # 重复添加元素类型，根据数量
            for _ in range(cost_value):
                cost_elements.append(cost_type)
        
        return cost_elements
    
    def extract_country_from_region(self, region_str: str) -> str:
        """从region字段提取国家信息"""
        if not region_str:
            return ""
        
        for country in self.countries:
            if country in region_str:
                return country
        return ""
    
    def extract_element_from_skills(self, skills: List[Dict[str, Any]]) -> str:
        """从技能费用中提取元素信息"""
        if not skills:
            return ""
        
        first_skill = skills[0] if skills else {}
        if "cost" in first_skill:
            costs = first_skill["cost"]
            for cost in costs:
                if isinstance(cost, dict) and "type" in cost:
                    cost_type = cost["type"]
                    if cost_type in self.element_types:
                        return cost_type
                    if "始基力" in cost_type:
                        if "荒性" in cost_type:
                            return "荒性"
                        elif "芒性" in cost_type:
                            return "芒性"
                elif isinstance(cost, str) and cost in self.element_types:
                    return cost
        
        return ""
    
    def extract_weapon_type_from_region(self, region_str: str) -> str:
        """从region字段提取武器类型"""
        if not region_str:
            return ""
        
        for weapon_type in self.weapon_types:
            if weapon_type in region_str:
                return weapon_type
        return ""
    
    def generate_tags_for_card(self, card_data: Dict[str, Any], card_type: str) -> List[str]:
        """为卡牌生成标签"""
        tags = []
        
        # 根据卡牌类型添加基本标签
        if card_type:
            tags.append(card_type.strip())
        
        # 添加元素标签（如果是角色牌或有元素的卡牌）
        element = card_data.get('element_type')
        if element:
            tags.append(element)
        
        # 添加国家/地区标签
        region = card_data.get('region', '')
        countries = ["蒙德", "璃月", "稻妻", "须弥", "枫丹", "纳塔", "至冬", "魔物", "愚人众", "丘丘人"]
        for country in countries:
            if country in region:
                tags.append(country)
                break
        
        # 添加武器类型标签（如果是角色牌）
        weapon_type = card_data.get('weapon_type')
        if weapon_type:
            tags.append(weapon_type)
        
        # 从技能中提取标签
        skills = card_data.get('skills', [])
        if skills and isinstance(skills, list):
            for skill in skills:
                skill_type = skill.get('type')
                if skill_type:
                    if skill_type not in tags:  # 避免重复
                        tags.append(skill_type)
                    
                # 检查技能描述中是否有特殊关键词
                description = skill.get('description', '')
                if '治疗' in description:
                    tags.append('治疗')
                if '护盾' in description:
                    tags.append('护盾')
                if '伤害' in description:
                    tags.append('伤害')
                if '元素' in description and '反应' in description:
                    tags.append('元素反应')
        
        # 从子类型添加标签
        character_subtype = card_data.get('character_subtype')
        if character_subtype:
            tags.append(character_subtype)
        
        # 从稀有度添加标签
        rarity = card_data.get('rarity')
        if rarity:
            tags.append(f'{rarity}星')
        
        # 去重并返回
        return list(set(tags))

    def standardize_character_card(self, char_data: Dict[str, Any]) -> Dict[str, Any]:
        """标准化角色卡数据"""
        region = char_data.get('region', '')
        
        # 提取国家和武器类型
        country = self.extract_country_from_region(region)
        weapon_type = self.extract_weapon_type_from_region(region)
        
        # 从技能中提取元素
        element = self.extract_element_from_skills(char_data.get('skills', []))
        
        # 确定卡牌类型
        card_type = "角色牌"
        
        # 生成标签
        tags = self.generate_tags_for_card(char_data, card_type)
        
        # 构建CardData对象所需的数据
        card_data_dict = {
            'id': char_data.get('id', str(uuid.uuid4())),
            'name': char_data.get('name', ''),
            'card_type': card_type,
            'element_type': element,
            'cost': json.dumps([], ensure_ascii=False),  # 角色牌通常没有打出成本
            'description': char_data.get('description', ''),
            'character_subtype': region,
            'rarity': char_data.get('rarity', 5),  # 假设角色都是5星
            'skills': json.dumps(char_data.get('skills', []), ensure_ascii=False),  # 确保中文不被转义
            'tags': json.dumps(tags, ensure_ascii=False),  # 存储标签
            # 角色特定属性
            'health': char_data.get('health', 10),
            'health_max': char_data.get('health', 10),  # 替换原来的max_health
            'energy': 0,
            'energy_max': 2,  # 替换原来的max_energy
            'weapon_type': weapon_type,
            'image_url': char_data.get('name_url', ''),
            'country': country,  # 国家
        }
        
        return card_data_dict
    
    def standardize_action_card(self, card_data: Dict[str, Any], card_type: str) -> Dict[str, Any]:
        """标准化行动卡（事件、装备、支援）数据"""
        # 解析成本（通常从第一个技能获取）
        total_cost = []
        if 'skills' in card_data and card_data['skills']:
            first_skill = card_data['skills'][0]
            if 'cost' in first_skill:
                total_cost = self.parse_cost_from_data(first_skill['cost'])
        
        # 确定元素类型
        element = self.extract_element_from_skills(card_data.get('skills', []))
        
        # 生成标签
        tags = self.generate_tags_for_card(card_data, card_type)
        
        # 从region字段提取国家，如果available
        region = card_data.get('region', '')
        country = self.extract_country_from_region(region)
        
        # 构建CardData对象所需的数据
        result = {
            'id': card_data.get('id', str(uuid.uuid4())),
            'name': card_data.get('name', ''),
            'card_type': card_type,
            'element_type': element,
            'cost': json.dumps(total_cost) if total_cost else [],
            'description': card_data.get('description', ''),
            'character_subtype': card_data.get('subtype', card_data.get('category', '')),
            'rarity': card_data.get('rarity', 1),
            'skills': json.dumps(card_data.get('skills', []), ensure_ascii=False),  # 确保中文不被转义
            'tags': json.dumps(tags, ensure_ascii=False),  # 存储标签
            'image_url': card_data.get('image_url', card_data.get('name_url', '')),
            'country': country,  # 国家
        }
        
        return result
    
    def process_character_cards(self, characters_data: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """处理角色卡数据"""
        processed_cards = []
        
        for char_data in characters_data:
            try:
                processed_card = self.standardize_character_card(char_data)
                processed_cards.append(processed_card)
            except Exception as e:
                self.logger.error(f"处理角色卡 {char_data.get('name', 'Unknown')} 时出错: {str(e)}")
                continue
        
        return processed_cards
    
    def process_action_cards(self, cards_data: List[Dict[str, Any]], card_type: str) -> List[Dict[str, Any]]:
        """处理行动卡（事件、装备、支援）数据"""
        processed_cards = []
        
        for card_data in cards_data:
            try:
                processed_card = self.standardize_action_card(card_data, card_type)
                processed_cards.append(processed_card)
            except Exception as e:
                self.logger.error(f"处理{card_type} {card_data.get('name', 'Unknown')} 时出错: {str(e)}")
                continue
        
        return processed_cards
    
    def process_all_cards(self, 
                         characters_path: str = None,
                         events_path: str = None, 
                         equipments_path: str = None,
                         supports_path: str = None) -> List[Dict[str, Any]]:
        """处理所有类型的卡牌数据"""
        all_processed_cards = []
        
        # 处理角色卡
        if characters_path and os.path.exists(characters_path):
            with open(characters_path, 'r', encoding='utf-8') as f:
                characters_data = json.load(f)
            all_processed_cards.extend(self.process_character_cards(characters_data))
        
        # 处理事件卡
        if events_path and os.path.exists(events_path):
            with open(events_path, 'r', encoding='utf-8') as f:
                events_data = json.load(f)
            all_processed_cards.extend(self.process_action_cards(events_data, "事件牌"))
        
        # 处理装备卡
        if equipments_path and os.path.exists(equipments_path):
            with open(equipments_path, 'r', encoding='utf-8') as f:
                equipments_data = json.load(f)
            all_processed_cards.extend(self.process_action_cards(equipments_data, "武器"))
        
        # 处理支援卡
        if supports_path and os.path.exists(supports_path):
            with open(supports_path, 'r', encoding='utf-8') as f:
                supports_data = json.load(f)
            all_processed_cards.extend(self.process_action_cards(supports_data, "支援牌"))
        
        return all_processed_cards


def load_card_data_from_db():
    """从数据库加载卡牌数据，提供给前端使用（兼容原有deck_builder的接口）"""
    from models.db_models import CardData, db
    
    cards = db.session.query(CardData).filter(CardData.is_active == True).all()
    
    # 转换为前端兼容的格式
    all_cards = []
    
    for card in cards:
        # 处理cost字段
        card_cost = card.cost if card.cost else []
        if isinstance(card_cost, str):
            try:
                card_cost = json.loads(card_cost) if card_cost else []
            except json.JSONDecodeError:
                card_cost = []
        
        # 尝试从技能中提取cost和description
        card_description = card.description or ""
        if card.card_type != "角色牌" and card.skills:
            try:
                skills_data = card.skills if isinstance(card.skills, list) else json.loads(card.skills)
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
                    skills_data = card.skills if isinstance(card.skills, list) else json.loads(card.skills)
                    if skills_data and isinstance(skills_data, list) and len(skills_data) > 0:
                        first_skill = skills_data[0]
                        if "cost" in first_skill:
                            card_cost = first_skill["cost"]
                        if "description" in first_skill:
                            card_description = first_skill["description"]
                except (json.JSONDecodeError, TypeError):
                    pass
        
        # 提取国家信息
        region_info = (
            getattr(card, "weapon_type", "")
            or getattr(card, "character_subtype", "")
            or ""
        )
        
        # 确定国家
        countries = [
            "蒙德", "璃月", "稻妻", "须弥", "枫丹", "纳塔", "至冬", "魔物", "愚人众", "丘丘人"
        ]
        country = next((c for c in countries if c in region_info), "")
        
        # 确定元素
        element = card.element_type or ""
        if not element and card.skills:
            try:
                skills_data = card.skills if isinstance(card.skills, list) else json.loads(card.skills)
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

        # 确定武器类型
        weapon_type = getattr(card, "weapon_type", "") or ""
        weapon_types = ["单手剑", "双手剑", "长柄武器", "弓", "法器", "其他武器"]
        if not weapon_type:
            for wt in weapon_types:
                if wt in region_info:
                    weapon_type = wt
                    break

        # 构建兼容格式的卡牌数据
        card_dict = {
            "id": card.id,
            "name": card.name,
            "type": card.card_type,
            "subtype": card.character_subtype,
            "title": region_info,
            "description": card_description,
            "cost": card_cost,
            "skills": json.loads(card.skills) if card.skills else [],
            "country": country,
            "element": element,
            "weapon_type": weapon_type,
            "rarity": card.rarity,
            "image_url": card.image_url,
        }
        
        all_cards.append(card_dict)
    
    return all_cards


def get_element_from_character(character):
    """从角色数据中提取元素（兼容原函数）"""
    processor = CardDataProcessor()
    return processor.extract_element_from_skills(character.get("skills", []))


def extract_country_from_region(region):
    """从region提取国家（兼容原函数）"""
    processor = CardDataProcessor()
    return processor.extract_country_from_region(region)


def extract_weapon_type_from_region(region):
    """从region提取武器类型（兼容原函数）"""
    processor = CardDataProcessor()
    return processor.extract_weapon_type_from_region(region)