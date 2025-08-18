"""
Starmap Authentication System
Flask-Login based authentication with JWT support
"""

import os
import jwt
from datetime import datetime, timedelta
from flask_login import UserMixin
from werkzeug.security import check_password_hash, generate_password_hash

class User(UserMixin):
    """Simple User class for Flask-Login"""
    
    def __init__(self, id, username, password_hash, role='admin'):
        self.id = id
        self.username = username
        self.password_hash = password_hash
        self.role = role
        self._is_active = True
    
    def check_password(self, password):
        """Check if the provided password matches the stored hash"""
        return check_password_hash(self.password_hash, password)
    
    def get_id(self):
        """Return user ID as string (required by Flask-Login)"""
        return str(self.id)
    
    @property
    def is_active(self):
        """Return if user is active (required by Flask-Login)"""
        return self._is_active
    
    def to_dict(self):
        """Convert user to dictionary for JWT"""
        return {
            'id': self.id,
            'username': self.username,
            'role': self.role
        }

class AuthManager:
    """Manages authentication for Starmap"""
    
    def __init__(self, secret_key):
        self.secret_key = secret_key
        self.users = self._create_default_users()
    
    def _create_default_users(self):
        """Create default admin users - in production, load from secure storage"""
        return {
            'admin': User(
                id=1,
                username='admin',
                password_hash=generate_password_hash('felgenland_secure_2025'),  # Change in production!
                role='admin'
            ),
            'starmap_admin': User(
                id=2,
                username='starmap_admin',
                password_hash=generate_password_hash('galactic_command_auth'),  # Change in production!
                role='admin'
            )
        }
    
    def get_user(self, user_id):
        """Get user by ID (for Flask-Login user_loader)"""
        for user in self.users.values():
            if user.id == int(user_id):
                return user
        return None
    
    def authenticate_user(self, username, password):
        """Authenticate user by username and password"""
        user = self.users.get(username)
        if user and user.check_password(password):
            return user
        return None
    
    def generate_jwt_token(self, user, expires_in_hours=24):
        """Generate JWT token for API access"""
        payload = {
            'user': user.to_dict(),
            'exp': datetime.utcnow() + timedelta(hours=expires_in_hours),
            'iat': datetime.utcnow(),
            'iss': 'starmap-auth'
        }
        return jwt.encode(payload, self.secret_key, algorithm='HS256')
    
    def verify_jwt_token(self, token):
        """Verify and decode JWT token"""
        try:
            payload = jwt.decode(token, self.secret_key, algorithms=['HS256'])
            user_data = payload.get('user')
            
            if user_data:
                # Return a temporary User object from JWT data
                return User(
                    id=user_data['id'],
                    username=user_data['username'],
                    password_hash='',  # Not needed for JWT verification
                    role=user_data.get('role', 'admin')
                )
            return None
        except jwt.ExpiredSignatureError:
            return None
        except jwt.InvalidTokenError:
            return None

# Security configuration
def get_auth_config():
    """Get authentication configuration"""
    return {
        'SECRET_KEY': os.environ.get('STARMAP_SECRET_KEY', 'felgenland-union-secure-key-2025-change-in-production'),
        'SESSION_TIMEOUT_HOURS': 8,
        'JWT_EXPIRES_HOURS': 24,
        'REMEMBER_COOKIE_DURATION': timedelta(days=7),
        'REMEMBER_COOKIE_SECURE': True,  # Set to True in production with HTTPS
        'REMEMBER_COOKIE_HTTPONLY': True,
    }