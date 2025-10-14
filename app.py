from flask import Flask, jsonify
import logging
from flask_cors import CORS
from flask_jwt_extended import JWTManager
from flask_sqlalchemy import SQLAlchemy
from flask_socketio import SocketIO
import os

# 初始化扩展
db = SQLAlchemy()
socketio = SocketIO(cors_allowed_origins="*")

def create_app():
    app = Flask(__name__)
    
    # 配置
    app.config['JWT_SECRET_KEY'] = os.environ.get('JWT_SECRET_KEY', 'super-secret-key-for-development')
    app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get('DATABASE_URL', 'sqlite:///game.db')
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    
    # 初始化扩展
    CORS(app)  # 启用CORS
    jwt = JWTManager(app)
    db.init_app(app)
    socketio.init_app(app)
    
    # 配置日志
    logging.basicConfig(level=logging.INFO)
    
    # 在应用上下文中导入模型和蓝图
    with app.app_context():
        # 初始化模型中的 db 实例
        from models.db_models import init_models_db
        init_models_db(db)

        # 导入模型以确保它们被注册到 SQLAlchemy
        from models.db_models import User, CardData, Deck, GameHistory
        
        # 导入并注册蓝图
        try:
            from api.auth import auth_bp
            app.register_blueprint(auth_bp, url_prefix='/api/auth')
        except ImportError as e:
            logging.warning(f"Could not import auth blueprint: {e}")
        
        try:
            from api.cards import cards_bp
            app.register_blueprint(cards_bp, url_prefix='/api')
        except ImportError as e:
            logging.warning(f"Could not import cards blueprint: {e}")
        
        try:
            from api.local_game import local_game_bp
            app.register_blueprint(local_game_bp, url_prefix='/api/local-game')
        except ImportError as e:
            logging.warning(f"Could not import local game blueprint: {e}")

    # API endpoints for character data
    try:
        from api.characters_parse import fetch_html, parse_characters
        from api.parse_equipment import parse_equipments
        from api.parse_supports import parse_supports
        from api.parse_events import parse_events
        
        TARGET_JS_URL = "https://wiki.biligame.com/ys/%E5%8D%A1%E7%89%8C%E4%B8%80%E8%A7%88"

        @app.route("/api/characters", methods=["GET"])
        def get_characters():
            try:
                html = fetch_html(TARGET_JS_URL)
                data = parse_characters(html)
                return jsonify(data)
            except Exception as e:
                logging.exception("API 处理异常")
                return jsonify({"error": str(e)}), 500

        @app.route("/api/equipments")
        def get_equipments():
            try:
                html = fetch_html(TARGET_JS_URL)
                return jsonify(parse_equipments(html))
            except Exception as e:
                logging.exception("装备解析失败")
                return jsonify({"error": str(e)}), 500

        @app.route('/api/supports')
        def get_supports():
            try:
                html = fetch_html(TARGET_JS_URL)
                return jsonify(parse_supports(html))
            except Exception as e:
                logging.exception("支援牌解析失败")
                return jsonify({"error": str(e)}), 500

        @app.route('/api/events')
        def get_events():
            try:
                html = fetch_html(TARGET_JS_URL)
                return jsonify(parse_events(html))
            except Exception as e:
                logging.exception("事件牌解析失败")
                return jsonify({"error": str(e)}), 500
    except ImportError as e:
        logging.warning(f"Some parsing modules could not be loaded: {e}")

    @app.route('/health', methods=['GET'])
    def health_check():
        return jsonify({"status": "healthy", "message": "七圣召唤游戏服务器运行正常"}), 200

    return app

# 创建应用实例
app = create_app()

if __name__ == "__main__":
    with app.app_context():
        db.create_all()  # 创建数据库表
    socketio.run(app, host="0.0.0.0", port=5000, debug=True)
