"""
开发服务器启动脚本
"""

import os
import sys
from app import create_app, socketio
from database_manager import db_manager


def setup_dev_environment():
    """设置开发环境"""
    print("设置开发环境...")

    # 创建上传目录（如果不存在）
    os.makedirs("uploads", exist_ok=True)
    os.makedirs("card_data", exist_ok=True)

    # 创建应用
    app = create_app()

    # 创建数据库表
    with app.app_context():
        db = db_manager.get_db()
        db.create_all()
        print("数据库表创建完成")

    return app


def run_dev_server():
    """运行开发服务器"""
    app = setup_dev_environment()

    print("\n启动开发服务器...")
    print("服务器将在 http://localhost:5000 运行")
    print("按 Ctrl+C 停止服务器")

    # 运行SocketIO服务器
    socketio.run(
        app,
        host="0.0.0.0",
        port=5000,
        debug=True,
        use_reloader=False,
        allow_unsafe_werkzeug=True,
    )


if __name__ == "__main__":
    print("七圣召唤开发服务器")
    print("=" * 30)
    run_dev_server()

