"""
七圣召唤数据库模型定义
"""
from datetime import datetime
import uuid
from flask_sqlalchemy import SQLAlchemy

# db 对象将在应用创建后被初始化
# 为了避免循环导入，使用延迟初始化模式
class ModelContainer:
    def __init__(self):
        self.db = None
        self.User = None
        self.CardData = None
        self.Deck = None
        self.GameHistory = None
        self._initialized = False

    def init_models_db(self, sqlalchemy_db):
        """
        初始化模型中的 db 对象
        此函数应在应用工厂中调用，以确保模型定义使用正确的 db 实例
        """
        if self._initialized:
            return  # 已经初始化过了，直接返回

        self._initialized = True
        self.db = sqlalchemy_db

        # 定义模型类
        class User(sqlalchemy_db.Model):
            """
            用户模型
            """
            __tablename__ = 'users'

            id = sqlalchemy_db.Column(sqlalchemy_db.String, primary_key=True, default=lambda: str(uuid.uuid4()))
            username = sqlalchemy_db.Column(sqlalchemy_db.String(80), unique=True, nullable=False, index=True)
            email = sqlalchemy_db.Column(sqlalchemy_db.String(120), unique=True, nullable=False, index=True)
            password_hash = sqlalchemy_db.Column(sqlalchemy_db.String(255), nullable=False)
            created_at = sqlalchemy_db.Column(sqlalchemy_db.DateTime, default=datetime.utcnow, index=True)
            updated_at = sqlalchemy_db.Column(sqlalchemy_db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
            is_active = sqlalchemy_db.Column(sqlalchemy_db.Boolean, default=True, index=True)

            # 关联关系
            decks = sqlalchemy_db.relationship("Deck", back_populates="user")
            # 为 game_histories 关系指定外键，避免歧义
            player1_games = sqlalchemy_db.relationship("GameHistory", foreign_keys='GameHistory.player1_id', back_populates="player1")
            player2_games = sqlalchemy_db.relationship("GameHistory", foreign_keys='GameHistory.player2_id', back_populates="player2")
            won_games = sqlalchemy_db.relationship("GameHistory", foreign_keys='GameHistory.winner_id', back_populates="winner")


        class CardData(sqlalchemy_db.Model):
            """
            卡牌数据模型
            """
            __tablename__ = 'card_data'

            id = sqlalchemy_db.Column(sqlalchemy_db.String, primary_key=True, default=lambda: str(uuid.uuid4()))
            name = sqlalchemy_db.Column(sqlalchemy_db.String(100), nullable=False, index=True)  # 卡牌名称
            card_type = sqlalchemy_db.Column(sqlalchemy_db.String(50), nullable=False, index=True)  # 卡牌类型
            character_subtype = sqlalchemy_db.Column(sqlalchemy_db.String(50), index=True)  # 子类型（如武器类型、元素类型等）
            element_type = sqlalchemy_db.Column(sqlalchemy_db.String(50), index=True)  # 元素类型
            cost = sqlalchemy_db.Column(sqlalchemy_db.JSON)  # 费用，存储为JSON格式
            description = sqlalchemy_db.Column(sqlalchemy_db.Text)  # 卡牌描述
            rarity = sqlalchemy_db.Column(sqlalchemy_db.Integer, index=True)  # 稀有度
            version = sqlalchemy_db.Column(sqlalchemy_db.String(20))  # 卡牌版本
            created_at = sqlalchemy_db.Column(sqlalchemy_db.DateTime, default=datetime.utcnow, index=True)
            updated_at = sqlalchemy_db.Column(sqlalchemy_db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
            is_active = sqlalchemy_db.Column(sqlalchemy_db.Boolean, default=True, index=True)
            # 角色卡特定字段
            health = sqlalchemy_db.Column(sqlalchemy_db.Integer)
            health_max = sqlalchemy_db.Column(sqlalchemy_db.Integer)  # 替换原来的max_health
            energy = sqlalchemy_db.Column(sqlalchemy_db.Integer)
            energy_max = sqlalchemy_db.Column(sqlalchemy_db.Integer)  # 替换原来的max_energy
            weapon_type = sqlalchemy_db.Column(sqlalchemy_db.String(50))
            skills = sqlalchemy_db.Column(sqlalchemy_db.JSON)
            tags = sqlalchemy_db.Column(sqlalchemy_db.JSON)  # 新增tags字段
            image_url = sqlalchemy_db.Column(sqlalchemy_db.String(255))
            country = sqlalchemy_db.Column(sqlalchemy_db.String(50), index=True)  # 国家/地区

            
            def to_dict(self):
                """将模型实例转换为字典"""
                return {
                    'id': self.id,
                    'name': self.name,
                    'card_type': self.card_type,
                    'element_type': self.element_type,
                    'cost': self.cost,
                    'description': self.description,
                    'character_subtype': self.character_subtype,
                    'rarity': self.rarity,
                    'version': self.version,
                    'created_at': self.created_at.isoformat() if self.created_at else None,
                    'updated_at': self.updated_at.isoformat() if self.updated_at else None,
                    'is_active': self.is_active,
                    # 角色卡特定字段
                    'health': self.health,
                    'health_max': self.health_max,  # 替换原来的max_health
                    'energy': self.energy,
                    'energy_max': self.energy_max,  # 替换原来的max_energy
                    'weapon_type': self.weapon_type,
                    'skills': self.skills,
                    'tags': self.tags,  # 新增tags字段
                    'image_url': self.image_url,
                    'country': self.country  # 国家/地区
                }


        class Deck(sqlalchemy_db.Model):
            """
            卡组模型
            """
            __tablename__ = 'decks'

            id = sqlalchemy_db.Column(sqlalchemy_db.String, primary_key=True, default=lambda: str(uuid.uuid4()))
            name = sqlalchemy_db.Column(sqlalchemy_db.String(100), nullable=False)  # 卡组名称
            user_id = sqlalchemy_db.Column(sqlalchemy_db.String, sqlalchemy_db.ForeignKey('users.id'), nullable=False, index=True)  # 所属用户
            cards = sqlalchemy_db.Column(sqlalchemy_db.JSON)  # 卡牌ID列表，存储为JSON格式
            is_public = sqlalchemy_db.Column(sqlalchemy_db.Boolean, default=False, index=True)  # 是否公开
            created_at = sqlalchemy_db.Column(sqlalchemy_db.DateTime, default=datetime.utcnow, index=True)
            updated_at = sqlalchemy_db.Column(sqlalchemy_db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
            description = sqlalchemy_db.Column(sqlalchemy_db.Text)  # 卡组描述

            # 关联关系
            user = sqlalchemy_db.relationship("User", back_populates="decks")
            game_histories_as_deck1 = sqlalchemy_db.relationship("GameHistory", foreign_keys="GameHistory.deck1_id", back_populates="deck1")
            game_histories_as_deck2 = sqlalchemy_db.relationship("GameHistory", foreign_keys="GameHistory.deck2_id", back_populates="deck2")


        class GameHistory(sqlalchemy_db.Model):
            """
            游戏历史记录模型
            """
            __tablename__ = 'game_histories'

            id = sqlalchemy_db.Column(sqlalchemy_db.String, primary_key=True, default=lambda: str(uuid.uuid4()))
            player1_id = sqlalchemy_db.Column(sqlalchemy_db.String, sqlalchemy_db.ForeignKey('users.id'), nullable=False, index=True)  # 玩家1
            player2_id = sqlalchemy_db.Column(sqlalchemy_db.String, sqlalchemy_db.ForeignKey('users.id'), nullable=False, index=True)  # 玩家2
            winner_id = sqlalchemy_db.Column(sqlalchemy_db.String, sqlalchemy_db.ForeignKey('users.id'), index=True)  # 获胜者
            deck1_id = sqlalchemy_db.Column(sqlalchemy_db.String, sqlalchemy_db.ForeignKey('decks.id'), index=True)  # 玩家1使用的卡组
            deck2_id = sqlalchemy_db.Column(sqlalchemy_db.String, sqlalchemy_db.ForeignKey('decks.id'), index=True)  # 玩家2使用的卡组
            game_data = sqlalchemy_db.Column(sqlalchemy_db.JSON)  # 完整游戏数据，存储为JSON格式
            game_result = sqlalchemy_db.Column(sqlalchemy_db.String(50), index=True)  # 游戏结果
            duration = sqlalchemy_db.Column(sqlalchemy_db.Integer)  # 游戏时长(秒)
            created_at = sqlalchemy_db.Column(sqlalchemy_db.DateTime, default=datetime.utcnow, index=True)
            updated_at = sqlalchemy_db.Column(sqlalchemy_db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

            # 关联关系
            player1 = sqlalchemy_db.relationship("User", foreign_keys=[player1_id], back_populates="player1_games")
            player2 = sqlalchemy_db.relationship("User", foreign_keys=[player2_id], back_populates="player2_games")
            winner = sqlalchemy_db.relationship("User", foreign_keys=[winner_id], back_populates="won_games")
            deck1 = sqlalchemy_db.relationship("Deck", foreign_keys=[deck1_id], back_populates="game_histories_as_deck1")
            deck2 = sqlalchemy_db.relationship("Deck", foreign_keys=[deck2_id], back_populates="game_histories_as_deck2")

        # 将模型类设置为容器属性
        self.User = User
        self.CardData = CardData
        self.Deck = Deck
        self.GameHistory = GameHistory


# 创建模型容器实例
model_container = ModelContainer()

# 为了向后兼容，暴露初始化函数和模型类
init_models_db = model_container.init_models_db
User = model_container.User
CardData = model_container.CardData
Deck = model_container.Deck
GameHistory = model_container.GameHistory