"""
Nations Blueprint - Modular API Routes
Handles all nation-related API endpoints in a dedicated blueprint.
"""

from flask import Blueprint, request
from typing import Dict, Any
from app.services.nation_service import NationService
from app.middleware.auth_middleware import api_auth_required
from app.utils.response_utils import success_response, error_response
import logging

logger = logging.getLogger(__name__)

# Create blueprint
nations_bp = Blueprint('nations', __name__, url_prefix='/api/v1')

# Initialize service
nation_service = NationService()

@nations_bp.route('/nations')
def get_nations() -> Dict[str, Any]:
    """Get all nations with their basic information"""
    try:
        result: Dict[str, Any] = nation_service.get_all_nations()
        if result.get('success'):
            return success_response(result['data'], count=len(result['data']))
        return error_response(result.get('error', 'Failed to retrieve nations'), 500)

    except Exception as e:
        logger.error(f"Error in get_nations: {e}")
        return error_response("Failed to retrieve nations", 500)

@nations_bp.route('/provinces')
def get_provinces() -> Dict[str, Any]:
    """Union provinces, optionally filtered by ?world= or ?star_id=."""
    try:
        from models.database import Database
        db = Database()
        rows = db.get_provinces(
            world=request.args.get('world'),
            star_id=request.args.get('star_id', type=int),
        )
        return success_response(rows, count=len(rows))
    except Exception as e:
        logger.error(f"Error in get_provinces: {e}")
        return error_response("Failed to retrieve provinces", 500)


@nations_bp.route('/nations/<nation_id>')
def get_nation_by_id(nation_id: str) -> Dict[str, Any]:
    """Get detailed information for a specific nation"""
    try:
        result: Dict[str, Any] = nation_service.get_nation_by_id(nation_id)
        return result

    except Exception as e:
        logger.error(f"Error getting nation {nation_id}: {e}")
        return error_response("Nation not found", 404)

@nations_bp.route('/nations/<nation_id>/stars')
def get_nation_stars(nation_id: str) -> Dict[str, Any]:
    """Get all stars controlled by a specific nation"""
    try:
        result: Dict[str, Any] = nation_service.get_nation_stars(nation_id)
        return result

    except Exception as e:
        logger.error(f"Error getting stars for nation {nation_id}: {e}")
        return error_response("Failed to retrieve nation stars", 500)

@nations_bp.route('/nations/<nation_id>/territories')
def get_nation_territories(nation_id: str) -> Dict[str, Any]:
    """Get territory boundaries for a specific nation"""
    try:
        result: Dict[str, Any] = nation_service.get_nation_territories(nation_id)
        return result

    except Exception as e:
        logger.error(f"Error getting territories for nation {nation_id}: {e}")
        return error_response("Failed to retrieve nation territories", 500)
