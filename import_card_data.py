"""
导入卡牌数据到数据库
"""
import json
import os
from app import create_app, db
from models.db_models import CardData
from models.enums import ElementType

def parse_cost_from_data(cost_data):
    """将原始成本数据转换为存储格式"""
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

def get_card_type_from_region(region_str):
    """根据region字段判断卡牌类型"""
    if not region_str:
        return "事件牌"
    
    if "角色牌" in region_str:
        return "角色牌"
    elif "武器" in region_str:
        return "武器"
    elif "圣遗物" in region_str:
        return "圣遗物"
    elif "事件牌" in region_str:
        return "事件牌"
    elif "支援牌" in region_str:
        return "支援牌"
    else:
        return "事件牌"  # 默认

def get_element_type_from_region(region_str):
    """从region字段提取元素类型"""
    if not region_str:
        return None
    
    elements = ["火", "水", "雷", "草", "风", "岩", "冰"]
    for element in elements:
        if element in region_str:
            return element
    
    # 检查特殊的"角色牌"字段
    if "角色牌" in region_str:
        # 从region字符串中提取元素信息
        if "岩" in region_str:
            return "岩"
        elif "风" in region_str:
            return "风"
        elif "雷" in region_str:
            return "雷"
        elif "水" in region_str:
            return "水"
        elif "火" in region_str:
            return "火"
        elif "冰" in region_str:
            return "冰"
        elif "草" in region_str:
            return "草"
    
    return None

def import_character_cards():
    """导入角色卡数据"""
    print("开始导入角色卡数据...")
    
    with open('card_data/characters.json', 'r', encoding='utf-8') as f:
        characters_data = json.load(f)
    
    for char_data in characters_data:
        try:
            # 确定卡牌类型和元素类型
            card_type = get_card_type_from_region(char_data.get('region', ''))
            element_type = get_element_type_from_region(char_data.get('region', ''))
            
            # 解析第一个技能作为示例成本（如果有技能）
            skills_data = []
            total_cost = []
            if 'skills' in char_data and char_data['skills']:
                for skill in char_data['skills']:
                    skill_cost = parse_cost_from_data(skill.get('cost', []))
                    skills_data.append({
                        'id': skill.get('name', '').replace(' ', '_'),
                        'name': skill.get('name', ''),
                        'description': skill.get('description', ''),
                        'cost': skill_cost,
                        'type': skill.get('type', '')
                    })
                    
                    # 累积所有技能的成本作为卡牌成本（实际游戏中角色牌无成本）
                    # 这里我们可能需要特殊处理，因为角色牌通常没有打出成本
                    # 而是技能有成本
            
            # 创建CardData记录
            card = CardData(
                name=char_data['name'],
                card_type=card_type,
                element_type=element_type,
                cost=[],  # 角色牌通常没有打出成本，只有技能成本
                description=char_data.get('description', ''),
                character_subtype=char_data.get('region', ''),
                rarity=char_data.get('rarity', 5),  # 假设角色都是5星
                skills=json.dumps(skills_data),
                # 基本生命值和能量值（对于角色牌）
                health=char_data.get('health', 10),
                max_health=char_data.get('health', 10),
                energy=0,
                max_energy=2,  # 默认2点能量上限
                weapon_type=char_data.get('weapon_type', ''),
            )
            
            db.session.add(card)
            print(f"导入角色: {char_data['name']}")
            
        except Exception as e:
            print(f"导入角色 {char_data.get('name', 'Unknown')} 时出错: {str(e)}")
            continue
    
    db.session.commit()
    print(f"角色卡导入完成，共导入 {len(characters_data)} 张角色卡")

def import_event_cards():
    """导入事件卡数据"""
    print("开始导入事件卡数据...")
    
    with open('card_data/events.json', 'r', encoding='utf-8') as f:
        events_data = json.load(f)
    
    for event_data in events_data:
        try:
            # 解析技能成本（通常事件牌只有一个技能描述）
            total_cost = []
            if 'skills' in event_data and event_data['skills']:
                # 使用第一个技能的成本作为卡牌成本
                first_skill = event_data['skills'][0]
                total_cost = parse_cost_from_data(first_skill.get('cost', []))
            
            # 确定卡牌类型
            card_type = get_card_type_from_region(event_data.get('category', ''))
            
            # 创建CardData记录
            card = CardData(
                name=event_data['name'],
                card_type=card_type,
                element_type=None,  # 事件牌通常没有元素类型
                cost=json.dumps(total_cost),
                description=event_data.get('description', ''),
                character_subtype=event_data.get('subtype', ''),
                rarity=event_data.get('rarity', 3),  # 默认3星
            )
            
            db.session.add(card)
            print(f"导入事件: {event_data['name']}")
            
        except Exception as e:
            print(f"导入事件 {event_data.get('name', 'Unknown')} 时出错: {str(e)}")
            continue
    
    db.session.commit()
    print(f"事件卡导入完成，共导入 {len(events_data)} 张事件卡")

def import_equipment_cards():
    """导入装备卡数据"""
    print("开始导入装备卡数据...")
    
    with open('card_data/equipments.json', 'r', encoding='utf-8') as f:
        equipments_data = json.load(f)
    
    for equip_data in equipments_data:
        try:
            # 解析成本
            total_cost = []
            if 'skills' in equip_data and equip_data['skills']:
                # 使用第一个技能的成本作为卡牌成本
                first_skill = equip_data['skills'][0]
                total_cost = parse_cost_from_data(first_skill.get('cost', []))
            
            # 确定卡牌类型
            card_type = get_card_type_from_region(equip_data.get('category', ''))
            
            # 确定角色子类型
            character_subtype = equip_data.get('related_characters', equip_data.get('category', ''))
            
            # 创建CardData记录
            card = CardData(
                name=equip_data['name'],
                card_type=card_type,
                element_type=None,
                cost=json.dumps(total_cost),
                description=equip_data.get('description', ''),
                character_subtype=character_subtype,
                rarity=equip_data.get('rarity', 3),
            )
            
            db.session.add(card)
            print(f"导入装备: {equip_data['name']}")
            
        except Exception as e:
            print(f"导入装备 {equip_data.get('name', 'Unknown')} 时出错: {str(e)}")
            continue
    
    db.session.commit()
    print(f"装备卡导入完成，共导入 {len(equipments_data)} 张装备卡")

def import_support_cards():
    """导入支援卡数据"""
    print("开始导入支援卡数据...")
    
    with open('card_data/supports.json', 'r', encoding='utf-8') as f:
        supports_data = json.load(f)
    
    for support_data in supports_data:
        try:
            # 解析成本
            total_cost = []
            if 'skills' in support_data and support_data['skills']:
                # 使用第一个技能的成本作为卡牌成本
                first_skill = support_data['skills'][0]
                total_cost = parse_cost_from_data(first_skill.get('cost', []))
            
            # 确定卡牌类型
            card_type = get_card_type_from_region(support_data.get('category', ''))
            
            # 创建CardData记录
            card = CardData(
                name=support_data['name'],
                card_type=card_type,
                element_type=None,
                cost=json.dumps(total_cost),
                description=support_data.get('description', ''),
                character_subtype=support_data.get('subtype', ''),
                rarity=support_data.get('rarity', 2),  # 支援牌通常为2星
            )
            
            db.session.add(card)
            print(f"导入支援: {support_data['name']}")
            
        except Exception as e:
            print(f"导入支援 {support_data.get('name', 'Unknown')} 时出错: {str(e)}")
            continue
    
    db.session.commit()
    print(f"支援卡导入完成，共导入 {len(supports_data)} 张支援卡")

def import_all_cards():
    """导入所有卡牌数据"""
    app = create_app()
    
    with app.app_context():
        print("开始导入所有卡牌数据到数据库...")
        
        # 检查数据库是否已存在数据，避免重复导入
        existing_count = db.session.query(CardData).count()
        if existing_count > 0:
            print(f"警告: 数据库中已存在 {existing_count} 张卡牌，跳过导入以避免重复")
            response = input("是否要清空现有数据并重新导入？(y/N): ")
            if response.lower() != 'y':
                print("取消导入操作")
                return
            else:
                # 清空现有数据
                db.session.execute(db.delete(CardData))
                db.session.commit()
                print("现有数据已清空")
        
        # 导入各类卡牌
        import_character_cards()
        import_event_cards()
        import_equipment_cards()
        import_support_cards()
        
        print("所有卡牌数据导入完成！")

if __name__ == "__main__":
    import_all_cards()