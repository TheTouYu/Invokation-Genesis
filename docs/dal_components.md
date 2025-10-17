# 七圣召唤项目数据访问层（DAL）主要组件介绍

## UserDAL - 用户数据操作组件

UserDAL负责处理所有与用户相关的数据库操作。

### 方法列表

#### create_user(username: str, email: str, password_hash: str) -> object
创建新用户
- **参数**：
  - `username`：用户名
  - `email`：用户邮箱
  - `password_hash`：密码哈希值
- **返回值**：创建的用户对象
- **异常**：SQLAlchemyError

#### get_user_by_id(user_id: str) -> Optional[object]
根据ID获取用户
- **参数**：`user_id`：用户ID
- **返回值**：用户对象或None（如果未找到）

#### get_user_by_username(username: str) -> Optional[object]
根据用户名获取用户
- **参数**：`username`：用户名
- **返回值**：用户对象或None（如果未找到）

#### get_user_by_email(email: str) -> Optional[object]
根据邮箱获取用户
- **参数**：`email`：用户邮箱
- **返回值**：用户对象或None（如果未找到）

#### update_user(user_id: str, **kwargs) -> bool
更新用户信息
- **参数**：
  - `user_id`：用户ID
  - `**kwargs`：要更新的字段名值对
- **返回值**：更新成功返回True，否则返回False

#### delete_user(user_id: str) -> bool
删除用户
- **参数**：`user_id`：用户ID
- **返回值**：删除成功返回True，否则返回False

---

## CardDataDAL - 卡牌数据操作组件

CardDataDAL负责处理所有与卡牌数据相关的数据库操作。

### 方法列表

#### create_card(**kwargs) -> object
创建新卡牌
- **参数**：`**kwargs`：卡牌的各个字段名值对
- **返回值**：创建的卡牌对象
- **异常**：SQLAlchemyError

#### get_card_by_id(card_id: str) -> Optional[object]
根据ID获取卡牌
- **参数**：`card_id`：卡牌ID
- **返回值**：卡牌对象或None（如果未找到）

#### get_cards_by_type(card_type: str, limit: Optional[int] = None) -> List[object]
根据类型获取卡牌
- **参数**：
  - `card_type`：卡牌类型
  - `limit`：可选，限制返回数量
- **返回值**：卡牌对象列表

#### get_cards_by_rarity(rarity: int) -> List[object]
根据稀有度获取卡牌
- **参数**：`rarity`：稀有度值
- **返回值**：卡牌对象列表

#### search_cards(query_str: str) -> List[object]
搜索卡牌
- **参数**：`query_str`：搜索字符串
- **返回值**：匹配的卡牌对象列表

#### update_card(card_id: str, **kwargs) -> bool
更新卡牌信息
- **参数**：
  - `card_id`：卡牌ID
  - `**kwargs`：要更新的字段名值对
- **返回值**：更新成功返回True，否则返回False

---

## DeckDAL - 卡组数据操作组件

DeckDAL负责处理所有与卡组相关的数据库操作。

### 方法列表

#### create_deck(name: str, user_id: str, cards: List[str], description: str = "", is_public: bool = False) -> object
创建新卡组
- **参数**：
  - `name`：卡组名称
  - `user_id`：用户ID
  - `cards`：卡牌ID列表
  - `description`：可选，卡组描述
  - `is_public`：可选，是否公开卡组
- **返回值**：创建的卡组对象
- **异常**：SQLAlchemyError

#### get_deck_by_id(deck_id: str) -> Optional[object]
根据ID获取卡组
- **参数**：`deck_id`：卡组ID
- **返回值**：卡组对象或None（如果未找到）

#### get_decks_by_user(user_id: str) -> List[object]
获取用户的卡组
- **参数**：`user_id`：用户ID
- **返回值**：卡组对象列表

#### get_public_decks(limit: Optional[int] = None) -> List[object]
获取公开卡组
- **参数**：`limit`：可选，限制返回数量
- **返回值**：卡组对象列表

#### update_deck(deck_id: str, **kwargs) -> bool
更新卡组信息
- **参数**：
  - `deck_id`：卡组ID
  - `**kwargs`：要更新的字段名值对
- **返回值**：更新成功返回True，否则返回False

#### delete_deck(deck_id: str) -> bool
删除卡组
- **参数**：`deck_id`：卡组ID
- **返回值**：删除成功返回True，否则返回False

---

## GameHistoryDAL - 游戏历史数据操作组件

GameHistoryDAL负责处理所有与游戏历史记录相关的数据库操作。

### 方法列表

#### create_game_history(player1_id: str, player2_id: str, game_data: Dict[str, Any], winner_id: Optional[str] = None, deck1_id: Optional[str] = None, deck2_id: Optional[str] = None, game_result: Optional[str] = None, duration: Optional[int] = None) -> object
创建游戏历史记录
- **参数**：
  - `player1_id`：玩家1 ID
  - `player2_id`：玩家2 ID
  - `game_data`：游戏数据字典
  - `winner_id`：可选，获胜者ID
  - `deck1_id`：可选，玩家1使用的卡组ID
  - `deck2_id`：可选，玩家2使用的卡组ID
  - `game_result`：可选，游戏结果
  - `duration`：可选，游戏时长
- **返回值**：创建的游戏历史记录对象
- **异常**：SQLAlchemyError

#### get_game_history_by_id(game_id: str) -> Optional[object]
根据ID获取游戏历史记录
- **参数**：`game_id`：游戏历史记录ID
- **返回值**：游戏历史记录对象或None（如果未找到）

#### get_games_by_user(user_id: str) -> List[object]
获取用户参与的游戏
- **参数**：`user_id`：用户ID
- **返回值**：游戏历史记录对象列表（按创建时间倒序）

#### get_games_by_winner(winner_id: str) -> List[object]
获取由特定用户获胜的游戏
- **参数**：`winner_id`：获胜者ID
- **返回值**：游戏历史记录对象列表（按创建时间倒序）

#### get_recent_games(limit: int = 10) -> List[object]
获取最近的游戏
- **参数**：`limit`：限制返回数量，默认10
- **返回值**：游戏历史记录对象列表（按创建时间倒序）