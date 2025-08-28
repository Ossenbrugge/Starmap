"""
Star Repository - Data Access Layer
Handles all star-related database operations
"""

from typing import Dict, List, Any, Optional
from app.repositories.base_repository import BaseRepository, with_caching, with_metrics


class StarRepository(BaseRepository):
    """Repository for star data access operations"""

    def __init__(self, star_model=None, cache=None, enable_cache: bool = True):
        """Initialize repository with optional star model dependency"""
        super().__init__(cache=cache, enable_cache=enable_cache)

        # Load the model using the base class method
        self.star_model = star_model or self._load_model()

    def _get_model_class(self):
        """Return the model class for this repository"""
        try:
            from models.star_model_db import StarModelDB
            return StarModelDB
        except ImportError:
            return None

    def _get_model_import_path(self) -> str:
        """Return the import path for the model class"""
        return "models.star_model_db.StarModelDB"

    def get_stars(self, limit: int = 1000, mag_limit: float = 8.0,
                  spectral_type: str = "") -> Dict[str, Any]:
        """
        Get stars from enhanced storage with filtering

        Args:
            limit: Maximum number of stars to return
            mag_limit: Magnitude limit filter
            spectral_type: Spectral class filter

        Returns:
            Dictionary with success status and data or error
        """
        try:
            if self.star_model:
                stars = self.star_model.get_stars(limit=limit, mag_limit=mag_limit, spectral_type=spectral_type)
                return {'success': True, 'data': stars}
            else:
                return {'success': False, 'error': 'Enhanced star features not available'}

        except Exception as e:
            return self._handle_database_error('get_stars', e)

    def get_star_by_id(self, star_id: int) -> Dict[str, Any]:
        """Get a specific star by ID"""
        try:
            if self.star_model:
                star = self.star_model.get_star_by_id(star_id)
                return {'success': True, 'data': star}
            else:
                return {'success': False, 'error': 'Enhanced star features not available'}

        except Exception as e:
            return self._handle_database_error('get_star_by_id', e)

    def get_trade_routes_by_star(self, star_id: int) -> Dict[str, Any]:
        """Get trade routes connected to a star"""
        try:
            if self.star_model:
                routes = self.star_model.get_trade_routes_by_star(star_id)
                return {'success': True, 'data': routes}
            else:
                return {'success': False, 'error': 'Enhanced trade route features not available'}

        except Exception as e:
            return self._handle_database_error('get_trade_routes_by_star', e)

    def get_stars_by_nation(self, nation_id: str) -> Dict[str, Any]:
        """Get stars controlled by a specific nation"""
        try:
            if self.star_model:
                stars = self.star_model.get_stars_by_nation(nation_id)
                return {'success': True, 'data': stars}
            else:
                return {'success': False, 'error': 'Enhanced star features not available'}

        except Exception as e:
            return self._handle_database_error('get_stars_by_nation', e)

    def get_fictional_stars(self) -> Dict[str, Any]:
        """Get all fictional stars"""
        try:
            if self.star_model:
                # This might need a custom implementation in StarModelDB
                return {'success': False, 'error': 'Fictional stars feature not implemented'}
            else:
                return {'success': False, 'error': 'Enhanced features not available'}

        except Exception as e:
            return self._handle_database_error('get_fictional_stars', e)

    def add_fictional_star(self, star_data: Dict[str, Any]) -> Dict[str, Any]:
        """Add a new fictional star"""
        try:
            # Implementation would depend on the actual storage mechanism
            return {'success': False, 'error': 'Add fictional star not implemented'}

        except Exception as e:
            return {'success': False, 'error': f'Database error: {str(e)}'}

    def delete_fictional_star(self, star_id: int) -> Dict[str, Any]:
        """Delete a fictional star"""
        try:
            # Implementation would depend on the actual storage mechanism
            return {'success': False, 'error': 'Delete fictional star not implemented'}

        except Exception as e:
            return {'success': False, 'error': f'Database error: {str(e)}'}

    def get_fictional_exoplanets(self) -> Dict[str, Any]:
        """Get fictional exoplanets"""
        try:
            from models.database import Database
            db = Database()

            fictional_exoplanets = db.get_fictional_exoplanets()
            return {'success': True, 'data': fictional_exoplanets}

        except Exception as e:
            return {'success': False, 'error': f'Database error: {str(e)}'}

    def get_exoplanets(self) -> Dict[str, Any]:
        """Get real exoplanets"""
        try:
            from models.database import Database
            db = Database()

            exoplanets = db.get_exoplanets()
            return {'success': True, 'data': exoplanets}

        except Exception as e:
            return {'success': False, 'error': f'Database error: {str(e)}'}

    def add_fictional_exoplanet(self, exoplanet_data: Dict[str, Any]) -> Dict[str, Any]:
        """Add a new fictional exoplanet"""
        try:
            from models.database import Database
            db = Database()

            # This would need to be implemented in the Database class
            return {'success': False, 'error': 'Add fictional exoplanet not implemented'}

        except Exception as e:
            return {'success': False, 'error': f'Database error: {str(e)}'}

    def get_cache_stats(self) -> Dict[str, Any]:
        """Get caching statistics if available"""
        try:
            if self.star_model and hasattr(self.star_model, 'get_cache_stats'):
                return self.star_model.get_cache_stats()
            else:
                return {'success': False, 'error': 'Cache stats not available'}

        except Exception as e:
            return self._handle_database_error('get_cache_stats', e)
