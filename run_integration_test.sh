#!/bin/bash
# 一键运行集成测试脚本

echo "七圣召唤 API 集成测试"
echo "========================"

# 检查服务器是否运行
if lsof -i :5000 > /dev/null; then
    echo "⚠️  发现正在运行的服务器进程，建议停止后重新测试以确保数据一致性"
    read -p "是否继续？(y/N): " -n 1 -r
    echo
    if [[ ! $REPLY =~ ^[Yy]$ ]]; then
        echo "测试已取消"
        exit 1
    fi
else
    echo "启动开发服务器..."
    cd /Users/wonder/bindolabs/ys_qs && rm -f game.db && uv run python initialize_db.py && uv run python run_dev_server.py &
    
    # 等待服务器启动
    sleep 5
fi

echo "运行集成测试..."
cd /Users/wonder/bindolabs/ys_qs && uv run python integration_test_final.py

TEST_RESULT=$?

if [ $TEST_RESULT -eq 0 ]; then
    echo ""
    echo "🎉 集成测试成功完成！"
else
    echo ""
    echo "❌ 集成测试失败！"
fi

exit $TEST_RESULT