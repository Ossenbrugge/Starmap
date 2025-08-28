"""
Authentication middleware for handling JWT and session authentication
"""

import logging
from functools import wraps
from flask import request, session
from flask_login import current_user
from app.services.auth_service import auth_service
from app.utils.response_utils import error_response

logger = logging.getLogger(__name__)

def api_auth_required(f):
    """
    Custom decorator for API authentication (supports both session and JWT)

    This decorator checks for authentication in the following order:
    1. Flask-Login session authentication
    2. JWT token in Authorization header
    """
    @wraps(f)
    def decorated_function(*args, **kwargs):
        # Check for JWT token in Authorization header
        auth_header = request.headers.get('Authorization')
        if auth_header and auth_header.startswith('Bearer '):
            token = auth_header.split(' ')[1]
            user = auth_service.verify_jwt_token(token)
            if user:
                # Set current_user for the request
                session['_user_id'] = str(user.id)
                logger.info(f"✅ JWT authentication successful for user {user.username}")
                return f(*args, **kwargs)

        # Fall back to Flask-Login session authentication
        if current_user.is_authenticated:
            logger.info(f"✅ Session authentication successful for user {current_user.username}")
            return f(*args, **kwargs)

        # No valid authentication found
        logger.warning("❌ Authentication failed - no valid session or JWT token")
        return error_response(
            'Authentication required',
            401,
            {
                'message': 'Please provide valid credentials via session login or JWT token',
                'accepted_methods': ['session', 'jwt']
            }
        )

    return decorated_function

def require_role(required_role: str):
    """
    Decorator to require specific user role

    Args:
        required_role: Required role name ('admin', 'moderator', etc.)
    """
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            if not current_user.is_authenticated:
                logger.warning("❌ Role check failed - user not authenticated")
                return error_response('Authentication required', 401)

            user_role = getattr(current_user, 'role', 'user')

            # Define role hierarchy (higher roles include lower roles)
            role_hierarchy = {
                'admin': ['admin', 'moderator', 'user'],
                'moderator': ['moderator', 'user'],
                'user': ['user']
            }

            allowed_roles = role_hierarchy.get(user_role, [user_role])

            if required_role not in allowed_roles:
                logger.warning(f"❌ Role check failed - user {current_user.username} has role '{user_role}', required '{required_role}'")
                return error_response(
                    'Insufficient permissions',
                    403,
                    {
                        'user_role': user_role,
                        'required_role': required_role
                    }
                )

            logger.info(f"✅ Role check passed for user {current_user.username} (role: {user_role})")
            return f(*args, **kwargs)

        return decorated_function
    return decorator

def rate_limit(limit_type: str = 'api_requests_per_minute'):
    """
    Decorator for rate limiting

    Args:
        limit_type: Type of rate limit to apply
    """
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            # For now, just log the request
            # In a real implementation, this would check and enforce rate limits
            client_ip = request.remote_addr

            logger.info(f"📊 Rate limit check for {client_ip} on {limit_type}")
            # TODO: Implement actual rate limiting logic

            return f(*args, **kwargs)

        return decorated_function
    return decorator

def validate_request_data(required_fields: list = None, optional_fields: list = None):
    """
    Decorator to validate request data

    Args:
        required_fields: List of required field names
        optional_fields: List of optional field names
    """
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            if not request.is_json:
                return error_response('Request must be JSON', 400)

            data = request.get_json()
            if not data:
                return error_response('No data provided', 400)

            # Check required fields
            if required_fields:
                missing_fields = [field for field in required_fields if field not in data]
                if missing_fields:
                    return error_response(
                        f'Missing required fields: {", ".join(missing_fields)}',
                        400,
                        {'missing_fields': missing_fields}
                    )

            # Validate field types and sanitize input
            validation_errors = []
            for field in (required_fields or []) + (optional_fields or []):
                if field in data:
                    validation_errors.extend(_validate_field(field, data[field]))

            if validation_errors:
                return error_response(
                    'Validation errors',
                    400,
                    {'validation_errors': validation_errors}
                )

            logger.info(f"✅ Request validation passed for {len(data)} fields")
            return f(*args, **kwargs)

        return decorated_function
    return decorator

def _validate_field(field_name: str, value) -> list:
    """
    Validate individual field value

    Returns list of validation error messages
    """
    errors = []

    # Basic validation rules (can be extended)
    validation_rules = {
        'username': lambda v: isinstance(v, str) and 3 <= len(v) <= 50 and v.isalnum(),
        'email': lambda v: isinstance(v, str) and '@' in v,
        'password': lambda v: isinstance(v, str) and len(v) >= 8,
    }

    # Apply specific validation for known fields
    if field_name in validation_rules:
        if not validation_rules[field_name](value):
            errors.append(f"Invalid {field_name} format")

    # General type checking
    if not isinstance(value, (str, int, float, bool)):
        errors.append(f"Invalid type for {field_name}: {type(value).__name__}")

    # Length limits for strings
    if isinstance(value, str) and len(value) > 1000:
        errors.append(f"{field_name} too long (max 1000 characters)")

    return errors

def log_request_info():
    """
    Decorator to log request information
    """
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            logger.info(f"📡 {request.method} {request.path} from {request.remote_addr}")
            if request.is_json:
                logger.debug(f"Request data: {request.get_json()}")

            return f(*args, **kwargs)

        return decorated_function
    return decorator
