# 七圣召唤项目数据访问层（DAL）完整使用指南

## 目录
1. [概述](#概述)
2. [主要组件](#主要组件)
3. [基本使用方法](#基本使用方法)
4. [高级使用示例](#高级使用示例)
5. [API路由集成](#api路由集成)
6. [性能优化建议](#性能优化建议)
7. [最佳实践](#最佳实践)

## 概述

数据访问层（Data Access Layer，DAL）是七圣召唤卡牌游戏项目的核心组件，它提供了一个抽象层，用于处理所有数据库操作。DAL将业务逻辑与数据库操作分离，提高代码可维护性和可测试性。

### DAL的主要优势
- **代码分离**：将数据访问逻辑与业务逻辑分离
- **代码复用**：通用数据库操作被封装成可重用方法
- **统一访问**：所有数据库操作通过统一接口进行
- **错误处理**：内置完善的错误处理和事务管理
- **易于测试**：通过接口抽象，便于单元测试

### 核心组件结构
```python
# DAL组件层次结构
DatabaseDAL (主入口) 
├── UserDAL      # 用户数据操作
├── CardDataDAL  # 卡牌数据操作
├── DeckDAL      # 卡组数据操作
└── GameHistoryDAL # 游戏历史数据操作
```

## 主要组件

### UserDAL - 用户数据操作
处理所有与用户相关的数据库操作，如创建、查询、更新和删除用户。

### CardDataDAL - 卡牌数据操作
处理卡牌数据的存储与检索，包括按类型、稀有度等条件查询。

### DeckDAL - 卡组数据操作
管理用户卡组的创建、更新、删除及查询操作。

### GameHistoryDAL - 游戏历史数据操作
记录和管理游戏历史数据，支持按用户、获胜者等条件查询。

## 基本使用方法

### 导入和初始化

```python
from dal import db_dal
```

`db_dal` 是全局实例，可以直接访问所有DAL组件。

### 用户操作示例

```python
# 创建用户
user = db_dal.users.create_user(
    username="new_user",
    email="user@example.com", 
    password_hash="hashed_password"
)

# 查询用户
user = db_dal.users.get_user_by_username("test_user")

# 更新用户
success = db_dal.users.update_user(
    user_id=user.id,
    email="updated@example.com"
)

# 删除用户
success = db_dal.users.delete_user(user.id)
```

### 卡牌操作示例

```python
# 创建卡牌
card = db_dal.cards.create_card(
    name="迪卢克",
    card_type="角色牌",
    rarity=5
)

# 查询卡牌
cards = db_dal.cards.get_cards_by_type("角色牌", limit=10)

# 搜索卡牌
results = db_dal.cards.search_cards("迪卢克")
```

### 卡组操作示例

```python
# 创建卡组
deck = db_dal.decks.create_deck(
    name="火元素快攻",
    user_id=user.id,
    cards=[card1.id, card2.id, card3.id]
)

# 获取用户卡组
user_decks = db_dal.decks.get_decks_by_user(user.id)

# 更新卡组
success = db_dal.decks.update_deck(
    deck_id=deck.id,
    name="更新后的卡组名"
)
```

## 高级使用示例

### 事务处理

```python
def create_user_with_default_deck(username, email, password_hash):
    """在单个事务中创建用户和默认卡组"""
    from models.db_models import User
    from database_manager import db_manager
    
    try:
        # 创建用户
        user = User(
            username=username,
            email=email,
            password_hash=password_hash
        )
        db_manager.db.session.add(user)
        db_manager.db.session.flush()  # 获取ID但不提交
        
        # 创建默认卡组
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
        db_manager.db.session.rollback()
        raise e
```

### 批量操作

```python
def bulk_create_cards(cards_data_list):
    """批量创建卡牌"""
    from models.db_models import CardData
    from database_manager import db_manager
    
    try:
        db_manager.db.session.bulk_insert_mappings(CardData, cards_data_list)
        db_manager.db.session.commit()
        return True
    except Exception as e:
        db_manager.db.session.rollback()
        print(f"批量创建卡牌失败: {e}")
        return False
```

### 条件查询和过滤

```python
def get_user_cards_by_criteria(user_id, card_type=None, rarity=None):
    """根据条件获取用户的卡牌"""
    # 获取用户卡组
    decks = db_dal.decks.get_decks_by_user(user_id)
    
    # 从卡组中提取所有卡牌ID
    all_card_ids = []
    for deck in decks:
        card_ids = deck.card_ids if deck.card_ids else []
        all_card_ids.extend(card_ids)
    
    # 去重
    unique_card_ids = list(set(all_card_ids))
    
    # 构建查询
    from models.db_models import CardData
    query = CardData.query.filter(CardData.id.in_(unique_card_ids))
    
    if card_type:
        query = query.filter_by(card_type=card_type)
    if rarity is not None:
        query = query.filter_by(rarity=rarity)
    
    return query.all()
```

## API路由集成

### 基本API模式

```python
from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from dal import db_dal
import json

cards_bp = Blueprint("cards_api", __name__)

@cards_bp.route("/decks", methods=["GET"])
@jwt_required()
def get_user_decks():
    """获取当前用户的所有卡组"""
    try:
        current_user_id = get_jwt_identity()
        decks = db_dal.decks.get_decks_by_user(current_user_id)
        
        result = []
        for deck in decks:
            result.append({
                "id": deck.id,
                "name": deck.name,
                "description": deck.description,
                "cards": json.loads(deck.card_ids) if deck.card_ids else [],
                "created_at": deck.created_at.isoformat(),
            })
        
        return jsonify({"decks": result}), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500
```

### 权限验证和安全考虑

```python
def validate_deck_ownership(deck_id, user_id):
    """验证用户是否拥有指定卡组"""
    deck = db_dal.decks.get_deck_by_id(deck_id)
    if not deck:
        return False, "卡组不存在"
    if deck.user_id != user_id:
        return False, "无权限访问此卡组"
    return True, deck

@cards_bp.route("/decks/<string:deck_id>", methods=["PUT"])
@jwt_required()
def update_deck(deck_id):
    current_user_id = get_jwt_identity()
    
    # 验证权限
    is_valid, result = validate_deck_ownership(deck_id, current_user_id)
    if not is_valid:
        return jsonify({"error": result}), 404
    
    # 执行更新
    data = request.get_json()
    success = db_dal.decks.update_deck(deck_id=deck_id, **data)
    
    if success:
        return jsonify({"message": "卡组更新成功"}), 200
    else:
        return jsonify({"error": "更新失败"}), 500
```

## 性能优化建议

### 1. 索引策略
在经常查询的字段上创建索引：

```python
# 在模型中定义索引
username = db.Column(db.String(80), unique=True, nullable=False, index=True)
card_type = db.Column(db.String(50), nullable=False, index=True)
created_at = db.Column(db.DateTime, default=datetime.utcnow, index=True)
```

### 2. 避免N+1查询
使用SQLAlchemy的急切加载：

```python
from sqlalchemy.orm import joinedload

# 预加载关联数据，避免N+1查询
decks_with_user = Deck.query.options(joinedload(Deck.user)).all()
```

### 3. 分页查询
对大量数据使用分页：

```python
def get_paginated_cards(page=1, per_page=20):
    from models.db_models import CardData
    
    paginated = CardData.query.filter_by(is_active=True).paginate(
        page=page,
        per_page=per_page,
        error_out=False
    )
    return paginated
```

### 4. 缓存策略
对频繁查询的数据使用缓存：

```python
from functools import lru_cache

@lru_cache(maxsize=128)
def get_cached_cards_by_type(card_type):
    """缓存按类型查询的卡牌数据"""
    return db_dal.cards.get_cards_by_type(card_type)
```

## 最佳实践

### 1. 错误处理
始终处理数据库操作可能发生的异常：

```python
def safe_user_operation():
    try:
        user = db_dal.users.create_user(
            username="test_user",
            email="test@example.com",
            password_hash="hash"
        )
        return user
    except Exception as e:
        import logging
        logging.error(f"创建用户失败: {e}")
        return None
```

### 2. 数据验证
在调用DAL方法前验证数据：

```python
def validate_deck_data(data):
    """验证卡组数据"""
    errors = []
    
    if not data.get("name"):
        errors.append("卡组名称不能为空")
    if not isinstance(data.get("cards"), list):
        errors.append("卡牌列表格式不正确")
    
    return errors
```

### 3. 资源清理
确保在长时间运行的应用中定期清理数据库连接：

```python
# 在应用配置中设置连接池参数
app.config['SQLALCHEMY_ENGINE_OPTIONS'] = {
    'pool_size': 20,
    'pool_recycle': 3600,
    'pool_pre_ping': True,
    'max_overflow': 30,
}
```

### 4. 日志记录
记录重要操作和错误：

```python
import logging

def create_deck_with_logging(name, user_id, cards):
    try:
        logging.info(f"用户 {user_id} 正在创建卡组 {name}")
        deck = db_dal.decks.create_deck(name=name, user_id=user_id, cards=cards)
        logging.info(f"卡组创建成功，ID: {deck.id}")
        return deck
    except Exception as e:
        logging.error(f"创建卡组失败: {e}")
        raise
```

## 总结

七圣召唤项目的DAL提供了一套完整、高效的数据访问解决方案。通过合理使用DAL的各个组件、遵循最佳实践和应用性能优化技巧，可以构建稳定、高效的卡牌游戏应用。DAL的模块化设计使得代码易于维护和扩展，同时提供了良好的错误处理和事务管理机制。

使用此指南，开发者可以快速上手DAL的使用，构建高质量的七圣召唤卡牌游戏应用。