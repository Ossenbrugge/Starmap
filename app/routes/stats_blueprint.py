"""
Stats Blueprint - Modular API Routes
Handles all statistics-related API endpoints in a dedicated blueprint.
"""

from flask import Blueprint, request
from typing import Dict, Any
from app.services.stats_service import StatsService
from app.middleware.auth_middleware import api_auth_required
from app.utils.response_utils import success_response, error_response
import logging

logger = logging.getLogger(__name__)

# Create blueprint
stats_bp = Blueprint('stats', __name__, url_prefix='/api/v1')

# Initialize service
stats_service = StatsService()

@stats_bp.route('/stats')
def get_stats() -> Dict[str, Any]:
    """Get application statistics"""
    try:
        authenticated = request.headers.get('Authorization') is not None
        result: Dict[str, Any] = stats_service.get_stats(authenticated=authenticated)
        if result['success']:
            return success_response(result['data'])
        return error_response(result.get('error', 'Failed to retrieve statistics'), 500)

    except Exception as e:
        logger.error(f"Error in get_stats: {e}")
        return error_response("Failed to retrieve statistics", 500)

@stats_bp.route('/galactic-directions')
def get_galactic_directions() -> Dict[str, Any]:
    """Get galactic directions data"""
    try:
        result: Dict[str, Any] = stats_service.get_galactic_directions()
        if result['success']:
            return success_response(result['data'], count=len(result['data']))
        return error_response(result.get('error', 'Failed to retrieve galactic directions'), 500)

    except Exception as e:
        logger.error(f"Error in get_galactic_directions: {e}")
        return error_response("Failed to retrieve galactic directions", 500)
