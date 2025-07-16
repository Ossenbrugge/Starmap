"""
API Controller for Starmap V2
Handles all API endpoints with clean response formatting
"""

from flask import jsonify
from typing import Dict, List, Any

class APIController:
    """Handles all API operations with consistent response formatting"""
    
    def __init__(self, database):
        self.db = database
    
    def _success_response(self, data: Any, message: str = None) -> Dict:
        """Create standardized success response"""
        response = {
            'success': True,
            'data': data
        }
        if message:
            response['message'] = message
        return jsonify(response)
    
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
            stellar_regions_path = '../stellar_regions.json'
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
                # Fallback to simple regions
                regions = [
                    {'name': 'Core Worlds', 'center': [0, 0, 0], 'radius': 10, 'color': '#4CAF50'},
                    {'name': 'Rimward Colonies', 'center': [-20, 0, 0], 'radius': 15, 'color': '#2196F3'}
                ]
                return self._success_response(regions, f"Loaded {len(regions)} stellar regions (fallback)")
        except Exception as e:
            return self._error_response(f"Error loading stellar regions: {str(e)}", 500)
    
    def get_galactic_directions(self):
        """Get galactic coordinate directions"""
        try:
            directions = [
                {'name': 'Galactic Center', 'position': [25, 0, 0], 'color': '#FFD700'},
                {'name': 'Galactic Edge', 'position': [-25, 0, 0], 'color': '#FF4444'},
                {'name': 'Spinward', 'position': [0, 25, 0], 'color': '#44FF44'},
                {'name': 'Anti-Spinward', 'position': [0, -25, 0], 'color': '#4444FF'},
                {'name': 'Galactic North', 'position': [0, 0, 25], 'color': '#FF44FF'},
                {'name': 'Galactic South', 'position': [0, 0, -25], 'color': '#44FFFF'}
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