from flask import jsonify, Response
from abc import ABC, abstractmethod


class BaseView(ABC):
    """Base view class providing common response formatting"""
    
    def success_response(self, data, message=None):
        """Create a successful JSON response"""
        response_data = {
            'success': True,
            'data': data
        }
        
        if message:
            response_data['message'] = message
        
        return jsonify(response_data)
    
    def error_response(self, error_message, status_code=400):
        """Create an error JSON response"""
        response_data = {
            'success': False,
            'error': str(error_message)
        }
        
        return jsonify(response_data), status_code
    
    def paginated_response(self, data, total_count, page=1, per_page=50):
        """Create a paginated JSON response"""
        response_data = {
            'success': True,
            'data': data,
            'pagination': {
                'total_count': total_count,
                'page': page,
                'per_page': per_page,
                'total_pages': (total_count + per_page - 1) // per_page
            }
        }
        
        return jsonify(response_data)
    
    def csv_response(self, csv_content, filename):
        """Create a CSV download response"""
        return Response(
            csv_content,
            mimetype='text/csv',
            headers={'Content-Disposition': f'attachment; filename={filename}'}
        )
    
    def format_star_data(self, star_data):
        """Format star data for API response"""
        if not star_data:
            return None
        
        # Ensure all numeric fields are properly converted
        formatted_data = {}
        
        for key, value in star_data.items():
            if key in ['id']:
                formatted_data[key] = int(value) if value is not None else None
            elif key in ['x', 'y', 'z', 'mag', 'dist']:
                formatted_data[key] = float(value) if value is not None else 0.0
            elif key in ['all_names', 'catalog_ids']:
                formatted_data[key] = value if isinstance(value, list) else []
            else:
                formatted_data[key] = str(value) if value is not None else ''
        
        return formatted_data
    
    def format_planet_data(self, planet_data):
        """Format planet data for API response"""
        if not planet_data:
            return None
        
        formatted_data = {}
        
        for key, value in planet_data.items():
            if key in ['distance_au', 'mass_earth', 'radius_earth', 
                      'orbital_period_days', 'temperature_k']:
                formatted_data[key] = float(value) if value is not None else 0.0
            elif key == 'confirmed':
                formatted_data[key] = bool(value) if value is not None else False
            elif key == 'moons':
                formatted_data[key] = value if isinstance(value, list) else []
            else:
                formatted_data[key] = str(value) if value is not None else ''
        
        return formatted_data
    
    def format_nation_data(self, nation_data):
        """Format nation data for API response"""
        if not nation_data:
            return None
        
        formatted_data = {}
        
        for key, value in nation_data.items():
            if key == 'territories':
                formatted_data[key] = value if isinstance(value, list) else []
            elif key in ['founding_date', 'population']:
                formatted_data[key] = value if value is not None else 'Unknown'
            else:
                formatted_data[key] = str(value) if value is not None else ''
        
        return formatted_data
    
    def format_coordinates(self, x, y, z):
        """Format 3D coordinates"""
        return {
            'x': float(x) if x is not None else 0.0,
            'y': float(y) if y is not None else 0.0,
            'z': float(z) if z is not None else 0.0
        }
    
    def validate_required_params(self, params, required_fields):
        """Validate that required parameters are present"""
        missing_fields = []
        
        for field in required_fields:
            if field not in params or params[field] is None:
                missing_fields.append(field)
        
        if missing_fields:
            raise ValueError(f"Missing required parameters: {', '.join(missing_fields)}")
        
        return True