"""
Nation Service - Business Logic Layer
Handles nation-related operations with clean separation of concerns
"""

from typing import Dict, List, Any, Optional
from app.repositories.nation_repository import NationRepository


class NationService:
    """Service for nation business logic operations"""

    def __init__(self, nation_repository: Optional[NationRepository] = None):
        """Initialize service with repository dependency"""
        self.nation_repository = nation_repository or NationRepository()

    def get_nations(self) -> Dict[str, Any]:
        """Get all nations"""
        try:
            result = self.nation_repository.get_nations()

            if not result['success']:
                return result

            nations = result.get('data', [])

            return {
                'success': True,
                'data': nations
            }

        except Exception as e:
            return {'success': False, 'error': f'Failed to retrieve nations: {str(e)}'}

    def get_all_nations(self) -> Dict[str, Any]:
        """Alias for get_nations to fix API compatibility"""
        return self.get_nations()

    def get_fictional_nations(self) -> Dict[str, Any]:
        """Get all fictional nations"""
        try:
            result = self.nation_repository.get_fictional_nations()

            if not result['success']:
                return result

            return result

        except Exception as e:
            return {'success': False, 'error': f'Failed to retrieve fictional nations: {str(e)}'}

    def get_nation_stats(self) -> Dict[str, Any]:
        """Get nation statistics"""
        try:
            result = self.nation_repository.get_nation_stats()

            if not result['success']:
                return result

            return result

        except Exception as e:
            return {'success': False, 'error': f'Failed to get nation stats: {str(e)}'}

    def add_fictional_nation(self, nation_data: Dict[str, Any]) -> Dict[str, Any]:
        """Add a new fictional nation"""
        try:
            # Validate required fields
            required_fields = ['name', 'capital_system', 'government_type']
            if not all(field in nation_data for field in required_fields):
                return {'success': False, 'error': 'Missing required fields: name, capital_system, government_type'}

            # Validate government type
            valid_governments = ['democracy', 'monarchy', 'republic', 'dictatorship', 'federation', 'confederation', 'empire']
            if nation_data.get('government_type', '').lower() not in valid_governments:
                return {'success': False, 'error': f'Invalid government type. Must be one of: {", ".join(valid_governments)}'}

            result = self.nation_repository.add_fictional_nation(nation_data)

            if result['success']:
                return {'success': True, 'data': result.get('data')}

            return result

        except Exception as e:
            return {'success': False, 'error': f'Failed to add fictional nation: {str(e)}'}

    def get_nation_by_id(self, nation_id: str) -> Dict[str, Any]:
        """Get a specific nation by ID"""
        try:
            result = self.nation_repository.get_nation_by_id(nation_id)
            if not result['success']:
                return result
            if not result.get('data'):
                return {'success': False, 'error': 'Nation not found'}
            return result
        except Exception as e:
            return {'success': False, 'error': f'Failed to retrieve nation: {str(e)}'}

    def get_nation_stars(self, nation_id: str) -> Dict[str, Any]:
        """Get all stars controlled by a specific nation"""
        try:
            from app.repositories.star_repository import StarRepository
            star_repo = StarRepository()
            result = star_repo.get_stars_by_nation(nation_id)
            if not result['success']:
                return result
            return {'success': True, 'data': result['data']}
        except Exception as e:
            return {'success': False, 'error': f'Failed to retrieve nation stars: {str(e)}'}

    def get_nation_territories(self, nation_id: str) -> Dict[str, Any]:
        """Get territory information for a specific nation"""
        try:
            nation_result = self.get_nation_by_id(nation_id)
            if not nation_result['success']:
                return nation_result
            nation = nation_result['data']
            territories = nation.get('territories', [])
            return {
                'success': True,
                'data': {
                    'nation_id': nation_id,
                    'territories': territories,
                    'territory_count': len(territories)
                }
            }
        except Exception as e:
            return {'success': False, 'error': f'Failed to retrieve nation territories: {str(e)}'}

    def delete_fictional_nation(self, nation_id: str) -> Dict[str, Any]:
        """Delete a fictional nation"""
        try:
            result = self.nation_repository.delete_fictional_nation(nation_id)
            if result['success']:
                return {'success': True, 'message': 'Fictional nation deleted successfully'}
            return result
        except Exception as e:
            return {'success': False, 'error': f'Failed to delete fictional nation: {str(e)}'}
