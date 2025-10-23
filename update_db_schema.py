"""
直接执行SQL更新数据库结构
"""
from app import create_app
import sqlite3
import os

def update_database_schema():
    """手动更新数据库模式以添加新列"""
    app = create_app()
    
    # 获取数据库路径
    db_path = app.config['SQLALCHEMY_DATABASE_URI'].replace('sqlite:///', '')
    
    # 连接数据库
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    print(f"更新数据库模式: {db_path}")
    
    # 为card_data表添加新列
    new_card_columns = [
        ('element_type', 'TEXT'),
        ('character_subtype', 'TEXT'), 
        ('health', 'INTEGER'),
        ('health_max', 'INTEGER'),  # 替换原来的max_health
        ('energy', 'INTEGER'),
        ('energy_max', 'INTEGER'),  # 替换原来的max_energy
        ('tags', 'TEXT'),           # 新增tags字段
        ('weapon_type', 'TEXT'),
        ('skills', 'TEXT'),  # SQLite中使用TEXT存储JSON
        ('image_url', 'TEXT')
    ]
    
    for col_name, col_type in new_card_columns:
        try:
            cursor.execute(f"ALTER TABLE card_data ADD COLUMN {col_name} {col_type}")
            print(f"✓ 添加列 {col_name} 到 card_data 表")
        except sqlite3.OperationalError:
            print(f"- 列 {col_name} 已存在于 card_data 表")
    
    # 为decks表添加cards列并删除旧的card_ids列
    try:
        # 检查是否已存在cards列
        cursor.execute("SELECT name FROM pragma_table_info('decks') WHERE name='cards'")
        cards_exists = cursor.fetchone()
        
        if not cards_exists:
            cursor.execute("ALTER TABLE decks ADD COLUMN cards TEXT")  # TEXT存储JSON
            print("✓ 添加列 cards 到 decks 表")
        else:
            print("- 列 cards 已存在于 decks 表")
    except sqlite3.OperationalError as e:
        print(f"错误添加cards列: {e}")
    
    # 提交更改
    conn.commit()
    conn.close()
    
    print("数据库模式更新完成！")

if __name__ == "__main__":
    update_database_schema()