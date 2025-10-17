# 项目概述

这是一个复刻《原神》中七圣召唤卡牌游戏的项目，旨在重现原版游戏的核心玩法和机制。

## 项目结构说明

```
.
├── api/                 # API 路由和端点
│   ├── auth.py          # 用户认证相关API
│   ├── cards.py         # 卡牌数据API
│   └── local_game.py    # 单人游戏API
├── card_data/           # 存储抓取的卡牌数据JSON文件
├── database_container.md # 数据库容器配置
├── fetch_and_save_cards.py # 从网页抓取卡牌数据的脚本
├── frontend/            # 前端React应用目录
├── game_engine/         # 游戏引擎核心逻辑
│   └── core.py          # 游戏引擎实现
├── init_db.py           # 初始化数据库并导入卡牌数据
├── main.py              # 主程序入口
├── models/              # 数据模型定义
│   ├── db_models.py     # 数据库模型
│   ├── enums.py         # 游戏枚举类型
│   └── game_models.py   # 游戏核心数据模型
├── pyproject.toml       # Python项目依赖配置
├── start.md             # 启动说明
├── test_auth.sh         # 认证测试脚本
└── uv.lock              # 依赖锁定文件
```

## 核心技术栈

- 后端：Python 3.12+、Flask、Flask-SocketIO、SQLAlchemy、JWT
- 前端：React (TypeScript)、Styled Components、Redux Toolkit
- 数据库：SQLite/PostgreSQL
- 部署：Docker

## 游戏特性

### 核心游戏机制

1. **回合制对战**：游戏按投掷阶段 → 行动阶段 → 结束阶段循环进行
2. **元素系统**：支持7种元素（冰、水、火、雷、风、岩、草）及万能元素
3. **角色系统**：包含角色牌、装备牌、支援牌、事件牌等
4. **游戏状态管理**：完整的游戏状态跟踪（玩家状态、骰子、手牌、召唤物等）
5. **多种游戏模式**：
   - 单人游戏模式
   - 多人在线游戏模式（通过WebSocket）

### 游戏架构

- **模型层**：包含游戏数据模型、枚举类型定义
- **引擎层**：核心游戏逻辑处理
- **API层**：RESTful API接口
- **前端层**：React应用界面

## 开发计划

项目遵循详细的开发计划，分为6个阶段：

1. **基础建设**：搭建核心数据模型、数据库、用户认证系统
2. **单人游戏模式**：实现游戏引擎核心和基本前端UI
3. **多人游戏基础设施**：集成WebSocket通信和匹配系统
4. **UI与游戏交互**：完善游戏界面和交互逻辑
5. **多人游戏体验优化**：增强连接稳定性、观战功能
6. **测试与部署**：全面测试并准备部署方案

## 运行和构建指南

### 环境准备

```bash
# 安装依赖
pip install -e .

# 或使用uv
uv sync
```

### 数据初始化

```bash
# 初始化数据库
python init_db.py

# 抓取卡牌数据
python fetch_and_save_cards.py
```

### 启动服务

```bash
# 启动后端服务
python app.py

# 启动前端开发服务器（在frontend目录下）
cd frontend
npm start
```

## 开发规范

### 代码约定

1. 使用PEP 8代码风格
2. 类型注解遵循Python类型提示标准
3. 所有API接口都使用HTTP状态码和JSON响应格式
4. 游戏逻辑模块化设计，便于维护和扩展

### 测试说明

项目包含测试目录，使用pytest进行单元测试和集成测试。

## 数据模型

### 主要数据实体

1. **用户 (User)**：存储用户账号信息
2. **卡牌数据 (CardData)**：存储从网页抓取的卡牌信息
3. **牌组 (Deck)**：用户的卡组配置
4. **游戏历史 (GameHistory)**：记录游戏对局

### 游戏状态模型

1. **卡牌 (Card)**：基础卡牌数据
2. **角色卡 (CharacterCard)**：角色卡牌特有属性
3. **玩家状态 (PlayerState)**：玩家的当前游戏状态
4. **游戏状态 (GameState)**：整个游戏的状态信息

## API 接口

### 认证相关
- POST `/api/auth/register` - 用户注册
- POST `/api/auth/login` - 用户登录
- GET `/api/auth/profile` - 获取用户信息

### 游戏相关
- GET `/api/characters` - 获取角色卡牌数据
- GET `/api/equipments` - 获取装备卡牌数据
- GET `/api/supports` - 获取支援卡牌数据
- GET `/api/events` - 获取事件卡牌数据
- POST `/api/local-game/start` - 开始单人游戏
- POST `/api/local-game/{session_id}/action` - 发送游戏动作

## 部署配置

项目支持Docker部署，包含docker-compose.yml配置文件。

## 游戏规则

根据项目中的核心规则文档，游戏包括以下主要机制：
- 8个骰子投掷阶段
- 行动阶段中的战斗行动和快速行动
- 角色切换机制
- 元素反应系统
- 装备和支援牌系统
- 胜利条件判断