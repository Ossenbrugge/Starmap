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
        """Add a new fictional star (not yet implemented)"""
        return {'success': False, 'error': 'Add fictional star not implemented'}

    def delete_fictional_star(self, star_id: int) -> Dict[str, Any]:
        """Delete a fictional star (not yet implemented)"""
        return {'success': False, 'error': 'Delete fictional star not implemented'}

    def add_fictional_exoplanet(self, exoplanet_data: Dict[str, Any]) -> Dict[str, Any]:
        """Add a new fictional exoplanet (not yet implemented)"""
        return {'success': False, 'error': 'Add fictional exoplanet not implemented'}

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
