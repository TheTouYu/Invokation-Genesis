# 七圣召唤（Genshin Impact Card Game）项目文档

## 项目概述

这是一个复刻原神中七圣召唤卡牌游戏的开源项目，实现了完整的卡牌对战功能，包括519张卡牌数据、完整的战斗系统、元素反应机制和卡组构筑功能。项目采用Flask作为后端框架，提供完整的REST API接口，支持用户认证、卡牌管理、卡组构建和游戏对战功能。

## 技术栈

- **后端**: Python 3.12+, Flask, SQLAlchemy, JWT
- **数据库**: SQLite (开发)/PostgreSQL (生产)
- **包管理**: uv
- **前端**: React + TypeScript (计划中)
- **测试**: pytest

## 项目结构

```
ys_qs/
├── api/                 # API路由模块
├── card_data/           # 卡牌数据JSON文件
├── dev_tools/           # 开发工具
├── docs/                # 项目文档
├── game_engine/         # 游戏引擎核心
├── models/              # 数据模型
├── socket_handlers/     # WebSocket处理器
├── utils/               # 工具函数
├── app.py              # Flask应用主文件
├── database_manager.py # 数据库管理器
├── dal.py              # 数据访问层
├── start_dev.sh        # 开发服务器启动脚本
├── pyproject.toml      # 项目依赖配置
└── README.md           # 项目说明文件
```

## 主要功能

- **完整卡牌系统**: 包含519张卡牌（121角色牌、104事件牌、226装备牌、68支援牌）
- **核心游戏规则**: 完整的回合流程、行动系统、胜利条件
- **元素反应系统**: 实现所有官方元素反应效果
- **卡组构筑**: 支持完整的卡组创建、验证和管理
- **REST API**: 提供完整的后端API接口
- **用户认证**: 基于JWT的用户认证系统
- **测试套件**: 全面的单元测试和集成测试

## 核心模块

### API模块 (api/)

- **auth.py**: 用户认证相关API (注册、登录、获取用户信息)
- **standardized_cards.py**: 标准化卡牌数据API (获取卡牌、过滤、搜索等)
- **deck_builder.py**: 卡组构建和管理API
- **local_game.py**: 本地游戏会话管理API

### 数据模型 (models/)

- **db_models.py**: 定义数据库模型 (User, CardData, Deck, GameHistory)
- 使用UUID作为主键，支持用户、卡牌、卡组、游戏历史等实体

### 数据访问层 (dal.py)

- **UserDAL**: 用户数据访问接口
- **CardDataDAL**: 卡牌数据访问接口
- **DeckDAL**: 卡组数据访问接口
- **GameHistoryDAL**: 游戏历史数据访问接口

### 数据库管理 (database_manager.py)

- **DatabaseManager**: 集中化数据库管理，支持SQLite和PostgreSQL，提供 `db_manager.get_db()` 方法避免循环导入
- 集成Flask-Migrate用于数据库迁移
- **ModelContainer**: 在 `models/db_models.py` 中实现的模型容器模式，通过 `model_container` 实例访问数据库模型，支持延迟初始化

### 开发模式

- **数据库访问**: 使用 `database_manager.db_manager.get_db()` 获取数据库实例
- **模型访问**: 使用 `models.db_models.model_container` 访问数据库模型
- **API开发**: 在API文件中使用 `get_models()` 函数进行延迟模型导入

## API端点

### 认证相关
- `POST /api/auth/register` - 用户注册
- `POST /api/auth/login` - 用户登录
- `GET /api/auth/profile` - 获取用户信息

### 卡牌相关
- `GET /api/cards` - 获取卡牌列表（支持分页和过滤）
- `GET /api/cards/<card_id>` - 获取特定卡牌
- `GET /api/cards/types` - 获取卡牌类型列表
- `GET /api/cards/elements` - 获取元素类型列表
- `GET /api/cards/countries` - 获取国家列表
- `GET /api/cards/weapon_types` - 获取武器类型列表
- `GET /api/cards/random` - 获取随机卡牌

### 卡组相关
- `GET /api/decks` - 获取用户卡组列表
- `POST /api/decks` - 创建卡组
- `PUT /api/decks/<deck_id>` - 更新卡组
- `DELETE /api/decks/<deck_id>` - 删除卡组
- `GET /api/decks/<deck_id>` - 获取特定卡组
- `POST /api/decks/validate` - 验证卡组

### 其他
- `GET /health` - 健康检查端点
- `GET /api/test` - API测试页面

## 构建和运行

### 环境要求
- Python 3.12+
- uv 包管理器

### 安装步骤
```bash
# 安装依赖
uv sync

# 启动开发服务器
bash start_dev.sh
```

### 访问服务
- 服务器地址：http://localhost:5000
- API测试页面：http://localhost:5000/api/test
- 健康检查：http://localhost:5000/health

### API测试
```bash
# 生成测试令牌
uv run python dev_tools/generate_test_token.py

# 测试卡牌API
curl -H "Authorization: Bearer YOUR_JWT_TOKEN" \
     "http://localhost:5000/api/cards?per_page=10"
```

## 开发约定

### 数据库操作
- 所有数据库操作通过DAL层进行
- 使用SQLAlchemy ORM进行数据库交互
- 数据库迁移使用Flask-Migrate

### API设计
- 所有API端点使用JWT认证
- 返回统一格式的JSON响应
- 实现分页和过滤功能

### 代码风格
- 使用Python 3.12+语法
- 遵循PEP 8代码风格指南
- 使用类型注解提高代码可读性

## 当前开发状态

项目已完成基础架构和核心API开发，正在进行前端UI开发。已完成的主要功能包括：

- 基础环境搭建
- 用户认证系统
- 完整的卡牌数据系统
- 卡组构建和验证
- 基础游戏引擎
- 集成测试套件

目前正在进行前端UI开发，后续计划实现元素反应系统、多人游戏和AI对手等功能。

## 文档资源

- [游戏规则](docs/GAME_RULES.md) - 详细的七圣召唤游戏规则说明
- [API参考](docs/API_REFERENCE.md) - 完整的API接口文档
- [开发指南](docs/DEVELOPMENT_GUIDE.md) - 开发环境搭建和编码规范
- [用户指南](docs/USER_GUIDE.md) - 系统使用和游戏玩法教程
- [架构设计](docs/ARCHITECTURE.md) - 系统架构和技术栈说明
- [测试文档](docs/TESTING.md) - 测试策略和方法