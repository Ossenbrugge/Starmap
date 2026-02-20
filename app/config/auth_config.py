"""
Authentication configuration settings
Centralized configuration for security settings
"""

import os
from datetime import timedelta

_DEFAULT_SECRET = 'felgenland-union-secure-key-2025-change-in-production'
_secret_key = os.environ.get('STARMAP_SECRET_KEY', _DEFAULT_SECRET)

# Refuse to start with the default key in production
def _validate_secret_key(key: str) -> str:
    if key == _DEFAULT_SECRET and os.environ.get('FLASK_ENV') == 'production':
        raise RuntimeError(
            'STARMAP_SECRET_KEY must be set to a strong random value in production. '
            'Generate one with: python -c "import secrets; print(secrets.token_hex(32))"'
        )
    return key

# Authentication configuration
auth_config = {
    'SECRET_KEY': _validate_secret_key(_secret_key),
    'SESSION_TIMEOUT_HOURS': int(os.environ.get('SESSION_TIMEOUT_HOURS', 8)),
    'JWT_EXPIRES_HOURS': int(os.environ.get('JWT_EXPIRES_HOURS', 24)),
    'JWT_ALGORITHM': 'HS256',
    'REMEMBER_COOKIE_DURATION': timedelta(days=7),
    'REMEMBER_COOKIE_SECURE': os.environ.get('REMEMBER_COOKIE_SECURE', 'false').lower() == 'true',
    'REMEMBER_COOKIE_HTTPONLY': True,
    'SESSION_COOKIE_SECURE': os.environ.get('SESSION_COOKIE_SECURE', 'false').lower() == 'true',
    'SESSION_COOKIE_HTTPONLY': True,
    'SESSION_COOKIE_SAMESITE': 'Lax',
}

# Password policy configuration
password_policy = {
    'MIN_LENGTH': int(os.environ.get('PASSWORD_MIN_LENGTH', 8)),
    'REQUIRE_UPPERCASE': os.environ.get('REQUIRE_UPPERCASE', 'true').lower() == 'true',
    'REQUIRE_LOWERCASE': os.environ.get('REQUIRE_LOWERCASE', 'true').lower() == 'true',
    'REQUIRE_DIGITS': os.environ.get('REQUIRE_DIGITS', 'true').lower() == 'true',
    'REQUIRE_SPECIAL_CHARS': os.environ.get('REQUIRE_SPECIAL_CHARS', 'false').lower() == 'true',
    'MAX_LOGIN_ATTEMPTS': int(os.environ.get('MAX_LOGIN_ATTEMPTS', 5)),
    'LOCKOUT_DURATION_MINUTES': int(os.environ.get('LOCKOUT_DURATION_MINUTES', 30)),
}

# Rate limiting configuration
rate_limits = {
    'LOGIN_ATTEMPTS_PER_HOUR': int(os.environ.get('LOGIN_ATTEMPTS_PER_HOUR', 10)),
    'API_REQUESTS_PER_MINUTE': int(os.environ.get('API_REQUESTS_PER_MINUTE', 60)),
    'SEARCH_REQUESTS_PER_MINUTE': int(os.environ.get('SEARCH_REQUESTS_PER_MINUTE', 30)),
}

# Security headers
security_headers = {
    'X-Frame-Options': 'SAMEORIGIN',
    'X-Content-Type-Options': 'nosniff',
    'X-XSS-Protection': '1; mode=block',
    'Strict-Transport-Security': 'max-age=31536000; includeSubDomains',
    'Content-Security-Policy': "default-src 'self' https://cdn.jsdelivr.net https://cdnjs.cloudflare.com https://unpkg.com https://aframe.io https://fonts.gstatic.com; script-src 'self' 'unsafe-inline' 'unsafe-eval' https://cdn.jsdelivr.net https://cdnjs.cloudflare.com https://unpkg.com https://aframe.io; style-src 'self' 'unsafe-inline' https://cdn.jsdelivr.net https://fonts.googleapis.com; img-src 'self' data: blob: https://cdn.aframe.io https://migaku-public-data.migaku.com; connect-src 'self' https://cdn.aframe.io https://migaku-public-data.migaku.com; font-src 'self' https://cdn.jsdelivr.net https://cdn.aframe.io https://migaku-public-data.migaku.com https://fonts.gstatic.com; object-src 'none'; media-src 'self' data: blob:; worker-src 'self' blob:; frame-ancestors 'none'",
}

def get_auth_config():
    """Get authentication configuration (backwards compatibility)"""
    return auth_config

def is_production():
    """Check if running in production environment"""
    return os.environ.get('FLASK_ENV') == 'production'

def get_cors_origins():
    """Get allowed CORS origins"""
    origins = os.environ.get('CORS_ORIGINS', 'http://localhost:3000,http://localhost:8080')
    return [origin.strip() for origin in origins.split(',') if origin.strip()]
