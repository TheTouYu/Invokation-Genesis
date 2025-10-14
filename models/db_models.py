"""
七圣召唤数据库模型定义
"""
from datetime import datetime
import uuid
from flask_sqlalchemy import SQLAlchemy

# db 对象将在应用创建后被初始化
db = None

def init_models_db(sqlalchemy_db):
    """
    初始化模型中的 db 对象
    此函数应在应用工厂中调用，以确保模型定义使用正确的 db 实例
    """
    global db
    db = sqlalchemy_db

    # 定义模型类
    class User(db.Model):
        """
        用户模型
        """
        __tablename__ = 'users'

        id = db.Column(db.String, primary_key=True, default=lambda: str(uuid.uuid4()))
        username = db.Column(db.String(80), unique=True, nullable=False)
        email = db.Column(db.String(120), unique=True, nullable=False)
        password_hash = db.Column(db.String(255), nullable=False)
        created_at = db.Column(db.DateTime, default=datetime.utcnow)
        updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
        is_active = db.Column(db.Boolean, default=True)

        # 关联关系
        decks = db.relationship("Deck", back_populates="user")
        # 为 game_histories 关系指定外键，避免歧义
        player1_games = db.relationship("GameHistory", foreign_keys='GameHistory.player1_id', back_populates="player1")
        player2_games = db.relationship("GameHistory", foreign_keys='GameHistory.player2_id', back_populates="player2")
        won_games = db.relationship("GameHistory", foreign_keys='GameHistory.winner_id', back_populates="winner")


    class CardData(db.Model):
        """
        卡牌数据模型
        """
        __tablename__ = 'card_data'

        id = db.Column(db.String, primary_key=True, default=lambda: str(uuid.uuid4()))
        name = db.Column(db.String(100), nullable=False)  # 卡牌名称
        card_type = db.Column(db.String(50), nullable=False)  # 卡牌类型
        sub_type = db.Column(db.String(50))  # 子类型（如武器类型、元素类型等）
        cost = db.Column(db.JSON)  # 费用，存储为JSON格式
        description = db.Column(db.Text)  # 卡牌描述
        character_name = db.Column(db.String(100))  # 角色名称（如果是角色牌或角色装备牌）
        rarity = db.Column(db.Integer)  # 稀有度
        version = db.Column(db.String(20))  # 卡牌版本
        created_at = db.Column(db.DateTime, default=datetime.utcnow)
        updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
        is_active = db.Column(db.Boolean, default=True)
        
        def to_dict(self):
            """将模型实例转换为字典"""
            return {
                'id': self.id,
                'name': self.name,
                'card_type': self.card_type,
                'sub_type': self.sub_type,
                'cost': self.cost,
                'description': self.description,
                'character_name': self.character_name,
                'rarity': self.rarity,
                'version': self.version,
                'created_at': self.created_at.isoformat() if self.created_at else None,
                'updated_at': self.updated_at.isoformat() if self.updated_at else None,
                'is_active': self.is_active
            }


    class Deck(db.Model):
        """
        卡组模型
        """
        __tablename__ = 'decks'

        id = db.Column(db.String, primary_key=True, default=lambda: str(uuid.uuid4()))
        name = db.Column(db.String(100), nullable=False)  # 卡组名称
        user_id = db.Column(db.String, db.ForeignKey('users.id'), nullable=False)  # 所属用户
        card_ids = db.Column(db.JSON)  # 卡牌ID列表，存储为JSON格式
        is_public = db.Column(db.Boolean, default=False)  # 是否公开
        created_at = db.Column(db.DateTime, default=datetime.utcnow)
        updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
        description = db.Column(db.Text)  # 卡组描述

        # 关联关系
        user = db.relationship("User", back_populates="decks")
        game_histories_as_deck1 = db.relationship("GameHistory", foreign_keys="GameHistory.deck1_id", back_populates="deck1")
        game_histories_as_deck2 = db.relationship("GameHistory", foreign_keys="GameHistory.deck2_id", back_populates="deck2")


    class GameHistory(db.Model):
        """
        游戏历史记录模型
        """
        __tablename__ = 'game_histories'

        id = db.Column(db.String, primary_key=True, default=lambda: str(uuid.uuid4()))
        player1_id = db.Column(db.String, db.ForeignKey('users.id'), nullable=False)  # 玩家1
        player2_id = db.Column(db.String, db.ForeignKey('users.id'), nullable=False)  # 玩家2
        winner_id = db.Column(db.String, db.ForeignKey('users.id'))  # 获胜者
        deck1_id = db.Column(db.String, db.ForeignKey('decks.id'))  # 玩家1使用的卡组
        deck2_id = db.Column(db.String, db.ForeignKey('decks.id'))  # 玩家2使用的卡组
        game_data = db.Column(db.JSON)  # 完整游戏数据，存储为JSON格式
        game_result = db.Column(db.String(50))  # 游戏结果
        duration = db.Column(db.Integer)  # 游戏时长(秒)
        created_at = db.Column(db.DateTime, default=datetime.utcnow)
        updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

        # 关联关系
        player1 = db.relationship("User", foreign_keys=[player1_id], back_populates="player1_games")
        player2 = db.relationship("User", foreign_keys=[player2_id], back_populates="player2_games")
        winner = db.relationship("User", foreign_keys=[winner_id], back_populates="won_games")
        deck1 = db.relationship("Deck", foreign_keys=[deck1_id], back_populates="game_histories_as_deck1")
        deck2 = db.relationship("Deck", foreign_keys=[deck2_id], back_populates="game_histories_as_deck2")

    # 将模型类设置为模块属性，以便其他模块可以导入
    globals()['User'] = User
    globals()['CardData'] = CardData
    globals()['Deck'] = Deck
    globals()['GameHistory'] = GameHistory