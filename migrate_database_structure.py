#!/usr/bin/env python3
"""
数据库结构迁移脚本
执行以下操作：
1. 重命名 max_health 列为 health_max
2. 重命名 max_energy 列为 energy_max
3. 添加 tags 列
"""

import sqlite3
import os
from datetime import datetime

def migrate_database_structure():
    # 获取数据库路径
    project_root = os.path.dirname(os.path.abspath(__file__))
    db_path = os.path.join(project_root, 'instance', 'game.db')
    
    if not os.path.exists(db_path):
        print(f"数据库文件不存在: {db_path}")
        return False
    
    print(f"开始迁移数据库结构: {db_path}")
    
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    try:
        # 检查当前表结构
        cursor.execute("PRAGMA table_info(card_data)")
        columns = {row[1]: row for row in cursor.fetchall()}  # 列名: (cid, name, type, notnull, dflt_value, pk)
        
        print(f"当前card_data表列: {list(columns.keys())}")
        
        # 检查是否需要重命名max_health为health_max
        needs_health_max = 'max_health' in columns and 'health_max' not in columns
        # 检查是否需要重命名max_energy为energy_max
        needs_energy_max = 'max_energy' in columns and 'energy_max' not in columns
        # 检查是否需要添加tags列
        needs_tags = 'tags' not in columns
        
        if not any([needs_health_max, needs_energy_max, needs_tags]):
            print("数据库结构已是最新，无需迁移")
            return True
        
        # 创建临时表
        create_temp_table_sql = """
        CREATE TABLE card_data_temp (
            id TEXT PRIMARY KEY,
            name TEXT NOT NULL,
            card_type TEXT NOT NULL,
            character_subtype TEXT,
            element_type TEXT,
            cost TEXT, -- JSON数据
            description TEXT,
            rarity INTEGER,
            version TEXT,
            created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
            updated_at DATETIME DEFAULT CURRENT_TIMESTAMP,
            is_active BOOLEAN DEFAULT 1,
            health INTEGER,
            health_max INTEGER,  -- 重命名max_health为health_max
            energy INTEGER,
            energy_max INTEGER,  -- 重命名max_energy为energy_max
            weapon_type TEXT,
            skills TEXT,  -- JSON数据
            tags TEXT,  -- 新增tags字段
            image_url TEXT
        );
        """
        cursor.execute(create_temp_table_sql)
        print("已创建临时表 card_data_temp")
        
        # 复制数据
        if needs_health_max and needs_energy_max:
            # 需要重命名列
            copy_data_sql = """
            INSERT INTO card_data_temp (
                id, name, card_type, character_subtype, element_type, cost, description,
                rarity, version, created_at, updated_at, is_active,
                health, health_max, energy, energy_max, weapon_type, skills, tags, image_url
            )
            SELECT 
                id, name, card_type, character_subtype, element_type, cost, description,
                rarity, version, created_at, updated_at, is_active,
                health, max_health, energy, max_energy, weapon_type, skills, 
                NULL as tags, image_url
            FROM card_data;
            """
        else:
            # 使用现有列名
            copy_data_sql = """
            INSERT INTO card_data_temp (
                id, name, card_type, character_subtype, element_type, cost, description,
                rarity, version, created_at, updated_at, is_active,
                health, health_max, energy, energy_max, weapon_type, skills, tags, image_url
            )
            SELECT 
                id, name, card_type, character_subtype, element_type, cost, description,
                rarity, version, created_at, updated_at, is_active,
                health, health_max, energy, energy_max, weapon_type, skills, 
                tags, image_url
            FROM card_data;
            """
        
        cursor.execute(copy_data_sql)
        print(f"已复制 {cursor.rowcount} 条记录到临时表")
        
        # 删除原表
        cursor.execute("DROP TABLE card_data;")
        print("已删除原表 card_data")
        
        # 重命名临时表
        cursor.execute("ALTER TABLE card_data_temp RENAME TO card_data;")
        print("已重命名临时表为 card_data")
        
        # 创建索引
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_card_name ON card_data(name);")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_card_type ON card_data(card_type);")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_element_type ON card_data(element_type);")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_character_subtype ON card_data(character_subtype);")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_is_active ON card_data(is_active);")
        print("已创建索引")
        
        # 提交更改
        conn.commit()
        
        # 验证迁移结果
        cursor.execute("PRAGMA table_info(card_data)")
        new_columns = [row[1] for row in cursor.fetchall()]
        print(f"迁移后card_data表列: {new_columns}")
        
        expected_cols = ['health_max', 'energy_max', 'tags']
        missing_cols = [col for col in expected_cols if col not in new_columns]
        
        if missing_cols:
            print(f"错误：以下列未成功添加: {missing_cols}")
            return False
        
        print("数据库结构迁移完成！")
        return True
        
    except sqlite3.Error as e:
        print(f"数据库迁移错误: {e}")
        conn.rollback()
        return False
    finally:
        conn.close()

def main():
    print("开始执行数据库结构迁移...")
    print("此脚本将重命名 max_health 为 health_max, max_energy 为 energy_max, 并添加 tags 字段")
    
    success = migrate_database_structure()
    
    if success:
        print("✓ 数据库结构迁移成功完成")
    else:
        print("✗ 数据库结构迁移失败")

if __name__ == "__main__":
    main()