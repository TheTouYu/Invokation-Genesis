# 七圣召唤项目DAL API路由集成示例

## 概述

本节展示了如何在Flask API路由中使用数据访问层（DAL）进行数据库操作。通过实际的API端点示例，说明了DAL在Web应用中的集成方式。

## 基本路由框架

### 1. 导入DAL和相关依赖

```python
from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from dal import db_dal
import json
```

### 2. 创建蓝图

```python
cards_bp = Blueprint("standardized_cards", __name__)
```

## 实际API路由示例

### 1. 获取用户卡组列表

```python
@cards_bp.route("/decks", methods=["GET"])
@jwt_required()
def get_user_decks():
    """
    获取当前用户的所有卡组
    """
    try:
        current_user_id = get_jwt_identity()

        # 使用DAL获取用户卡组
        decks = db_dal.decks.get_decks_by_user(current_user_id)

        result = []
        for deck in decks:
            result.append({
                "id": deck.id,
                "name": deck.name,
                "description": deck.description,
                "cards": json.loads(deck.card_ids) if deck.card_ids else [],
                "created_at": deck.created_at.isoformat(),
                "updated_at": deck.updated_at.isoformat(),
            })

        return jsonify({"decks": result}), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500
```

### 2. 创建新卡组

```python
@cards_bp.route("/decks", methods=["POST"])
@jwt_required()
def create_deck():
    """
    创建新的卡组
    """
    try:
        current_user_id = get_jwt_identity()
        data = request.get_json()

        name = data.get("name")
        description = data.get("description", "")
        card_list = data.get("cards", [])

        if not name:
            return jsonify({"error": "卡组名称不能为空"}), 400

        # 使用DAL创建卡组
        try:
            deck = db_dal.decks.create_deck(
                name=name,
                user_id=current_user_id,
                cards=card_list,
                description=description
            )

            return jsonify({
                "message": "卡组创建成功",
                "deck": {
                    "id": deck.id,
                    "name": deck.name,
                    "description": deck.description,
                    "cards": card_list,
                    "created_at": deck.created_at.isoformat(),
                },
            }), 201
        except Exception as e:
            return jsonify({"error": f"创建卡组失败: {str(e)}"}), 500

    except Exception as e:
        return jsonify({"error": str(e)}), 500
```

### 3. 更新卡组信息

```python
@cards_bp.route("/decks/<string:deck_id>", methods=["PUT"])
@jwt_required()
def update_deck(deck_id):
    """
    更新卡组
    """
    try:
        current_user_id = get_jwt_identity()
        data = request.get_json()

        # 首先获取卡组并验证权限
        deck = db_dal.decks.get_deck_by_id(deck_id)
        if not deck or deck.user_id != current_user_id:
            return jsonify({"error": "卡组不存在或无权限访问"}), 404

        name = data.get("name", deck.name)
        description = data.get("description", deck.description)
        card_list = data.get("cards", json.loads(deck.card_ids) if deck.card_ids else [])

        # 使用DAL更新卡组
        success = db_dal.decks.update_deck(
            deck_id=deck_id,
            name=name,
            description=description,
            card_ids=card_list
        )

        if not success:
            return jsonify({"error": "更新卡组失败"}), 500

        # 获取更新后的卡组
        updated_deck = db_dal.decks.get_deck_by_id(deck_id)
        return jsonify({
            "message": "卡组更新成功",
            "deck": {
                "id": updated_deck.id,
                "name": updated_deck.name,
                "description": updated_deck.description,
                "cards": json.loads(updated_deck.card_ids) if updated_deck.card_ids else [],
                "created_at": updated_deck.created_at.isoformat(),
                "updated_at": updated_deck.updated_at.isoformat(),
            },
        }), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500
```

### 4. 获取特定卡组详情

```python
@cards_bp.route("/decks/<string:deck_id>", methods=["GET"])
@jwt_required()
def get_deck_by_id(deck_id):
    """
    获取特定卡组详情
    """
    try:
        current_user_id = get_jwt_identity()

        # 获取卡组并验证权限
        deck = db_dal.decks.get_deck_by_id(deck_id)
        if not deck or deck.user_id != current_user_id:
            return jsonify({"error": "卡组不存在或无权限访问"}), 404

        # 返回卡组详情
        return jsonify({
            "deck": {
                "id": deck.id,
                "name": deck.name,
                "description": deck.description,
                "cards": json.loads(deck.card_ids) if deck.card_ids else [],
                "created_at": deck.created_at.isoformat(),
                "updated_at": deck.updated_at.isoformat(),
            }
        }), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500
```

### 5. 删除卡组

```python
@cards_bp.route("/decks/<string:deck_id>", methods=["DELETE"])
@jwt_required()
def delete_deck(deck_id):
    """
    删除卡组
    """
    try:
        current_user_id = get_jwt_identity()

        # 验证卡组存在和权限
        deck = db_dal.decks.get_deck_by_id(deck_id)
        if not deck or deck.user_id != current_user_id:
            return jsonify({"error": "卡组不存在或无权限访问"}), 404

        # 使用DAL删除卡组
        success = db_dal.decks.delete_deck(deck_id)

        if not success:
            return jsonify({"error": "删除卡组失败"}), 500

        return jsonify({"message": "卡组删除成功"}), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500
```

### 6. 获取卡牌数据

```python
@cards_bp.route("/cards", methods=["GET"])
@jwt_required()
def get_all_cards():
    """
    获取卡牌数据 - 支持多种过滤条件和分页
    """
    try:
        # 获取查询参数
        card_type = request.args.get("type")
        element = request.args.get("element")
        page = request.args.get("page", 1, type=int)
        per_page = min(request.args.get("per_page", 20, type=int), 100)

        # 构建查询（这里仍然使用直接查询，但可以通过DAL扩展）
        from models.db_models import CardData
        query = CardData.query.filter(CardData.is_active == True)

        # 应用过滤条件
        if card_type:
            if card_type == "非角色牌":
                query = query.filter(CardData.card_type != "角色牌")
            else:
                query = query.filter(CardData.card_type == card_type)

        if element:
            query = query.filter(CardData.element_type == element)

        # 分页
        cards = query.paginate(page=page, per_page=per_page, error_out=False)

        # 转换为所需格式
        result = []
        for card in cards.items:
            result.append({
                "id": card.id,
                "name": card.name,
                "type": card.card_type,
                "description": card.description,
                "cost": card.cost,
                "rarity": card.rarity,
            })

        return jsonify({
            "cards": result,
            "total": cards.total,
            "pages": cards.pages,
            "current_page": page,
            "per_page": per_page,
            "has_next": cards.has_next,
            "has_prev": cards.has_prev,
        }), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500
```

## 权限验证和安全考虑

### 1. JWT身份验证

所有需要用户身份的路由都应使用`@jwt_required()`装饰器：

```python
@cards_bp.route("/decks", methods=["GET"])
@jwt_required()  # 验证JWT令牌
def get_user_decks():
    current_user_id = get_jwt_identity()  # 获取当前用户ID
    # ... 其他操作
```

### 2. 数据验证和权限检查

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
    
    # 执行更新操作
    deck = result
    # ... 更新逻辑
```

## 错误处理策略

### 1. 统一错误响应格式

```python
def handle_error(error_msg, status_code=500):
    """统一错误处理"""
    import logging
    logging.error(f"API错误: {error_msg}")
    return jsonify({"error": error_msg}), status_code

@cards_bp.route("/decks", methods=["POST"])
@jwt_required()
def create_deck():
    try:
        # 操作逻辑
        pass
    except ValueError as e:
        return handle_error(f"参数错误: {str(e)}", 400)
    except Exception as e:
        return handle_error(f"服务器错误: {str(e)}", 500)
```

### 2. 输入验证

```python
def validate_deck_data(data):
    """验证卡组数据"""
    errors = []
    
    if not data.get("name"):
        errors.append("卡组名称不能为空")
    
    if not isinstance(data.get("cards"), list):
        errors.append("卡牌列表格式不正确")
    
    if len(data.get("cards", [])) > 40:  # 假设最大40张卡
        errors.append("卡组卡牌数量超出限制")
    
    return errors

@cards_bp.route("/decks", methods=["POST"])
@jwt_required()
def create_deck():
    data = request.get_json()
    
    # 数据验证
    validation_errors = validate_deck_data(data)
    if validation_errors:
        return jsonify({"error": "数据验证失败", "details": validation_errors}), 400
    
    # 继续处理
    try:
        deck = db_dal.decks.create_deck(
            name=data["name"],
            user_id=get_jwt_identity(),
            cards=data["cards"],
            description=data.get("description", "")
        )
        # 返回成功响应
    except Exception as e:
        return handle_error(str(e))
```

## 最佳实践总结

1. **始终使用`@jwt_required()`**：对需要身份验证的端点使用JWT装饰器
2. **验证权限**：在执行操作前验证用户是否有权访问特定资源
3. **统一错误处理**：使用一致的错误响应格式
4. **输入验证**：验证客户端提交的数据格式和内容
5. **使用DAL方法**：通过DAL执行数据库操作，而不是直接查询数据库
6. **记录日志**：记录错误和重要操作以便调试
7. **适当分页**：对大量数据返回时实施分页