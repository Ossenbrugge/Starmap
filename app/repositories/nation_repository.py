"""
Nation Repository - Data Access Layer
Handles all nation-related database operations
"""

from typing import Dict, Any, Optional


class NationRepository:
    """Repository for nation data access operations"""

    def __init__(self):
        """Initialize repository with shared database singleton"""
        self.database = None
        self._init_database()

    def _init_database(self):
        """Attach to the application-wide Database singleton"""
        try:
            # Use the singleton from app_refactored to avoid re-loading files
            from app_refactored import get_database
            self.database = get_database()
        except Exception:
            # Fallback: import directly (still singleton via module-level caching)
            try:
                from models.database import Database
                self.database = Database()
            except Exception as e:
                print(f"Warning: Could not initialize database: {e}")
                self.database = None

    def get_nations(self) -> Dict[str, Any]:
        """Get all nations from database"""
        try:
            if not self.database:
                return {'success': False, 'error': 'Database not available'}
            nations = self.database.get_nations()
            return {'success': True, 'data': nations}
        except Exception as e:
            return {'success': False, 'error': f'Database error: {str(e)}'}

    def get_nation_by_id(self, nation_id: str) -> Dict[str, Any]:
        """Retrieve a specific nation by ID"""
        try:
            if not self.database:
                return {'success': False, 'error': 'Database not available'}
            nation = self.database.get_nation_by_id(nation_id)
            if nation:
                return {'success': True, 'data': nation}
            return {'success': False, 'error': 'Nation not found'}
        except Exception as e:
            return {'success': False, 'error': f'Database error: {str(e)}'}

    def get_fictional_nations(self) -> Dict[str, Any]:
        """Get all fictional nations (currently all nations are fictional)"""
        return self.get_nations()

    def add_fictional_nation(self, nation_data: Dict[str, Any]) -> Dict[str, Any]:
        """Add a new fictional nation"""
        return self.create(nation_data)

    def delete_fictional_nation(self, nation_id: str) -> Dict[str, Any]:
        """Delete a fictional nation"""
        return self.delete(nation_id)

    def get_nation_stats(self) -> Dict[str, Any]:
        """Get nation statistics"""
        try:
            if not self.database:
                return {'success': False, 'error': 'Database not available'}
            nations = self.database.get_nations()
            return {'success': True, 'data': {'total_nations': len(nations)}}
        except Exception as e:
            return {'success': False, 'error': f'Database error: {str(e)}'}

    def get_cache_stats(self) -> Dict[str, Any]:
        """Cache stats not implemented"""
        return {'success': False, 'error': 'Cache stats not available'}

    # ── BaseRepository interface ─────────────────────────────────────────────

    def get_by_id(self, id: Any) -> Dict[str, Any]:
        return self.get_nation_by_id(str(id))

    def get_all(self) -> Dict[str, Any]:
        return self.get_nations()

    def create(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Create new nation entity"""
        try:
            if not self.database:
                return {'success': False, 'error': 'Database not available'}
            if self.database.add_nation(data):
                return {'success': True, 'data': data}
            return {'success': False, 'error': 'Failed to create nation'}
        except Exception as e:
            return {'success': False, 'error': f'Create error: {str(e)}'}

    def update(self, id: Any, data: Dict[str, Any]) -> Dict[str, Any]:
        """Nation update not yet implemented"""
        return {'success': False, 'error': 'Nation update not implemented'}

    def delete(self, id: Any) -> Dict[str, Any]:
        """Nation delete not yet implemented"""
        return {'success': False, 'error': 'Nation delete not implemented'}
