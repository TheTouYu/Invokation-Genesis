"""
Script to reset the database and import card data
"""

import os
import json
import uuid
from datetime import datetime
from app import create_app
from database_manager import db_manager
from models.db_models import model_container


def load_json_file(file_path):
    """加载JSON文件"""
    with open(file_path, "r", encoding="utf-8") as file:
        return json.load(file)


def reset_and_import_db():
    """重置数据库并导入卡牌数据"""
    # Create Flask app
    app = create_app()
    
    with app.app_context():
        # Get database instance from the database manager
        db = db_manager.get_db()
        
        # Get the models from the model container
        CardData = model_container.CardData
        
        # Drop all existing tables
        db.drop_all()
        
        # Create all tables again
        db.create_all()
        
        try:
            # From card_data directory load card data
            card_data_dir = os.path.join(os.path.dirname(__file__), 'card_data')
            
            # Read all card data files
            card_files = {
                'characters': os.path.join(card_data_dir, 'characters.json'),
                'equipments': os.path.join(card_data_dir, 'equipments.json'),
                'supports': os.path.join(card_data_dir, 'supports.json'),
                'events': os.path.join(card_data_dir, 'events.json')
            }
            
            card_type_mapping = {
                'characters': '角色牌',
                'equipments': '装备牌',  # May need to be further categorized as '武器', '圣遗物', '天赋'
                'supports': '支援牌',
                'events': '事件牌'
            }
            
            for card_type, file_path in card_files.items():
                if os.path.exists(file_path):
                    print(f"正在导入 {card_type} 数据...")
                    card_list = load_json_file(file_path)
                    
                    for card_info in card_list:
                        # Determine the type and subtype based on the card data
                        card_db_type = card_type_mapping[card_type]
                        
                        # For equipment cards, we need to further classify them
                        if card_type == 'equipments':
                            equipment_type = card_info.get('equipment_type', '')
                            if equipment_type == '武器':
                                card_db_type = '武器'
                            elif equipment_type == '圣遗物':
                                card_db_type = '圣遗物'
                            elif equipment_type == '天赋':
                                card_db_type = '天赋'
                            else:
                                card_db_type = '装备牌'  # Default to '装备牌' if unknown type
                        
                        # Get sub type based on card type
                        sub_type = card_info.get('element_type', '')  # Default to element_type
                        if card_type == 'characters':
                            # For characters, the region field might contain country information
                            region_field = card_info.get('region', '')
                            # Check if the region field contains a country name
                            country_keywords = ["蒙德", "璃月", "稻妻", "须弥", "枫丹", "纳塔", "至冬", "魔物", "愚人众", "丘丘人"]
                            country_in_region = next((country for country in country_keywords if country in region_field), None)
                            
                            # Use the country from region field if found, otherwise use element_type
                            sub_type = country_in_region if country_in_region else card_info.get('element_type', '')
                            
                            # Also store country in weapon_type field as backup for country detection
                            weapon_type = card_info.get('weapon', '') or country_in_region or ''
                        elif card_type == 'equipments':
                            sub_type = card_info.get('equipment_type', '') or card_info.get('weapon_type', '')
                        elif card_type == 'supports':
                            sub_type = card_info.get('support_type', '')
                        elif card_type == 'events':
                            sub_type = card_info.get('event_type', '')
                        
                        # Handle the 'cost' field as JSON
                        cost = card_info.get('cost', [])
                        
                        # Handle the 'skills' field as JSON
                        skills = card_info.get('skills', [])
                        
                        # Extract weapon type from character data - prioritizing the weapon_type field
                        region_field = card_info.get('region', '')
                        country_keywords = ["蒙德", "璃月", "稻妻", "须弥", "枫丹", "纳塔", "至冬", "魔物", "愚人众", "丘丘人"]
                        country_in_region = next((country for country in country_keywords if country in region_field), None)
                        
                        # Prioritize the explicit weapon_type field, then fallback to weapon, then to country from region
                        weapon_info = card_info.get('weapon_type', '') or card_info.get('weapon', '') or country_in_region
                        
                        # Create card data object
                        card_data = CardData(
                            id=str(uuid.uuid4()),
                            name=card_info.get('name', ''),
                            card_type=card_db_type,
                            character_subtype=sub_type,
                            cost=cost,  # Store as JSON (SQLAlchemy handles JSON automatically)
                            description=card_info.get('description', ''),
                            rarity=card_info.get('rarity', 1),
                            version=card_info.get('version', '1.0.0'),
                            skills=skills,  # Store skills as JSON
                            element_type=card_info.get('element_type'),
                            weapon_type=weapon_info,
                            health=card_info.get('health'),
                            energy=card_info.get('energy'),
                            health_max=card_info.get('max_health'),
                            energy_max=card_info.get('max_energy'),
                            image_url=card_info.get('name_url', None) or card_info.get('image_url'),
                            is_active=True,
                            created_at=datetime.utcnow(),
                            updated_at=datetime.utcnow()
                        )
                        
                        # Add to session
                        db.session.add(card_data)
                    
                    # Commit current batch
                    db.session.commit()
                    print(f"成功导入 {len(card_list)} 张 {card_type} 卡牌")
                else:
                    print(f"警告: 未找到文件 {file_path}")
            
            print("数据库重置和初始化完成！")
            
        except Exception as e:
            print(f"导入数据时发生错误: {e}")
            db.session.rollback()


if __name__ == "__main__":
    reset_and_import_db()