"""
API v2 - 统一入口
将所有模块化组件整合到一个蓝图中
"""
from flask import Blueprint
from .cards import cards_bp
from .characters import characters_bp
from .equipments import equipments_bp
from .supports import supports_bp
from .events import events_bp
from .decks import decks_bp


# 创建API v2的主蓝图
api_v2_bp = Blueprint("api_v2", __name__)

# 注册所有子蓝图
api_v2_bp.register_blueprint(cards_bp)
api_v2_bp.register_blueprint(characters_bp)
api_v2_bp.register_blueprint(equipments_bp)
api_v2_bp.register_blueprint(supports_bp)
api_v2_bp.register_blueprint(events_bp)
api_v2_bp.register_blueprint(decks_bp)