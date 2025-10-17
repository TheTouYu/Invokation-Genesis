"""
标准化的卡牌数据导入模块
将JSON文件数据导入到数据库中，统一数据源
"""
import json
import os
import logging
from typing import List, Dict, Any
from utils.card_data_processor import CardDataProcessor
import uuid


class CardDataImporter:
    """卡牌数据导入器：将JSON文件数据导入数据库"""
    
    def __init__(self):
        self.processor = CardDataProcessor()

    def _get_card_data_class(self):
        """延迟加载CardData类，仅在需要时导入"""
        from models.db_models import CardData
        return CardData
    
    def load_json_data(self, filepath: str) -> List[Dict[str, Any]]:
        """从JSON文件加载数据"""
        if not os.path.exists(filepath):
            logging.warning(f"文件不存在: {filepath}")
            return []
        
        with open(filepath, 'r', encoding='utf-8') as f:
            return json.load(f)
    
    def import_character_cards(self, characters_path: str = "card_data/characters.json"):
        """导入角色卡数据"""
        print("🔄 开始导入角色卡数据...")
        
        from models.db_models import db
        CardData = self._get_card_data_class()
        
        characters_data = self.load_json_data(characters_path)
        if not characters_data:
            print("⚠️ 角色卡数据文件为空或不存在")
            return 0
        
        imported_count = 0
        
        for char_data in characters_data:
            try:
                # 标准化数据
                card_data = self.processor.standardize_character_card(char_data)
                
                # 检查是否已存在（根据名称）
                existing_card = CardData.query.filter_by(name=card_data['name'], card_type='角色牌').first()
                
                if existing_card:
                    # 更新现有记录
                    for key, value in card_data.items():
                        setattr(existing_card, key, value)
                    print(f"🔄 更新角色: {card_data['name']}")
                else:
                    # 创建新记录
                    card_record = CardData(**card_data)
                    db.session.add(card_record)
                    print(f"🆕 添加角色: {card_data['name']}")
                
                imported_count += 1
                
            except Exception as e:
                logging.error(f"导入角色 {char_data.get('name', 'Unknown')} 时出错: {str(e)}")
                continue
        
        db.session.commit()
        print(f"✅ 角色卡导入完成，共处理 {imported_count} 张卡牌")
        return imported_count
    
    def import_action_cards(self, cards_data: List[Dict[str, Any]], card_type: str):
        """导入行动卡（事件、装备、支援）数据"""
        from models.db_models import db
        CardData = self._get_card_data_class()
        imported_count = 0
        
        for card_data in cards_data:
            try:
                # 标准化数据
                processed_card = self.processor.standardize_action_card(card_data, card_type)
                
                # 检查是否已存在（根据名称和类型）
                existing_card = CardData.query.filter_by(
                    name=processed_card['name'], 
                    card_type=card_type
                ).first()
                
                if existing_card:
                    # 更新现有记录
                    for key, value in processed_card.items():
                        setattr(existing_card, key, value)
                    print(f"🔄 更新{card_type}: {processed_card['name']}")
                else:
                    # 创建新记录
                    card_record = CardData(**processed_card)
                    db.session.add(card_record)
                    print(f"🆕 添加{card_type}: {processed_card['name']}")
                
                imported_count += 1
                
            except Exception as e:
                logging.error(f"导入{card_type} {card_data.get('name', 'Unknown')} 时出错: {str(e)}")
                continue
        
        return imported_count
    
    def import_event_cards(self, events_path: str = "card_data/events.json"):
        """导入事件卡数据"""
        print("🔄 开始导入事件卡数据...")
        
        from models.db_models import db
        
        events_data = self.load_json_data(events_path)
        if not events_data:
            print("⚠️ 事件卡数据文件为空或不存在")
            return 0
        
        imported_count = self.import_action_cards(events_data, "事件牌")
        
        db.session.commit()
        print(f"✅ 事件卡导入完成，共处理 {imported_count} 张卡牌")
        return imported_count
    
    def import_equipment_cards(self, equipments_path: str = "card_data/equipments.json"):
        """导入装备卡数据"""
        print("🔄 开始导入装备卡数据...")
        
        from models.db_models import db
        
        equipments_data = self.load_json_data(equipments_path)
        if not equipments_data:
            print("⚠️ 装备卡数据文件为空或不存在")
            return 0
        
        imported_count = self.import_action_cards(equipments_data, "武器")
        
        db.session.commit()
        print(f"✅ 装备卡导入完成，共处理 {imported_count} 张卡牌")
        return imported_count
    
    def import_support_cards(self, supports_path: str = "card_data/supports.json"):
        """导入支援卡数据"""
        print("🔄 开始导入支援卡数据...")
        
        from models.db_models import db
        
        supports_data = self.load_json_data(supports_path)
        if not supports_data:
            print("⚠️ 支援卡数据文件为空或不存在")
            return 0
        
        imported_count = self.import_action_cards(supports_data, "支援牌")
        
        db.session.commit()
        print(f"✅ 支援卡导入完成，共处理 {imported_count} 张卡牌")
        return imported_count
    
    def import_all_cards(self):
        """导入所有卡牌数据"""
        print("🔄 开始导入所有卡牌数据到数据库...")
        
        # 导入各类卡牌
        character_count = self.import_character_cards()
        event_count = self.import_event_cards()
        equipment_count = self.import_equipment_cards()
        support_count = self.import_support_cards()
        
        total = character_count + event_count + equipment_count + support_count
        print(f"🎉 所有卡牌数据导入完成！共导入 {total} 张卡牌")
        print(f"📊 统计: {character_count} 张角色牌, {event_count} 张事件牌, {equipment_count} 张装备牌, {support_count} 张支援牌")
    
    def update_cards_from_source(self):
        """从源数据更新数据库中的卡牌数据"""
        print("🔄 开始更新卡牌数据...")
        
        from models.db_models import db
        CardData = self._get_card_data_class()
        
        # 从JSON文件读取最新数据
        characters = self.load_json_data("card_data/characters.json")
        events = self.load_json_data("card_data/events.json")
        equipments = self.load_json_data("card_data/equipments.json")
        supports = self.load_json_data("card_data/supports.json")
        
        # 为每种卡牌类型进行更新
        updated_count = 0
        
        # 更新角色卡
        if characters:
            for char_data in characters:
                card_data = self.processor.standardize_character_card(char_data)
                
                # 查找现有卡牌
                existing_card = CardData.query.filter_by(
                    name=card_data['name'], 
                    card_type='角色牌'
                ).first()
                
                if existing_card:
                    # 更新现有卡牌
                    for key, value in card_data.items():
                        setattr(existing_card, key, value)
                    updated_count += 1
        
        # 更新事件卡
        if events:
            for card_data in events:
                processed_card = self.processor.standardize_action_card(card_data, "事件牌")
                
                existing_card = CardData.query.filter_by(
                    name=processed_card['name'], 
                    card_type='事件牌'
                ).first()
                
                if existing_card:
                    for key, value in processed_card.items():
                        setattr(existing_card, key, value)
                    updated_count += 1
        
        # 更新装备卡
        if equipments:
            for card_data in equipments:
                processed_card = self.processor.standardize_action_card(card_data, "武器")
                
                existing_card = CardData.query.filter_by(
                    name=processed_card['name'], 
                    card_type='武器'
                ).first()
                
                if existing_card:
                    for key, value in processed_card.items():
                        setattr(existing_card, key, value)
                    updated_count += 1
        
        # 更新支援卡
        if supports:
            for card_data in supports:
                processed_card = self.processor.standardize_action_card(card_data, "支援牌")
                
                existing_card = CardData.query.filter_by(
                    name=processed_card['name'], 
                    card_type='支援牌'
                ).first()
                
                if existing_card:
                    for key, value in processed_card.items():
                        setattr(existing_card, key, value)
                    updated_count += 1
        
        db.session.commit()
        print(f"✅ 卡牌数据更新完成，共更新 {updated_count} 张卡牌")
        
        return updated_count


def import_all_cards():
    """便捷函数：导入所有卡牌数据"""
    from app import create_app
    from models.db_models import db
    app = create_app()
    
    with app.app_context():
        importer = CardDataImporter()
        importer.import_all_cards()


def update_cards_from_source():
    """便捷函数：从源数据更新卡牌数据"""
    from app import create_app
    from models.db_models import db
    app = create_app()
    
    with app.app_context():
        importer = CardDataImporter()
        importer.update_cards_from_source()


if __name__ == "__main__":
    import_all_cards()