"""
测试数据库管理器功能
"""
import pytest
from database_manager import db_manager
from flask import Flask
from werkzeug.security import generate_password_hash


def test_database_manager_initialization():
    """测试数据库管理器初始化"""
    app = Flask(__name__)
    app.config['TESTING'] = True
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///:memory:'
    
    # 初始化数据库管理器
    db_instance = db_manager.init_app(app)
    
    assert db_instance is not None


def test_database_manager_get_db():
    """测试获取数据库实例"""
    app = Flask(__name__)
    app.config['TESTING'] = True
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///:memory:'
    
    # 初始化数据库管理器
    db_instance = db_manager.init_app(app)
    
    # 获取数据库实例
    retrieved_db = db_manager.get_db()
    
    assert retrieved_db is not None
    assert retrieved_db == db_instance


def test_database_manager_create_tables():
    """测试创建表功能"""
    app = Flask(__name__)
    app.config['TESTING'] = True
    app.config['ENV'] = 'development'  # 允许在非生产环境创建表
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///:memory:'
    
    # 初始化数据库管理器
    db_instance = db_manager.init_app(app)
    
    # 创建表
    db_manager.create_tables(app)
    
    # 测试是否可以创建用户
    with app.app_context():
        from models.db_models import init_models_db
        init_models_db(db_instance)
        
        # 动态导入模型
        from models.db_models import User
        
        # 尝试创建一个用户
        user = User(
            username='testuser',
            email='test@example.com',
            password_hash=generate_password_hash('password123')
        )
        
        db_instance.session.add(user)
        db_instance.session.commit()
        
        # 验证用户已创建
        retrieved_user = User.query.filter_by(username='testuser').first()
        assert retrieved_user is not None
        assert retrieved_user.username == 'testuser'
        assert isinstance(retrieved_user.id, str)  # ID 应该是字符串类型