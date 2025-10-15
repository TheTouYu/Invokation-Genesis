#!/bin/bash
# API测试命令脚本

echo "七圣召唤 API 测试命令"
echo "========================"
echo
echo "首先，您需要获取一个JWT令牌："
echo "uv run python dev_tools/generate_test_token.py"
echo
echo "然后使用以下命令替换 YOUR_JWT_TOKEN_HERE 为实际的令牌"
echo
echo "1. 健康检查："
echo "curl http://localhost:5000/health"
echo
echo "2. 获取所有卡牌："
echo "curl -H \"Authorization: Bearer YOUR_JWT_TOKEN_HERE\" http://localhost:5000/api/cards"
echo
echo "3. 获取角色卡："
echo "curl -H \"Authorization: Bearer YOUR_JWT_TOKEN_HERE\" \"http://localhost:5000/api/cards/characters?per_page=5\""
echo
echo "4. 获取事件卡："
echo "curl -H \"Authorization: Bearer YOUR_JWT_TOKEN_HERE\" \"http://localhost:5000/api/cards/events?per_page=5\""
echo
echo "5. 获取用户卡组："
echo "curl -H \"Authorization: Bearer YOUR_JWT_TOKEN_HERE\" http://localhost:5000/api/decks"
echo
echo "6. 创建卡组示例（需要先获取一些卡牌ID）："
echo "curl -X POST -H \"Content-Type: application/json\" -H \"Authorization: Bearer YOUR_JWT_TOKEN_HERE\" -d '{\"name\":\"测试卡组\",\"description\":\"通过API创建的卡组\",\"cards\":[\"card_id1\",\"card_id2\",\"card_id3\"]}' http://localhost:5000/api/decks"
echo
echo "7. 格式化输出（需要安装jq）："
echo "curl -H \"Authorization: Bearer YOUR_JWT_TOKEN_HERE\" http://localhost:5000/api/cards | jq"
echo
echo "注意：首次使用前请确保服务器正在运行（uv run python run_dev_server.py）"