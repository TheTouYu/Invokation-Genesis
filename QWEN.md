# 七圣召唤游戏服务器项目

## 项目概述

这是一个基于Flask框架构建的七圣召唤游戏服务器项目。该项目提供了游戏的核心功能，包括用户认证、卡牌数据管理、卡组构建、游戏历史记录等功能。项目采用现代Web技术栈，支持WebSocket实时通信，并提供了完整的API接口供前端应用使用。

### 主要特性

- 用户认证系统 (JWT)
- 卡牌数据管理
- 卡组构建与管理
- 游戏历史记录
- WebSocket实时通信支持
- RESTful API接口
- 数据库迁移支持

## 技术栈

- **后端**: Python 3.12+, Flask, Flask-SocketIO, Flask-JWT-Extended
- **数据库**: SQLite (开发环境), 支持SQLAlchemy ORM
- **前端**: 嵌入式HTML测试页面
- **构建工具**: uv (Python包管理器)

## 项目结构

```
.
├── app.py              # Flask应用主入口
├── run_dev_server.py   # 开发服务器启动脚本
├── start_dev.sh        # 开发服务器快速启动脚本
├── database_manager.py # 数据库管理模块
├── models/             # 数据模型定义
│   └── db_models.py    # 数据库模型
├── api/                # API路由定义
├── dev_tools/          # 开发工具
│   └── generate_test_token.py # 生成测试令牌工具
├── test/               # 测试代码
│   └── test_api_with_token.py # API测试脚本
├── initialize_db.py    # 数据库初始化脚本
└── ...
```

## 运行和构建

### 开发环境启动

```bash
# 快速启动开发服务器 (推荐方式)
./start_dev.sh

# 或者逐个执行步骤
uv run python initialize_db.py  # 初始化数据库
uv run python run_dev_server.py # 启动开发服务器
```

### API测试

项目提供多种测试方式：

1. **图形化API测试页面**：
   - 访问 `http://localhost:5000/api/test` 浏览器中测试

2. **命令行测试令牌生成**：
   ```bash
   uv run python dev_tools/generate_test_token.py
   ```

3. **命令行API测试**：
   ```bash
   uv run python test/test_api_with_token.py
   ```

4. **直接HTTP请求测试**：
   ```bash
   curl http://localhost:5000/health
   ```

### 数据库管理

- 数据库存储在 `game.db` 文件中
- 使用 `initialize_db.py` 脚本进行数据库初始化
- 支持数据库迁移 (通过Flask-Migrate)

## 开发约定

### 数据库模型

数据库模型定义在 `models/db_models.py` 中。模型使用延迟初始化方式，确保在应用上下文中正确绑定数据库实例。

### API架构

API路由按照功能划分在不同的模块中：
- `/api/auth` - 认证相关接口
- `/api/card` - 卡牌相关接口
- `/api/deck` - 卡组相关接口
- `/api/game` - 游戏相关接口

### 开发流程

1. 使用 `start_dev.sh` 脚本快速启动开发环境
2. 修改代码后重启服务器或使用热重载
3. 使用提供的测试工具验证API功能
4. 数据库变更使用Flask-Migrate进行管理

## 部署说明

项目设计为开发环境使用，但也可用于生产部署。需要注意以下事项：

- 生产环境应使用更安全的数据库连接方式
- 使用生产级WSGI服务器替代开发服务器
- 配置适当的环境变量和安全设置
- 适配生产环境的数据库URI

## 注意事项

- 开发环境使用SQLite数据库，生产环境需替换为MySQL、PostgreSQL等
- 所有API请求都需要携带有效的JWT令牌
- 卡牌数据需要在数据库中预先加载才能使用
- 服务器默认监听所有网络接口 (0.0.0.0:5000)