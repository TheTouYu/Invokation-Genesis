"""
数据库迁移脚本 - 更新表结构
"""
from app import create_app, db
import sqlite3
import os

def migrate_database():
    """迁移数据库以更新表结构"""
    app = create_app()
    
    with app.app_context():
        # 创建所有表（如果不存在）
        db.create_all()
        
        # 连接到SQLite数据库
        database_path = app.config['SQLALCHEMY_DATABASE_URI'].replace('sqlite:///', '')
        conn = sqlite3.connect(database_path)
        cursor = conn.cursor()
        
        try:
            # 检查card_data表是否已有element_type列
            cursor.execute("PRAGMA table_info(card_data)")
            columns = [column[1] for column in cursor.fetchall()]
            
            if 'element_type' not in columns:
                print("添加element_type列到card_data表...")
                cursor.execute("ALTER TABLE card_data ADD COLUMN element_type TEXT")
            
            if 'character_subtype' not in columns:
                print("添加character_subtype列到card_data表...")
                cursor.execute("ALTER TABLE card_data ADD COLUMN character_subtype TEXT")
                
            if 'health' not in columns:
                print("添加health列到card_data表...")
                cursor.execute("ALTER TABLE card_data ADD COLUMN health INTEGER")
                
            if 'health_max' not in columns:
                print("添加health_max列到card_data表...")  # 替换原来的max_health
                cursor.execute("ALTER TABLE card_data ADD COLUMN health_max INTEGER")
                
            if 'energy' not in columns:
                print("添加energy列到card_data表...")
                cursor.execute("ALTER TABLE card_data ADD COLUMN energy INTEGER")
                
            if 'energy_max' not in columns:
                print("添加energy_max列到card_data表...")  # 替换原来的max_energy
                cursor.execute("ALTER TABLE card_data ADD COLUMN energy_max INTEGER")
                
            if 'tags' not in columns:
                print("添加tags列到card_data表...")  # 新增字段
                cursor.execute("ALTER TABLE card_data ADD COLUMN tags JSON")
                
            if 'weapon_type' not in columns:
                print("添加weapon_type列到card_data表...")
                cursor.execute("ALTER TABLE card_data ADD COLUMN weapon_type TEXT")
                
            if 'skills' not in columns:
                print("添加skills列到card_data表...")
                cursor.execute("ALTER TABLE card_data ADD COLUMN skills JSON")
                
            if 'image_url' not in columns:
                print("添加image_url列到card_data表...")
                cursor.execute("ALTER TABLE card_data ADD COLUMN image_url TEXT")
            
            # 检查decks表是否已有cards列
            cursor.execute("PRAGMA table_info(decks)")
            deck_columns = [column[1] for column in cursor.fetchall()]
            
            if 'card_ids' in deck_columns and 'cards' not in deck_columns:
                print("重命名card_ids列到cards...")
                # SQLite不支持直接重命名列，我们需要创建新表
                cursor.execute("""
                    CREATE TABLE decks_new (
                        id TEXT PRIMARY KEY,
                        name TEXT NOT NULL,
                        user_id TEXT NOT NULL,
                        cards JSON,
                        is_public BOOLEAN DEFAULT 0,
                        created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                        updated_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                        description TEXT,
                        FOREIGN KEY (user_id) REFERENCES users (id)
                    )
                """)
                
                # 复制数据
                cursor.execute("""
                    INSERT INTO decks_new (id, name, user_id, cards, is_public, created_at, updated_at, description)
                    SELECT id, name, user_id, card_ids, is_public, created_at, updated_at, description
                    FROM decks
                """)
                
                # 删除旧表并重命名新表
                cursor.execute("DROP TABLE decks")
                cursor.execute("ALTER TABLE decks_new RENAME TO decks")
                
            elif 'cards' not in deck_columns:
                print("添加cards列到decks表...")
                cursor.execute("ALTER TABLE decks ADD COLUMN cards JSON")
            
            # 提交更改
            conn.commit()
            print("数据库迁移完成！")
            
        except sqlite3.OperationalError as e:
            print(f"数据库操作错误: {e}")
            print("可能是表已经存在所需的列")
        
        finally:
            conn.close()

if __name__ == "__main__":
    print("开始数据库迁移...")
    migrate_database()
    print("迁移完成！请重启服务器以应用更改。")