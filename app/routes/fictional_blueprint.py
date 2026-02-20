"""
Fictional Entities Blueprint - Modular API Routes
Handles all fictional stars, planets, and entities in a dedicated blueprint.
"""

from flask import Blueprint, request, jsonify
from typing import Dict, List, Any, Optional
from app.services.star_service import StarService
from app.middleware.auth_middleware import api_auth_required
from app.utils.response_utils import success_response, error_response
import logging

logger = logging.getLogger(__name__)

# Create blueprint
fictional_bp = Blueprint('fictional', __name__, url_prefix='/api')

# Initialize services
star_service = StarService()

@fictional_bp.route('/fictional-stars')
def get_fictional_stars() -> Dict[str, Any]:
    """Get all fictional stars - public for overlay functionality"""
    try:
        result: Dict[str, Any] = star_service.get_fictional_stars()
        return result

    except Exception as e:
        logger.error(f"Error getting fictional stars: {e}")
        return error_response("Failed to retrieve fictional stars", 500)

@fictional_bp.route('/fictional-stars', methods=['POST'])
@api_auth_required
def add_fictional_star() -> Dict[str, Any]:
    """Add a new fictional star"""
    try:
        star_data: Dict[str, Any] = request.get_json()
        if not star_data:
            return error_response("JSON data required", 400)

        result: Dict[str, Any] = star_service.add_fictional_star(star_data)
        return result

    except Exception as e:
        logger.error(f"Error adding fictional star: {e}")
        return error_response("Failed to add fictional star", 500)

@fictional_bp.route('/fictional-stars/<int:star_id>', methods=['DELETE'])
@api_auth_required
def delete_fictional_star(star_id: int) -> Dict[str, Any]:
    """Delete a fictional star"""
    try:
        result: Dict[str, Any] = star_service.delete_fictional_star(star_id)
        return result

    except Exception as e:
        logger.error(f"Error deleting fictional star {star_id}: {e}")
        return error_response("Failed to delete fictional star", 500)

@fictional_bp.route('/fictional-exoplanets')
def get_fictional_exoplanets() -> Dict[str, Any]:
    """Get all fictional exoplanets (public access)"""
    try:
        result: Dict[str, Any] = star_service.get_fictional_exoplanets()
        return success_response(result['data'] if 'data' in result else [])

    except Exception as e:
        logger.error(f"Error getting fictional exoplanets: {e}")
        return error_response("Failed to retrieve fictional exoplanets", 500)

@fictional_bp.route('/fictional-exoplanets', methods=['POST'])
@api_auth_required
def add_fictional_exoplanet() -> Dict[str, Any]:
    """Add a new fictional exoplanet"""
    try:
        planet_data: Dict[str, Any] = request.get_json()
        if not planet_data:
            return error_response("JSON data required", 400)

        result: Dict[str, Any] = star_service.add_fictional_exoplanet(planet_data)
        return result

    except Exception as e:
        logger.error(f"Error adding fictional exoplanet: {e}")
        return error_response("Failed to add fictional exoplanet", 500)
