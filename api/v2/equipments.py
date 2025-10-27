"""
API v2 - 装备牌功能
"""
from flask import Blueprint, request, jsonify, g
from flask_jwt_extended import jwt_required
from .utils import get_models, extract_card_info
from utils.logger import get_logger, log_api_call


equipments_bp = Blueprint("equipments_v2", __name__)


@equipments_bp.route("/equipments", methods=["GET"])
@log_api_call
def get_equipments():
    """
    兼容原API端点：获取装备牌数据
    """
    logger = get_logger(__name__)
    request_id = getattr(g, 'request_id', 'N/A')
    
    logger.info(f"Fetch equipments request with filters: {dict(request.args)}, Request-ID: {request_id}")
    
    try:
        CardData, Deck = get_models()
        # 查询装备牌（在数据库中存储为"武器"）
        query = CardData.query.filter(
            CardData.card_type == "武器", CardData.is_active == True
        )

        # 分页参数
        page = request.args.get("page", 1, type=int)
        per_page = min(request.args.get("per_page", 20, type=int), 100)

        cards = query.paginate(page=page, per_page=per_page, error_out=False)
        result = [extract_card_info(card) for card in cards.items]
        
        logger.info(f"Successfully fetched {len(result)} equipments, Request-ID: {request_id}")

        return jsonify(result), 200
    except Exception as e:
        logger.error(f"Failed to fetch equipments: {str(e)}, Request-ID: {request_id}")
        return jsonify({"error": str(e)}), 500