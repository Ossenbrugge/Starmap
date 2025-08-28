"""
Search Service - Business Logic Layer
Handles search operations across different data types with clean separation of concerns
"""

from typing import Dict, List, Any, Optional
from app.services.star_service import StarService


class SearchService:
    """Service for search operations across multiple data sources"""

    def __init__(self, star_service: Optional[StarService] = None):
        """Initialize service with star service dependency"""
        self.star_service = star_service or StarService()

    def search_stars(self, query: str, limit: int = 20, spectral_type: str = "") -> Dict[str, Any]:
        """
        Search stars by name or other criteria

        Args:
            query: Search query string
            limit: Maximum number of results to return
            spectral_type: Optional spectral class filter

        Returns:
            Dictionary with success status and search results or error
        """
        try:
            # Validate inputs
            if not query or not query.strip():
                return {'success': True, 'data': []}

            if limit < 1 or limit > 100:
                return {'success': False, 'error': 'Limit must be between 1 and 100'}

            # Perform star search using star service
            # This is a simplified implementation - in a real system you might have
            # a dedicated search repository or use elasticsearch/full-text search
            result = self._perform_star_search(query, limit, spectral_type)

            if result['success']:
                return result
            else:
                return {'success': False, 'error': 'Search failed'}

        except Exception as e:
            return {'success': False, 'error': f'Search error: {str(e)}'}

    def search_systems(self, query: str, limit: int = 20) -> Dict[str, Any]:
        """Search for star systems by name"""
        try:
            if not query or not query.strip():
                return {'success': True, 'data': []}

            # Delegate to star search for now
            result = self._perform_star_search(query, limit)
            return result

        except Exception as e:
            return {'success': False, 'error': f'System search error: {str(e)}'}

    def search_nations(self, query: str, limit: int = 20) -> Dict[str, Any]:
        """Search for nations by name"""
        try:
            if not query or not query.strip():
                return {'success': True, 'data': []}

            # This would need to be implemented with nation service
            # For now, return empty results
            return {'success': True, 'data': []}

        except Exception as e:
            return {'success': False, 'error': f'Nation search error: {str(e)}'}

    def _perform_star_search(self, query: str, limit: int, spectral_type: str = "") -> Dict[str, Any]:
        """Internal method to perform star search"""
        try:
            from models.database import Database

            db = Database()

            # Try enhanced search first
            if self._has_enhanced_search():
                return self._perform_enhanced_star_search(query, limit, spectral_type)
            else:
                # Fallback to basic search
                return self._perform_basic_star_search(query, limit, spectral_type)

        except Exception as e:
            return {'success': False, 'error': f'Search execution error: {str(e)}'}

    def _perform_enhanced_star_search(self, query: str, limit: int, spectral_type: str = "") -> Dict[str, Any]:
        """Perform search using enhanced database features"""
        try:
            # This would use StarModelDB's search capabilities
            # For now, delegate to star service
            stars_result = self.star_service.get_stars(limit=500, mag_limit=12.0)

            if not stars_result['success']:
                return stars_result

            stars = stars_result['data']
            query_lower = query.lower()

            # Perform basic text matching
            matching_stars = []
            for star in stars:
                star_names = star.get('names', {})
                star_name = star_names.get('primary_name', '').lower() if star_names else ''
                fictional_name = star_names.get('fictional_name', '').lower() if star_names else ''

                if query_lower in star_name or query_lower in fictional_name:
                    matching_stars.append(star)

                    # Limit results
                    if len(matching_stars) >= limit:
                        break

            return {'success': True, 'data': matching_stars}

        except Exception as e:
            return {'success': False, 'error': f'Enhanced search error: {str(e)}'}

    def _perform_basic_star_search(self, query: str, limit: int, spectral_type: str = "") -> Dict[str, Any]:
        """Perform search using basic database features"""
        try:
            from models.database import Database

            db = Database()
            stars_data = db.get_stars(limit=limit * 2)  # Get more to filter

            if isinstance(stars_data, dict) and 'data' in stars_data:
                stars = stars_data['data']
            else:
                stars = stars_data

            query_lower = query.lower()

            # Filter stars by query
            matching_stars = []
            for star in stars:
                star_name = star.get('name', '').lower()
                if query_lower in star_name:
                    if spectral_type and spectral_type.upper() not in star.get('spectral_class', ''):
                        continue

                    matching_stars.append(star)
                    if len(matching_stars) >= limit:
                        break

            return {'success': True, 'data': matching_stars}

        except Exception as e:
            return {'success': False, 'error': f'Basic search error: {str(e)}'}

    def _has_enhanced_search(self) -> bool:
        """Check if enhanced search capabilities are available"""
        try:
            # Check if StarModelDB is available and has search methods
            from models.star_model_db import StarModelDB
            return hasattr(StarModelDB, 'search_stars')
        except (ImportError, AttributeError):
            return False
