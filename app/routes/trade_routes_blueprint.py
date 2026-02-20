"""
Trade Routes Blueprint - Modular API Routes
Handles all trade route-related API endpoints in a dedicated blueprint.
"""

from flask import Blueprint
from typing import Dict, Any
from app.services.trade_route_service import TradeRouteService
from app.utils.response_utils import success_response, error_response
import logging

logger = logging.getLogger(__name__)

# Create blueprint
trade_routes_bp = Blueprint('trade_routes', __name__, url_prefix='/api')

# Initialize service
trade_route_service = TradeRouteService()

@trade_routes_bp.route('/trade-routes')
def get_trade_routes() -> Dict[str, Any]:
    """Get all trade routes - public for overlay functionality"""
    try:
        result: Dict[str, Any] = trade_route_service.get_trade_routes()
        if result['success']:
            return success_response(result['data'], count=len(result['data']))
        return error_response(result.get('error', 'Failed to retrieve trade routes'), 500)

    except Exception as e:
        logger.error(f"Error in get_trade_routes: {e}")
        return error_response("Failed to retrieve trade routes", 500)
