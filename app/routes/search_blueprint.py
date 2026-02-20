"""
Search Blueprint - Modular API Routes
Handles all search-related API endpoints in a dedicated blueprint.
"""

from flask import Blueprint, request
from typing import Dict, Any
from app.services.search_service import SearchService
from app.middleware.auth_middleware import api_auth_required
from app.utils.response_utils import success_response, error_response
import logging

logger = logging.getLogger(__name__)

# Create blueprint
search_bp = Blueprint('search', __name__, url_prefix='/api/v1')

# Initialize service
search_service = SearchService()

@search_bp.route('/search')
@api_auth_required
def search() -> Dict[str, Any]:
    """Search across all data types"""
    try:
        query: str = request.args.get('q', '')
        limit: int = request.args.get('limit', 10, type=int)
        spectral_type: str = request.args.get('spectral_type', '')

        if not query.strip():
            return success_response([], count=0)

        result: Dict[str, Any] = search_service.search_stars(query, limit, spectral_type)
        if result['success']:
            return success_response(result['data'], count=len(result['data']))
        return error_response(result.get('error', 'Search failed'), 500)

    except Exception as e:
        logger.error(f"Error in search: {e}")
        return error_response("Search failed", 500)
