"""
Nations Blueprint - Modular API Routes
Handles all nation-related API endpoints in a dedicated blueprint.
"""

from flask import Blueprint, request, jsonify
from typing import Dict, List, Any, Optional
from flask_login import login_required
from app.services.nation_service import NationService
from app.middleware.auth_middleware import api_auth_required
from app.utils.response_utils import success_response, error_response
import logging

logger = logging.getLogger(__name__)

# Create blueprint
nations_bp = Blueprint('nations', __name__, url_prefix='/api')

# Initialize service
nation_service = NationService()

@nations_bp.route('/nations')
def get_nations() -> Dict[str, Any]:
    """Get all nations with their basic information"""
    try:
        result: Dict[str, Any] = nation_service.get_all_nations()
        return result

    except Exception as e:
        logger.error(f"Error in get_nations: {e}")
        return error_response("Failed to retrieve nations", 500)

@nations_bp.route('/nations/<nation_id>')
@api_auth_required
def get_nation_by_id(nation_id: str) -> Dict[str, Any]:
    """Get detailed information for a specific nation"""
    try:
        result: Dict[str, Any] = nation_service.get_nation_by_id(nation_id)
        return result

    except Exception as e:
        logger.error(f"Error getting nation {nation_id}: {e}")
        return error_response("Nation not found", 404)

@nations_bp.route('/nations/<nation_id>/stars')
@api_auth_required
def get_nation_stars(nation_id: str) -> Dict[str, Any]:
    """Get all stars controlled by a specific nation"""
    try:
        result: Dict[str, Any] = nation_service.get_nation_stars(nation_id)
        return result

    except Exception as e:
        logger.error(f"Error getting stars for nation {nation_id}: {e}")
        return error_response("Failed to retrieve nation stars", 500)

@nations_bp.route('/nations/<nation_id>/territories')
@api_auth_required
def get_nation_territories(nation_id: str) -> Dict[str, Any]:
    """Get territory boundaries for a specific nation"""
    try:
        result: Dict[str, Any] = nation_service.get_nation_territories(nation_id)
        return result

    except Exception as e:
        logger.error(f"Error getting territories for nation {nation_id}: {e}")
        return error_response("Failed to retrieve nation territories", 500)
