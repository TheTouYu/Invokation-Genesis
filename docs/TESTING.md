# 七圣召唤测试文档

## 测试策略

本项目采用多层次测试策略，确保代码质量和功能正确性：

- **单元测试**: 验证单个函数和类的正确性
- **集成测试**: 验证模块之间的交互
- **API测试**: 验证REST API端点的功能和响应
- **端到端测试**: 验证完整的用户工作流程

## 测试工具

- **测试框架**: pytest
- **断言库**: Python内置assert
- **测试覆盖率**: coverage.py (可选)
- **API测试**: 内置HTML测试页面 + curl/Postman

## 测试目录结构

```
tests/
├── test_auth.py          # 用户认证测试
├── test_cards.py         # 卡牌系统测试
├── test_deck_builder.py  # 卡组构建测试
├── test_game_engine.py   # 游戏引擎测试
├── test_models.py        # 数据模型测试
└── conftest.py           # 测试配置和fixture
```

## 单元测试指南

### 编写单元测试

1. **测试文件命名**: 以`test_`开头，对应被测试模块
2. **测试函数命名**: 以`test_`开头，描述测试场景
3. **使用fixture**: 通过`conftest.py`提供共享测试数据
4. **边界条件**: 测试正常情况、边界情况和异常情况

### 示例: 卡组验证测试
```python
def test_valid_deck_structure():
    """测试有效的卡组结构 (3角色+30行动牌)"""
    deck = create_valid_deck()
    result = validate_deck(deck)
    assert result.is_valid is True

def test_invalid_deck_too_few_characters():
    """测试角色牌不足的卡组"""
    deck = create_deck_with_few_characters()
    result = validate_deck(deck)
    assert result.is_valid is False
    assert "角色牌数量必须为3" in result.errors
```

## 集成测试指南

### 运行集成测试

```bash
# 运行完整的集成测试套件
python integration_test_final.py

# 运行基础集成测试
python integration_test.py
```

### 集成测试内容

1. **数据库集成**: 验证数据模型与数据库的交互
2. **API路由集成**: 验证API端点与后端逻辑的集成
3. **游戏引擎集成**: 验证游戏规则与API的集成

## API测试方法

### 使用内置测试页面

1. 启动开发服务器: `bash start_dev.sh`
2. 访问: `http://localhost:5000/api/test`
3. 在页面中测试各个API端点

### 使用命令行测试

#### 1. 生成测试令牌
```bash
uv run python dev_tools/generate_test_token.py
```

#### 2. 测试认证API
```bash
# 注册用户
curl -X POST http://localhost:5000/api/auth/register \
  -H "Content-Type: application/json" \
  -d '{"username": "testuser", "password": "testpass"}'

# 登录获取令牌
curl -X POST http://localhost:5000/api/auth/login \
  -H "Content-Type: application/json" \
  -d '{"username": "testuser", "password": "testpass"}'
```

#### 3. 测试卡牌API
```bash
# 获取卡牌列表 (需要JWT令牌)
curl -H "Authorization: Bearer YOUR_JWT_TOKEN" \
     "http://localhost:5000/api/cards?per_page=5"

# 获取特定卡牌
curl -H "Authorization: Bearer YOUR_JWT_TOKEN" \
     "http://localhost:5000/api/cards/CARD_ID"
```

#### 4. 测试卡组API
```bash
# 创建卡组
curl -X POST http://localhost:5000/api/decks \
  -H "Authorization: Bearer YOUR_JWT_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"name": "Test Deck", "cards": ["CARD_ID_1", "CARD_ID_2"]}'

# 验证卡组
curl -X POST http://localhost:5000/api/decks/validate \
  -H "Authorization: Bearer YOUR_JWT_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"cards": ["CARD_ID_1", "CARD_ID_2"]}'
```

#### 5. 测试游戏API
```bash
# 开始游戏
curl -X POST http://localhost:5000/api/local-game/start \
  -H "Authorization: Bearer YOUR_JWT_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"deck_id": "DECK_ID"}'

# 执行游戏行动
curl -X POST http://localhost:5000/api/local-game/SESSION_ID/action \
  -H "Authorization: Bearer YOUR_JWT_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"action_type": "PASS"}'
```

## 测试覆盖率

### 关键模块测试覆盖率目标

- **认证模块**: 100%
- **卡牌系统**: 95%+
- **卡组验证**: 100%
- **游戏引擎**: 90%+
- **API路由**: 95%+

### 运行覆盖率检查 (可选)
```bash
# 安装coverage
pip install coverage

# 运行测试并生成覆盖率报告
coverage run -m pytest tests/
coverage report
coverage html  # 生成HTML报告
```

## 自动化测试流程

### 本地开发测试流程

1. **编写代码**: 实现新功能或修复bug
2. **编写测试**: 为新代码添加相应的单元测试
3. **运行单元测试**: `python -m pytest tests/`
4. **运行集成测试**: `python integration_test_final.py`
5. **手动测试**: 使用API测试页面验证功能
6. **提交代码**: 确保所有测试通过后再提交

### CI/CD测试流程 (建议)

1. **代码推送**: 推送到GitHub仓库
2. **自动构建**: CI系统拉取代码并安装依赖
3. **运行测试**: 执行单元测试和集成测试
4. **生成报告**: 生成测试结果和覆盖率报告
5. **部署**: 测试通过后自动部署到测试环境

## 常见测试场景

### 认证测试场景
- [ ] 新用户注册成功
- [ ] 重复用户名注册失败
- [ ] 有效凭据登录成功
- [ ] 无效凭据登录失败
- [ ] JWT令牌验证成功
- [ ] 过期令牌访问被拒绝

### 卡牌系统测试场景
- [ ] 获取所有卡牌成功
- [ ] 按类型筛选卡牌
- [ ] 按元素筛选卡牌
- [ ] 按国家筛选卡牌
- [ ] 搜索卡牌功能
- [ ] 分页功能正常

### 卡组验证测试场景
- [ ] 有效卡组 (3角色+30行动牌) 通过验证
- [ ] 角色牌数量不足被拒绝
- [ ] 行动牌数量不足被拒绝
- [ ] 同名牌超限被拒绝
- [ ] 天赋牌缺少对应角色被拒绝
- [ ] 元素共鸣牌缺少对应元素角色被拒绝

### 游戏引擎测试场景
- [ ] 游戏初始化正确
- [ ] 回合流程正常
- [ ] 元素反应正确触发
- [ ] 胜利条件正确判断
- [ ] 行动费用正确计算
- [ ] 角色切换功能正常

## 测试数据管理

### 测试数据来源
- **真实卡牌数据**: 使用项目中的JSON卡牌数据
- **模拟用户数据**: 在测试中动态创建
- **预定义测试场景**: 在`conftest.py`中定义常用测试数据

### 测试数据清理
- **数据库测试**: 每个测试用例使用独立的临时数据库
- **内存状态**: 测试前后重置全局状态
- **文件系统**: 避免在测试中创建持久文件

## 调试测试失败

### 常见测试失败原因
1. **环境问题**: 依赖未正确安装
2. **数据问题**: 测试数据与预期不符
3. **时序问题**: 异步操作未正确等待
4. **配置问题**: 测试配置与生产配置差异

### 调试方法
1. **查看详细输出**: 使用`pytest -v`查看详细测试输出
2. **添加日志**: 在被测试代码中添加临时日志
3. **隔离测试**: 单独运行失败的测试用例
4. **检查依赖**: 确保所有依赖都已正确安装

## 测试维护

### 测试代码质量
- **可读性**: 测试代码应该清晰易懂
- **可维护性**: 避免重复代码，使用fixture和helper函数
- **独立性**: 每个测试用例应该独立运行

### 测试更新策略
- **功能变更**: 相关测试必须同步更新
- **重构**: 确保重构不破坏现有测试
- **性能优化**: 添加性能相关的测试用例

## 附录: API测试命令脚本

项目根目录下的`api_test_commands.sh`文件包含了常用的API测试命令，可以直接运行或作为参考：

```bash
# 查看测试命令脚本
cat api_test_commands.sh

# 运行测试命令
bash api_test_commands.sh
```

这些命令涵盖了主要的API端点测试，是快速验证系统功能的有效工具。