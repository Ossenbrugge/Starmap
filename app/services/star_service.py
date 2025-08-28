"""
Star Service - Business Logic Layer
Handles star-related operations with clean separation of concerns
"""

import math
from typing import Dict, List, Any, Optional, Union
from app.repositories.star_repository import StarRepository


class StarService:
    """Service for star business logic operations"""

    def __init__(self, star_repository: Optional[StarRepository] = None):
        """Initialize service with repository dependency"""
        self.star_repository = star_repository or StarRepository()

    def get_stars(self, limit: int = 1000, mag_limit: float = 8.0,
                  spectral_type: str = "") -> Dict[str, Any]:
        """
        Get stars with filtering and business logic

        Args:
            limit: Maximum number of stars to return
            mag_limit: Magnitude limit for filtering
            spectral_type: Spectral class filter

        Returns:
            Dictionary with success status and data or error
        """
        try:
            # Validate parameters
            if limit < 1 or limit > 2000:
                return {'success': False, 'error': 'Limit must be between 1 and 2000'}

            if mag_limit < -2.0 or mag_limit > 15.0:
                return {'success': False, 'error': 'Magnitude limit must be between -2.0 and 15.0'}

            # Parse spectral type if provided
            spectral_type = spectral_type.upper().strip()
            valid_spectral = ['O', 'B', 'A', 'F', 'G', 'K', 'M']
            if spectral_type and spectral_type[0] not in valid_spectral:
                return {'success': False, 'error': 'Invalid spectral type'}

            # Get data from repository
            result = self.star_repository.get_stars(limit, mag_limit, spectral_type)

            if not result['success']:
                # Fallback to basic implementation if enhanced features unavailable
                return self._get_stars_basic(limit, mag_limit, spectral_type)

            stars = result['data']
            # Convert to client format
            client_stars = []
            for star in stars:
                client_star = self._convert_star_to_client_format(star)
                client_stars.append(client_star)

            return {
                'success': True,
                'data': client_stars
            }

        except Exception as e:
            return {'success': False, 'error': f'Failed to retrieve stars: {str(e)}'}

    def get_star_details(self, star_id: int) -> Dict[str, Any]:
        """Get detailed information for a specific star"""
        try:
            result = self.star_repository.get_star_by_id(star_id)

            if not result['success']:
                return result

            star = result['data']
            if not star:
                return {'success': False, 'error': 'Star not found'}

            # Get connected trade routes
            trade_result = self.star_repository.get_trade_routes_by_star(star_id)
            trade_routes = trade_result['data'] if trade_result['success'] else []

            # Format detailed response
            detail = {
                'id': star['_id'],
                'names': star['names'],
                'coordinates': star['coordinates'],
                'physical_properties': star['physical_properties'],
                'classification': star['classification'],
                'exoplanets': star['exoplanets'],
                'political': star.get('political'),
                'trade_routes': [
                    {
                        'id': route['_id'],
                        'name': route['name'],
                        'route_type': route['route_type'],
                        'connected_to': route['endpoints']['to']['system'] if route['endpoints']['from']['star_id'] == star_id else route['endpoints']['from']['system']
                    }
                    for route in trade_routes
                ],
                'is_fictional': star.get('is_fictional', False)
            }

            return {'success': True, 'data': detail}

        except Exception as e:
            return {'success': False, 'error': f'Failed to retrieve star details: {str(e)}'}

    def get_fictional_exoplanets(self) -> Dict[str, Any]:
        """Get fictional exoplanets (public access)"""
        try:
            result = self.star_repository.get_fictional_exoplanets()

            if not result['success']:
                return result

            return result

        except Exception as e:
            return {'success': False, 'error': f'Failed to retrieve fictional exoplanets: {str(e)}'}

    def get_exoplanets(self) -> Dict[str, Any]:
        """Get real exoplanets (public access)"""
        try:
            result = self.star_repository.get_exoplanets()

            if not result['success']:
                return result

            return result

        except Exception as e:
            return {'success': False, 'error': f'Failed to retrieve exoplanets: {str(e)}'}

    def get_stars_by_nation(self, nation_id: str) -> Dict[str, Any]:
        """Get all stars controlled by a nation"""
        try:
            result = self.star_repository.get_stars_by_nation(nation_id)

            if not result['success']:
                return result

            stars = result['data']
            client_stars = [self._convert_star_to_client_format(star) for star in stars]

            return {'success': True, 'data': client_stars}

        except Exception as e:
            return {'success': False, 'error': f'Failed to retrieve stars by nation: {str(e)}'}

    def get_fictional_stars(self) -> Dict[str, Any]:
        """Get all fictional stars"""
        try:
            result = self.star_repository.get_fictional_stars()

            if not result['success']:
                return result

            return result

        except Exception as e:
            return {'success': False, 'error': f'Failed to retrieve fictional stars: {str(e)}'}

    def add_fictional_star(self, star_data: Dict[str, Any]) -> Dict[str, Any]:
        """Add a new fictional star"""
        try:
            # Validate required fields
            required_fields = ['name', 'x', 'y', 'z']
            if not all(field in star_data for field in required_fields):
                return {'success': False, 'error': 'Missing required fields: name, x, y, z'}

            # Validate coordinate ranges
            coords = ['x', 'y', 'z']
            for coord in coords:
                value = star_data.get(coord, 0)
                if not isinstance(value, (int, float)) or abs(value) > 1000.0:
                    return {'success': False, 'error': f'Invalid {coord} coordinate'}

            result = self.star_repository.add_fictional_star(star_data)

            if result['success']:
                return {'success': True, 'data': result['data']}

            return result

        except Exception as e:
            return {'success': False, 'error': f'Failed to add fictional star: {str(e)}'}

    def delete_fictional_star(self, star_id: int) -> Dict[str, Any]:
        """Delete a fictional star"""
        try:
            result = self.star_repository.delete_fictional_star(star_id)

            if result['success']:
                return {'success': True, 'message': 'Fictional star deleted successfully'}

            return result

        except Exception as e:
            return {'success': False, 'error': f'Failed to delete fictional star: {str(e)}'}

    def add_fictional_exoplanet(self, exoplanet_data: Dict[str, Any]) -> Dict[str, Any]:
        """Add a new fictional exoplanet"""
        try:
            # Validate required fields
            required_fields = ['name', 'star_name', 'distance', 'period']
            if not all(field in exoplanet_data for field in required_fields):
                return {'success': False, 'error': 'Missing required fields: name, star_name, distance, period'}

            result = self.star_repository.add_fictional_exoplanet(exoplanet_data)

            if result['success']:
                return {'success': True, 'data': result['data']}

            return result

        except Exception as e:
            return {'success': False, 'error': f'Failed to add fictional exoplanet: {str(e)}'}

    def _convert_star_to_client_format(self, star: Dict[str, Any]) -> Dict[str, Any]:
        """Convert star data to client-friendly format"""
        return {
            'id': star['_id'],
            'name': star['names']['primary_name'],
            'fictional_name': star['names'].get('fictional_name'),
            'fictional_description': star['names'].get('fictional_description'),
            'x': star['coordinates']['x'],
            'y': star['coordinates']['y'],
            'z': star['coordinates']['z'],
            'distance': star['coordinates']['dist'],
            'magnitude': star['physical_properties']['magnitude'],
            'spectral_class': star['physical_properties']['spectral_class'],
            'constellation': star['classification']['constellation'],
            'exoplanet_count': star['exoplanets']['count'],
            'has_planets': star['exoplanets']['has_planets']
        }

    def _get_stars_basic(self, limit: int, mag_limit: float, spectral_type: str) -> Dict[str, Any]:
        """Fallback implementation when enhanced features are unavailable"""
        try:
            from models.database import Database
            db = Database()

            stars_data = db.get_stars(limit=limit, mag_limit=mag_limit)
            if isinstance(stars_data, dict) and 'data' in stars_data:
                stars = stars_data['data']
            else:
                stars = stars_data

            # Apply spectral type filter if specified
            if spectral_type:
                spectral_type = spectral_type.upper()
                stars = [star for star in stars if star.get('spectral_class', '').startswith(spectral_type)]

            return {'success': True, 'data': stars}

        except Exception as e:
            return {'success': False, 'error': f'Database error: {str(e)}'}
