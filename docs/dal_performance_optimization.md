# 七圣召唤项目DAL性能优化提示

## 索引使用建议

### 1. 数据库索引策略

为了优化DAL查询性能，应该在数据库中为经常查询的字段创建索引：

#### 在User模型中创建索引
```python
class User(db.Model):
    # ...
    username = db.Column(db.String(80), unique=True, nullable=False, index=True)  # 用户名索引
    email = db.Column(db.String(120), unique=True, nullable=False, index=True)    # 邮箱索引
    created_at = db.Column(db.DateTime, default=datetime.utcnow, index=True)       # 创建时间索引
    is_active = db.Column(db.Boolean, default=True, index=True)                   # 活跃状态索引
```

#### 在CardData模型中创建索引
```python
class CardData(db.Model):
    # ...
    name = db.Column(db.String(100), nullable=False, index=True)      # 卡牌名称索引
    card_type = db.Column(db.String(50), nullable=False, index=True)  # 卡牌类型索引
    sub_type = db.Column(db.String(50), index=True)                   # 子类型索引
    character_name = db.Column(db.String(100), index=True)            # 角色名称索引
    rarity = db.Column(db.Integer, index=True)                        # 稀有度索引
    created_at = db.Column(db.DateTime, default=datetime.utcnow, index=True)  # 创建时间索引
    is_active = db.Column(db.Boolean, default=True, index=True)       # 活跃状态索引
```

#### 在Deck模型中创建索引
```python
class Deck(db.Model):
    # ...
    user_id = db.Column(db.String, db.ForeignKey('users.id'), nullable=False, index=True)  # 用户ID索引
    is_public = db.Column(db.Boolean, default=False, index=True)      # 公开状态索引
    created_at = db.Column(db.DateTime, default=datetime.utcnow, index=True)  # 创建时间索引
```

#### 在GameHistory模型中创建索引
```python
class GameHistory(db.Model):
    # ...
    player1_id = db.Column(db.String, db.ForeignKey('users.id'), nullable=False, index=True)  # 玩家1索引
    player2_id = db.Column(db.String, db.ForeignKey('users.id'), nullable=False, index=True)  # 玩家2索引
    winner_id = db.Column(db.String, db.ForeignKey('users.id'), index=True)  # 获胜者索引
    deck1_id = db.Column(db.String, db.ForeignKey('decks.id'), index=True)    # 卡组1索引
    deck2_id = db.Column(db.String, db.ForeignKey('decks.id'), index=True)    # 卡组2索引
    game_result = db.Column(db.String(50), index=True)              # 游戏结果索引
    created_at = db.Column(db.DateTime, default=datetime.utcnow, index=True)  # 创建时间索引
```

### 2. 复合索引

对于经常一起查询的字段，创建复合索引：

```sql
-- 在数据库中为用户活跃状态和创建时间创建复合索引
CREATE INDEX idx_users_active_created ON users (is_active, created_at);

-- 为卡牌类型和稀有度创建复合索引
CREATE INDEX idx_card_type_rarity ON card_data (card_type, rarity);

-- 为卡牌活跃状态和类型创建复合索引
CREATE INDEX idx_card_active_type ON card_data (is_active, card_type);

-- 为游戏历史的玩家ID和创建时间创建复合索引
CREATE INDEX idx_gamehistory_player_created ON game_histories (player1_id, created_at);
CREATE INDEX idx_gamehistory_player2_created ON game_histories (player2_id, created_at);
```

## 批量操作技巧

### 1. 批量创建操作

使用SQLAlchemy的bulk操作进行批量插入：

```python
def bulk_create_cards(cards_data_list):
    """批量创建卡牌的优化方法"""
    from models.db_models import CardData
    from database_manager import db_manager
    
    try:
        # 使用bulk_insert_mappings进行批量插入
        db_manager.db.session.bulk_insert_mappings(CardData, cards_data_list)
        db_manager.db.session.commit()
        return True
    except Exception as e:
        db_manager.db.session.rollback()
        print(f"批量创建卡牌失败: {e}")
        return False

# 使用示例
cards_data = [
    {
        "name": "卡牌1",
        "card_type": "角色牌",
        "rarity": 5,
        # ... 其他字段
    },
    {
        "name": "卡牌2", 
        "card_type": "事件牌",
        "rarity": 3,
        # ... 其他字段
    }
    # ... 更多卡牌数据
]
bulk_create_cards(cards_data)
```

### 2. 批量更新操作

```python
def bulk_update_cards(card_updates):
    """批量更新卡牌的优化方法
    
    Args:
        card_updates: 包含id和其他要更新字段的字典列表
    """
    from models.db_models import CardData
    from database_manager import db_manager
    
    try:
        # 使用bulk_update_mappings进行批量更新
        db_manager.db.session.bulk_update_mappings(CardData, card_updates)
        db_manager.db.session.commit()
        return True
    except Exception as e:
        db_manager.db.session.rollback()
        print(f"批量更新卡牌失败: {e}")
        return False

# 使用示例
updates = [
    {"id": "card_id_1", "rarity": 4, "name": "更新的卡牌1"},
    {"id": "card_id_2", "rarity": 5, "name": "更新的卡牌2"},
    # ... 更多更新数据
]
bulk_update_cards(updates)
```

### 3. 优化查询操作

#### 使用延迟加载和急切加载

```python
def get_deck_with_cards(deck_id):
    """获取卡组及其卡牌信息的优化查询"""
    from models.db_models import Deck
    from sqlalchemy.orm import joinedload
    
    # 使用急切加载避免N+1查询问题
    deck = Deck.query.options(
        joinedload(Deck.user),  # 预加载用户信息
    ).filter_by(id=deck_id).first()
    
    return deck
```

#### 分页查询优化

```python
def get_paginated_cards(card_type=None, page=1, per_page=20):
    """分页获取卡牌的优化方法"""
    from models.db_models import CardData
    
    query = CardData.query.filter(CardData.is_active == True)
    
    if card_type:
        query = query.filter(CardData.card_type == card_type)
    
    # 使用分页
    paginated_result = query.paginate(
        page=page, 
        per_page=per_page, 
        error_out=False
    )
    
    return paginated_result
```

## 查询优化技巧

### 1. 使用原生SQL查询

对于复杂查询，可以使用原生SQL提高性能：

```python
def get_user_deck_statistics(user_id):
    """获取用户卡组统计信息的优化查询"""
    from database_manager import db_manager
    
    sql = """
    SELECT 
        COUNT(*) as total_decks,
        COUNT(CASE WHEN is_public = 1 THEN 1 END) as public_decks,
        AVG(LENGTH(card_ids)) as avg_card_count
    FROM decks 
    WHERE user_id = :user_id
    """
    
    result = db_manager.db.session.execute(sql, {"user_id": user_id})
    row = result.fetchone()
    
    return {
        "total_decks": row[0],
        "public_decks": row[1],
        "avg_card_count": row[2]
    }
```

### 2. 避免N+1查询问题

```python
def get_users_with_decks():
    """获取用户及其卡组的优化查询"""
    from models.db_models import User
    from sqlalchemy.orm import joinedload
    
    # 使用joinedload避免N+1查询
    users = User.query.options(
        joinedload(User.decks)
    ).all()
    
    return users
```

### 3. 缓存常见查询结果

```python
from functools import lru_cache
import json

@lru_cache(maxsize=128)
def get_cached_cards_by_type(card_type, limit=None):
    """缓存按类型查询的卡牌数据"""
    from models.db_models import CardData
    
    query = CardData.query.filter_by(card_type=card_type, is_active=True)
    if limit:
        query = query.limit(limit)
    
    cards = query.all()
    # 转换为可哈希的格式以便缓存
    return tuple((card.id, card.name, card.card_type) for card in cards)

# 对于需要JSON格式的缓存
import time
from typing import Dict, Any

# 简单内存缓存
_cache = {}
_CACHE_TIMEOUT = 300  # 5分钟

def get_cards_with_cache(card_type: str, timeout: int = _CACHE_TIMEOUT) -> Dict[str, Any]:
    """带超时的卡牌查询缓存"""
    cache_key = f"cards_{card_type}"
    
    # 检查缓存
    if cache_key in _cache:
        cached_data, timestamp = _cache[cache_key]
        if time.time() - timestamp < timeout:
            return cached_data
    
    # 查询数据库
    from models.db_models import CardData
    cards = CardData.query.filter_by(card_type=card_type, is_active=True).all()
    
    # 转换为JSON格式
    result = [card.to_dict() for card in cards]
    
    # 存储到缓存
    _cache[cache_key] = (result, time.time())
    
    return result
```

## 事务管理优化

### 1. 合理使用事务

```python
def create_user_with_default_deck(username, email, password_hash):
    """在单个事务中创建用户和默认卡组"""
    from models.db_models import User
    from database_manager import db_manager
    
    try:
        # 开始事务
        user = User(
            username=username,
            email=email,
            password_hash=password_hash
        )
        db_manager.db.session.add(user)
        db_manager.db.session.flush()  # 获取分配的ID，但不提交
        
        # 创建默认卡组
        from dal import db_dal
        default_deck = db_dal.decks.create_deck(
            name="默认卡组",
            user_id=user.id,
            cards=[],
            description="新用户默认卡组"
        )
        
        # 提交事务
        db_manager.db.session.commit()
        return user, default_deck
    
    except Exception as e:
        # 回滚事务
        db_manager.db.session.rollback()
        raise e
```

### 2. 批量事务处理

```python
def batch_process_deck_updates(updates_list):
    """批量处理卡组更新的事务优化"""
    from database_manager import db_manager
    
    updated_decks = []
    failed_updates = []
    
    try:
        for update_data in updates_list:
            try:
                success = db_dal.decks.update_deck(
                    deck_id=update_data['deck_id'],
                    **update_data['fields']
                )
                if success:
                    updated_decks.append(update_data['deck_id'])
                else:
                    failed_updates.append(update_data['deck_id'])
            except Exception as e:
                failed_updates.append(update_data['deck_id'])
                print(f"更新卡组 {update_data['deck_id']} 失败: {e}")
        
        # 提交所有更改
        db_manager.db.session.commit()
        return updated_decks, failed_updates
    
    except Exception as e:
        db_manager.db.session.rollback()
        raise e
```

## 连接池和数据库性能

### 1. 数据库连接池配置

在应用配置中优化连接池设置：

```python
# 在database_manager.py中配置连接池
class DatabaseManager:
    def init_app(self, app):
        # ... 其他配置 ...
        
        # 数据库配置
        app.config['SQLALCHEMY_ENGINE_OPTIONS'] = {
            'pool_size': 20,          # 连接池大小
            'pool_recycle': 3600,     # 连接回收时间（秒）
            'pool_pre_ping': True,    # 连接预检查
            'max_overflow': 30,       # 最大溢出连接数
        }
        
        # ... 初始化代码 ...
```

### 2. 查询性能分析

```python
import time
import functools

def measure_db_query_time(func):
    """装饰器：测量数据库查询时间"""
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        start_time = time.time()
        result = func(*args, **kwargs)
        end_time = time.time()
        
        query_time = end_time - start_time
        if query_time > 1.0:  # 如果查询时间超过1秒，记录警告
            print(f"警告: 查询 {func.__name__} 耗时 {query_time:.2f} 秒")
        
        return result
    return wrapper

# 使用示例
@measure_db_query_time
def get_all_cards_with_performance_tracking():
    return db_dal.cards.get_cards_by_type("角色牌")
```

## 内存优化建议

### 1. 控制查询结果大小

```python
def get_cards_safe(card_type, limit=100):
    """安全获取卡牌，限制返回数量"""
    # 在DAL层应用限制
    return db_dal.cards.get_cards_by_type(card_type, limit=min(limit, 1000))
```

### 2. 使用生成器处理大量数据

```python
def process_large_deck_set(deck_ids):
    """使用生成器处理大量卡组，避免内存溢出"""
    for deck_id in deck_ids:
        deck = db_dal.decks.get_deck_by_id(deck_id)
        if deck:
            # 处理单个卡组
            yield deck
```

## 总结

通过以上优化策略，可以显著提高七圣召唤项目中DAL的性能：

1. **索引优化**：为经常查询的字段创建适当的索引
2. **批量操作**：使用SQLAlchemy的批量操作功能
3. **查询优化**：避免N+1查询问题，使用合适的加载策略
4. **缓存策略**：对频繁查询的数据使用缓存
5. **事务管理**：合理使用事务，批量处理相关操作
6. **连接池配置**：优化数据库连接池设置
7. **性能监控**：测量查询时间，及时发现性能问题

这些优化技术将帮助您的应用在处理大量数据时保持良好的性能表现。