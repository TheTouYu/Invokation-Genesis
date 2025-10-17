# 七圣召唤项目文档索引

## 项目概览
- [README](../readme.md) - 项目主介绍文件
- [项目任务列表](../PROJECT_TASKS.md) - 开发任务跟踪

## 核心文档
- [游戏规则](GAME_RULES.md) - 详细的七圣召唤游戏规则说明
- [API参考](API_REFERENCE.md) - 完整的API接口文档
- [架构设计](ARCHITECTURE.md) - 系统架构和技术栈说明
- [开发指南](DEVELOPMENT_GUIDE.md) - 开发环境搭建和编码规范
- [测试文档](TESTING.md) - 测试策略和方法
- [用户指南](USER_GUIDE.md) - 系统使用和游戏玩法教程

## 数据访问层 (DAL) 文档
- [DAL概述](dal_overview.md) - 数据访问层设计与实现
- [DAL完整指南](dal_complete_guide.md) - 数据访问层完整使用指南
- [DAL组件详解](dal_components.md) - 各DAL组件详细说明
- [DAL性能优化](dal_performance_optimization.md) - 数据访问层性能优化
- [DAL集成API](dal_api_integration.md) - DAL与API集成说明
- [DAL使用示例](dal_usage_examples.md) - 数据访问层使用示例

## 技术架构
- API层
  - 用户认证 API (`api/auth.py`)
  - 卡牌数据 API (`api/standardized_cards.py`)
  - 卡组管理 API (`api/deck_builder/`)
  - 本地游戏 API (`api/local_game.py`)
- 业务逻辑层
  - 游戏引擎 (`game_engine/`)
  - 卡组验证 (`utils/deck_validator.py`)
- 数据访问层
  - 数据库管理器 (`database_manager.py`)
  - 数据访问层 (`dal.py`)
- 数据模型层
  - 数据库模型 (`models/db_models.py`)
  - 游戏模型 (`models/game_models.py`)
  - 枚举类型 (`models/enums.py`)

## 开发流程
1. [环境搭建](DEVELOPMENT_GUIDE.md#环境搭建) - 设置开发环境
2. [编码规范](DEVELOPMENT_GUIDE.md#编码规范) - 遵循的编码标准
3. [开发工作流](DEVELOPMENT_GUIDE.md#开发工作流) - 开发流程和工作方式
4. [测试指南](TESTING.md) - 测试策略和实践方法

## API 端点参考
- **认证相关**
  - POST `/api/auth/register` - 用户注册
  - POST `/api/auth/login` - 用户登录
  - GET `/api/auth/profile` - 获取用户信息
- **卡牌相关**
  - GET `/api/cards` - 获取卡牌列表
  - GET `/api/cards/{id}` - 获取特定卡牌
  - GET `/api/cards/types` - 获取卡牌类型
- **卡组相关**
  - GET `/api/decks` - 获取用户卡组
  - POST `/api/decks` - 创建卡组
  - PUT `/api/decks/{id}` - 更新卡组
  - DELETE `/api/decks/{id}` - 删除卡组
- **游戏相关**
  - POST `/api/local-game/start` - 开始游戏
  - POST `/api/local-game/{session_id}/action` - 游戏行动
  - GET `/api/local-game/{session_id}/state` - 获取游戏状态

## 测试文档
- [单元测试](TESTING.md#单元测试指南) - 各模块的单元测试
- [DAL测试](TESTING.md#dal-数据访问层-测试指南) - 数据访问层专门测试
- [集成测试](TESTING.md#集成测试指南) - 模块间集成测试
- [API测试](TESTING.md#api测试方法) - API端点测试方法

## 常见问题
参见各文档中的"常见问题解决"章节

## 贡献指南
- [开发指南](DEVELOPMENT_GUIDE.md#贡献指南) - 贡献代码的流程和要求
- [编码规范](DEVELOPMENT_GUIDE.md#编码规范) - 代码风格和规范