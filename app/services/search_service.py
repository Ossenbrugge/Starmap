"""
Search Service - Business Logic Layer
Handles search operations across different data types
"""

from typing import Dict, List, Any, Optional
from app.services.star_service import StarService


class SearchService:
    """Service for search operations across multiple data sources"""

    def __init__(self, star_service: Optional[StarService] = None):
        self.star_service = star_service or StarService()

    def search_stars(self, query: str, limit: int = 20, spectral_type: str = "") -> Dict[str, Any]:
        """Search stars by name or other criteria"""
        try:
            if not query or not query.strip():
                return {'success': True, 'data': []}

            limit = max(1, min(limit, 100))

            return self._perform_star_search(query, limit, spectral_type)

        except Exception as e:
            return {'success': False, 'error': f'Search error: {str(e)}'}

    def search_systems(self, query: str, limit: int = 20) -> Dict[str, Any]:
        """Search for star systems by name"""
        return self.search_stars(query, limit)

    def search_nations(self, query: str, limit: int = 20) -> Dict[str, Any]:
        """Search for nations by name"""
        try:
            if not query or not query.strip():
                return {'success': True, 'data': []}

            from app.repositories.nation_repository import NationRepository
            repo = NationRepository()
            result = repo.get_nations()
            if not result['success']:
                return {'success': True, 'data': []}

            query_lower = query.lower()
            matches = [
                n for n in result['data']
                if query_lower in n.get('name', '').lower()
            ][:limit]

            return {'success': True, 'data': matches}

        except Exception as e:
            return {'success': False, 'error': f'Nation search error: {str(e)}'}

    def _perform_star_search(self, query: str, limit: int, spectral_type: str = "") -> Dict[str, Any]:
        """Search stars using the shared Database singleton"""
        try:
            from app_refactored import get_database
            db = get_database()

            stars = db.search_stars(query, limit * 2)  # Get more then filter

            query_lower = query.lower()
            results: List[Dict[str, Any]] = []

            for star in stars:
                name = star.get('name', '')
                fictional = star.get('fictional_name', '')
                constellation = star.get('constellation', '')
                search_text = f"{name} {fictional} {constellation}".lower()

                if query_lower in search_text:
                    if spectral_type:
                        sc = star.get('spectral_class', star.get('spect', ''))
                        if spectral_type.upper() not in sc.upper():
                            continue
                    results.append(star)
                    if len(results) >= limit:
                        break

            return {'success': True, 'data': results, 'count': len(results)}

        except Exception as e:
            return {'success': False, 'error': f'Search execution error: {str(e)}'}
