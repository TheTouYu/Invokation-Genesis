# 七圣召唤项目DAL使用方法和示例代码

## 基本导入和初始化

在使用DAL之前，首先需要导入：

```python
from dal import db_dal
```

`db_dal` 是一个全局实例，包含了所有DAL组件的访问入口。

## 常见操作的代码示例

### 1. 用户操作示例

#### 创建用户
```python
# 创建新用户
try:
    user = db_dal.users.create_user(
        username="new_user",
        email="user@example.com",
        password_hash="hashed_password_here"
    )
    print(f"用户创建成功，ID: {user.id}")
except Exception as e:
    print(f"创建用户失败: {e}")
```

#### 查询用户
```python
# 根据ID查询用户
user = db_dal.users.get_user_by_id("user_id_here")
if user:
    print(f"用户: {user.username}, 邮箱: {user.email}")
else:
    print("用户不存在")

# 根据用户名查询用户
user = db_dal.users.get_user_by_username("test_user")
if user:
    print(f"找到用户: {user.username}")

# 根据邮箱查询用户
user = db_dal.users.get_user_by_email("test@example.com")
if user:
    print(f"找到邮箱匹配用户: {user.username}")
```

#### 更新用户
```python
# 更新用户信息
success = db_dal.users.update_user(
    user_id="user_id_here",
    username="updated_username",
    email="updated_email@example.com"
)
if success:
    print("用户信息更新成功")
else:
    print("更新失败，可能是用户不存在")
```

#### 删除用户
```python
# 删除用户
success = db_dal.users.delete_user("user_id_here")
if success:
    print("用户删除成功")
else:
    print("删除失败，可能是用户不存在")
```

### 2. 卡牌操作示例

#### 创建卡牌
```python
# 创建新卡牌
try:
    card = db_dal.cards.create_card(
        name="迪卢克",
        card_type="角色牌",
        cost=[{"type": "火", "value": 1}, {"type": "无色", "value": 2}],
        description="火元素角色",
        character_subtype="火元素",
        rarity=5,
        element_type="火"
    )
    print(f"卡牌创建成功，ID: {card.id}")
except Exception as e:
    print(f"创建卡牌失败: {e}")
```

#### 查询卡牌
```python
# 根据ID查询卡牌
card = db_dal.cards.get_card_by_id("card_id_here")
if card:
    print(f"卡牌: {card.name}, 类型: {card.card_type}")

# 根据类型查询卡牌
cards = db_dal.cards.get_cards_by_type("角色牌", limit=10)
print(f"找到 {len(cards)} 张角色牌")
for card in cards:
    print(f"- {card.name}")

# 根据稀有度查询卡牌
rare_cards = db_dal.cards.get_cards_by_rarity(5)
print(f"找到 {len(rare_cards)} 张5星卡牌")

# 搜索卡牌
search_results = db_dal.cards.search_cards("迪卢克")
print(f"搜索到 {len(search_results)} 张相关卡牌")
```

#### 更新卡牌
```python
# 更新卡牌信息
success = db_dal.cards.update_card(
    card_id="card_id_here",
    name="更新后的卡牌名称",
    description="更新后的卡牌描述"
)
if success:
    print("卡牌信息更新成功")
else:
    print("更新失败，可能是卡牌不存在")
```

### 3. 卡组操作示例

#### 创建卡组
```python
# 创建新卡组
try:
    deck = db_dal.decks.create_deck(
        name="火元素快攻",
        user_id="user_id_here",
        cards=["card1_id", "card2_id", "card3_id"],  # 卡牌ID列表
        description="以火元素角色为核心的快攻卡组",
        is_public=True
    )
    print(f"卡组创建成功，ID: {deck.id}")
except Exception as e:
    print(f"创建卡组失败: {e}")
```

#### 查询卡组
```python
# 根据ID查询卡组
deck = db_dal.decks.get_deck_by_id("deck_id_here")
if deck:
    print(f"卡组: {deck.name}, 用户: {deck.user_id}")

# 获取用户的卡组
user_decks = db_dal.decks.get_decks_by_user("user_id_here")
print(f"用户有 {len(user_decks)} 个卡组")
for deck in user_decks:
    print(f"- {deck.name}")

# 获取公开卡组
public_decks = db_dal.decks.get_public_decks(limit=5)
print(f"获取到 {len(public_decks)} 个公开卡组")
```

#### 更新和删除卡组
```python
# 更新卡组
success = db_dal.decks.update_deck(
    deck_id="deck_id_here",
    name="更新后的卡组名",
    description="更新后的卡组描述"
)
if success:
    print("卡组更新成功")
else:
    print("更新失败")

# 删除卡组
success = db_dal.decks.delete_deck("deck_id_here")
if success:
    print("卡组删除成功")
else:
    print("删除失败")
```

### 4. 游戏历史操作示例

#### 创建游戏历史
```python
# 创建游戏历史记录
try:
    game_history = db_dal.game_history.create_game_history(
        player1_id="player1_id",
        player2_id="player2_id", 
        game_data={
            "initial_deck": ["card1", "card2"],
            "moves": [],
            "winner": "player1_id"
        },
        winner_id="player1_id",
        deck1_id="deck1_id",
        deck2_id="deck2_id",
        game_result="胜负详情",
        duration=300  # 游戏时长，秒
    )
    print(f"游戏历史创建成功，ID: {game_history.id}")
except Exception as e:
    print(f"创建游戏历史失败: {e}")
```

#### 查询游戏历史
```python
# 根据ID查询游戏历史
game = db_dal.game_history.get_game_history_by_id("game_id_here")
if game:
    print(f"游戏: {game.id}, 玩家: {game.player1_id} vs {game.player2_id}")

# 获取用户参与的游戏
user_games = db_dal.game_history.get_games_by_user("user_id_here")
print(f"用户参与了 {len(user_games)} 场游戏")

# 获取用户获胜的游戏
win_games = db_dal.game_history.get_games_by_winner("user_id_here")
print(f"用户获胜了 {len(win_games)} 场游戏")

# 获取最近的游戏
recent_games = db_dal.game_history.get_recent_games(limit=10)
print(f"最近有 {len(recent_games)} 场游戏")
```

## 错误处理最佳实践

### 1. 数据库操作异常处理
```python
from sqlalchemy.exc import SQLAlchemyError

def safe_user_operation():
    try:
        user = db_dal.users.create_user(
            username="test_user",
            email="test@example.com", 
            password_hash="hash"
        )
        return user
    except SQLAlchemyError as e:
        print(f"数据库操作错误: {e}")
        # 记录日志
        import logging
        logging.error(f"创建用户失败: {e}")
        return None
    except Exception as e:
        print(f"未知错误: {e}")
        return None
```

### 2. 查询结果验证
```python
def get_user_safely(user_id):
    user = db_dal.users.get_user_by_id(user_id)
    if user is None:
        print(f"用户 {user_id} 不存在")
        return None
    return user

def get_deck_with_validation(deck_id, expected_user_id):
    deck = db_dal.decks.get_deck_by_id(deck_id)
    if deck is None:
        raise ValueError(f"卡组 {deck_id} 不存在")
    if deck.user_id != expected_user_id:
        raise ValueError("无权限访问此卡组")
    return deck
```

### 3. 批量操作
```python
def create_multiple_cards(card_data_list):
    """批量创建卡牌的示例"""
    created_cards = []
    for card_data in card_data_list:
        try:
            card = db_dal.cards.create_card(**card_data)
            created_cards.append(card)
        except Exception as e:
            print(f"创建卡牌失败: {card_data.get('name', '未知卡牌')}, 错误: {e}")
            continue
    return created_cards
```

## 高级用法

### 1. 结合Flask应用上下文使用
```python
from flask import current_app
from dal import db_dal

def get_cards_in_app_context():
    """在Flask应用上下文中使用DAL"""
    with current_app.app_context():
        cards = db_dal.cards.get_cards_by_type("角色牌")
        return [card.to_dict() for card in cards]
```

### 2. 事务处理
```python
def complex_user_operation():
    """涉及多个数据库操作的复杂事务"""
    success = False
    try:
        # 创建新用户
        user = db_dal.users.create_user(
            username="new_user",
            email="new@example.com",
            password_hash="hash"
        )
        
        # 创建默认卡组
        default_deck = db_dal.decks.create_deck(
            name="默认卡组",
            user_id=user.id,
            cards=[],
            description="新用户默认卡组"
        )
        
        # 创建初始游戏历史
        game_history = db_dal.game_history.create_game_history(
            player1_id=user.id,
            player2_id="system",
            game_data={"type": "tutorial"},
            game_result="completed"
        )
        
        success = True
        return {"user": user, "deck": default_deck, "game": game_history}
    
    except Exception as e:
        # 事务会自动回滚，因为DAL内部处理了回滚
        print(f"复杂操作失败: {e}")
        return None
```

以上示例涵盖了DAL的主要使用场景，通过这些示例，开发者可以快速理解并使用七圣召唤项目的数据访问层。