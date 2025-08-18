"""
API Controller for Starmap V2
Handles all API endpoints with clean response formatting
"""

from flask import jsonify, request
from typing import Dict, List, Any
from handlers import StarHandler, ExoplanetHandler, NationHandler, TradeRouteHandler

class APIController:
    """Handles all API operations with consistent response formatting"""
    
    def __init__(self, database):
        self.db = database
        
        # Initialize handlers
        self.star_handler = StarHandler()
        self.exoplanet_handler = ExoplanetHandler()
        self.nation_handler = NationHandler()
        self.trade_route_handler = TradeRouteHandler()
    
    def _success_response(self, data: Any, message: str = None) -> Dict:
        """Create standardized success response"""
        response = {
            'success': True,
            'data': data
        }
        if message:
            response['message'] = message
        json_response = jsonify(response)
        json_response.headers['Cache-Control'] = 'no-cache, no-store, must-revalidate'
        json_response.headers['Pragma'] = 'no-cache'
        json_response.headers['Expires'] = '0'
        return json_response
    
    def _error_response(self, error: str, status_code: int = 400) -> Dict:
        """Create standardized error response"""
        return jsonify({
            'success': False,
            'error': error
        }), status_code
    
    def get_stars(self, limit: int, mag_limit: float, spectral_type: str):
        """Get filtered star data"""
        try:
            stars = self.db.get_stars(limit, mag_limit, spectral_type)
            return self._success_response(stars, f"Loaded {len(stars)} stars")
        except Exception as e:
            return self._error_response(f"Error loading stars: {str(e)}", 500)
    
    def get_star_details(self, star_id: int):
        """Get detailed star information"""
        try:
            star = self.db.get_star_by_id(star_id)
            if not star:
                return self._error_response(f"Star {star_id} not found", 404)
            
            # Enhance star data with additional details
            enhanced_star = star.copy()
            
            # Add fictional data section
            enhanced_star['fictional_data'] = {
                'name': star.get('fictional_name'),
                'description': star.get('fictional_description'),
                'source': 'Starmap Universe' if star.get('fictional_name') else None
            }
            
            # Add habitability info
            enhanced_star['habitability'] = {
                'score': 0.0,  # Placeholder
                'category': 'Unknown',
                'has_planets': star.get('has_planets', False),
                'planet_count': star.get('exoplanet_count', 0)
            }
            
            return self._success_response(enhanced_star)
            
        except Exception as e:
            return self._error_response(f"Error loading star details: {str(e)}", 500)
    
    def get_nations(self):
        """Get all nations"""
        try:
            nations = self.db.get_nations()
            return self._success_response(nations, f"Loaded {len(nations)} nations")
        except Exception as e:
            return self._error_response(f"Error loading nations: {str(e)}", 500)
    
    def get_trade_routes(self):
        """Get all trade routes"""
        try:
            routes = self.db.get_trade_routes()
            return self._success_response(routes, f"Loaded {len(routes)} trade routes")
        except Exception as e:
            return self._error_response(f"Error loading trade routes: {str(e)}", 500)
    
    def search_stars(self, query: str, limit: int):
        """Search stars by name"""
        try:
            if not query:
                return self._error_response("Search query is required")
            
            results = self.db.search_stars(query, limit)
            return self._success_response(results, f"Found {len(results)} matches")
        except Exception as e:
            return self._error_response(f"Error searching stars: {str(e)}", 500)
    
    def get_stats(self):
        """Get application statistics"""
        try:
            stats = self.db.get_stats()
            return self._success_response(stats)
        except Exception as e:
            return self._error_response(f"Error loading stats: {str(e)}", 500)
    
    def get_stellar_regions(self):
        """Get stellar regions (galactic octants)"""
        try:
            import json
            import os
            
            # Load stellar regions from JSON file
            stellar_regions_path = 'data/stellar_regions.json'
            if os.path.exists(stellar_regions_path):
                with open(stellar_regions_path, 'r') as f:
                    data = json.load(f)
                    
                regions = []
                for region in data['regions']:
                    # Convert RGB color to hex
                    color = f"#{region['color'][0]:02x}{region['color'][1]:02x}{region['color'][2]:02x}"
                    
                    regions.append({
                        'name': region['name'],
                        'short_name': region['short_name'],
                        'description': region['description'],
                        'center': region['center_point'],
                        'x_range': region['x_range'],
                        'y_range': region['y_range'],
                        'z_range': region['z_range'],
                        'color': color,
                        'octant_number': region['octant_number'],
                        'brightest_star': region['brightest_star'],
                        'diameter': region['diameter']
                    })
                    
                return self._success_response(regions, f"Loaded {len(regions)} stellar regions")
            else:
                # Fallback to simple regions scaled to 30 parsec limit
                regions = [
                    {'name': 'Core Worlds', 'center': [0, 0, 0], 'x_range': [-15, 15], 'y_range': [-15, 15], 'z_range': [-15, 15], 'color': '#4CAF50'},
                    {'name': 'Rimward Colonies', 'center': [-20, 0, 0], 'x_range': [-30, -10], 'y_range': [-15, 15], 'z_range': [-15, 15], 'color': '#2196F3'}
                ]
                return self._success_response(regions, f"Loaded {len(regions)} stellar regions (fallback)")
        except Exception as e:
            return self._error_response(f"Error loading stellar regions: {str(e)}", 500)
    
    def get_galactic_directions(self):
        """Get galactic coordinate directions"""
        try:
            # Scale to 30 parsec limit
            directions = [
                {'name': 'Galactic Center', 'position': [30, 0, 0], 'color': '#FFD700'},
                {'name': 'Galactic Edge', 'position': [-30, 0, 0], 'color': '#FF4444'},
                {'name': 'Spinward', 'position': [0, 30, 0], 'color': '#44FF44'},
                {'name': 'Anti-Spinward', 'position': [0, -30, 0], 'color': '#4444FF'},
                {'name': 'Galactic North', 'position': [0, 0, 30], 'color': '#FF44FF'},
                {'name': 'Galactic South', 'position': [0, 0, -30], 'color': '#44FFFF'}
            ]
            return self._success_response(directions, f"Loaded {len(directions)} galactic directions")
        except Exception as e:
            return self._error_response(f"Error loading galactic directions: {str(e)}", 500)
    
    def get_fictional_exoplanets(self):
        """Get all fictional exoplanets"""
        try:
            exoplanets = self.db.get_fictional_exoplanets()
            return self._success_response(exoplanets, f"Loaded {len(exoplanets)} fictional exoplanets")
        except Exception as e:
            return self._error_response(f"Error loading fictional exoplanets: {str(e)}", 500)
    
    def get_exoplanets(self):
        """Get all exoplanets (real catalog data)"""
        try:
            exoplanets = self.db.get_exoplanets()
            return self._success_response(exoplanets, f"Loaded {len(exoplanets)} exoplanets")
        except Exception as e:
            return self._error_response(f"Error loading exoplanets: {str(e)}", 500)
    
    # Handler-based endpoints for adding fictional entities
    
    def add_fictional_star(self):
        """Add a new fictional star"""
        try:
            data = request.get_json()
            if not data:
                return self._error_response("No data provided", 400)
            
            result = self.star_handler.add_fictional_star(data)
            
            if result['success']:
                # Reload database cache to include new star
                self.db.reload_cache()
                return self._success_response(result['data'], result['message'])
            else:
                return self._error_response(result['error'], 400)
                
        except Exception as e:
            return self._error_response(f"Error adding fictional star: {str(e)}", 500)
    
    def add_fictional_exoplanet(self):
        """Add a new fictional exoplanet"""
        try:
            data = request.get_json()
            if not data:
                return self._error_response("No data provided", 400)
            
            result = self.exoplanet_handler.add_fictional_exoplanet(data)
            
            if result['success']:
                # Reload database cache to include new exoplanet
                self.db.reload_cache()
                return self._success_response(result['data'], result['message'])
            else:
                return self._error_response(result['error'], 400)
                
        except Exception as e:
            return self._error_response(f"Error adding fictional exoplanet: {str(e)}", 500)
    
    def add_fictional_nation(self):
        """Add a new fictional nation"""
        try:
            data = request.get_json()
            if not data:
                return self._error_response("No data provided", 400)
            
            result = self.nation_handler.add_fictional_nation(data)
            
            if result['success']:
                # Reload database cache to include new nation
                self.db.reload_cache()
                return self._success_response(result['data'], result['message'])
            else:
                return self._error_response(result['error'], 400)
                
        except Exception as e:
            return self._error_response(f"Error adding fictional nation: {str(e)}", 500)
    
    def add_fictional_trade_route(self):
        """Add a new fictional trade route"""
        try:
            data = request.get_json()
            if not data:
                return self._error_response("No data provided", 400)
            
            result = self.trade_route_handler.add_fictional_trade_route(data)
            
            if result['success']:
                # Reload database cache to include new trade route
                self.db.reload_cache()
                return self._success_response(result['data'], result['message'])
            else:
                return self._error_response(result['error'], 400)
                
        except Exception as e:
            return self._error_response(f"Error adding fictional trade route: {str(e)}", 500)
    
    def get_fictional_stars(self):
        """Get all fictional stars"""
        try:
            stars = self.star_handler.get_fictional_stars()
            return self._success_response(stars, f"Loaded {len(stars)} fictional stars")
        except Exception as e:
            return self._error_response(f"Error loading fictional stars: {str(e)}", 500)
    
    def get_fictional_nations(self):
        """Get all fictional nations"""
        try:
            nations = self.nation_handler.get_fictional_nations()
            return self._success_response(nations, f"Loaded {len(nations)} fictional nations")
        except Exception as e:
            return self._error_response(f"Error loading fictional nations: {str(e)}", 500)
    
    def get_fictional_trade_routes(self):
        """Get all fictional trade routes"""
        try:
            routes = self.trade_route_handler.get_fictional_trade_routes()
            return self._success_response(routes, f"Loaded {len(routes)} fictional trade routes")
        except Exception as e:
            return self._error_response(f"Error loading fictional trade routes: {str(e)}", 500)
    
    def delete_fictional_star(self, star_id: int):
        """Delete a fictional star"""
        try:
            result = self.star_handler.delete_fictional_star(star_id)
            
            if result['success']:
                return self._success_response(None, result['message'])
            else:
                return self._error_response(result['error'], 404)
                
        except Exception as e:
            return self._error_response(f"Error deleting fictional star: {str(e)}", 500)
    
    def delete_fictional_nation(self, nation_id: str):
        """Delete a fictional nation"""
        try:
            result = self.nation_handler.delete_nation(nation_id)
            
            if result['success']:
                return self._success_response(None, result['message'])
            else:
                return self._error_response(result['error'], 404)
                
        except Exception as e:
            return self._error_response(f"Error deleting fictional nation: {str(e)}", 500)
    
    def delete_fictional_trade_route(self, route_id: str):
        """Delete a fictional trade route"""
        try:
            result = self.trade_route_handler.delete_trade_route(route_id)
            
            if result['success']:
                return self._success_response(None, result['message'])
            else:
                return self._error_response(result['error'], 404)
                
        except Exception as e:
            return self._error_response(f"Error deleting fictional trade route: {str(e)}", 500)