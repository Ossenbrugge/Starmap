"""
Stats Service - Business Logic Layer
Handles statistics and utility operations with clean separation of concerns
"""

import math
from typing import Dict, List, Any, Optional
from datetime import datetime


class StatsService:
    """Service for statistics and utility operations"""

    def __init__(self):
        """Initialize service"""
        pass

    def get_stats(self, authenticated: bool = False) -> Dict[str, Any]:
        """
        Get application statistics

        Args:
            authenticated: Whether the request is from an authenticated user

        Returns:
            Dictionary with success status and statistics data or error
        """
        try:
            # Base stats available to all users
            stats = {
                'timestamp': datetime.now().isoformat(),
                'authenticated': authenticated
            }

            # Enhanced stats only for authenticated users
            if authenticated:
                enhanced_stats = self._get_enhanced_stats()
                stats.update(enhanced_stats)

            return {'success': True, 'data': stats}

        except Exception as e:
            return {'success': False, 'error': f'Failed to retrieve statistics: {str(e)}'}

    def get_stellar_regions(self) -> Dict[str, Any]:
        """Get stellar regions data"""
        try:
            result = self._get_stellar_regions_from_db()

            if result['success']:
                return result
            else:
                # Fallback to hardcoded data
                return self._get_default_stellar_regions()

        except Exception as e:
            return {'success': False, 'error': f'Failed to retrieve stellar regions: {str(e)}'}

    def get_galactic_directions(self) -> Dict[str, Any]:
        """Get galactic directions data"""
        try:
            # Calculate galactic directions using astronomical calculations
            directions = self._calculate_galactic_directions()
            return {'success': True, 'data': directions}

        except Exception as e:
            return {'success': False, 'error': f'Failed to calculate galactic directions: {str(e)}'}

    def _get_enhanced_stats(self) -> Dict[str, Any]:
        """Get enhanced statistics for authenticated users"""
        try:
            stats = {}

            # Try to get database stats
            db_stats = self._get_database_stats()
            if db_stats['success']:
                stats['database'] = db_stats['data']

            # Try to get cache statistics
            cache_stats = self._get_cache_stats()
            if cache_stats['success']:
                stats['performance'] = {
                    'caches': cache_stats['data']
                }

            return stats

        except Exception as e:
            return {'database_error': str(e)}

    def _get_database_stats(self) -> Dict[str, Any]:
        """Get database statistics"""
        try:
            from database.config import get_collection_stats

            if get_collection_stats:
                stats = get_collection_stats()
                return {'success': True, 'data': stats}
            else:
                return {'success': False, 'error': 'Database stats not available'}

        except Exception as e:
            return {'success': False, 'error': str(e)}

    def _get_cache_stats(self) -> Dict[str, Any]:
        """Get cache statistics from all repositories"""
        try:
            cache_stats = {}

            # Try to get cache stats from each repository
            repos_to_check = [
                ('stars', 'app.repositories.star_repository.StarRepository'),
                ('nations', 'app.repositories.nation_repository.NationRepository'),
                ('trade_routes', 'app.repositories.trade_route_repository.TradeRouteRepository'),
            ]

            for cache_name, repo_path in repos_to_check:
                try:
                    module_path, class_name = repo_path.rsplit('.', 1)
                    module = __import__(module_path, fromlist=[class_name])
                    repo_class = getattr(module, class_name)

                    # Create a temporary instance to get cache stats
                    repo = repo_class()
                    stats_result = repo.get_cache_stats()

                    if stats_result.get('success', False):
                        cache_stats[cache_name] = stats_result.get('data', {})
                    else:
                        cache_stats[cache_name] = {'status': 'not_available'}

                except Exception:
                    cache_stats[cache_name] = {'status': 'error'}

            return {'success': True, 'data': cache_stats}

        except Exception as e:
            return {'success': False, 'error': str(e)}

    def _get_stellar_regions_from_db(self) -> Dict[str, Any]:
        """Get stellar regions from database"""
        try:
            from database.config import get_database

            db_conn = get_database()
            if not db_conn:
                return {'success': False, 'error': 'Database not initialized'}

            stellar_regions = db_conn.stellar_regions
            regions = list(stellar_regions.find())

            return {'success': True, 'data': regions}

        except Exception as e:
            return {'success': False, 'error': str(e)}

    def _get_default_stellar_regions(self) -> Dict[str, Any]:
        """Get default stellar regions (hardcoded)"""
        regions = [
            {
                'name': 'Solar Vicinity',
                'center': [0, 0, 0],
                'radius': 50,
                'description': 'The local region around Sol, including nearby star systems'
            },
            {
                'name': 'Orion Arm',
                'center': [1000, 500, 0],
                'radius': 2000,
                'description': 'The Orion Arm of the Milky Way galaxy'
            },
            {
                'name': 'Galactic Core',
                'center': [8000, 0, 0],
                'radius': 5000,
                'description': 'The central region of the Milky Way galaxy'
            }
        ]

        return {'success': True, 'data': regions}

    def _calculate_galactic_directions(self) -> List[Dict[str, Any]]:
        """Calculate galactic direction markers"""
        try:
            def ra_dec_to_xyz(ra: float, dec: float, distance: float) -> List[float]:
                """Convert RA/DEC coordinates to cartesian coordinates"""
                ra_rad = math.radians(ra)
                dec_rad = math.radians(dec)
                x = distance * math.cos(dec_rad) * math.cos(ra_rad)
                y = distance * math.cos(dec_rad) * math.sin(ra_rad)
                z = distance * math.sin(dec_rad)
                return [x, y, z]

            directions = [
                {
                    'name': 'Galactic Center',
                    'position': ra_dec_to_xyz(266.4, -29.0, 25),
                    'color': '#ff6b6b',
                    'description': 'Direction toward the center of the Milky Way'
                },
                {
                    'name': 'Galactic North',
                    'position': ra_dec_to_xyz(192.9, 27.1, 25),
                    'color': '#4ecdc4',
                    'description': 'Direction toward the galactic north pole'
                },
                {
                    'name': 'Galactic South',
                    'position': ra_dec_to_xyz(12.9, -27.1, 25),
                    'color': '#45b7d1',
                    'description': 'Direction toward the galactic south pole'
                },
                {
                    'name': 'Galactic Anticenter',
                    'position': ra_dec_to_xyz(86.4, 29.0, 25),
                    'color': '#f9ca24',
                    'description': 'Direction opposite to the galactic center'
                },
                {
                    'name': 'Sol',
                    'position': [0.0, 0.0, 0.0],
                    'color': '#ffeb3b',
                    'description': 'Solar system - our reference point'
                }
            ]

            return directions

        except Exception as e:
            # Fallback to simplified directions
            return [
                {
                    'name': 'Galactic Center',
                    'position': [25, 0, 0],
                    'color': '#ff6b6b',
                    'description': 'Direction toward the center of the Milky Way'
                },
                {
                    'name': 'Sol',
                    'position': [0.0, 0.0, 0.0],
                    'color': '#ffeb3b',
                    'description': 'Solar system - our reference point'
                }
            ]
