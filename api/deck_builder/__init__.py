from flask import Blueprint, render_template_string
from .templates import DECK_BUILDER_TEMPLATE
from .api_routes import deck_builder_api

# 主要的Blueprint，包含页面路由
deck_builder_bp = Blueprint("deck_builder", __name__)


@deck_builder_bp.route("/deck-builder")
def deck_builder_page():
    """Serve the deck builder HTML page"""
    return render_template_string(DECK_BUILDER_TEMPLATE)


# 导入API路由
from . import api_routes


def register_deck_builder_routes(app):
    """注册卡组构建器的所有路由"""
    app.register_blueprint(deck_builder_bp)
    app.register_blueprint(deck_builder_api)

