from flask import Flask, jsonify
import logging
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
    app.config['JWT_SECRET_KEY'] = os.environ.get('JWT_SECRET_KEY', 'super-secret-key-for-development')
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    
    # 初始化数据库管理器
    db = db_manager.init_app(app)
    
    # 初始化其他扩展
    CORS(app)  # 启用CORS
    jwt = JWTManager(app)
    socketio.init_app(app)
    
    # 配置日志
    logging.basicConfig(level=logging.INFO)
    
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
        
        # 导入并注册蓝图
        try:
            from api.auth import auth_bp
            app.register_blueprint(auth_bp, url_prefix='/api/auth')
        except ImportError as e:
            logging.warning(f"Could not import auth blueprint: {e}")
        
        # 使用新的标准化API蓝图
        try:
            from api.standardized_cards import cards_bp
            app.register_blueprint(cards_bp, url_prefix='/api')
        except ImportError as e:
            logging.error(f"Could not import standardized cards blueprint: {e}")
        
        try:
            from api.local_game import local_game_bp
            app.register_blueprint(local_game_bp, url_prefix='/api')
        except ImportError as e:
            logging.warning(f"Could not import local game blueprint: {e}")
        
        try:
            from api.deck_builder import register_deck_builder_routes
            register_deck_builder_routes(app)
        except ImportError as e:
            logging.warning(f"Could not import deck builder blueprint: {e}")

    @app.route('/health', methods=['GET'])
    def health_check():
        return jsonify({"status": "healthy", "message": "七圣召唤游戏服务器运行正常"}), 200

    @app.route('/api/test', methods=['GET'])
    def api_test_page():
        """提供API测试页面"""
        test_page_html = '''
<!DOCTYPE html>
<html lang="zh-CN">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>七圣召唤API测试页面</title>
    <style>
        body {
            font-family: Arial, sans-serif;
            max-width: 1200px;
            margin: 0 auto;
            padding: 20px;
            background-color: #f5f5f5;
        }
        .container {
            background-color: white;
            padding: 20px;
            border-radius: 8px;
            box-shadow: 0 2px 10px rgba(0,0,0,0.1);
        }
        h1 {
            color: #333;
            text-align: center;
        }
        .section {
            margin: 20px 0;
            padding: 15px;
            border: 1px solid #ddd;
            border-radius: 5px;
            background-color: #fafafa;
        }
        input, button {
            padding: 8px;
            margin: 5px;
            border: 1px solid #ccc;
            border-radius: 4px;
        }
        button {
            background-color: #4CAF50;
            color: white;
            cursor: pointer;
        }
        button:hover {
            background-color: #45a049;
        }
        .result {
            margin-top: 10px;
            padding: 10px;
            background-color: #f9f9f9;
            border: 1px solid #ddd;
            border-radius: 4px;
            white-space: pre-wrap;
            word-wrap: break-word;
            max-height: 400px;
            overflow-y: auto;
        }
        .token-section {
            background-color: #e8f5e8;
        }
        .info-box {
            background-color: #d4edda;
            border: 1px solid #c3e6cb;
            border-radius: 4px;
            padding: 10px;
            margin: 10px 0;
        }
        .error {
            color: #721c24;
            background-color: #f8d7da;
            border: 1px solid #f5c6cb;
            padding: 10px;
            border-radius: 4px;
            margin: 10px 0;
        }
        .success {
            color: #155724;
            background-color: #d4edda;
            border: 1px solid #c3e6cb;
            padding: 10px;
            border-radius: 4px;
            margin: 10px 0;
        }
    </style>
</head>
<body>
    <div class="container">
        <h1>七圣召唤 API 测试页面</h1>
        
        <div class="info-box">
            <strong>提示：</strong>运行 <code>uv run python dev_tools/generate_test_token.py</code> 生成测试令牌
        </div>
        
        <div class="section token-section">
            <h3>1. 设置JWT令牌</h3>
            <p>在下方输入您的JWT认证令牌：</p>
            <input type="text" id="jwtToken" placeholder="输入JWT令牌..." style="width: 80%;">
            <button onclick="testToken()">验证令牌</button>
        </div>

        <div class="section">
            <h3>2. 测试API端点</h3>
            
            <div>
                <h4>健康检查</h4>
                <button onclick="testHealth()">测试健康检查</button>
            </div>
            
            <div>
                <h4>获取卡牌</h4>
                <label>每页数量: <input type="number" id="per_page" value="5" min="1" max="50"></label>
                <label>类型: <select id="card_type"><option value="">所有类型</option><option value="角色牌">角色牌</option><option value="事件牌">事件牌</option></select></label>
                <button onclick="getCards()">获取卡牌</button>
            </div>
            
            <div>
                <h4>获取角色卡</h4>
                <label>每页数量: <input type="number" id="char_per_page" value="5" min="1" max="50"></label>
                <button onclick="getCharacterCards()">获取角色卡</button>
            </div>
            
            <div>
                <h4>获取事件卡</h4>
                <label>每页数量: <input type="number" id="event_per_page" value="5" min="1" max="50"></label>
                <button onclick="getEventCards()">获取事件卡</button>
            </div>
            
            <div>
                <h4>获取用户卡组</h4>
                <button onclick="getUserDecks()">获取卡组</button>
            </div>
        </div>

        <div class="section">
            <h3>3. 测试结果</h3>
            <div id="result" class="result">测试结果将显示在这里...</div>
        </div>
    </div>

    <script>
        const baseURL = window.location.origin;

        // 验证令牌格式
        function isValidJWT(token) {
            if (!token) return false;
            // 检查是不是基本的JWT格式 (3个部分用点分隔)
            const parts = token.split('.');
            return parts.length === 3;
        }

        // 验证令牌
        function testToken() {
            const token = document.getElementById('jwtToken').value;
            const resultDiv = document.getElementById('result');
            
            if (!token) {
                resultDiv.innerHTML = '<div class="error">请先输入JWT令牌！</div>';
                return;
            }
            
            if (!isValidJWT(token)) {
                resultDiv.innerHTML = '<div class="error">JWT令牌格式不正确！请确保令牌包含3个用点分隔的部分。</div>';
                return;
            }
            
            // 尝试访问一个需要认证的端点来验证令牌
            fetch(`${baseURL}/api/cards?per_page=1`, {
                headers: {
                    'Authorization': `Bearer ${token}`
                }
            })
            .then(response => {
                if (response.status === 200) {
                    resultDiv.innerHTML = '<div class="success">令牌验证成功！您可以使用此令牌测试其他API端点。</div>';
                } else {
                    return response.json().then(data => {
                        resultDiv.innerHTML = `<div class="error">令牌验证失败！状态码: ${response.status}<br>错误信息: ${JSON.stringify(data)}</div>`;
                    });
                }
            })
            .catch(error => {
                resultDiv.innerHTML = `<div class="error">请求失败: ${error.message}</div>`;
            });
        }

        // 通用API调用函数
        async function callAPI(endpoint, method = 'GET', data = null) {
            const token = document.getElementById('jwtToken').value;
            if (!token) {
                alert('请先输入JWT令牌！');
                return;
            }

            if (!isValidJWT(token)) {
                alert('JWT令牌格式不正确！请确保令牌包含3个用点分隔的部分。');
                return;
            }

            try {
                const config = {
                    method: method,
                    headers: {
                        'Authorization': `Bearer ${token}`,
                        'Content-Type': 'application/json'
                    }
                };

                if (data && method !== 'GET') {
                    config.body = JSON.stringify(data);
                }

                const response = await fetch(`${baseURL}${endpoint}`, config);
                const result = await response.json();
                
                document.getElementById('result').innerHTML = `状态码: ${response.status}\n\n${JSON.stringify(result, null, 2)}`;
            } catch (error) {
                document.getElementById('result').innerHTML = `错误: ${error.message}`;
            }
        }

        // 测试健康检查
        async function testHealth() {
            try {
                const response = await fetch(`${baseURL}/health`);
                const result = await response.json();
                document.getElementById('result').innerHTML = `状态码: ${response.status}\n\n${JSON.stringify(result, null, 2)}`;
            } catch (error) {
                document.getElementById('result').innerHTML = `错误: ${error.message}`;
            }
        }

        // 获取卡牌
        async function getCards() {
            const perPage = document.getElementById('per_page').value;
            const cardType = document.getElementById('card_type').value;
            let url = `${baseURL}/api/cards?per_page=${perPage}`;
            if (cardType) {
                url += `&type=${encodeURIComponent(cardType)}`;
            }
            
            const token = document.getElementById('jwtToken').value;
            if (!token) {
                alert('请先输入JWT令牌！');
                return;
            }

            if (!isValidJWT(token)) {
                alert('JWT令牌格式不正确！请确保令牌包含3个用点分隔的部分。');
                return;
            }

            try {
                const response = await fetch(url, {
                    headers: {
                        'Authorization': `Bearer ${token}`
                    }
                });
                const result = await response.json();
                document.getElementById('result').innerHTML = `状态码: ${response.status}\n\n${JSON.stringify(result, null, 2)}`;
            } catch (error) {
                document.getElementById('result').innerHTML = `错误: ${error.message}`;
            }
        }

        // 获取角色卡
        async function getCharacterCards() {
            const perPage = document.getElementById('char_per_page').value;
            const token = document.getElementById('jwtToken').value;
            
            if (!token) {
                alert('请先输入JWT令牌！');
                return;
            }

            if (!isValidJWT(token)) {
                alert('JWT令牌格式不正确！请确保令牌包含3个用点分隔的部分。');
                return;
            }

            try {
                const response = await fetch(`${baseURL}/api/cards/characters?per_page=${perPage}`, {
                    headers: {
                        'Authorization': `Bearer ${token}`
                    }
                });
                const result = await response.json();
                document.getElementById('result').innerHTML = `状态码: ${response.status}\n\n${JSON.stringify(result, null, 2)}`;
            } catch (error) {
                document.getElementById('result').innerHTML = `错误: ${error.message}`;
            }
        }

        // 获取事件卡
        async function getEventCards() {
            const perPage = document.getElementById('event_per_page').value;
            const token = document.getElementById('jwtToken').value;
            
            if (!token) {
                alert('请先输入JWT令牌！');
                return;
            }

            if (!isValidJWT(token)) {
                alert('JWT令牌格式不正确！请确保令牌包含3个用点分隔的部分。');
                return;
            }

            try {
                const response = await fetch(`${baseURL}/api/cards/events?per_page=${perPage}`, {
                    headers: {
                        'Authorization': `Bearer ${token}`
                    }
                });
                const result = await response.json();
                document.getElementById('result').innerHTML = `状态码: ${response.status}\n\n${JSON.stringify(result, null, 2)}`;
            } catch (error) {
                document.getElementById('result').innerHTML = `错误: ${error.message}`;
            }
        }

        // 获取用户卡组
        async function getUserDecks() {
            const token = document.getElementById('jwtToken').value;
            
            if (!token) {
                alert('请先输入JWT令牌！');
                return;
            }

            if (!isValidJWT(token)) {
                alert('JWT令牌格式不正确！请确保令牌包含3个用点分隔的部分。');
                return;
            }

            try {
                const response = await fetch(`${baseURL}/api/decks`, {
                    headers: {
                        'Authorization': `Bearer ${token}`
                    }
                });
                const result = await response.json();
                document.getElementById('result').innerHTML = `状态码: ${response.status}\n\n${JSON.stringify(result, null, 2)}`;
            } catch (error) {
                document.getElementById('result').innerHTML = `错误: ${error.message}`;
            }
        }
    </script>
</body>
</html>
        '''
        return test_page_html, 200, {'Content-Type': 'text/html'}

    return app

# 应用实例在运行时创建，而不是在导入时创建
if __name__ == "__main__":
    app = create_app()
    socketio.run(app, host="0.0.0.0", port=5000, debug=True)
