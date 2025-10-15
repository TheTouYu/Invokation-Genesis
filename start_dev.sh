#!/bin/bash
# 快速启动开发服务器脚本

echo "七圣召唤开发服务器快速启动"
echo "==============================="

# 清理旧进程
echo "清理旧的服务进程..."
pkill -f "python run_dev_server.py" 2>/dev/null || true

# 删除旧数据库文件以确保使用最新表结构
echo "创建干净的数据库..."
rm -f game.db

# 初始化数据库
echo "初始化数据库..."
uv run python initialize_db.py

# 启动服务器
echo "启动开发服务器..."
uv run python run_dev_server.py &

# 等待服务器启动
echo "等待服务器启动..."
sleep 5

echo "服务器已在 http://localhost:5000 运行"
echo ""
echo "要测试API，请使用以下方法之一："
echo ""
echo "1. 图形化API测试页面（推荐）："
echo "   访问 http://localhost:5000/api/test 在浏览器中测试"
echo ""
echo "2. 命令行生成测试令牌："
echo "   uv run python dev_tools/generate_test_token.py"
echo ""
echo "3. 命令行运行API测试："
echo "   uv run python test_api_with_token.py"
echo ""
echo "4. 直接访问端点示例："
echo "   curl http://localhost:5000/health"
echo ""
echo "按 Ctrl+C 停止服务器"