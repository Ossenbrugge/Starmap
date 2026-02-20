"""
Trade Route Service - Business Logic Layer
Handles trade route-related operations with clean separation of concerns
"""

from typing import Dict, Any, Optional
from app.repositories.trade_route_repository import TradeRouteRepository


class TradeRouteService:
    """Service for trade route business logic operations"""

    def __init__(self, trade_route_repository: Optional[TradeRouteRepository] = None):
        """Initialize service with repository dependency"""
        self.trade_route_repository = trade_route_repository or TradeRouteRepository()

    def get_trade_routes(self) -> Dict[str, Any]:
        """Get all trade routes"""
        try:
            result = self.trade_route_repository.get_trade_routes()

            if not result['success']:
                return result

            routes = result.get('data', [])

            return {
                'success': True,
                'data': routes
            }

        except Exception as e:
            return {'success': False, 'error': f'Failed to retrieve trade routes: {str(e)}'}

    def get_fictional_trade_routes(self) -> Dict[str, Any]:
        """Get all fictional trade routes"""
        try:
            result = self.trade_route_repository.get_fictional_trade_routes()

            if not result['success']:
                return result

            return result

        except Exception as e:
            return {'success': False, 'error': f'Failed to retrieve fictional trade routes: {str(e)}'}

    def get_network_analysis(self) -> Dict[str, Any]:
        """Get trade network analysis"""
        try:
            result = self.trade_route_repository.get_trade_network_analysis()

            if not result['success']:
                return result

            return result

        except Exception as e:
            return {'success': False, 'error': f'Failed to analyze trade network: {str(e)}'}

    def add_fictional_trade_route(self, route_data: Dict[str, Any]) -> Dict[str, Any]:
        """Add a new fictional trade route"""
        try:
            # Validate required fields
            required_fields = ['name', 'start_system', 'end_system', 'route_type']
            if not all(field in route_data for field in required_fields):
                return {'success': False, 'error': 'Missing required fields: name, start_system, end_system, route_type'}

            # Validate route type
            valid_types = ['commercial', 'military', 'smuggling', 'diplomatic', 'research']
            if route_data.get('route_type', '').lower() not in valid_types:
                return {'success': False, 'error': f'Invalid route type. Must be one of: {", ".join(valid_types)}'}

            # Validate distance if provided
            if 'estimated_travel_time' in route_data:
                travel_time = route_data['estimated_travel_time']
                if not isinstance(travel_time, (int, float)) or travel_time <= 0:
                    return {'success': False, 'error': 'Invalid travel time. Must be a positive number.'}

            result = self.trade_route_repository.add_fictional_trade_route(route_data)

            if result['success']:
                return {'success': True, 'data': result.get('data')}

            return result

        except Exception as e:
            return {'success': False, 'error': f'Failed to add fictional trade route: {str(e)}'}

    def delete_fictional_trade_route(self, route_id: str) -> Dict[str, Any]:
        """Delete a fictional trade route"""
        try:
            result = self.trade_route_repository.delete_fictional_trade_route(route_id)

            if result['success']:
                return {'success': True, 'message': 'Fictional trade route deleted successfully'}

            return result

        except Exception as e:
            return {'success': False, 'error': f'Failed to delete fictional trade route: {str(e)}'}
