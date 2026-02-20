"""
Stellar Regions Blueprint - Modular API Routes
Handles all stellar region-related API endpoints in a dedicated blueprint.
"""

from flask import Blueprint
from typing import Dict, Any
from app.services.stats_service import StatsService
from app.utils.response_utils import success_response, error_response
import logging

logger = logging.getLogger(__name__)

# Create blueprint
stellar_regions_bp = Blueprint('stellar_regions', __name__, url_prefix='/api/v1')

# Initialize service
stats_service = StatsService()

@stellar_regions_bp.route('/stellar-regions')
def get_stellar_regions() -> Dict[str, Any]:
    """Get all stellar regions - public for overlay functionality"""
    try:
        result: Dict[str, Any] = stats_service.get_stellar_regions()
        if result['success']:
            return success_response(result['data'], count=len(result['data']))
        return error_response(result.get('error', 'Failed to retrieve stellar regions'), 500)

    except Exception as e:
        logger.error(f"Error in get_stellar_regions: {e}")
        return error_response("Failed to retrieve stellar regions", 500)
