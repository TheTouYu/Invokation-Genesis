"""
将 card_data/ 目录下的 JSON 文件导入数据库的脚本
"""

import os
import json
import uuid
from datetime import datetime
from app import create_app
from database_manager import db_manager
from models.db_models import CardData, init_models_db
from models.enums import CardType


def load_json_file(file_path):
    """加载JSON文件"""
    with open(file_path, "r", encoding="utf-8") as file:
        return json.load(file)


def init_db():
    """初始化数据库并导入卡牌数据"""
    # Create Flask app and initialize database
    app = create_app()
    db = db_manager.init_app(app)
    
    with app.app_context():
        # Initialize models
        init_models_db(db)
        
        # Create all tables
        db.create_all()
        
        try:
            # Clear existing card data
            db.session.query(CardData).delete()
            db.session.commit()
            
            # From card_data directory load card data
            card_data_dir = os.path.join(os.path.dirname(__file__), 'card_data')
            
            # Read all card data files
            card_files = {
                'characters': os.path.join(card_data_dir, 'characters.json'),
                'equipments': os.path.join(card_data_dir, 'equipments.json'),
                'supports': os.path.join(card_data_dir, 'supports.json'),
                'events': os.path.join(card_data_dir, 'events.json')
            }
            
            for card_type, file_path in card_files.items():
                if os.path.exists(file_path):
                    print(f"正在导入 {card_type} 数据...")
                    card_list = load_json_file(file_path)
                    
                    for card_info in card_list:
                        # 根据卡牌类型确定子类型
                        sub_type = None
                        if card_type == 'characters':
                            sub_type = card_info.get('element_type', '')  # 角色的元素类型
                        elif card_type == 'equipments':
                            sub_type = card_info.get('equipment_type', '')  # 装备类型
                        elif card_type == 'supports':
                            sub_type = card_info.get('support_type', '')  # 支援类型
                        elif card_type == 'events':
                            sub_type = card_info.get('event_type', '')  # 事件类型
                        
                        # Create card data object
                        card_data = CardData(
                            id=str(uuid.uuid4()),
                            name=card_info.get('name', ''),
                            card_type=card_type,
                            sub_type=sub_type,
                            cost=card_info.get('cost', []),
                            description=card_info.get('description', ''),
                            character_name=card_info.get('character_name', ''),
                            rarity=card_info.get('rarity', 1),
                            version=card_info.get('version', '1.0.0'),
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
            
            print("数据库初始化完成！")
            
        except Exception as e:
            print(f"导入数据时发生错误: {e}")
            db.session.rollback()


if __name__ == "__main__":
    init_db()

