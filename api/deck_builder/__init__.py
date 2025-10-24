"""
模块化的卡组构建器蓝图
"""
from flask import Blueprint, render_template_string
import os
from .api_routes import deck_builder_api

# 创建蓝图
deck_builder_bp = Blueprint('deck_builder', __name__)

# 从文件中读取HTML模板
def get_deck_builder_template():
    template_path = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), 'modules', 'deck-build', 'index.html')
    with open(template_path, 'r', encoding='utf-8') as f:
        return f.read()

@deck_builder_bp.route("/deck-builder")
def deck_builder_page():
    template = get_deck_builder_template()
    return render_template_string(template)

def register_deck_builder_routes(app):
    """注册卡组构建器蓝图"""
    app.register_blueprint(deck_builder_bp)
    app.register_blueprint(deck_builder_api)