"""
Nation Repository - Data Access Layer
Handles all nation-related database operations
"""

from typing import Dict, List, Any, Optional
from app.repositories.base_repository import BaseRepository, with_caching, with_metrics


class NationRepository(BaseRepository):
    """Repository for nation data access operations"""

    def __init__(self, nation_model=None, cache=None, enable_cache: bool = True):
        """Initialize repository with optional nation model dependency"""
        super().__init__(cache=cache, enable_cache=enable_cache)

        # Load the model using the base class method
        self.nation_model = nation_model or self._load_model()

    def _get_model_class(self):
        """Return the model class for this repository"""
        try:
            from models.nation_model_db import NationModelDB
            return NationModelDB
        except ImportError:
            return None

    def _get_model_import_path(self) -> str:
        """Return the import path for the model class"""
        return "models.nation_model_db.NationModelDB"

    def get_nations(self) -> Dict[str, Any]:
        """Get all nations from enhanced storage"""
        try:
            if self.nation_model:
                nations = self.nation_model.get_nations()
                return {'success': True, 'data': nations}
            else:
                return {'success': False, 'error': 'Enhanced nation features not available'}

        except Exception as e:
            return self._handle_database_error('get_nations', e)

    def get_fictional_nations(self) -> Dict[str, Any]:
        """Get all fictional nations"""
        try:
            if self.nation_model:
                # This might need a custom implementation in NationModelDB
                return {'success': False, 'error': 'Fictional nations feature not implemented'}
            else:
                return {'success': False, 'error': 'Enhanced features not available'}

        except Exception as e:
            return self._handle_database_error('get_fictional_nations', e)

    def add_fictional_nation(self, nation_data: Dict[str, Any]) -> Dict[str, Any]:
        """Add a new fictional nation"""
        try:
            # Implementation would depend on the actual storage mechanism
            return {'success': False, 'error': 'Add fictional nation not implemented'}

        except Exception as e:
            return self._handle_database_error('add_fictional_nation', e)

    def delete_fictional_nation(self, nation_id: str) -> Dict[str, Any]:
        """Delete a fictional nation"""
        try:
            # Implementation would depend on the actual storage mechanism
            return {'success': False, 'error': 'Delete fictional nation not implemented'}

        except Exception as e:
            return self._handle_database_error('delete_fictional_nation', e)

    def get_nation_stats(self) -> Dict[str, Any]:
        """Get nation statistics"""
        try:
            if self.nation_model:
                stats = self.nation_model.get_nation_stats()
                return {'success': True, 'data': stats}
            else:
                return {'success': False, 'error': 'Enhanced nation features not available'}

        except Exception as e:
            return self._handle_database_error('get_nation_stats', e)

    def get_cache_stats(self) -> Dict[str, Any]:
        """Get caching statistics if available"""
        try:
            if self.nation_model and hasattr(self.nation_model, 'get_cache_stats'):
                return self.nation_model.get_cache_stats()
            else:
                return {'success': False, 'error': 'Cache stats not available'}

        except Exception as e:
            return self._handle_database_error('get_cache_stats', e)
