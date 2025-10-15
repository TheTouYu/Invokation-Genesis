# 七圣召唤 API 测试指南

## 1. 服务启动

首先确保服务器正在运行：

```bash
./start_dev.sh
```

这将：
- 清理旧进程
- 初始化数据库（包含已导入的519张卡牌数据）
- 启动开发服务器

## 2. 生成认证令牌

```bash
uv run python dev_tools/generate_test_token.py
```

这将：
- 自动创建测试用户（如果不存在）
- 生成有效的JWT令牌
- 输出使用示例

## 3. 图形化API测试（推荐方法）

服务器提供了一个内置的API测试页面：

1. 启动服务器后，访问 `http://localhost:5000/api/test`
2. 在页面上方输入JWT令牌（通过步骤2生成）
3. 使用页面上的按钮直接测试所有API端点
4. 查看返回结果

## 4. API端点测试

### 4.1 公共端点（无需认证）

**健康检查：**
```bash
curl http://localhost:5000/health
```

### 4.2 需要认证的端点

将以下命令中的 `YOUR_JWT_TOKEN` 替换为第2步中生成的令牌。

**获取所有卡牌：**
```bash
curl -H "Authorization: Bearer YOUR_JWT_TOKEN" \
     "http://localhost:5000/api/cards?per_page=10&page=1"
```

**获取角色卡：**
```bash
curl -H "Authorization: Bearer YOUR_JWT_TOKEN" \
     "http://localhost:5000/api/cards/characters?per_page=10"
```

**获取事件卡：**
```bash
curl -H "Authorization: Bearer YOUR_JWT_TOKEN" \
     "http://localhost:5000/api/cards/events?per_page=10"
```

**获取用户卡组：**
```bash
curl -H "Authorization: Bearer YOUR_JWT_TOKEN" \
     http://localhost:5000/api/decks
```

**创建卡组：**
```bash
curl -X POST \
     -H "Content-Type: application/json" \
     -H "Authorization: Bearer YOUR_JWT_TOKEN" \
     -d '{
       "name": "测试卡组",
       "description": "通过API创建的卡组",
       "cards": ["card_id1", "card_id2", "...", "card_id30"]
     }' \
     http://localhost:5000/api/decks
```

**获取特定卡组：**
```bash
curl -H "Authorization: Bearer YOUR_JWT_TOKEN" \
     http://localhost:5000/api/decks/DECK_ID
```

**更新卡组：**
```bash
curl -X PUT \
     -H "Content-Type: application/json" \
     -H "Authorization: Bearer YOUR_JWT_TOKEN" \
     -d '{
       "name": "更新的卡组名称",
       "description": "更新的描述",
       "cards": ["card_id1", "card_id2", "...", "card_id30"]
     }' \
     http://localhost:5000/api/decks/DECK_ID
```

**删除卡组：**
```bash
curl -X DELETE \
     -H "Authorization: Bearer YOUR_JWT_TOKEN" \
     http://localhost:5000/api/decks/DECK_ID
```

## 5. 本地游戏API测试

**开始本地游戏：**
```bash
curl -X POST \
     -H "Content-Type: application/json" \
     -H "Authorization: Bearer YOUR_JWT_TOKEN" \
     -d '{
       "deck_id": "YOUR_DECK_ID",
       "opponent_type": "ai"
     }' \
     http://localhost:5000/api/local-game/start
```

**处理游戏行动：**
```bash
curl -X POST \
     -H "Content-Type: application/json" \
     -H "Authorization: Bearer YOUR_JWT_TOKEN" \
     -d '{
       "action_type": "PLAY_CARD",
       "payload": {
         "card_id": "CARD_ID_TO_PLAY"
       }
     }' \
     http://localhost:5000/api/local-game/GAME_SESSION_ID/action
```

## 6. 使用Postman测试

1. 安装Postman（https://www.postman.com/）
2. 创建新请求
3. 设置HTTP方法和URL（如 `http://localhost:5000/api/cards`）
4. 在Headers选项卡中添加：
   - Key: `Authorization`
   - Value: `Bearer YOUR_JWT_TOKEN`
5. 发送请求

## 7. 常见问题

**Q: 401 Unauthorized错误**
A: JWT令牌无效或已过期，请重新生成令牌

**Q: 422 Missing claim: sub错误**
A: JWT令牌格式不正确，确保令牌载荷中包含sub字段

**Q: 500数据库错误**
A: 确保数据库已正确初始化，重新运行 `./start_dev.sh`

**Q: CORS错误（前端调用时）**
A: 后端已配置CORS允许所有来源，确保前端请求正确设置认证头