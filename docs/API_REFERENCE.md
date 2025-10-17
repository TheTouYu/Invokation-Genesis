# 七圣召唤 API 参考文档

## 概述

本API提供了完整的七圣召唤游戏功能，包括用户认证、卡牌数据管理、卡组构建、本地游戏功能等。API使用JWT进行身份验证，所有需要认证的端点都要求在请求头中包含有效的JWT令牌。

## 认证说明

所有需要认证的端点都需要在请求头中包含JWT令牌：

```
Authorization: Bearer {access_token}
```

令牌通过 `/api/auth/login` 端点获取。

## 错误处理

API使用标准的HTTP状态码和JSON格式的错误响应：

- `200`: 成功
- `201`: 创建成功
- `400`: 请求参数错误
- `401`: 未认证
- `403`: 无权限访问
- `404`: 资源不存在
- `500`: 服务器内部错误

错误响应格式：
```json
{
  "error": "错误描述"
}
```

## 认证接口

### POST /api/auth/register
创建新的用户账户。

**请求体参数**
| 参数名 | 类型 | 必需 | 描述 |
|--------|------|------|------|
| username | string | 是 | 用户名（必须唯一） |
| password | string | 是 | 密码 |
| email | string | 否 | 电子邮箱（如果未提供，将使用{username}@example.com） |

**响应**
- 成功 (201): `{"message": "User registered successfully."}`
- 错误 (400): `{"message": "Username already exists."}`
- 错误 (400): `{"message": "Username and password are required."}`

### POST /api/auth/login
获取JWT访问令牌。

**请求体参数**
| 参数名 | 类型 | 必需 | 描述 |
|--------|------|------|------|
| username | string | 是 | 用户名 |
| password | string | 是 | 密码 |

**响应**
- 成功 (200): `{"access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..."}`
- 错误 (400): `{"message": "Username and password are required."}`
- 错误 (401): `{"message": "Invalid credentials."}`

### GET /api/auth/profile
获取当前认证用户的信息。

**响应**
- 成功 (200): 
```json
{
  "id": "user-uuid-string",
  "username": "testuser"
}
```
- 错误 (404): `{"message": "User not found."}`

## 卡牌系统接口

### GET /api/cards
获取卡牌数据，支持多种过滤条件和分页。

**URL参数**
| 参数名 | 类型 | 必需 | 描述 |
|--------|------|------|------|
| type | string | 否 | 卡牌类型（角色牌, 事件牌, 武器, 圣遗物, 支援牌, 非角色牌） |
| element | string | 否 | 元素类型（火, 水, 雷, 草, 风, 岩, 冰, 物理, 万能等） |
| country | string | 否 | 国家（蒙德, 璃月, 稻妻等） |
| weapon_type | string | 否 | 武器类型（单手剑, 双手剑, 长柄武器, 弓, 法器等） |
| character_subtype | string | 否 | 角色子类型 |
| rarity | integer | 否 | 稀有度（1, 2, 3, 4, 5） |
| search | string | 否 | 搜索关键词 |
| tag | string[] | 否 | 标签列表（可多次使用此参数） |
| page | integer | 否 | 页码（默认为1） |
| per_page | integer | 否 | 每页数量（默认为20，最大为100） |

**响应**
- 成功 (200): 返回分页的卡牌列表和元数据

### GET /api/cards/{card_id}
根据ID获取特定卡牌的详细信息。

**路径参数**
| 参数名 | 类型 | 必需 | 描述 |
|--------|------|------|------|
| card_id | string | 是 | 卡牌的唯一ID |

**响应**
- 成功 (200): 返回卡牌详细信息
- 错误 (404): `{"error": "卡牌不存在"}`

### GET /api/cards/types
获取所有可用的卡牌类型列表。

**响应**
- 成功 (200): `{"types": ["角色牌", "事件牌", "武器", "圣遗物", "支援牌"]}`

### GET /api/cards/elements
获取所有可用的元素类型列表。

**响应**
- 成功 (200): `{"elements": ["火", "水", "雷", "草", "风", "岩", "冰", "物理", "万能"]}`

### GET /api/cards/countries
获取所有可用的国家/地区列表。

**响应**
- 成功 (200): `{"countries": ["蒙德", "璃月", "稻妻", "须弥", "枫丹", "纳塔", "至冬", "魔物", "愚人众"]}`

### GET /api/cards/weapon_types
获取所有可用的武器类型列表。

**响应**
- 成功 (200): `{"weapon_types": ["单手剑", "双手剑", "长柄武器", "弓", "法器", "其他武器"]}`

### GET /api/cards/tags
获取所有可用的卡牌标签列表。

**响应**
- 成功 (200): `{"tags": ["事件牌", "装备牌", "支援牌", "角色牌", "元素共鸣", "武器", "圣遗物", "天赋"]}`

### GET /api/cards/random
获取随机选择的卡牌，支持过滤条件。

**URL参数**
| 参数名 | 类型 | 必需 | 描述 |
|--------|------|------|------|
| type | string | 否 | 卡牌类型过滤 |
| element | string | 否 | 元素类型过滤 |
| country | string | 否 | 国家过滤 |
| weapon_type | string | 否 | 武器类型过滤 |
| count | integer | 否 | 获取卡牌数量（默认为1） |

## 卡组管理接口

### GET /api/decks
获取当前用户的所有卡组。

**响应**
- 成功 (200): 返回卡组列表

### POST /api/decks
创建一个新的卡组。

**请求体参数**
| 参数名 | 类型 | 必需 | 描述 |
|--------|------|------|------|
| name | string | 是 | 卡组名称 |
| description | string | 否 | 卡组描述 |
| cards | string[] | 否 | 卡牌ID列表 |

**响应**
- 成功 (201): 返回创建的卡组信息
- 错误 (400): `{"error": "卡组名称不能为空"}`
- 错误 (400): `{"error": "卡组验证失败", "details": ["错误详情"]}`

### PUT /api/decks/{deck_id}
更新指定ID的卡组。

**路径参数**
| 参数名 | 类型 | 必需 | 描述 |
|--------|------|------|------|
| deck_id | string | 是 | 卡组的唯一ID |

**请求体参数**
| 参数名 | 类型 | 必需 | 描述 |
|--------|------|------|------|
| name | string | 否 | 卡组名称 |
| description | string | 否 | 卡组描述 |
| cards | string[] | 否 | 卡牌ID列表 |

**响应**
- 成功 (200): 返回更新的卡组信息
- 错误 (404): `{"error": "卡组不存在或无权限访问"}`
- 错误 (400): `{"error": "卡组验证失败", "details": ["错误详情"]}`

### DELETE /api/decks/{deck_id}
删除指定ID的卡组。

**路径参数**
| 参数名 | 类型 | 必需 | 描述 |
|--------|------|------|------|
| deck_id | string | 是 | 卡组的唯一ID |

**响应**
- 成功 (200): `{"message": "卡组删除成功"}`
- 错误 (404): `{"error": "卡组不存在或无权限访问"}`

### GET /api/decks/{deck_id}
获取指定ID的卡组详细信息。

**路径参数**
| 参数名 | 类型 | 必需 | 描述 |
|--------|------|------|------|
| deck_id | string | 是 | 卡组的唯一ID |

**响应**
- 成功 (200): 返回卡组详细信息（包含完整卡牌数据）
- 错误 (404): `{"error": "卡组不存在或无权限访问"}`

### POST /api/decks/validate
验证卡组是否符合游戏规则。

**请求体参数**
| 参数名 | 类型 | 必需 | 描述 |
|--------|------|------|------|
| cards | string[] | 是 | 卡牌ID列表 |

**响应**
- 成功 (200): 返回验证结果，包含是否有效、错误列表、警告列表和详细信息

### POST /api/deck/validate
卡组构建器专用验证端点，验证一个卡组组成是否符合游戏规则。

**请求体参数**
| 参数名 | 类型 | 必需 | 描述 |
|--------|------|------|------|
| characters | string[] | 否 | 角色卡ID列表 |
| cards | string[] | 否 | 卡牌ID列表 |
| deck_name | string | 否 | 卡组名称 |

**响应**
- 成功 (200): 返回详细的验证结果，包含各规则的验证状态和消息
- 错误 (400): 返回验证错误信息

## 游戏接口

### POST /api/local-game/start
开始一个新的本地游戏。

**请求体参数**
| 参数名 | 类型 | 必需 | 描述 |
|--------|------|------|------|
| opponent_type | string | 否 | 对手类型（'ai' 或 'human'，默认为'ai'） |
| deck_id | string | 是 | 使用的卡组ID |

**响应**
- 成功 (200): 返回游戏会话ID和初始游戏状态
- 错误 (400): `{"error": "必须选择一个卡组"}`
- 错误 (404): `{"error": "卡组不存在或无权限访问"}`

### POST /api/local-game/{session_id}/action
处理游戏中的特定行动。

**路径参数**
| 参数名 | 类型 | 必需 | 描述 |
|--------|------|------|------|
| session_id | string | 是 | 游戏会话ID |

**请求体参数**
| 参数名 | 类型 | 必需 | 描述 |
|--------|------|------|------|
| action_type | string | 是 | 行动类型（PLAY_CARD, USE_SKILL, SWITCH_CHARACTER, PASS, REROLL_DICE, ELEMENTAL_TUNING, REPLACE_CARDS, QUICK_ACTION, COMBAT_ACTION） |
| payload | object | 否 | 行动相关数据，根据行动类型而定 |

**响应**
- 成功 (200): 返回更新后的游戏状态
- 错误 (400): `{"error": "必须指定行动类型"}`
- 错误 (404): `{"error": "游戏会话不存在"}`
- 错误 (403): `{"error": "无权访问此游戏会话"}`

### GET /api/local-game/{session_id}/state
获取当前游戏状态。

**路径参数**
| 参数名 | 类型 | 必需 | 描述 |
|--------|------|------|------|
| session_id | string | 是 | 游戏会话ID |

**响应**
- 成功 (200): 返回当前游戏状态
- 错误 (404): `{"error": "游戏会话不存在"}`
- 错误 (403): `{"error": "无权访问此游戏会话"}`

### POST /api/local-game/{session_id}/end
结束当前游戏会话。

**路径参数**
| 参数名 | 类型 | 必需 | 描述 |
|--------|------|------|------|
| session_id | string | 是 | 游戏会话ID |

**响应**
- 成功 (200): `{"message": "本地游戏已结束"}`
- 错误 (404): `{"error": "游戏会话不存在"}`
- 错误 (403): `{"error": "无权访问此游戏会话"}`

## 辅助接口

### GET /health
检查服务器健康状态。

**响应**
- 成功 (200): `{"status": "healthy", "message": "七圣召唤游戏服务器运行正常"}`

### GET /api/test
提供一个HTML页面用于测试API端点。

**响应**
- 成功 (200): 返回HTML测试页面