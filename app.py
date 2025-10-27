from flask import Flask, jsonify, request, g
import logging
import uuid
from flask_cors import CORS
from flask_jwt_extended import JWTManager
from flask_socketio import SocketIO
import os

# 导入数据库管理器
from database_manager import db_manager

socketio = SocketIO(cors_allowed_origins="*")


def create_app():
    app = Flask(__name__)

    # 配置 - let database manager handle the database URI
    app.config["JWT_SECRET_KEY"] = os.environ.get(
        "JWT_SECRET_KEY", "super-secret-key-for-development"
    )
    app.config["JWT_ACCESS_TOKEN_EXPIRES"] = 7 * 24 * 60 * 60  # 一周（以秒为单位）
    app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

    # 初始化数据库管理器
    db = db_manager.init_app(app)

    # 初始化其他扩展
    CORS(app)  # 启用CORS
    jwt = JWTManager(app)
    socketio.init_app(app)

    # 配置日志
    logging.basicConfig(level=logging.INFO)

    # 导入日志工具
    from utils.logger import (
        RequestIdFilter,
        add_request_id_to_context,
        setup_sqlalchemy_logger,
        CustomFormatter,
    )

    # 为根记录器添加request_id过滤器
    request_id_filter = RequestIdFilter()
    logging.getLogger().addFilter(request_id_filter)

    # 为根记录器设置自定义格式化器
    formatter = CustomFormatter(
        "%(asctime)s - %(name)s - %(levelname)s - [Request-ID: %(request_id)s] - %(message)s"
    )
    for handler in logging.getLogger().handlers:
        handler.setFormatter(formatter)

    # 为Flask的app logger也添加过滤器和格式化器
    app.logger.addFilter(request_id_filter)
    for handler in app.logger.handlers:
        handler.setFormatter(formatter)

    # 在应用上下文中添加中间件
    @app.before_request
    def add_request_id():
        add_request_id_to_context()
        # 确保当前请求ID在上下文中可用
        from utils.logger import _request_id_var

        request_id = getattr(g, "request_id", "N/A")
        print(f"set logging request_id: {request_id}")
        _request_id_var.set(request_id)
        # 设置SQLAlchemy日志记录器，包含request_id
        setup_sqlalchemy_logger()

    @app.before_request
    def log_request_info():
        app.logger.info(
            f"Request: {request.method} {request.url}, Headers: {dict(request.headers)}"
        )

    @app.after_request
    def log_response_info(response):
        app.logger.info(
            f"Response: Status {response.status_code}, Content-Type: {response.content_type}"
        )
        return response

    # 在应用上下文中导入模型和蓝图
    with app.app_context():
        # 初始化模型中的 db 实例（如果尚未初始化）
        from models.db_models import init_models_db, model_container

        init_models_db(db)

        # 更新模块中的模型引用
        from models import db_models

        db_models.User = model_container.User
        db_models.CardData = model_container.CardData
        db_models.Deck = model_container.Deck
        db_models.GameHistory = model_container.GameHistory

        # 导入模型以确保它们被注册到 SQLAlchemy
        User = model_container.User
        CardData = model_container.CardData
        Deck = model_container.Deck
        GameHistory = model_container.GameHistory

        # 直接为SQLAlchemy引擎的日志记录器设置RequestIdFilter
        from utils.logger import RequestIdFilter
        import logging as log_module

        # 获取SQLAlchemy引擎的日志记录器
        sql_logger = log_module.getLogger("sqlalchemy.engine")

        # 确保只有一个RequestIdFilter实例
        existing_filters = [
            f for f in sql_logger.filters if isinstance(f, RequestIdFilter)
        ]
        if not existing_filters:
            # 添加RequestIdFilter到SQLAlchemy日志记录器
            sql_logger.addFilter(RequestIdFilter())

        # 为SQLAlchemy引擎的日志记录器设置自定义格式化器
        from utils.logger import CustomFormatter

        formatter = CustomFormatter(
            "%(asctime)s - %(name)s - %(levelname)s - [Request-ID: %(request_id)s] - %(message)s"
        )
        for handler in sql_logger.handlers:
            handler.setFormatter(formatter)

        # 导入并注册蓝图
        try:
            from api.auth import auth_bp

            app.register_blueprint(auth_bp, url_prefix="/api/auth")
        except ImportError as e:
            logging.warning(f"Could not import auth blueprint: {e}")

        # 使用新的标准化API蓝图 (v2)
        try:
            from api.v2.cards import cards_bp

            app.register_blueprint(cards_bp, url_prefix="/api/v2")
        except ImportError as e:
            logging.error(f"Could not import standardized cards blueprint: {e}")

        # 使用新的API v2蓝图 - modularized version
        try:
            from api.v2 import api_v2_bp

            app.register_blueprint(api_v2_bp, url_prefix="/api")
        except ImportError as e:
            logging.error(f"Could not import API v2 blueprint: {e}")

        # 使用新的集成过滤器API蓝图
        try:
            from api.filters_integrated import filters_bp

            app.register_blueprint(filters_bp, url_prefix="/api")
        except ImportError as e:
            logging.error(f"Could not import filters blueprint: {e}")

        try:
            from api.local_game import local_game_bp

            app.register_blueprint(local_game_bp, url_prefix="/api")
        except ImportError as e:
            logging.warning(f"Could not import local game blueprint: {e}")

        try:
            from api.users import users_bp

            app.register_blueprint(users_bp, url_prefix="/api")
        except ImportError as e:
            logging.warning(f"Could not import users blueprint: {e}")

        try:
            from api.deck_builder import register_deck_builder_routes

            register_deck_builder_routes(app)
        except ImportError as e:
            logging.warning(f"Could not import deck builder blueprint: {e}")

    @app.route("/health", methods=["GET"])
    def health_check():
        return jsonify(
            {"status": "healthy", "message": "七圣召唤游戏服务器运行正常"}
        ), 200

    @app.route("/api/test", methods=["GET"])
    def api_test_page():
        """提供API测试页面"""
        import os
        from flask import send_from_directory

        # 使用绝对路径确保文件可以被找到
        modules_dir = os.path.join(
            os.path.dirname(os.path.abspath(__file__)), "modules", "api_test"
        )
        return send_from_directory(modules_dir, "index.html")

    @app.route("/game/test", methods=["GET"])
    def game_api_test_page():
        """提供游戏API测试页面"""
        import os
        from flask import send_from_directory

        # 使用绝对路径确保文件可以被找到
        modules_dir = os.path.join(
            os.path.dirname(os.path.abspath(__file__)), "modules", "game_test"
        )
        return send_from_directory(modules_dir, "index.html")

    # 静态文件路由
    @app.route("/modules/<path:filename>")
    def modules_static(filename):
        from flask import send_from_directory

        return send_from_directory("modules", filename)

    # 游戏测试静态文件路由
    @app.route("/game_test_static/<path:filename>")
    def game_test_static(filename):
        from flask import send_from_directory

        return send_from_directory("modules/game_test", filename)

    # API测试静态文件路由
    @app.route("/api_test_static/<path:filename>")
    def api_test_static(filename):
        from flask import send_from_directory

        return send_from_directory("modules/api_test", filename)

    # Deck构建静态文件路由
    @app.route("/deck_build_static/<path:filename>")
    def deck_build_static(filename):
        from flask import send_from_directory

        return send_from_directory("modules/deck-build", filename)

    return app


# 应用实例在运行时创建，而不是在导入时创建
if __name__ == "__main__":
    app = create_app()
    socketio.run(app, host="0.0.0.0", port=5000, debug=True)
