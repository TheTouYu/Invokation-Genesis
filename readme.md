# 七圣召唤（Genshin Impact Card Game）项目

![七圣召唤](https://example.com/ys-qs-logo.png)

这是一个复刻原神中七圣召唤卡牌游戏的开源项目，实现了完整的卡牌对战功能，包括519张卡牌数据、完整的战斗系统、元素反应机制和卡组构筑功能。

## 目录

- [项目简介](#项目简介)
- [主要功能](#主要功能)
- [快速开始](#快速开始)
- [项目结构](#项目结构)
- [文档导航](#文档导航)
- [贡献指南](#贡献指南)
- [许可证](#许可证)

## 项目简介

七圣召唤是原神中的一款集换式卡牌游戏。本项目旨在实现一个完全符合官方规则的七圣召唤游戏引擎，支持单人模式和多人对战，并提供完整的API接口供前端或其他客户端使用。

## 主要功能

- **完整卡牌系统**：包含519张卡牌（121角色牌、104事件牌、226装备牌、68支援牌）
- **核心游戏规则**：完整的回合流程、行动系统、胜利条件
- **元素反应系统**：实现所有官方元素反应效果
- **卡组构筑**：支持完整的卡组创建、验证和管理
- **REST API**：提供完整的后端API接口
- **用户认证**：基于JWT的用户认证系统
- **数据访问层 (DAL)**：采用数据访问层架构，统一管理数据库操作
- **测试套件**：全面的单元测试和集成测试

## 快速开始

### 环境要求

- Python 3.8+
- uv 包管理器（或 pip）

### 安装步骤

```bash
# 克隆仓库
git clone https://github.com/your-username/ys-qs-ui.git
cd ys-qs-ui

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

## 项目结构

```
ys_qs/
├── api/                 # API路由模块
├── card_data/           # 卡牌数据JSON文件
├── dev_tools/           # 开发工具
├── docs/                # 项目文档
│   ├── GAME_RULES.md    # 游戏规则文档
│   ├── API_REFERENCE.md # API参考文档
│   ├── DEVELOPMENT_GUIDE.md # 开发指南
│   ├── USER_GUIDE.md    # 用户指南
│   ├── ARCHITECTURE.md  # 架构设计文档
│   └── TESTING.md       # 测试文档
├── game_engine/         # 游戏引擎核心
├── models/              # 数据模型
├── database_manager.py  # 数据库管理器
├── dal.py               # 数据访问层 (DAL)
├── socket_handlers/     # WebSocket处理器
├── app.py              # Flask应用主文件
├── PROJECT_TASKS.md    # 项目任务列表
└── README.md           # 本文件
```

## 文档导航

- [游戏规则](docs/GAME_RULES.md) - 详细的七圣召唤游戏规则说明
- [API参考](docs/API_REFERENCE.md) - 完整的API接口文档
- [开发指南](docs/DEVELOPMENT_GUIDE.md) - 开发环境搭建和编码规范
- [用户指南](docs/USER_GUIDE.md) - 系统使用和游戏玩法教程
- [架构设计](docs/ARCHITECTURE.md) - 系统架构和技术栈说明
- [测试文档](docs/TESTING.md) - 测试策略和方法
- [DAL概述](docs/dal_overview.md) - 数据访问层设计与实现
- [DAL完整指南](docs/dal_complete_guide.md) - 数据访问层完整使用指南
- [DAL组件详解](docs/dal_components.md) - 各DAL组件详细说明
- [DAL性能优化](docs/dal_performance_optimization.md) - 数据访问层性能优化
- [DAL集成API](docs/dal_api_integration.md) - DAL与API集成说明
- [DAL使用示例](docs/dal_usage_examples.md) - 数据访问层使用示例

## 贡献指南

我们欢迎任何形式的贡献！在提交PR之前，请确保：

1. 遵循项目的编码规范
2. 添加必要的测试用例
3. 更新相关文档
4. 通过所有CI检查

详细的贡献指南请参阅 [开发指南](docs/DEVELOPMENT_GUIDE.md)。

## 许可证

本项目采用 [MIT 许可证](LICENSE)。