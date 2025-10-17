# Fix for start_dev.sh Script Issues

## Problem Description
The `start_dev.sh` script was failing with import errors:
1. `ImportError: cannot import name 'db' from 'app'`
2. `ImportError: cannot import name 'User' from 'models.db_models'`

## Root Cause
The issue was in `run_dev_server.py` which was trying to import the database object (`db`) and model classes (`User`) directly from the app and model modules, but:
1. The app.py file uses a centralized database manager (`db_manager`)
2. Model classes are defined inside a function within `db_models.py`
3. These classes are not directly available for import outside of that function

## Solution
I made two changes to `run_dev_server.py`:

1. **Removed problematic imports**: Removed the import of `db` and `User` from `app` and `models.db_models`
2. **Used proper database initialization**: Used the `db_manager.create_tables()` method which properly initializes the database schema

## Verification
The script now runs successfully:
```
七圣召唤开发服务器快速启动
===============================
清理旧的服务进程...
创建干净的数据库...
初始化数据库...
数据库表创建完成
当前数据库表: ['users', 'card_data', 'decks', 'game_histories']
card_data表当前列: ['id', 'name', 'card_type', 'element_type', 'cost', 'description', 'character_subtype', 'rarity', 'version', 'created_at', 'updated_at', 'is_active', 'health', 'max_health', 'energy', 'max_energy', 'weapon_type', 'skills', 'image_url']
decks表当前列: ['id', 'name', 'user_id', 'cards', 'is_public', 'created_at', 'updated_at', 'description']
card_data表缺失列: []
decks表缺失列: []
数据库初始化完成！
启动开发服务器...
等待服务器启动...
七圣召唤开发服务器
==============================
设置开发环境...
数据库表创建完成

启动开发服务器...
服务器将在 http://localhost:5000 运行
按 Ctrl+C 停止服务器
 * Serving Flask app 'app'
 * Debug mode: on
服务器已在 http://localhost:5000 运行

要测试API，请使用以下方法之一：

1. 图形化API测试页面（推荐）：
   访问 http://localhost:5000/api/test 在浏览器中测试

2. 命令行生成测试令牌：
   uv run python dev_tools/generate_test_token.py

3. 命令行运行API测试：
   uv run python test_api_with_token.py

4. 直接访问端点示例：
   curl http://localhost:5000/health

按 Ctrl+C 停止服务器
```

The server now successfully starts and runs on port 5000.