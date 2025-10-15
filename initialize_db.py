"""
完整的数据库初始化脚本
"""
import os
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
import uuid

# 创建应用和数据库实例
app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///game.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy()
db.init_app(app)

# 重置初始化标记
from models.db_models import _initialized, init_models_db
_initialized = False  # 手动重置标记

# 重新初始化模型
init_models_db(db)

def verify_and_fix_schema():
    """验证并修复数据库模式"""
    with app.app_context():
        # 导入模型
        from models.db_models import User, CardData, Deck, GameHistory
        
        # 创建所有表
        db.create_all()
        print("数据库表创建完成")
        
        # 验证表结构
        from sqlalchemy import text
        result = db.session.execute(text('SELECT name FROM sqlite_master WHERE type="table"'))
        tables = [row[0] for row in result]
        print(f"当前数据库表: {tables}")
        
        # 检查card_data表的列
        result = db.session.execute(text('PRAGMA table_info(card_data)'))
        card_data_cols = [row[1] for row in result]
        print(f"card_data表当前列: {card_data_cols}")
        
        # 检查decks表的列
        result = db.session.execute(text('PRAGMA table_info(decks)'))
        decks_cols = [row[1] for row in result]
        print(f"decks表当前列: {decks_cols}")
        
        # 验证是否所有必需的列都存在
        required_card_cols = ['element_type', 'character_subtype', 'health', 'max_health', 'energy', 'max_energy', 'weapon_type', 'skills', 'image_url']
        missing_card_cols = [col for col in required_card_cols if col not in card_data_cols]
        
        required_deck_cols = ['cards']
        missing_deck_cols = [col for col in required_deck_cols if col not in decks_cols]
        
        print(f"card_data表缺失列: {missing_card_cols}")
        print(f"decks表缺失列: {missing_deck_cols}")
        
        # 如果有缺失的列，需要修复
        if missing_card_cols or missing_deck_cols:
            print("发现缺失列，需要重建表...")
            # 在实际应用中，我们应使用数据库迁移工具，但这里我们手动修复
            rebuild_tables()

def rebuild_tables():
    """重建数据库表以确保结构正确"""
    with app.app_context():
        from models.db_models import User, CardData, Deck, GameHistory
        from sqlalchemy import text
        
        # 先删除旧表
        db.session.execute(text('DROP TABLE IF EXISTS decks'))
        db.session.execute(text('DROP TABLE IF EXISTS card_data'))
        db.session.execute(text('DROP TABLE IF EXISTS game_histories'))
        db.session.execute(text('DROP TABLE IF EXISTS users'))
        
        # 重新创建所有表
        db.create_all()
        
        print("表已重建，验证新结构...")
        
        # 验证重建结果
        result = db.session.execute(text('SELECT name FROM sqlite_master WHERE type="table"'))
        tables = [row[0] for row in result]
        print(f"重建后数据库表: {tables}")
        
        # 检查card_data表的列
        result = db.session.execute(text('PRAGMA table_info(card_data)'))
        card_data_cols = [row[1] for row in result]
        print(f"card_data表列: {card_data_cols}")
        
        # 检查decks表的列
        result = db.session.execute(text('PRAGMA table_info(decks)'))
        decks_cols = [row[1] for row in result]
        print(f"decks表列: {decks_cols}")

if __name__ == "__main__":
    verify_and_fix_schema()
    print("数据库初始化完成！")