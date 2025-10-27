"""
API v2 - 支援牌功能
"""
from flask import Blueprint, request, jsonify, g
from flask_jwt_extended import jwt_required
from .utils import get_models, extract_card_info
from utils.logger import get_logger, log_api_call


supports_bp = Blueprint("supports_v2", __name__)


@supports_bp.route("/supports", methods=["GET"])
@log_api_call
def get_supports():
    """
    兼容原API端点：获取支援牌数据
    """
    logger = get_logger(__name__)
    request_id = getattr(g, 'request_id', 'N/A')
    
    logger.info(f"Fetch supports request with filters: {dict(request.args)}, Request-ID: {request_id}")
    
    try:
        CardData, Deck = get_models()
        # 查询支援牌
        query = CardData.query.filter(
            CardData.card_type == "支援牌", CardData.is_active == True
        )

        # 分页参数
        page = request.args.get("page", 1, type=int)
        per_page = min(request.args.get("per_page", 20, type=int), 100)

        cards = query.paginate(page=page, per_page=per_page, error_out=False)
        result = [extract_card_info(card) for card in cards.items]
        
        logger.info(f"Successfully fetched {len(result)} supports, Request-ID: {request_id}")

        return jsonify(result), 200
    except Exception as e:
        logger.error(f"Failed to fetch supports: {str(e)}, Request-ID: {request_id}")
        return jsonify({"error": str(e)}), 500