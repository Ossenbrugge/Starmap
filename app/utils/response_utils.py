"""
Standardized response utilities for consistent API responses
"""

from flask import jsonify, Response
from typing import Any, Dict, Optional

def success_response(
    data: Any,
    message: Optional[str] = None,
    count: Optional[int] = None,
    status_code: int = 200
) -> Response:
    """Create standardized success response"""
    response_data: Dict[str, Any] = {
        'success': True,
        'data': data
    }

    if message:
        response_data['message'] = message

    # Use explicit count if provided, otherwise auto-calculate
    if count is not None:
        response_data['count'] = count
    elif isinstance(data, (list, tuple)) or hasattr(data, '__len__'):
        response_data['count'] = len(data) if hasattr(data, '__len__') else len(list(data))

    response = jsonify(response_data)
    response.status_code = status_code
    _add_standard_headers(response)
    return response

def error_response(
    error: str,
    status_code: int = 400,
    details: Optional[Dict[str, Any]] = None
) -> Response:
    """Create standardized error response"""
    response_data: Dict[str, Any] = {
        'success': False,
        'error': error
    }

    if details:
        response_data['details'] = details

    response = jsonify(response_data)
    response.status_code = status_code
    _add_standard_headers(response)
    return response

def create_response(
    data: Any = None,
    success: bool = True,
    message: Optional[str] = None,
    error: Optional[str] = None,
    status_code: int = 200
) -> Response:
    """Create standardized response (backward compatibility function)"""
    if success:
        return success_response(data, message, status_code=status_code)
    else:
        return error_response(error or 'An error occurred', status_code)

def _add_standard_headers(response: Response) -> None:
    """Add standard headers to all responses"""
    response.headers['Cache-Control'] = 'no-cache, no-store, must-revalidate'
    response.headers['Pragma'] = 'no-cache'
    response.headers['Expires'] = '0'
    response.headers['X-Content-Type-Options'] = 'nosniff'

def paginated_response(
    data: list,
    page: int,
    limit: int,
    total_count: int,
    message: Optional[str] = None
) -> Response:
    """Create paginated response with metadata"""
    response_data = {
        'success': True,
        'data': data,
        'count': len(data),
        'pagination': {
            'page': page,
            'limit': limit,
            'total_count': total_count,
            'total_pages': (total_count + limit - 1) // limit,
            'has_next': page * limit < total_count,
            'has_prev': page > 1
        }
    }

    if message:
        response_data['message'] = message

    response = jsonify(response_data)
    _add_standard_headers(response)
    return response
