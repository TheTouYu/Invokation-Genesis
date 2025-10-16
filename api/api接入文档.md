✦ 七圣召唤后端API接口文档

  概述

  本API提供了完整的七圣召唤游戏功能，包括用户认证、卡牌数据管理、卡组构建、本地游戏功能等。API使用JWT进行身份验证，所有需要认证的端点都要求在请求头中包含有效的JWT令牌。

  认证接口

  1. 用户注册 - /api/auth/register (POST)
  创建新的用户账户。

  请求信息
   - 方法: POST
   - URL: /api/auth/register

  请求体参数

  ┌──────────┬────────┬──────┬──────────────────────────────────────────────────────┐
  │ 参数名   │ 类型   │ 必需 │ 描述                                                 │
  ├──────────┼────────┼──────┼──────────────────────────────────────────────────────┤
  │ username │ string │ 是   │ 用户名（必须唯一）                                   │
  │ password │ string │ 是   │ 密码                                                 │
  │ email    │ string │ 否   │ 电子邮箱（如果未提供，将使用{username}@example.com） │
  └──────────┴────────┴──────┴──────────────────────────────────────────────────────┘


  响应
   - 成功响应 (201):

   1   {
   2     "message": "User registered successfully."
   3   }

   - 错误响应 (400):

   1   {
   2     "message": "Username already exists."
   3   }

   - 错误响应 (400):

   1   {
   2     "message": "Username and password are required."
   3   }

  示例请求

   1 curl -X POST http://localhost:5000/api/auth/register \
   2   -H "Content-Type: application/json" \
   3   -d '{
   4     "username": "testuser",
   5     "password": "password123",
   6     "email": "test@example.com"
   7   }'

  2. 用户登录 - /api/auth/login (POST)
  获取JWT访问令牌。

  请求信息
   - 方法: POST
   - URL: /api/auth/login

  请求体参数

  ┌──────────┬────────┬──────┬────────┐
  │ 参数名   │ 类型   │ 必需 │ 描述   │
  ├──────────┼────────┼──────┼────────┤
  │ username │ string │ 是   │ 用户名 │
  │ password │ string │ 是   │ 密码   │
  └──────────┴────────┴──────┴────────┘


  响应
   - 成功响应 (200):

   1   {
   2     "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..."
   3   }

   - 错误响应 (400):

   1   {
   2     "message": "Username and password are required."
   3   }

   - 错误响应 (401):

   1   {
   2     "message": "Invalid credentials."
   3   }

  示例请求

   1 curl -X POST http://localhost:5000/api/auth/login \
   2   -H "Content-Type: application/json" \
   3   -d '{
   4     "username": "testuser",
   5     "password": "password123"
   6   }'

  3. 获取用户资料 - /api/auth/profile (GET)
  获取当前认证用户的信息。

  请求信息
   - 方法: GET
   - URL: /api/auth/profile
   - 认证: 需要在请求头中包含JWT令牌

  请求头

  ┌───────────────┬────────────────┐
  │ 头部          │ 值             │
  ├───────────────┼────────────────┤
  │ Authorization │ Bearer {token} │
  └───────────────┴────────────────┘


  响应
   - 成功响应 (200):

   1   {
   2     "id": "user-uuid-string",
   3     "username": "testuser"
   4   }

   - 错误响应 (404):

   1   {
   2     "message": "User not found."
   3   }

  示例请求

   1 curl -X GET http://localhost:5000/api/auth/profile \
   2   -H "Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..."

  卡牌系统接口

  1. 获取所有卡牌 - /api/cards (GET)
  获取卡牌数据，支持多种过滤条件和分页。

  请求信息
   - 方法: GET
   - URL: /api/cards
   - 认证: 需要在请求头中包含JWT令牌

  URL参数

  ┌───────────────────┬──────────┬──────┬────────────────────────────────────────────────────────────┐
  │ 参数名            │ 类型     │ 必需 │ 描述                                                       │
  ├───────────────────┼──────────┼──────┼────────────────────────────────────────────────────────────┤
  │ type              │ string   │ 否   │ 卡牌类型（角色牌, 事件牌, 武器, 圣遗物, 支援牌, 非角色牌） │
  │ element           │ string   │ 否   │ 元素类型（火, 水, 雷, 草, 风, 岩, 冰, 物理, 万能等）       │
  │ country           │ string   │ 否   │ 国家（蒙德, 璃月, 稻妻等）                                 │
  │ weapon_type       │ string   │ 否   │ 武器类型（单手剑, 双手剑, 长柄武器, 弓, 法器等）           │
  │ character_subtype │ string   │ 否   │ 角色子类型                                                 │
  │ rarity            │ integer  │ 否   │ 稀有度（1, 2, 3, 4, 5）                                    │
  │ search            │ string   │ 否   │ 搜索关键词（在名称、描述、类型、子类型、技能中搜索）       │
  │ tag               │ string[] │ 否   │ 标签列表（可多次使用此参数）                               │
  │ page              │ integer  │ 否   │ 页码（默认为1）                                            │
  │ per_page          │ integer  │ 否   │ 每页数量（默认为20，最大为100）                            │
  └───────────────────┴──────────┴──────┴────────────────────────────────────────────────────────────┘


  响应
   - 成功响应 (200):

    1   {
    2     "cards": [
    3       {
    4         "id": "card-id-string",
    5         "name": "卡牌名称",
    6         "type": "角色牌",
    7         "description": "卡牌描述",
    8         "cost": [
    9           {
   10             "type": "火",
   11             "count": 1
   12           }
   13         ],
   14         "rarity": 5,
   15         "element_type": "火",
   16         "character_subtype": "蒙德",
   17         "image_url": "https://example.com/image.jpg",
   18         "country": "蒙德",
   19         "element": "火",
   20         "weapon_type": "单手剑",
   21         "skills": [
   22           {
   23             "name": "技能名称",
   24             "description": "技能描述",
   25             "cost": [...]
   26           }
   27         ],
   28         "title": "角色称号",
   29         "health": 10,
   30         "energy": 0,
   31         "max_health": 10,
   32         "max_energy": 3
   33       }
   34     ],
   35     "total": 150,
   36     "pages": 8,
   37     "current_page": 1,
   38     "per_page": 20,
   39     "has_next": true,
   40     "has_prev": false
   41   }

  示例请求

   1 curl -X GET "http://localhost:5000/api/cards?type=角色牌&element=火&page=1&per_page=10" \
   2   -H "Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..."

  2. 获取卡牌详情 - /api/cards/<card_id> (GET)
  根据ID获取特定卡牌的详细信息。

  请求信息
   - 方法: GET
   - URL: /api/cards/{card_id}
   - 认证: 需要在请求头中包含JWT令牌

  路径参数

  ┌─────────┬────────┬──────┬──────────────┐
  │ 参数名  │ 类型   │ 必需 │ 描述         │
  ├─────────┼────────┼──────┼──────────────┤
  │ card_id │ string │ 是   │ 卡牌的唯一ID │
  └─────────┴────────┴──────┴──────────────┘


  响应
   - 成功响应 (200):

    1   {
    2     "card": {
    3       "id": "card-id-string",
    4       "name": "卡牌名称",
    5       "type": "角色牌",
    6       "description": "卡牌描述",
    7       "cost": [
    8         {
    9           "type": "火",
   10           "count": 1
   11         }
   12       ],
   13       "rarity": 5,
   14       "element_type": "火",
   15       "character_subtype": "蒙德",
   16       "image_url": "https://example.com/image.jpg",
   17       "country": "蒙德",
   18       "element": "火",
   19       "weapon_type": "单手剑",
   20       "skills": [...],
   21       "title": "角色称号",
   22       "health": 10,
   23       "energy": 0,
   24       "max_health": 10,
   25       "max_energy": 3
   26     }
   27   }

   - 错误响应 (404):

   1   {
   2     "error": "卡牌不存在"
   3   }

  示例请求

   1 curl -X GET "http://localhost:5000/api/cards/card-uuid-string" \
   2   -H "Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..."

  3. 卡牌类型列表 - /api/cards/types (GET)
  获取所有可用的卡牌类型列表。

  请求信息
   - 方法: GET
   - URL: /api/cards/types
   - 认证: 需要在请求头中包含JWT令牌

  响应
   - 成功响应 (200):

   1   {
   2     "types": ["角色牌", "事件牌", "武器", "圣遗物", "支援牌"]
   3   }

  示例请求

   1 curl -X GET "http://localhost:5000/api/cards/types" \
   2   -H "Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..."

  4. 元素类型列表 - /api/cards/elements (GET)
  获取所有可用的元素类型列表。

  请求信息
   - 方法: GET
   - URL: /api/cards/elements
   - 认证: 需要在请求头中包含JWT令牌

  响应
   - 成功响应 (200):

   1   {
   2     "elements": ["火", "水", "雷", "草", "风", "岩", "冰", "物理", "万能"]
   3   }

  示例请求

   1 curl -X GET "http://localhost:5000/api/cards/elements" \
   2   -H "Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..."

  5. 国家列表 - /api/cards/countries (GET)
  获取所有可用的国家/地区列表。

  请求信息
   - 方法: GET
   - URL: /api/cards/countries
   - 认证: 需要在请求头中包含JWT令牌

  响应
   - 成功响应 (200):

   1   {
   2     "countries": ["蒙德", "璃月", "稻妻", "须弥", "枫丹", "纳塔", "至冬", "魔物", "愚人众"]
   3   }

  示例请求

   1 curl -X GET "http://localhost:5000/api/cards/countries" \
   2   -H "Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..."

  6. 武器类型列表 - /api/cards/weapon_types (GET)
  获取所有可用的武器类型列表。

  请求信息
   - 方法: GET
   - URL: /api/cards/weapon_types
   - 认证: 需要在请求头中包含JWT令牌

  响应
   - 成功响应 (200):

   1   {
   2     "weapon_types": ["单手剑", "双手剑", "长柄武器", "弓", "法器", "其他武器"]
   3   }

  示例请求

   1 curl -X GET "http://localhost:5000/api/cards/weapon_types" \
   2   -H "Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..."

  7. 卡牌标签列表 - /api/cards/tags (GET)
  获取所有可用的卡牌标签列表。

  请求信息
   - 方法: GET
   - URL: /api/cards/tags
   - 认证: 需要在请求头中包含JWT令牌

  响应
   - 成功响应 (200):

   1   {
   2     "tags": ["事件牌", "装备牌", "支援牌", "角色牌", "元素共鸣", "武器", "圣遗物", "天赋"]
   3   }

  示例请求

   1 curl -X GET "http://localhost:5000/api/cards/tags" \
   2   -H "Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..."

  8. 随机卡牌 - /api/cards/random (GET)
  获取随机选择的卡牌，支持过滤条件。

  请求信息
   - 方法: GET
   - URL: /api/cards/random
   - 认证: 需要在请求头中包含JWT令牌

  URL参数

  ┌─────────────┬─────────┬──────┬─────────────────────────┐
  │ 参数名      │ 类型    │ 必需 │ 描述                    │
  ├─────────────┼─────────┼──────┼─────────────────────────┤
  │ type        │ string  │ 否   │ 卡牌类型过滤            │
  │ element     │ string  │ 否   │ 元素类型过滤            │
  │ country     │ string  │ 否   │ 国家过滤                │
  │ weapon_type │ string  │ 否   │ 武器类型过滤            │
  │ count       │ integer │ 否   │ 获取卡牌数量（默认为1） │
  └─────────────┴─────────┴──────┴─────────────────────────┘


  响应
   - 成功响应 (200):

    1   {
    2     "cards": [
    3       {
    4         "id": "card-id-string",
    5         "name": "卡牌名称",
    6         "type": "角色牌",
    7         "description": "卡牌描述",
    8         "cost": [...],
    9         "rarity": 5,
   10         "element_type": "火",
   11         "character_subtype": "蒙德",
   12         "image_url": "https://example.com/image.jpg",
   13         "country": "蒙德",
   14         "element": "火",
   15         "weapon_type": "单手剑",
   16         "skills": [...],
   17         "title": "角色称号",
   18         "health": 10,
   19         "energy": 0,
   20         "max_health": 10,
   21         "max_energy": 3
   22       }
   23     ],
   24     "total": 1
   25   }

  示例请求

   1 curl -X GET "http://localhost:5000/api/cards/random?type=角色牌&count=3" \
   2   -H "Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..."

  9. 角色过滤选项 - /api/characters/filters (GET)
  获取角色的过滤选项（国家、元素、武器类型）。

  请求信息
   - 方法: GET
   - URL: /api/characters/filters
   - 认证: 需要在请求头中包含JWT令牌

  响应
   - 成功响应 (200):

   1   {
   2     "countries": ["蒙德", "璃月", "稻妻"],
   3     "elements": ["火", "水", "雷", "草", "风", "岩", "冰"],
   4     "weapon_types": ["单手剑", "双手剑", "长柄武器", "弓", "法器"]
   5   }

  示例请求

   1 curl -X GET "http://localhost:5000/api/characters/filters" \
   2   -H "Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..."

  10. 搜索卡牌 - /api/cards/search (GET)
  搜索卡牌（此接口与/api/cards具有相同功能，作为别名存在）。

  请求信息
   - 方法: GET
   - URL: /api/cards/search
   - 认证: 需要在请求头中包含JWT令牌

  URL参数
  与/api/cards接口相同

  响应
  与/api/cards接口相同

  11. 过滤卡牌 - /api/cards/filter (GET)
  使用统一过滤参数过滤卡牌。

  请求信息
   - 方法: GET
   - URL: /api/cards/filter
   - 认证: 需要在请求头中包含JWT令牌

  URL参数

  ┌───────────────────┬──────────┬──────┬────────────────────────────────────┐
  │ 参数名            │ 类型     │ 必需 │ 描述                               │
  ├───────────────────┼──────────┼──────┼────────────────────────────────────┤
  │ type              │ string   │ 否   │ 卡牌类型                           │
  │ element           │ string   │ 否   │ 元素类型                           │
  │ country           │ string   │ 否   │ 国家                               │
  │ weapon_type       │ string   │ 否   │ 武器类型                           │
  │ character_subtype │ string   │ 否   │ 角色子类型                         │
  │ rarity            │ integer  │ 否   │ 稀有度                             │
  │ search            │ string   │ 否   │ 搜索关键词（兼容q参数）            │
  │ q                 │ string   │ 否   │ 搜索关键词（与search参数功能相同） │
  │ tag               │ string[] │ 否   │ 标签列表（可多次使用此参数）       │
  └───────────────────┴──────────┴──────┴────────────────────────────────────┘


  响应
   - 成功响应 (200):

   1   {
   2     "cards": [...],
   3     "total": 10
   4   }

  12. 角色牌列表 - /api/characters (GET)
  兼容性端点：获取角色牌数据。

  请求信息
   - 方法: GET
   - URL: /api/characters
   - 认证: 需要在请求头中包含JWT令牌

  URL参数

  ┌──────────┬─────────┬──────┬─────────────────────────────────┐
  │ 参数名   │ 类型    │ 必需 │ 描述                            │
  ├──────────┼─────────┼──────┼─────────────────────────────────┤
  │ page     │ integer │ 否   │ 页码（默认为1）                 │
  │ per_page │ integer │ 否   │ 每页数量（默认为20，最大为100） │
  └──────────┴─────────┴──────┴─────────────────────────────────┘


  响应
   - 成功响应 (200):

    1   [
    2     {
    3       "id": "char-id-string",
    4       "name": "角色名称",
    5       "type": "角色牌",
    6       "description": "角色描述",
    7       "cost": [...],
    8       "rarity": 5,
    9       "element_type": "火",
   10       "character_subtype": "蒙德",
   11       "image_url": "https://example.com/image.jpg",
   12       "country": "蒙德",
   13       "element": "火",
   14       "weapon_type": "单手剑",
   15       "skills": [...],
   16       "title": "角色称号",
   17       "health": 10,
   18       "energy": 0,
   19       "max_health": 10,
   20       "max_energy": 3
   21     }
   22   ]

  13. 装备牌列表 - /api/equipments (GET)
  兼容性端点：获取装备牌数据。

  请求信息
   - 方法: GET
   - URL: /api/equipments
   - 认证: 需要在请求头中包含JWT令牌

  URL参数

  ┌──────────┬─────────┬──────┬─────────────────────────────────┐
  │ 参数名   │ 类型    │ 必需 │ 描述                            │
  ├──────────┼─────────┼──────┼─────────────────────────────────┤
  │ page     │ integer │ 否   │ 页码（默认为1）                 │
  │ per_page │ integer │ 否   │ 每页数量（默认为20，最大为100） │
  └──────────┴─────────┴──────┴─────────────────────────────────┘


  响应
   - 成功响应 (200):

    1   [
    2     {
    3       "id": "equip-id-string",
    4       "name": "装备名称",
    5       "type": "武器",
    6       "description": "装备描述",
    7       "cost": [...],
    8       "rarity": 4,
    9       "element_type": null,
   10       "character_subtype": "单手剑角色",
   11       "image_url": "https://example.com/image.jpg",
   12       "country": "",
   13       "element": "",
   14       "weapon_type": "单手剑",
   15       "skills": [],
   16       "title": "武器名",
   17       "health": null,
   18       "energy": null,
   19       "max_health": null,
   20       "max_energy": null
   21     }
   22   ]

  14. 支援牌列表 - /api/supports (GET)
  兼容性端点：获取支援牌数据。

  请求信息
   - 方法: GET
   - URL: /api/supports
   - 认证: 需要在请求头中包含JWT令牌

  URL参数

  ┌──────────┬─────────┬──────┬─────────────────────────────────┐
  │ 参数名   │ 类型    │ 必需 │ 描述                            │
  ├──────────┼─────────┼──────┼─────────────────────────────────┤
  │ page     │ integer │ 否   │ 页码（默认为1）                 │
  │ per_page │ integer │ 否   │ 每页数量（默认为20，最大为100） │
  └──────────┴─────────┴──────┴─────────────────────────────────┘


  响应
   - 成功响应 (200):

    1   [
    2     {
    3       "id": "support-id-string",
    4       "name": "支援名称",
    5       "type": "支援牌",
    6       "description": "支援描述",
    7       "cost": [...],
    8       "rarity": 3,
    9       "element_type": null,
   10       "character_subtype": null,
   11       "image_url": "https://example.com/image.jpg",
   12       "country": "",
   13       "element": "",
   14       "weapon_type": "",
   15       "skills": [],
   16       "title": "",
   17       "health": null,
   18       "energy": null,
   19       "max_health": null,
   20       "max_energy": null
   21     }
   22   ]

  15. 事件牌列表 - /api/events (GET)
  兼容性端点：获取事件牌数据。

  请求信息
   - 方法: GET
   - URL: /api/events
   - 认证: 需要在请求头中包含JWT令牌

  URL参数

  ┌──────────┬─────────┬──────┬─────────────────────────────────┐
  │ 参数名   │ 类型    │ 必需 │ 描述                            │
  ├──────────┼─────────┼──────┼─────────────────────────────────┤
  │ page     │ integer │ 否   │ 页码（默认为1）                 │
  │ per_page │ integer │ 否   │ 每页数量（默认为20，最大为100） │
  └──────────┴─────────┴──────┴─────────────────────────────────┘


  响应
   - 成功响应 (200):

    1   [
    2     {
    3       "id": "event-id-string",
    4       "name": "事件名称",
    5       "type": "事件牌",
    6       "description": "事件描述",
    7       "cost": [...],
    8       "rarity": 2,
    9       "element_type": null,
   10       "character_subtype": null,
   11       "image_url": "https://example.com/image.jpg",
   12       "country": "",
   13       "element": "",
   14       "weapon_type": "",
   15       "skills": [],
   16       "title": "",
   17       "health": null,
   18       "energy": null,
   19       "max_health": null,
   20       "max_energy": null
   21     }
   22   ]

  卡组管理接口

  1. 获取用户卡组列表 - /api/decks (GET)
  获取当前用户的所有卡组。

  请求信息
   - 方法: GET
   - URL: /api/decks
   - 认证: 需要在请求头中包含JWT令牌

  响应
   - 成功响应 (200):

    1   {
    2     "decks": [
    3       {
    4         "id": "deck-id-string",
    5         "name": "卡组名称",
    6         "description": "卡组描述",
    7         "cards": [
    8           "card-id-1",
    9           "card-id-2",
   10           "card-id-3"
   11         ],
   12         "created_at": "2023-01-01T00:00:00.000Z",
   13         "updated_at": "2023-01-01T00:00:00.000Z"
   14       }
   15     ]
   16   }

  示例请求

   1 curl -X GET "http://localhost:5000/api/decks" \
   2   -H "Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..."

  2. 创建卡组 - /api/decks (POST)
  创建一个新的卡组。

  请求信息
   - 方法: POST
   - URL: /api/decks
   - 认证: 需要在请求头中包含JWT令牌

  请求体参数

  ┌─────────────┬──────────┬──────┬────────────┐
  │ 参数名      │ 类型     │ 必需 │ 描述       │
  ├─────────────┼──────────┼──────┼────────────┤
  │ name        │ string   │ 是   │ 卡组名称   │
  │ description │ string   │ 否   │ 卡组描述   │
  │ cards       │ string[] │ 否   │ 卡牌ID列表 │
  └─────────────┴──────────┴──────┴────────────┘


  响应
   - 成功响应 (201):

    1   {
    2     "message": "卡组创建成功",
    3     "deck": {
    4       "id": "deck-id-string",
    5       "name": "新卡组",
    6       "description": "卡组描述",
    7       "cards": [
    8         "card-id-1",
    9         "card-id-2",
   10         "card-id-3"
   11       ],
   12       "created_at": "2023-01-01T00:00:00.000Z"
   13     }
   14   }

   - 错误响应 (400):

   1   {
   2     "error": "卡组名称不能为空"
   3   }

   - 错误响应 (400):

   1   {
   2     "error": "卡组验证失败",
   3     "details": ["错误详情"]
   4   }

  示例请求

    1 curl -X POST "http://localhost:5000/api/decks" \
    2   -H "Content-Type: application/json" \
    3   -H "Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..." \
    4   -d '{
    5     "name": "火系角色卡组",
    6     "description": "以火元素角色为主力的卡组",
    7     "cards": [
    8       "card-id-1",
    9       "card-id-2"
   10     ]
   11   }'

  3. 更新卡组 - /api/decks/<deck_id> (PUT)
  更新指定ID的卡组。

  请求信息
   - 方法: PUT
   - URL: /api/decks/{deck_id}
   - 认证: 需要在请求头中包含JWT令牌

  路径参数

  ┌─────────┬────────┬──────┬──────────────┐
  │ 参数名  │ 类型   │ 必需 │ 描述         │
  ├─────────┼────────┼──────┼──────────────┤
  │ deck_id │ string │ 是   │ 卡组的唯一ID │
  └─────────┴────────┴──────┴──────────────┘


  请求体参数

  ┌─────────────┬──────────┬──────┬────────────┐
  │ 参数名      │ 类型     │ 必需 │ 描述       │
  ├─────────────┼──────────┼──────┼────────────┤
  │ name        │ string   │ 否   │ 卡组名称   │
  │ description │ string   │ 否   │ 卡组描述   │
  │ cards       │ string[] │ 否   │ 卡牌ID列表 │
  └─────────────┴──────────┴──────┴────────────┘


  响应
   - 成功响应 (200):

    1   {
    2     "message": "卡组更新成功",
    3     "deck": {
    4       "id": "deck-id-string",
    5       "name": "更新后卡组名",
    6       "description": "更新后卡组描述",
    7       "cards": [
    8         "card-id-1",
    9         "card-id-2"
   10       ],
   11       "updated_at": "2023-01-01T00:00:00.000Z"
   12     }
   13   }

   - 错误响应 (404):

   1   {
   2     "error": "卡组不存在或无权限访问"
   3   }

   - 错误响应 (400):

   1   {
   2     "error": "卡组验证失败",
   3     "details": ["错误详情"]
   4   }

  示例请求

    1 curl -X PUT "http://localhost:5000/api/decks/deck-uuid-string" \
    2   -H "Content-Type: application/json" \
    3   -H "Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..." \
    4   -d '{
    5     "name": "优化后的火系卡组",
    6     "description": "经过优化的火元素角色卡组",
    7     "cards": [
    8       "card-id-1",
    9       "card-id-2",
   10       "card-id-3"
   11     ]
   12   }'

  4. 删除卡组 - /api/decks/<deck_id> (DELETE)
  删除指定ID的卡组。

  请求信息
   - 方法: DELETE
   - URL: /api/decks/{deck_id}
   - 认证: 需要在请求头中包含JWT令牌

  路径参数

  ┌─────────┬────────┬──────┬──────────────┐
  │ 参数名  │ 类型   │ 必需 │ 描述         │
  ├─────────┼────────┼──────┼──────────────┤
  │ deck_id │ string │ 是   │ 卡组的唯一ID │
  └─────────┴────────┴──────┴──────────────┘


  响应
   - 成功响应 (200):

   1   {
   2     "message": "卡组删除成功"
   3   }

   - 错误响应 (404):

   1   {
   2     "error": "卡组不存在或无权限访问"
   3   }

  示例请求

   1 curl -X DELETE "http://localhost:5000/api/decks/deck-uuid-string" \
   2   -H "Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..."

  5. 获取卡组详情 - /api/decks/<deck_id> (GET)
  获取指定ID的卡组详细信息。

  请求信息
   - 方法: GET
   - URL: /api/decks/{deck_id}
   - 认证: 需要在请求头中包含JWT令牌

  路径参数

  ┌─────────┬────────┬──────┬──────────────┐
  │ 参数名  │ 类型   │ 必需 │ 描述         │
  ├─────────┼────────┼──────┼──────────────┤
  │ deck_id │ string │ 是   │ 卡组的唯一ID │
  └─────────┴────────┴──────┴──────────────┘


  响应
   - 成功响应 (200):

    1   {
    2     "deck": {
    3       "id": "deck-id-string",
    4       "name": "卡组名称",
    5       "description": "卡组描述",
    6       "cards": [
    7         {
    8           "id": "card-id-string",
    9           "name": "卡牌名称",
   10           "type": "角色牌",
   11           "description": "卡牌描述",
   12           "cost": [...],
   13           "rarity": 5,
   14           "element_type": "火",
   15           "character_subtype": "蒙德",
   16           "image_url": "https://example.com/image.jpg",
   17           "country": "蒙德",
   18           "element": "火",
   19           "weapon_type": "单手剑",
   20           "skills": [...],
   21           "title": "角色称号",
   22           "health": 10,
   23           "energy": 0,
   24           "max_health": 10,
   25           "max_energy": 3
   26         }
   27       ],
   28       "created_at": "2023-01-01T00:00:00.000Z",
   29       "updated_at": "2023-01-01T00:00:00.000Z"
   30     }
   31   }

   - 错误响应 (404):

   1   {
   2     "error": "卡组不存在或无权限访问"
   3   }

  示例请求

   1 curl -X GET "http://localhost:5000/api/decks/deck-uuid-string" \
   2   -H "Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..."

  6. 验证卡组 - /api/decks/validate (POST)
  验证卡组是否符合游戏规则。

  请求信息
   - 方法: POST
   - URL: /api/decks/validate
   - 认证: 需要在请求头中包含JWT令牌

  请求体参数

  ┌────────┬──────────┬──────┬────────────┐
  │ 参数名 │ 类型     │ 必需 │ 描述       │
  ├────────┼──────────┼──────┼────────────┤
  │ cards  │ string[] │ 是   │ 卡牌ID列表 │
  └────────┴──────────┴──────┴────────────┘


  响应
   - 成功响应 (200):

    1   {
    2     "is_valid": true,
    3     "errors": [],
    4     "warnings": [],
    5     "details": {
    6       "character_count": 3,
    7       "total_cards": 30,
    8       "element_composition": ["火", "火", "物理"]
    9     }
   10   }

   - 错误响应 (200):

    1   {
    2     "is_valid": false,
    3     "errors": ["错误详情"],
    4     "warnings": ["警告详情"],
    5     "details": {
    6       "character_count": 2,
    7       "total_cards": 40,
    8       "element_composition": ["火", "火"]
    9     }
   10   }

  示例请求

    1 curl -X POST "http://localhost:5000/api/decks/validate" \
    2   -H "Content-Type: application/json" \
    3   -H "Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..." \
    4   -d '{
    5     "cards": [
    6       "card-id-1",
    7       "card-id-2",
    8       "card-id-3"
    9     ]
   10   }'

  游戏接口

  1. 开始本地游戏 - /api/local-game/start (POST)
  开始一个新的本地游戏。

  请求信息
   - 方法: POST
   - URL: /api/local-game/start
   - 认证: 需要在请求头中包含JWT令牌

  请求体参数

  ┌───────────────┬────────┬──────┬─────────────────────────────────────────┐
  │ 参数名        │ 类型   │ 必需 │ 描述                                    │
  ├───────────────┼────────┼──────┼─────────────────────────────────────────┤
  │ opponent_type │ string │ 否   │ 对手类型（'ai' 或 'human'，默认为'ai'） │
  │ deck_id       │ string │ 是   │ 使用的卡组ID                            │
  └───────────────┴────────┴──────┴─────────────────────────────────────────┘


  响应
   - 成功响应 (200):

    1   {
    2     "game_session_id": "session-id-string",
    3     "message": "本地游戏已开始",
    4     "game_state": {
    5       "players": [
    6         {
    7           "player_id": "user-id-string",
    8           "characters": [
    9             {
   10               "id": "char-id",
   11               "name": "角色名称",
   12               "health": 10,
   13               "max_health": 10,
   14               "energy": 0,
   15               "max_energy": 3,
   16               "element_type": "火",
   17               "weapon_type": "单手剑",
   18               "status": "存活",
   19               "skills": [...]
   20             }
   21           ],
   22           "active_character_index": 0,
   23           "hand_cards": [...],
   24           "dice": ["火", "火", "万能"],
   25           "supports": [],
   26           "summons": []
   27         },
   28         {
   29           "player_id": "ai_opponent",
   30           "characters": [...],
   31           "active_character_index": 0,
   32           "hand_cards": [...],
   33           "dice": ["水", "水", "万能"],
   34           "supports": [],
   35           "summons": []
   36         }
   37       ],
   38       "current_player_index": 0,
   39       "round_number": 1,
   40       "phase": "行动阶段",
   41       "round_actions": 0,
   42       "game_log": [],
   43       "is_game_over": false,
   44       "winner": null
   45     }
   46   }

   - 错误响应 (400):

   1   {
   2     "error": "必须选择一个卡组"
   3   }

   - 错误响应 (404):

   1   {
   2     "error": "卡组不存在或无权限访问"
   3   }

  示例请求

   1 curl -X POST "http://localhost:5000/api/local-game/start" \
   2   -H "Content-Type: application/json" \
   3   -H "Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..." \
   4   -d '{
   5     "deck_id": "deck-uuid-string",
   6     "opponent_type": "ai"
   7   }'

  2. 处理游戏行动 - /api/local-game/<session_id>/action (POST)
  处理游戏中的特定行动。

  请求信息
   - 方法: POST
   - URL: /api/local-game/{session_id}/action
   - 认证: 需要在请求头中包含JWT令牌

  路径参数

  ┌────────────┬────────┬──────┬────────────┐
  │ 参数名     │ 类型   │ 必需 │ 描述       │
  ├────────────┼────────┼──────┼────────────┤
  │ session_id │ string │ 是   │ 游戏会话ID │
  └────────────┴────────┴──────┴────────────┘


  请求体参数

  ┌─────────────┬────────┬──────┬─────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────┐
  │ 参数名      │ 类型   │ 必需 │ 描述                                                                                                                        │
  ├─────────────┼────────┼──────┼─────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────┤
  │ action_type │ string │ 是   │ 行动类型（PLAY_CARD, USE_SKILL, SWITCH_CHARACTER, PASS, REROLL_DICE, ELEMENTAL_TUNING, REPLACE_CARDS, QUICK_ACTION, COMBAT_ACTION） │
  │ payload     │ object │ 否   │ 行动相关数据，根据行动类型而定                                                                                              │
  └─────────────┴────────┴──────┴─────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────┘


  响应
   - 成功响应 (200):

    1   {
    2     "game_session_id": "session-id-string",
    3     "message": "行动处理成功",
    4     "game_state": {
    5       "players": [...],
    6       "current_player_index": 0,
    7       "round_number": 1,
    8       "phase": "行动阶段",
    9       "round_actions": 1,
   10       "game_log": ["玩家使用技能攻击"],
   11       "is_game_over": false,
   12       "winner": null
   13     }
   14   }

   - 错误响应 (400):

   1   {
   2     "error": "必须指定行动类型"
   3   }

   - 错误响应 (404):

   1   {
   2     "error": "游戏会话不存在"
   3   }

   - 错误响应 (403):

   1   {
   2     "error": "无权访问此游戏会话"
   3   }

  示例请求

    1 curl -X POST "http://localhost:5000/api/local-game/session-uuid-string/action" \
    2   -H "Content-Type: application/json" \
    3   -H "Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..." \
    4   -d '{
    5     "action_type": "USE_SKILL",
    6     "payload": {
    7       "skill_index": 0,
    8       "target_character_index": 1
    9     }
   10   }'

  3. 获取游戏状态 - /api/local-game/<session_id>/state (GET)
  获取当前游戏状态。

  请求信息
   - 方法: GET
   - URL: /api/local-game/{session_id}/state
   - 认证: 需要在请求头中包含JWT令牌

  路径参数

  ┌────────────┬────────┬──────┬────────────┐
  │ 参数名     │ 类型   │ 必需 │ 描述       │
  ├────────────┼────────┼──────┼────────────┤
  │ session_id │ string │ 是   │ 游戏会话ID │
  └────────────┴────────┴──────┴────────────┘


  响应
   - 成功响应 (200):

    1   {
    2     "game_session_id": "session-id-string",
    3     "game_state": {
    4       "players": [...],
    5       "current_player_index": 0,
    6       "round_number": 1,
    7       "phase": "行动阶段",
    8       "round_actions": 1,
    9       "game_log": ["玩家使用技能攻击"],
   10       "is_game_over": false,
   11       "winner": null
   12     }
   13   }

   - 错误响应 (404):

   1   {
   2     "error": "游戏会话不存在"
   3   }

   - 错误响应 (403):

   1   {
   2     "error": "无权访问此游戏会话"
   3   }

  示例请求

   1 curl -X GET "http://localhost:5000/api/local-game/session-uuid-string/state" \
   2   -H "Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..."

  4. 结束游戏 - /api/local-game/<session_id>/end (POST)
  结束当前游戏会话。

  请求信息
   - 方法: POST
   - URL: /api/local-game/{session_id}/end
   - 认证: 需要在请求头中包含JWT令牌

  路径参数

  ┌────────────┬────────┬──────┬────────────┐
  │ 参数名     │ 类型   │ 必需 │ 描述       │
  ├────────────┼────────┼──────┼────────────┤
  │ session_id │ string │ 是   │ 游戏会话ID │
  └────────────┴────────┴──────┴────────────┘


  响应
   - 成功响应 (200):

   1   {
   2     "message": "本地游戏已结束"
   3   }

   - 错误响应 (404):

   1   {
   2     "error": "游戏会话不存在"
   3   }

   - 错误响应 (403):

   1   {
   2     "error": "无权访问此游戏会话"
   3   }

  示例请求

   1 curl -X POST "http://localhost:5000/api/local-game/session-uuid-string/end" \
   2   -H "Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..."

  辅助接口

  1. 健康检查 - /health (GET)
  检查服务器健康状态。

  请求信息
   - 方法: GET
   - URL: /health

  响应
   - 成功响应 (200):

   1   {
   2     "status": "healthy",
   3     "message": "七圣召唤游戏服务器运行正常"
   4   }

  示例请求

   1 curl -X GET "http://localhost:5000/health"

  2. API测试页面 - /api/test (GET)
  提供一个HTML页面用于测试API端点。

  请求信息
   - 方法: GET
   - URL: /api/test

  响应
   - 成功响应 (200):
    返回一个HTML页面，包含：
     - JWT令牌验证功能
     - 各种API端点的测试界面
     - 结果展示框
     - 参数输入框

  示例请求

   1 curl -X GET "http://localhost:5000/api/test"

  错误处理

  API使用标准的HTTP状态码和JSON格式的错误响应：

   - 200: 成功
   - 201: 创建成功
   - 400: 请求参数错误
   - 401: 未认证
   - 403: 无权限访问
   - 404: 资源不存在
   - 500: 服务器内部错误

  错误响应格式：

   1 {
   2   "error": "错误描述"
   3 }

  认证说明

  所有需要认证的端点都需要在请求头中包含JWT令牌：

   1 Authorization: Bearer {access_token}

  令牌通过/api/auth/login端点获取。


