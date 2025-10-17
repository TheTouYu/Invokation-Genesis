# 七圣召唤开发指南

## 环境搭建

### 系统要求
- **操作系统**: macOS, Linux, 或 Windows (WSL推荐)
- **Python版本**: 3.8 或更高版本
- **包管理器**: uv (推荐) 或 pip

### 安装步骤

#### 1. 克隆仓库
```bash
git clone https://github.com/your-username/ys-qs-ui.git
cd ys-qs-ui
```

#### 2. 安装依赖
使用 uv (推荐):
```bash
uv sync
```

或使用 pip:
```bash
pip install -r requirements.txt
```

#### 3. 数据库初始化
```bash
# 初始化数据库
python init_db.py

# 导入卡牌数据
python import_card_data.py
```

#### 4. 启动开发服务器
```bash
# 启动开发服务器
bash start_dev.sh
```

**重要说明**: `run_dev_server.py`中的数据库初始化方式已更新，现在使用`database_manager.create_tables()`方法替代原来的`db.create_all()`方法。这种方式更加符合项目的架构设计，通过中央化的数据库管理器来处理数据库初始化，确保了一致性和可维护性。

## 项目结构

```
ys_qs/
├── api/                 # API路由模块
│   ├── auth.py          # 用户认证API
│   ├── cards.py         # 卡牌管理API
│   ├── deck_builder/    # 卡组构建API
│   └── local_game.py    # 本地游戏API
├── card_data/           # 卡牌数据JSON文件
│   ├── characters.json  # 角色牌数据
│   ├── events.json      # 事件牌数据
│   ├── equipments.json  # 装备牌数据
│   └── supports.json    # 支援牌数据
├── dev_tools/           # 开发工具
│   └── generate_test_token.py  # 生成测试令牌
├── docs/                # 项目文档
├── frontend/            # 前端代码 (React + TypeScript)
│   ├── public/          # 静态资源
│   ├── src/             # 源代码
│   │   ├── components/  # React组件
│   │   ├── pages/       # 页面组件
│   │   ├── hooks/       # 自定义Hooks
│   │   ├── utils/       # 工具函数
│   │   ├── services/    # API服务
│   │   └── styles/      # 样式文件
│   ├── package.json     # npm依赖
│   └── tsconfig.json    # TypeScript配置
├── game_engine/         # 游戏引擎核心
│   ├── core.py          # 主游戏引擎
│   ├── element_reactions.py    # 元素反应系统
│   └── deck_validation.py      # 卡组验证系统
├── models/              # 数据模型
│   ├── db_models.py     # 数据库模型
│   ├── enums.py         # 枚举类型定义
│   └── game_models.py   # 游戏数据模型
├── database_manager.py  # 数据库管理器
├── dal.py               # 数据访问层 (DAL)
├── socket_handlers/     # WebSocket处理器
├── tests/               # 测试文件
├── app.py              # Flask应用主文件
├── run_dev_server.py   # 开发服务器启动脚本
├── start_dev.sh        # 开发服务器启动脚本
├── PROJECT_TASKS.md    # 项目任务列表
└── README.md           # 项目主文档
```

## Working with the Data Access Layer (DAL) and Database Manager

The project uses a Data Access Layer (DAL) combined with a centralized Database Manager to abstract database operations. All database interactions should go through the DAL rather than direct SQLAlchemy queries to maintain consistency and improve maintainability.

### Database Manager Pattern

The project uses a `DatabaseManager` class in `database_manager.py` to centralize database connections and avoid circular imports. To access the database instance, use:

```python
from database_manager import db_manager
db = db_manager.get_db()
```

### Model Container Pattern

Database models are managed through a `ModelContainer` in `models/db_models.py` to avoid circular imports. Models can be accessed via:

```python
from models.db_models import model_container
User = model_container.User
CardData = model_container.CardData
Deck = model_container.Deck
GameHistory = model_container.GameHistory
```

In API files, use the lazy loading pattern:

```python
def get_models():
    from models.db_models import model_container
    return model_container.User, model_container.CardData, model_container.Deck

# Usage in functions
User, CardData, Deck = get_models()
```

### Using the DAL in Your Code

To use the DAL, import it and access the appropriate data access object:

```python
from dal import db_dal

# For user operations
user = db_dal.users.create_user(username="test", email="test@example.com", password_hash="hash")
user = db_dal.users.get_user_by_id(user_id)

# For card operations
cards = db_dal.cards.get_cards_by_type("角色牌")
card = db_dal.cards.get_card_by_id(card_id)

# For deck operations  
deck = db_dal.decks.create_deck(name="My Deck", user_id=user_id, cards=card_ids)
decks = db_dal.decks.get_decks_by_user(user_id)

# For game history operations
game = db_dal.game_history.create_game_history(player1_id, player2_id, game_data)
games = db_dal.game_history.get_games_by_user(user_id)
```

### DAL Best Practices

1. **Always use DAL for database operations**: Instead of direct model queries like `User.query.filter(...)`, use the appropriate DAL method
2. **Handle errors appropriately**: DAL methods will return appropriate success/failure indicators or raise exceptions
3. **Use transactions when needed**: The DAL handles transaction management internally for individual operations, but for complex operations spanning multiple DAL calls, consider wrapping them in a transaction
4. **Keep business logic separate**: The DAL should only handle data access; business logic should remain in service layers
5. **Use database manager for direct DB access**: When you need direct database access (not through DAL), use `db_manager.get_db()` instead of importing `db` directly

### Creating New DAL Methods

When adding new functionality that requires database access:

1. Add the method to the appropriate DAL class in `dal.py`
2. Follow the existing pattern with proper error handling and logging
3. Use type hints and docstrings for consistency
4. Test the new DAL method separately
5. Update the model container if new models are added

## 编码规范

### Python 代码规范
- 遵循 [PEP 8](https://pep8.org/) 代码风格指南
- 使用类型注解 (Type Hints)
- 函数和类要有适当的文档字符串
- 保持函数简短（建议不超过50行）
- 使用有意义的变量和函数名

### 命名约定
- **变量和函数**: snake_case
- **类名**: PascalCase
- **常量**: UPPER_SNAKE_CASE
- **私有成员**: 以单下划线开头 `_private_method`

### 数据模型规范
- 所有游戏数据模型继承自 `dataclasses.dataclass`
- 数据库模型继承自 `db.Model`
- 枚举类型定义在 `models/enums.py` 中

### API 设计规范
- RESTful API 设计原则
- 使用标准 HTTP 状态码
- 错误响应统一格式: `{"error": "错误描述"}`
- 成功响应包含有意义的数据结构
- 认证使用 JWT 令牌
- 数据访问: 通过数据访问层 (DAL) 进行所有数据库操作，避免直接使用 SQLAlchemy 模型查询

## 开发工作流

### 1. 创建分支
```bash
git checkout -b feature/your-feature-name
```

### 2. 编写代码
- 遵循编码规范
- 编写必要的单元测试
- 更新相关文档

### 3. 运行测试
```bash
# 运行单元测试
python -m pytest tests/

# 运行集成测试
python integration_test_final.py
```

### 4. 提交代码
```bash
git add .
git commit -m "feat: describe your changes"
git push origin feature/your-feature-name
```

### 5. 创建 Pull Request
- 确保所有测试通过
- 更新相关文档
- 请求代码审查

## 调试方法

### 日志调试
使用 Python 内置的 logging 模块：
```python
import logging
logger = logging.getLogger(__name__)

logger.debug("Debug message")
logger.info("Info message")
logger.warning("Warning message")
logger.error("Error message")
```

### API 调试
1. **使用内置测试页面**:
   - 访问 `http://localhost:5000/api/test`
   - 输入 JWT 令牌进行测试

2. **使用命令行**:
   ```bash
   # 生成测试令牌
   uv run python dev_tools/generate_test_token.py
   
   # 测试API端点
   curl -H "Authorization: Bearer YOUR_JWT_TOKEN" \
        "http://localhost:5000/api/cards?per_page=5"
   ```

3. **使用 Postman**:
   - 设置 Authorization 头
   - 测试各种 API 端点

### 游戏引擎调试
- 在 `game_engine/core.py` 中添加调试日志
- 使用单元测试验证游戏逻辑
- 通过 API 测试页面观察游戏状态变化

## 测试指南

### 单元测试
- 为每个模块编写单元测试
- 测试边界条件和异常情况
- 使用 pytest 框架

### 集成测试
- 测试完整的 API 工作流程
- 验证游戏引擎与 API 的集成
- 运行 `integration_test_final.py`

### 手动测试
- 使用 API 测试页面进行端到端测试
- 验证核心游戏流程
- 测试各种游戏场景

## 常见问题解决

### 数据库问题
- **问题**: 数据库初始化失败
- **解决**: 删除 `instance/game.db` 文件，重新运行 `init_db.py`

### 依赖问题
- **问题**: 包版本冲突
- **解决**: 使用 `uv sync --clean` 重新安装所有依赖

### API 404 错误
- **问题**: API 路由返回 404
- **解决**: 检查 `app.py` 中的路由注册，确保 API 蓝图正确挂载

### JWT 认证问题
- **问题**: 401 Unauthorized 错误
- **解决**: 确保 JWT 令牌有效，检查令牌是否包含必要的声明

### 游戏逻辑问题
- **问题**: 游戏行为不符合预期
- **解决**: 检查 `game_engine/core.py` 中的相关逻辑，添加调试日志

## 贡献指南

### 代码审查
- 所有 PR 都需要至少一名团队成员审查
- 确保代码符合编码规范
- 验证所有测试通过

### 文档更新
- 任何功能变更都需要更新相关文档
- API 变更需要更新 API 参考文档
- 新功能需要在用户指南中说明

### 版本管理
- 使用语义化版本控制 (SemVer)
- 主要版本: 不兼容的 API 变更
- 次要版本: 向后兼容的功能新增
- 修订版本: 向后兼容的问题修正

## 资源链接

- [Python 官方文档](https://docs.python.org/3/)
- [Flask 文档](https://flask.palletsprojects.com/)
- [SQLAlchemy 文档](https://docs.sqlalchemy.org/)
- [JWT 规范](https://jwt.io/)
- [七圣召唤官方规则](https://genshin.hoyoverse.com/zh-cn/gcg)