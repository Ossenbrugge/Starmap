"""
Stats Service - Business Logic Layer
Handles statistics and utility operations with clean separation of concerns
"""

import math
from typing import Dict, List, Any
from datetime import datetime


class StatsService:
    """Service for statistics and utility operations"""

    def __init__(self):
        pass

    def get_stats(self, authenticated: bool = False) -> Dict[str, Any]:
        """Get application statistics"""
        try:
            stats: Dict[str, Any] = {
                'timestamp': datetime.now().isoformat(),
                'authenticated': authenticated
            }

            # Entity counts are public data (the underlying endpoints are
            # unauthenticated), so always include them for the stats panel.
            db_stats = self._get_database_stats()
            if db_stats['success']:
                stats.update(db_stats['data'])

            return {'success': True, 'data': stats}

        except Exception as e:
            return {'success': False, 'error': f'Failed to retrieve statistics: {str(e)}'}

    def get_all_stats(self) -> Dict[str, Any]:
        """Get all statistics (alias used by stats blueprint)"""
        return self.get_stats(authenticated=False)

    def get_stellar_regions(self) -> Dict[str, Any]:
        """Get stellar regions data"""
        try:
            result = self._get_stellar_regions_from_db()
            if result['success']:
                return result
            return self._get_default_stellar_regions()
        except Exception as e:
            return {'success': False, 'error': f'Failed to retrieve stellar regions: {str(e)}'}

    def get_galactic_directions(self) -> Dict[str, Any]:
        """Get galactic directions data"""
        try:
            directions = self._calculate_galactic_directions()
            return {'success': True, 'data': directions}
        except Exception as e:
            return {'success': False, 'error': f'Failed to calculate galactic directions: {str(e)}'}

    def _get_database_stats(self) -> Dict[str, Any]:
        """Get database statistics from the shared Database singleton"""
        try:
            from app_refactored import get_database
            db = get_database()
            stats = db.get_stats()
            return {'success': True, 'data': stats}
        except Exception as e:
            return {'success': False, 'error': str(e)}

    def _get_stellar_regions_from_db(self) -> Dict[str, Any]:
        """Get stellar regions from the JSON data file via the shared Database"""
        try:
            from app_refactored import get_database
            db = get_database()
            regions = db.get_stellar_regions()
            if regions:
                return {'success': True, 'data': regions}
            return {'success': False, 'error': 'No stellar regions found'}
        except Exception as e:
            return {'success': False, 'error': str(e)}

    def _get_default_stellar_regions(self) -> Dict[str, Any]:
        """Fallback hardcoded stellar regions"""
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
        def ra_dec_to_xyz(ra: float, dec: float, distance: float):
            ra_rad = math.radians(ra)
            dec_rad = math.radians(dec)
            x = distance * math.cos(dec_rad) * math.cos(ra_rad)
            y = distance * math.cos(dec_rad) * math.sin(ra_rad)
            z = distance * math.sin(dec_rad)
            return [x, y, z]

        return [
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
