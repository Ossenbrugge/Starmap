"""
Stars Blueprint - Modular API Routes
Handles all star-related API endpoints in a dedicated blueprint.
"""

from flask import Blueprint, request
from typing import Dict, Any, Optional
from app.services.star_service import StarService
from app.middleware.auth_middleware import api_auth_required
from app.utils.response_utils import success_response, error_response, paginated_response
import logging

logger = logging.getLogger(__name__)

# Create blueprint
stars_bp = Blueprint('stars', __name__, url_prefix='/api/v1')

# Initialize service
star_service = StarService()


@stars_bp.route('/stars')
def get_stars() -> Dict[str, Any]:
    """Get stars with optional filtering and pagination.

    Query params:
        page         (int, default 1)
        limit        (int, default 1000, max 10000)
        mag_limit    (float, default 8.0)
        spectral_type (str)
        constellation (str)
    """
    try:
        page: int = max(1, request.args.get('page', 1, type=int))
        limit: int = min(request.args.get('limit', 1000, type=int), 50000)
        mag_limit: Optional[float] = request.args.get('mag_limit', type=float)
        spectral_type: Optional[str] = request.args.get('spectral_type')
        constellation: Optional[str] = request.args.get('constellation')

        result: Dict[str, Any] = star_service.get_stars_paginated(
            page=page,
            limit=limit,
            mag_limit=mag_limit or 8.0,
            spectral_type=spectral_type or "",
            constellation=constellation or "",
        )

        if result['success']:
            return paginated_response(
                result['data'],
                page=page,
                limit=limit,
                total_count=result['total'],
            )
        return error_response(result.get('error', 'Failed to retrieve stars'), 500)

    except Exception as e:
        logger.error(f"Error in get_stars: {e}")
        return error_response("Failed to retrieve stars", 500)


@stars_bp.route('/stars/<int:star_id>')
def get_star_by_id(star_id: int) -> Dict[str, Any]:
    """Get detailed information for a specific star by ID"""
    try:
        result: Dict[str, Any] = star_service.get_star_by_id(star_id)
        if result['success']:
            return success_response(result['data'])
        elif result.get('error') == 'Star not found':
            return error_response('Star not found', 404)
        return error_response(result.get('error', 'Failed to retrieve star'), 500)

    except Exception as e:
        logger.error(f"Error getting star {star_id}: {e}")
        return error_response("Star not found", 404)


@stars_bp.route('/stars/search')
def search_stars() -> Dict[str, Any]:
    """Search stars by name or properties"""
    try:
        query: str = request.args.get('q', '')
        limit: int = request.args.get('limit', 10, type=int)

        result: Dict[str, Any] = star_service.search_stars(query, limit)
        if result['success']:
            return success_response(result['data'], count=len(result['data']))
        return error_response(result.get('error', 'Search failed'), 500)

    except Exception as e:
        logger.error(f"Error searching stars: {e}")
        return error_response("Search failed", 500)


@stars_bp.route('/stars/nearby')
def get_nearby_stars() -> Dict[str, Any]:
    """Get stars within specified radius of coordinates"""
    try:
        x: float = request.args.get('x', 0, type=float)
        y: float = request.args.get('y', 0, type=float)
        z: float = request.args.get('z', 0, type=float)
        radius: float = request.args.get('radius', 30.0, type=float)

        result: Dict[str, Any] = star_service.get_stars_in_radius(x, y, z, radius)
        if result['success']:
            return success_response(result['data'], count=result.get('count', len(result['data'])))
        return error_response(result.get('error', 'Failed to retrieve nearby stars'), 500)

    except Exception as e:
        logger.error(f"Error getting nearby stars: {e}")
        return error_response("Failed to retrieve nearby stars", 500)


@stars_bp.route('/exoplanets')
def get_exoplanets() -> Dict[str, Any]:
    """Get exoplanets data - public for overlay functionality"""
    try:
        result = star_service.get_exoplanets()
        if result['success']:
            return success_response(result['data'], count=len(result['data']))
        return error_response(result.get('error', 'Failed to retrieve exoplanets'), 500)
    except Exception as e:
        logger.error(f"Error in get_exoplanets: {e}")
        return error_response("Failed to retrieve exoplanets", 500)
