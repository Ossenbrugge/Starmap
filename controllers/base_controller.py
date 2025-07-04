from abc import ABC
from flask import request


class BaseController(ABC):
    """Base controller class providing common functionality"""
    
    def __init__(self, model, view):
        self.model = model
        self.view = view
    
    def get_request_params(self, required_params=None, optional_params=None):
        """Extract and validate request parameters"""
        params = {}
        
        # Get parameters from both query string and JSON body
        if request.is_json:
            json_data = request.get_json() or {}
            params.update(json_data)
        
        # Query parameters override JSON parameters
        params.update(request.args.to_dict())
        
        # Validate required parameters
        if required_params:
            missing_params = [param for param in required_params if param not in params]
            if missing_params:
                raise ValueError(f"Missing required parameters: {', '.join(missing_params)}")
        
        # Extract optional parameters with defaults
        if optional_params:
            for param, default_value in optional_params.items():
                if param not in params:
                    params[param] = default_value
        
        return params
    
    def handle_request(self, handler_func, *args, **kwargs):
        """Generic request handler with error handling"""
        try:
            return handler_func(*args, **kwargs)
        except ValueError as e:
            return self.view.error_response(str(e), 400)
        except KeyError as e:
            return self.view.error_response(f"Missing parameter: {str(e)}", 400)
        except Exception as e:
            return self.view.error_response(f"Server error: {str(e)}", 500)
    
    def parse_int_param(self, value, param_name):
        """Parse integer parameter with validation"""
        try:
            return int(value)
        except (ValueError, TypeError):
            raise ValueError(f"Parameter '{param_name}' must be an integer")
    
    def parse_float_param(self, value, param_name):
        """Parse float parameter with validation"""
        try:
            return float(value)
        except (ValueError, TypeError):
            raise ValueError(f"Parameter '{param_name}' must be a number")
    
    def parse_bool_param(self, value, param_name):
        """Parse boolean parameter with validation"""
        if isinstance(value, bool):
            return value
        
        if isinstance(value, str):
            if value.lower() in ('true', '1', 'yes', 'on'):
                return True
            elif value.lower() in ('false', '0', 'no', 'off'):
                return False
        
        raise ValueError(f"Parameter '{param_name}' must be a boolean value")
    
    def validate_pagination_params(self, page, per_page, max_per_page=1000):
        """Validate pagination parameters"""
        page = max(1, page)
        per_page = max(1, min(per_page, max_per_page))
        return page, per_page
    
    def apply_filters(self, data, filters):
        """Apply filters to data"""
        if not filters:
            return data
        
        # This is a generic implementation
        # Specific controllers can override this method
        filtered_data = data
        
        for key, value in filters.items():
            if hasattr(self.model, 'filter_data'):
                filtered_data = self.model.filter_data(**{key: value})
            
        return filtered_data