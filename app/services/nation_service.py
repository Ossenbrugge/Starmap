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

    def delete_fictional_nation(self, nation_id: str) -> Dict[str, Any]:
        """Delete a fictional nation"""
        try:
            result = self.nation_repository.delete_fictional_nation(nation_id)

            if result['success']:
                return {'success': True, 'message': 'Fictional nation deleted successfully'}

            return result

        except Exception as e:
            return {'success': False, 'error': f'Failed to delete fictional nation: {str(e)}'}
