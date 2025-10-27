# 七圣召唤（Genshin Impact Card Game）项目文档

## 项目概述

这是一个复刻原神中七圣召唤卡牌游戏的开源项目，实现了完整的卡牌对战功能，包括519张卡牌数据、完整的战斗系统、元素反应机制和卡组构筑功能。项目采用Flask作为后端框架，提供完整的REST API接口，支持用户认证、卡牌管理、卡组构建和游戏对战功能。

## 技术栈

- **后端**: Python 3.12+, Flask, SQLAlchemy, JWT, Flask-JWT-Extended, Flask-CORS, Flask-SocketIO
- **数据库**: SQLite (开发)/PostgreSQL (生产)
- **包管理**: uv
- **前端**: React + TypeScript (计划中)
- **测试**: pytest, 集成测试套件
- **其他**: Flask-Migrate, Alembic, bs4, lxml, requests

## 项目结构

```
ys_qs/
├── .pytest_cache/           # Pytest缓存目录
├── .venv/                  # Python虚拟环境
├── alembic/                # 数据库迁移目录
├── api/                    # API路由模块
├── card_data/              # 卡牌数据JSON文件
├── dev_tools/              # 开发工具
├── docs/                   # 项目文档
├── frontend/               # 前端目录
├── game_engine/            # 游戏引擎核心
├── instance/               # Flask实例目录
├── metabase-data/          # Metabase数据目录
├── models/                 # 数据模型
├── modules/                # 模块目录 (包含API测试页面、游戏测试页面等)
├── test/                   # 测试文件目录
├── utils/                  # 工具函数
├── venv/                   # Python虚拟环境
├── .env                    # 环境变量文件
├── .gitignore              # Git忽略文件配置
├── .python-version         # Python版本文件
├── alembic.ini             # Alembic数据库迁移配置
├── api_test_commands.sh    # API测试命令脚本
├── api_test_page.html      # API测试页面
├── app.py                  # Flask应用主文件
├── app.py.bak              # Flask应用备份文件
├── create_db_tables.py     # 创建数据库表脚本
├── create_test_accounts.py # 创建测试账户脚本
├── dal.py                  # 数据访问层
├── data_pipeline.py        # 数据管道脚本
├── database_container.md   # 数据库容器文档
├── database_importer.py    # 数据库导入器
├── database_importer.py.bak # 数据库导入器备份文件
├── database_manager.py     # 数据库管理器
├── db_init.py              # 数据库初始化脚本
├── docker_daemon.json      # Docker守护进程配置
├── docker-compose.yml      # Docker Compose配置文件
├── fetch_and_save_cards.py # 获取并保存卡牌数据脚本
├── fix_content_type.py     # 修复内容类型脚本
├── fix_unicode_storage.py  # 修复Unicode存储脚本
├── game_api_test_page.html # 游戏API测试页面
├── game_test_modular.html  # 游戏测试页面(模块化)
├── import_card_data.py     # 导入卡牌数据脚本
├── init_db.py              # 初始化数据库脚本
├── initialize_db.py        # 初始化数据库脚本
├── integration_test_final.py # 集成测试最终版本
├── integration_test_final.py.bak # 集成测试备份
├── integration_test.py     # 集成测试脚本
├── main.py                 # 主程序入口
├── METABASE_SETUP.md       # Metabase设置文档
├── migrate_database_structure.py # 数据库结构迁移脚本
├── migrate_db.py           # 数据库迁移脚本
├── original_api_test_page.html # 原始API测试页面
├── PROJECT_TASKS.md        # 项目任务文档
├── pyproject.toml          # 项目依赖配置文件
├── QWEN.md                 # 项目文档
├── readme.md               # 项目说明文件
├── reset_db.py             # 重置数据库脚本
├── run_dev_server.py       # 运行开发服务器脚本
├── run_integration_test.sh # 运行集成测试脚本
├── start_dev.sh            # 开发服务器启动脚本
├── start_server.py         # 服务器启动脚本
├── test_auth.sh            # 认证测试脚本
├── test_config.py          # 测试配置文件
├── test_db.py              # 数据库测试文件
├── test_game_engine.py     # 游戏引擎测试文件
├── update_db_schema.py     # 更新数据库模式脚本
├── update_test_page.py     # 更新测试页面脚本
├── uv.lock                 # uv依赖锁定文件
├── validate_refactor.py    # 重构验证脚本
└── verify_imported_data.py # 验证导入数据脚本
```

## 主要功能

- **完整卡牌系统**: 包含519张卡牌（121角色牌、104事件牌、226装备牌、68支援牌）
- **核心游戏规则**: 完整的回合流程、行动系统、胜利条件
- **元素反应系统**: 计划实现所有官方元素反应效果
- **卡组构筑**: 支持完整的卡组创建、验证和管理
- **REST API**: 提供完整的后端API接口
- **用户认证**: 基于JWT的用户认证系统
- **测试套件**: 全面的单元测试和集成测试
- **WebSocket支持**: 集成Flask-SocketIO支持实时通信

## 核心模块

### API模块 (api/)

- **auth.py**: 用户认证相关API (注册、登录、获取用户信息)
- **standardized_cards.py**: 标准化卡牌数据API (获取卡牌、过滤、搜索等)
- **deck_builder.py**: 卡组构建和管理API
- **local_game.py**: 本地游戏会话管理API
- **users.py**: 用户管理API
- **filters_integrated.py**: 集成过滤器API
- **v2/**: API v2 - 模块化API实现

### API V2模块 (api/v2/)

- **cards.py**: 卡牌相关API
- **characters.py**: 角色相关API
- **equipments.py**: 装备相关API
- **supports.py**: 支援牌相关API
- **events.py**: 事件牌相关API
- **decks.py**: 卡组相关API
- **utils.py**: API工具函数

### 数据模型 (models/)

- **db_models.py**: 定义数据库模型 (User, CardData, Deck, GameHistory)
- **enums.py**: 定义所有枚举类型
- **game_models.py**: 实现游戏核心数据类
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

### 游戏引擎 (game_engine/)

- **core.py**: 实现GameEngine类，包含游戏核心逻辑
- 实现核心方法：create_game_state, process_action, _roll_phase, _action_phase, _end_phase
- 实现基础动作处理逻辑和费用支付验证逻辑

### 开发模式

- **数据库访问**: 使用 `database_manager.db_manager.get_db()` 获取数据库实例
- **模型访问**: 使用 `models.db_models.model_container` 访问数据库模型
- **API开发**: 在API文件中使用 `get_models()` 函数进行延迟模型导入

## API端点

### 认证相关
- `POST /api/auth/register` - 用户注册
- `POST /api/auth/login` - 用户登录
- `GET /api/auth/profile` - 获取用户信息

### 卡牌相关 (位于 /api/)
- `GET /api/cards` - 获取卡牌列表（支持分页和过滤）
- `GET /api/cards/<card_id>` - 获取特定卡牌
- `GET /api/cards/types` - 获取卡牌类型列表
- `GET /api/cards/elements` - 获取元素类型列表
- `GET /api/cards/countries` - 获取国家列表
- `GET /api/cards/weapon_types` - 获取武器类型列表
- `GET /api/cards/random` - 获取随机卡牌
- `GET /api/characters/filters` - 获取角色过滤选项（国家、元素、武器类型）

### 卡牌相关 (API v2，位于 /api/)
- `GET /api/v2/cards` - 获取卡牌列表（支持分页和过滤）
- `GET /api/v2/cards/<card_id>` - 获取特定卡牌
- `GET /api/v2/cards/types` - 获取卡牌类型列表
- `GET /api/v2/cards/elements` - 获取元素类型列表
- `GET /api/v2/cards/countries` - 获取国家列表
- `GET /api/v2/cards/weapon_types` - 获取武器类型列表
- `GET /api/v2/cards/random` - 获取随机卡牌
- `GET /api/v2/characters` - 获取角色牌数据
- `GET /api/v2/equipments` - 获取装备牌数据
- `GET /api/v2/supports` - 获取支援牌数据
- `GET /api/v2/events` - 获取事件牌数据

### 卡组相关 (位于 /api/)
- `GET /api/decks` - 获取用户卡组列表
- `POST /api/decks` - 创建卡组
- `PUT /api/decks/<deck_id>` - 更新卡组
- `DELETE /api/decks/<deck_id>` - 删除卡组
- `GET /api/decks/<deck_id>` - 获取特定卡组
- `POST /api/decks/validate` - 验证卡组

### 过滤器相关
- `GET /api/filters` - 获取所有过滤选项
- `GET /api/filters/character` - 获取角色过滤选项
- `GET /api/filters/tags` - 获取卡牌标签

### 用户相关
- `GET /api/users/profile` - 获取用户资料
- `PUT /api/users/profile` - 更新用户资料

### 游戏相关
- `GET /api/local_game` - 获取本地游戏状态
- `POST /api/local_game/action` - 执行游戏动作

### 其他
- `GET /health` - 健康检查端点
- `GET /api/test` - API测试页面（位于 /modules/api_test/index.html）
- `GET /game/test` - 游戏API测试页面（位于 /modules/game_test/index.html）

## 构建和运行

### 环境要求
- Python 3.12+
- uv 包管理器

### 安装步骤
```bash
# 安装依赖
uv sync

# 初始化数据库
uv run python init_db.py

# 启动开发服务器
bash start_dev.sh
```

### 访问服务
- 服务器地址：http://localhost:5000
- API测试页面：http://localhost:5000/api/test
- 游戏API测试页面：http://localhost:5000/game/test
- 健康检查：http://localhost:5000/health

### API测试
```bash
# 生成测试令牌
uv run python dev_tools/generate_test_token.py

# 测试卡牌API
curl -H "Authorization: Bearer YOUR_JWT_TOKEN" \
     "http://localhost:5000/api/v1/cards?per_page=10"
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
- API v2支持模块化API结构

### 代码风格
- 使用Python 3.12+语法
- 遵循PEP 8代码风格指南
- 使用类型注解提高代码可读性
- 实现模块化设计和组件复用

## 当前开发状态

项目已完成基础架构和核心API开发，正在进行前端UI开发。已完成的主要功能包括：

- 基础环境搭建
- 用户认证系统
- 完整的卡牌数据系统（519张卡牌）
- API v1 和 API v2 设计
- 卡组构建和验证
- 基础游戏引擎
- 集成测试套件
- 数据库管理与迁移系统
- WebSocket通信支持

项目当前开发重点：

- 前端UI开发
- 完善游戏引擎逻辑
- 实现元素反应系统
- 优化卡组验证机制

待完成的主要功能：

- 元素反应系统：精确实现各种元素反应的复杂逻辑
- 完善角色击倒和胜利条件
- 修正行动类型规则（快速行动与战斗行动区分）
- 实现完整卡组验证规则
- 前端界面开发
- 多人游戏支持（集成WebSocket）
- AI对手开发

## 文档资源

- [游戏规则](docs/GAME_RULES.md) - 详细的七圣召唤游戏规则说明
- [API参考](docs/API_REFERENCE.md) - 完整的API接口文档
- [开发指南](docs/DEVELOPMENT_GUIDE.md) - 开发环境搭建和编码规范
- [用户指南](docs/USER_GUIDE.md) - 系统使用和游戏玩法教程
- [架构设计](docs/ARCHITECTURE.md) - 系统架构和技术栈说明
- [测试文档](docs/TESTING.md) - 测试策略和方法
- [项目任务](PROJECT_TASKS.md) - 项目开发任务列表