# 七圣召唤（Genshin Impact Card Game）项目启动指南

## 项目概述

这是一个复刻原神里面的七圣召唤的项目。《七圣召唤》是一款节奏紧凑、对抗激烈的卡牌类桌面对战游戏。本项目旨在实现完整的七圣召唤游戏体验，包括单人模式、多人对战、卡牌收集等功能。

## 当前开发状态

截至 2025年10月15日，项目已实现以下功能模块：

### 已完成的功能

1. **基础架构**
   - Flask后端服务，包含用户认证、卡牌管理、游戏逻辑等模块
   - SQLAlchemy数据库模型，支持SQLite/PostgreSQL
   - JWT用户认证系统
   - WebSocket支持（用于多人游戏）

2. **数据模型**
   - 完整的枚举类型定义（元素、卡牌类型、骰子类型等）
   - 游戏核心数据模型（卡牌、角色卡、玩家状态、游戏状态等）
   - 数据库模型（用户、卡牌数据、卡组、游戏历史等）

3. **卡牌系统**
   - 从JSON文件导入519张卡牌（121张角色牌、104张事件牌、226张装备牌、68张支援牌）
   - 卡牌获取API（分页、筛选、搜索）
   - 卡牌详情查询

4. **用户系统**
   - 用户注册/登录
   - 个人信息管理
   - 卡组管理（创建、编辑、删除、查询）

5. **游戏引擎**
   - 完整的回合流程控制（投骰阶段、行动阶段、结束阶段）
   - 费用支付系统（元素骰、万能骰、同色骰等）
   - 基础游戏操作（使用技能、切换角色、打出手牌、结束回合）
   - 游戏状态管理

6. **API接口**
   - 完整的REST API，包括认证、卡牌、卡组、游戏等端点
   - 本地单人游戏API
   - API测试页面

### 已修复的问题

- 修复了Flask-SQLAlchemy初始化问题
- 修复了dataclass参数顺序导致的Python错误
- 修复了API路由前缀重复导致的404问题（本地游戏API）
- 修复了卡组验证逻辑

### 集成测试

- 完整的API集成测试套件
- 自动化测试流程
- 一键运行所有测试

## 快速开始

### 环境准备

1. 确保已安装 Python 3.12+
2. 安装 uv 包管理器（或使用 pip）

### 启动步骤

1. **安装依赖**
   ```bash
   uv sync  # 或者 pip install -r requirements.txt
   ```

2. **启动开发服务器**
   ```bash
   bash start_dev.sh
   ```

3. **访问服务**
   - 服务器地址：http://localhost:5000
   - API测试页面：http://localhost:5000/api/test
   - 健康检查：http://localhost:5000/health

### API测试

1. **获取测试令牌**
   ```bash
   uv run python dev_tools/generate_test_token.py
   ```

2. **使用API测试页面**
   访问 http://localhost:5000/api/test 在浏览器中测试API

## 项目结构

```
ys_qs/
├── api/                 # API路由模块
├── card_data/           # 卡牌数据JSON文件
├── dev_tools/           # 开发工具
├── game_engine/         # 游戏引擎核心
├── models/              # 数据模型
│   ├── db_models.py     # 数据库模型
│   ├── enums.py         # 枚举类型
│   └── game_models.py   # 游戏数据模型
├── socket_handlers/     # WebSocket处理器
├── app.py              # Flask应用主文件
├── run_dev_server.py   # 开发服务器启动
├── integration_test_final.py  # 集成测试
└── start_dev.sh        # 开发服务器启动脚本
```

## 下一步开发计划

1. **前端开发**
   - React前端界面
   - 卡牌展示和交互组件
   - 游戏界面UI开发

2. **WebSocket多人游戏**
   - 实时对战功能
   - 匹配系统
   - 观战功能

3. **游戏逻辑完善**
   - 角色技能系统
   - 元素反应机制
   - 装备和天赋系统

4. **AI对手开发**
   - 智能对手逻辑
   - 不同难度等级

## 开发工具

- `dev_tools/generate_test_token.py` - 生成API测试令牌
- `integration_test_final.py` - 运行完整的API集成测试
- `api_test_page.html` - API测试页面
- `start_dev.sh` - 快速启动开发服务器