"""
API Route Handlers - Clean Architecture Layer
Protected/CRUD API endpoints with authentication middleware.
Read-only public endpoints are handled by the dedicated blueprints.
"""

from flask import Blueprint, request
from app.services.star_service import StarService
from app.services.nation_service import NationService
from app.services.trade_route_service import TradeRouteService
from app.middleware.auth_middleware import api_auth_required, rate_limit
from app.utils.response_utils import success_response, error_response
from typing import Optional

# Initialize services
star_service: Optional[StarService] = None
nation_service: Optional[NationService] = None
trade_service: Optional[TradeRouteService] = None


def init_api_services():
    """Initialize API services with proper dependencies"""
    global star_service, nation_service, trade_service

    try:
        star_service = StarService()
        nation_service = NationService()
        trade_service = TradeRouteService()
        return True
    except Exception as e:
        print(f"Failed to initialize API services: {e}")
        return False


# Blueprint for protected/CRUD API routes
api_bp = Blueprint('api', __name__, url_prefix='/api/v1')


@api_bp.route('/star/<int:star_id>')
@api_auth_required
@rate_limit('api_requests_per_minute')
def get_star_details(star_id):
    """Get detailed information for a specific star - protected"""
    try:
        result = star_service.get_star_details(star_id)
        if result['success']:
            return success_response(result['data'])
        elif result.get('error') == 'Star not found':
            return error_response('Star not found', 404)
        return error_response(result.get('error', 'Failed to retrieve star details'), 500)
    except Exception as e:
        return error_response(f'Internal server error: {str(e)}', 500)


@api_bp.route('/stars/nation/<nation_id>')
@api_auth_required
@rate_limit('api_requests_per_minute')
def get_stars_by_nation(nation_id):
    """Get all stars controlled by a nation - protected"""
    try:
        result = star_service.get_stars_by_nation(nation_id)
        if result['success']:
            return success_response(result['data'], count=len(result['data']))
        return error_response(result.get('error', 'Failed to retrieve stars by nation'), 500)
    except Exception as e:
        return error_response(f'Internal server error: {str(e)}', 500)


@api_bp.route('/network-analysis')
@api_auth_required
@rate_limit('analysis_requests_per_minute')
def get_network_analysis():
    """Get trade network analysis - protected"""
    try:
        result = trade_service.get_network_analysis()
        if result['success']:
            return success_response(result['data'])
        return error_response(result.get('error', 'Failed to retrieve network analysis'), 500)
    except Exception as e:
        return error_response(f'Internal server error: {str(e)}', 500)


# ── Fictional entity CRUD (protected) ──────────────────────────────────────

@api_bp.route('/fictional/stars', methods=['GET'])
@api_auth_required
@rate_limit('api_requests_per_minute')
def get_fictional_stars_protected():
    """Get all fictional stars - protected"""
    try:
        result = star_service.get_fictional_stars()
        if result['success']:
            return success_response(result['data'], count=len(result['data']))
        return error_response(result.get('error', 'Failed to retrieve fictional stars'), 500)
    except Exception as e:
        return error_response(f'Internal server error: {str(e)}', 500)


@api_bp.route('/fictional/stars', methods=['POST'])
@api_auth_required
@rate_limit('creation_requests_per_minute')
def add_fictional_star():
    """Add a new fictional star - protected"""
    try:
        data = request.get_json()
        result = star_service.add_fictional_star(data)
        if result['success']:
            return success_response(result['data'], message='Fictional star added successfully'), 201
        return error_response(result.get('error', 'Failed to add fictional star'), 400)
    except Exception as e:
        return error_response(f'Internal server error: {str(e)}', 500)


@api_bp.route('/fictional/stars/<int:star_id>', methods=['DELETE'])
@api_auth_required
@rate_limit('modification_requests_per_minute')
def delete_fictional_star(star_id):
    """Delete a fictional star - protected"""
    try:
        result = star_service.delete_fictional_star(star_id)
        if result['success']:
            return success_response(message=result.get('message', 'Fictional star deleted successfully'))
        elif result.get('error') == 'Star not found':
            return error_response('Fictional star not found', 404)
        return error_response(result.get('error', 'Failed to delete fictional star'), 500)
    except Exception as e:
        return error_response(f'Internal server error: {str(e)}', 500)


@api_bp.route('/fictional/exoplanets', methods=['GET'])
@api_auth_required
@rate_limit('api_requests_per_minute')
def get_fictional_exoplanets_protected():
    """Get all fictional exoplanets - protected"""
    try:
        result = star_service.get_fictional_exoplanets()
        if result['success']:
            return success_response(result['data'], count=len(result['data']))
        return error_response(result.get('error', 'Failed to retrieve fictional exoplanets'), 500)
    except Exception as e:
        return error_response(f'Internal server error: {str(e)}', 500)


@api_bp.route('/fictional/exoplanets', methods=['POST'])
@api_auth_required
@rate_limit('creation_requests_per_minute')
def add_fictional_exoplanet():
    """Add a new fictional exoplanet - protected"""
    try:
        data = request.get_json()
        result = star_service.add_fictional_exoplanet(data)
        if result['success']:
            return success_response(result['data'], message='Fictional exoplanet added successfully'), 201
        return error_response(result.get('error', 'Failed to add fictional exoplanet'), 400)
    except Exception as e:
        return error_response(f'Internal server error: {str(e)}', 500)


@api_bp.route('/fictional/nations', methods=['GET'])
@api_auth_required
@rate_limit('api_requests_per_minute')
def get_fictional_nations():
    """Get all fictional nations - protected"""
    try:
        result = nation_service.get_fictional_nations()
        if result['success']:
            return success_response(result['data'], count=len(result['data']))
        return error_response(result.get('error', 'Failed to retrieve fictional nations'), 500)
    except Exception as e:
        return error_response(f'Internal server error: {str(e)}', 500)


@api_bp.route('/fictional/nations', methods=['POST'])
@api_auth_required
@rate_limit('creation_requests_per_minute')
def add_fictional_nation():
    """Add a new fictional nation - protected"""
    try:
        data = request.get_json()
        result = nation_service.add_fictional_nation(data)
        if result['success']:
            return success_response(result['data'], message='Fictional nation added successfully'), 201
        return error_response(result.get('error', 'Failed to add fictional nation'), 400)
    except Exception as e:
        return error_response(f'Internal server error: {str(e)}', 500)


@api_bp.route('/fictional/nations/<string:nation_id>', methods=['DELETE'])
@api_auth_required
@rate_limit('modification_requests_per_minute')
def delete_fictional_nation(nation_id):
    """Delete a fictional nation - protected"""
    try:
        result = nation_service.delete_fictional_nation(nation_id)
        if result['success']:
            return success_response(message=result.get('message', 'Fictional nation deleted successfully'))
        elif result.get('error') == 'Nation not found':
            return error_response('Fictional nation not found', 404)
        return error_response(result.get('error', 'Failed to delete fictional nation'), 500)
    except Exception as e:
        return error_response(f'Internal server error: {str(e)}', 500)


@api_bp.route('/fictional/trade-routes', methods=['GET'])
@api_auth_required
@rate_limit('api_requests_per_minute')
def get_fictional_trade_routes():
    """Get all fictional trade routes - protected"""
    try:
        result = trade_service.get_fictional_trade_routes()
        if result['success']:
            return success_response(result['data'], count=len(result['data']))
        return error_response(result.get('error', 'Failed to retrieve fictional trade routes'), 500)
    except Exception as e:
        return error_response(f'Internal server error: {str(e)}', 500)


@api_bp.route('/fictional/trade-routes', methods=['POST'])
@api_auth_required
@rate_limit('creation_requests_per_minute')
def add_fictional_trade_route():
    """Add a new fictional trade route - protected"""
    try:
        data = request.get_json()
        result = trade_service.add_fictional_trade_route(data)
        if result['success']:
            return success_response(result['data'], message='Fictional trade route added successfully'), 201
        return error_response(result.get('error', 'Failed to add fictional trade route'), 400)
    except Exception as e:
        return error_response(f'Internal server error: {str(e)}', 500)


@api_bp.route('/fictional/trade-routes/<string:route_id>', methods=['DELETE'])
@api_auth_required
@rate_limit('modification_requests_per_minute')
def delete_fictional_trade_route(route_id):
    """Delete a fictional trade route - protected"""
    try:
        result = trade_service.delete_fictional_trade_route(route_id)
        if result['success']:
            return success_response(message=result.get('message', 'Fictional trade route deleted successfully'))
        elif result.get('error') == 'Trade route not found':
            return error_response('Fictional trade route not found', 404)
        return error_response(result.get('error', 'Failed to delete fictional trade route'), 500)
    except Exception as e:
        return error_response(f'Internal server error: {str(e)}', 500)


def init_api_routes(app):
    """Initialize API routes blueprint"""
    if init_api_services():
        print("✅ API services initialized successfully")
        app.register_blueprint(api_bp)
        print("✅ Protected API routes registered")
    else:
        print("❌ Failed to initialize API services")
