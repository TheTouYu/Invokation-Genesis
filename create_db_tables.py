"""
手动创建数据库表
"""
from app import create_app
from models.db_models import db
from sqlalchemy import text

def create_tables_manually():
    """手动创建数据库表"""
    # 首先确保没有初始化过的标记
    from models.db_models import _initialized
    print(f"模型初始化标记: {_initialized}")
    
    app = create_app()
    
    print(f"数据库URI: {app.config['SQLALCHEMY_DATABASE_URI']}")
    
    with app.app_context():
        # 确认模型已初始化
        from models.db_models import User, CardData, Deck, GameHistory
        print("模型类导入成功")
        
        # 创建所有表
        db.create_all()
        print("尝试创建表...")
        
        # 验证表是否创建成功
        result = db.session.execute(text('SELECT name FROM sqlite_master WHERE type="table"'))
        tables = [row[0] for row in result]
        print(f"数据库中的表: {tables}")
        
        # 验证特定表的结构
        if 'card_data' in tables:
            result = db.session.execute(text('PRAGMA table_info(card_data)'))
            columns = [row[1] for row in result]  # 列名在第二列
            print(f"card_data表的列: {columns}")
        
        if 'decks' in tables:
            result = db.session.execute(text('PRAGMA table_info(decks)'))
            columns = [row[1] for row in result]
            print(f"decks表的列: {columns}")

if __name__ == "__main__":
    create_tables_manually()