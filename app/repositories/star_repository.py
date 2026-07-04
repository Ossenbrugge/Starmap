"""
Star Repository - Data Access Layer
Handles all star-related database operations
"""

from typing import Dict, Any, Optional


class StarRepository:
    """Repository for star data access operations"""

    def __init__(self):
        """Initialize repository with shared database singleton"""
        self.database = None
        self._init_database()

    def _init_database(self):
        """Attach to the application-wide Database singleton"""
        try:
            from app_refactored import get_database
            self.database = get_database()
        except Exception:
            try:
                from models.database import Database
                self.database = Database()
            except Exception as e:
                print(f"Warning: Could not initialize database: {e}")
                self.database = None

    def get_stars(self, limit: int = 1000, mag_limit: float = 8.0,
                  spectral_type: str = "") -> Dict[str, Any]:
        """Get stars from database with filtering"""
        try:
            if not self.database:
                return {'success': False, 'error': 'Database not available'}
            stars = self.database.get_stars(limit=limit, mag_limit=mag_limit, spectral_type=spectral_type)
            return {'success': True, 'data': stars}
        except Exception as e:
            return {'success': False, 'error': f'Database error: {str(e)}'}

    def get_star_by_id(self, star_id: int) -> Dict[str, Any]:
        """Get a specific star by ID"""
        try:
            if not self.database:
                return {'success': False, 'error': 'Database not available'}
            star = self.database.get_star_by_id(star_id)
            if star:
                return {'success': True, 'data': star}
            return {'success': False, 'error': 'Star not found'}
        except Exception as e:
            return {'success': False, 'error': f'Database error: {str(e)}'}

    def get_trade_routes_by_star(self, star_id: int) -> Dict[str, Any]:
        """Get trade routes connected to a star"""
        try:
            if not self.database:
                return {'success': False, 'error': 'Database not available'}
            all_routes = self.database.get_trade_routes()
            connected = [
                r for r in all_routes
                if (r.get('endpoints', {}).get('from', {}).get('star_id') == star_id or
                    r.get('endpoints', {}).get('to', {}).get('star_id') == star_id)
            ]
            return {'success': True, 'data': connected}
        except Exception as e:
            return {'success': False, 'error': f'Database error: {str(e)}'}

    def get_stars_by_nation(self, nation_id: str) -> Dict[str, Any]:
        """Get stars controlled by a specific nation"""
        try:
            if not self.database:
                return {'success': False, 'error': 'Database not available'}
            all_stars = self.database.get_stars(limit=50000)
            nation_stars = [
                s for s in all_stars
                if (s.get('political', {}) or {}).get('nation_id') == nation_id
                   or s.get('nation_id') == nation_id
            ]
            return {'success': True, 'data': nation_stars}
        except Exception as e:
            return {'success': False, 'error': f'Database error: {str(e)}'}

    def get_fictional_stars(self) -> Dict[str, Any]:
        """Get all fictional stars"""
        try:
            if not self.database:
                return {'success': False, 'error': 'Database not available'}
            return {'success': True, 'data': self.database.get_fictional_stars()}
        except Exception as e:
            return {'success': False, 'error': f'Error: {str(e)}'}

    def get_fictional_exoplanets(self) -> Dict[str, Any]:
        """Get fictional exoplanets"""
        try:
            if not self.database:
                return {'success': False, 'error': 'Database not available'}
            return {'success': True, 'data': self.database.get_fictional_exoplanets()}
        except Exception as e:
            return {'success': False, 'error': f'Database error: {str(e)}'}

    def get_exoplanets(self) -> Dict[str, Any]:
        """Get real exoplanets"""
        try:
            if not self.database:
                return {'success': False, 'error': 'Database not available'}
            return {'success': True, 'data': self.database.get_exoplanets()}
        except Exception as e:
            return {'success': False, 'error': f'Database error: {str(e)}'}

    def add_fictional_star(self, star_data: Dict[str, Any]) -> Dict[str, Any]:
        """Add a new fictional star (is_fictional is always forced on)"""
        try:
            if not self.database:
                return {'success': False, 'error': 'Database not available'}

            data = dict(star_data)
            data['is_fictional'] = True
            if not data.get('fictional_name'):
                data['fictional_name'] = data.get('name') or ''

            star_id = data.get('id') or data.get('_id')
            if star_id is not None:
                existing = self.database.get_star_by_id(star_id)
                if existing and not existing.get('is_fictional'):
                    return {'success': False,
                            'error': f'Star {star_id} already exists and is not fictional'}

            new_id = self.database.add_star(data)
            if new_id is None:
                return {'success': False, 'error': 'Failed to add fictional star'}
            return {'success': True, 'data': self.database.get_star_by_id(new_id)}
        except Exception as e:
            return {'success': False, 'error': f'Database error: {str(e)}'}

    def delete_fictional_star(self, star_id: int) -> Dict[str, Any]:
        """Delete a fictional star (refuses to delete real catalog stars)"""
        try:
            if not self.database:
                return {'success': False, 'error': 'Database not available'}

            star = self.database.get_star_by_id(star_id)
            if not star:
                return {'success': False, 'error': 'Star not found'}
            if not star.get('is_fictional'):
                return {'success': False,
                        'error': f'Star {star_id} is not fictional and cannot be deleted'}

            if self.database.delete_star(star_id):
                return {'success': True,
                        'message': f'Fictional star {star_id} deleted successfully'}
            return {'success': False, 'error': 'Failed to delete fictional star'}
        except Exception as e:
            return {'success': False, 'error': f'Database error: {str(e)}'}

    def add_fictional_exoplanet(self, exoplanet_data: Dict[str, Any]) -> Dict[str, Any]:
        """Add a new fictional exoplanet (is_fictional is always forced on)"""
        try:
            if not self.database:
                return {'success': False, 'error': 'Database not available'}

            data = dict(exoplanet_data)
            host_name = data.get('host_star_name') or data.get('star_name') or ''
            payload = {
                'name': data.get('name'),
                'host_star_name': host_name,
                'is_fictional': True,
                # API shorthand: 'distance' = orbital distance (AU), 'period' = days
                'semi_major_axis_au': data.get('semi_major_axis_au', data.get('distance')),
                'orbital_period_days': data.get('orbital_period_days', data.get('period')),
                'planet_type': data.get('planet_type') or '',
                'planet_mass_earth': data.get('planet_mass_earth', data.get('mass')),
                'planet_radius_earth': data.get('planet_radius_earth', data.get('radius')),
                'equilibrium_temp_k': data.get('equilibrium_temp_k'),
                'potentially_habitable': data.get('potentially_habitable'),
                'discovery_method': data.get('discovery_method') or 'Fictional',
                'star_id': data.get('star_id'),
            }
            # Link to the host star when it exists so the map can place the planet
            if payload['star_id'] is None and host_name:
                host_id = self.database.find_star_id_by_name(host_name)
                if host_id is not None:
                    payload['star_id'] = host_id
                    host = self.database.get_star_by_id(host_id)
                    payload['distance'] = (host or {}).get('dist')

            new_id = self.database.add_exoplanet(payload)
            if new_id is None:
                return {'success': False, 'error': 'Failed to add fictional exoplanet'}
            payload['id'] = new_id
            return {'success': True, 'data': payload}
        except Exception as e:
            return {'success': False, 'error': f'Database error: {str(e)}'}

    def get_cache_stats(self) -> Dict[str, Any]:
        """Cache stats not implemented"""
        return {'success': False, 'error': 'Cache stats not available'}

    # ── BaseRepository interface ─────────────────────────────────────────────

    def get_by_id(self, id: Any) -> Dict[str, Any]:
        return self.get_star_by_id(id)

    def get_all(self) -> Dict[str, Any]:
        return self.get_stars()

    def create(self, data: Dict[str, Any]) -> Dict[str, Any]:
        try:
            if not self.database:
                return {'success': False, 'error': 'Database not available'}
            if self.database.add_star(data):
                return {'success': True, 'data': data}
            return {'success': False, 'error': 'Failed to create star'}
        except Exception as e:
            return {'success': False, 'error': f'Create error: {str(e)}'}

    def update(self, id: Any, data: Dict[str, Any]) -> Dict[str, Any]:
        try:
            if not self.database:
                return {'success': False, 'error': 'Database not available'}
            if self.database.update_star(id, data):
                return {'success': True, 'data': data}
            return {'success': False, 'error': 'Star not found or update failed'}
        except Exception as e:
            return {'success': False, 'error': f'Update error: {str(e)}'}

    def delete(self, id: Any) -> Dict[str, Any]:
        try:
            if not self.database:
                return {'success': False, 'error': 'Database not available'}
            if self.database.delete_star(id):
                return {'success': True, 'message': f'Star {id} deleted successfully'}
            return {'success': False, 'error': 'Star not found or delete failed'}
        except Exception as e:
            return {'success': False, 'error': f'Delete error: {str(e)}'}
