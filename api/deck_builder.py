from flask import Flask
from .deck_builder import deck_builder_bp
from .api_routes import deck_builder_api

# 创建一个函数来注册所有蓝图
def register_deck_builder_routes(app):
    """注册卡组构建器的所有路由"""
    app.register_blueprint(deck_builder_bp)
    app.register_blueprint(deck_builder_api)