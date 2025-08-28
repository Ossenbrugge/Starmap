"""
Authentication service handling business logic for user authentication
"""

import logging
from flask import render_template
from auth import AuthManager
from app.repositories.user_repository import user_repository
from app.config.auth_config import auth_config

logger = logging.getLogger(__name__)

class AuthService:
    """Service for handling authentication business logic"""

    def __init__(self):
        self.auth_manager = AuthManager(auth_config['SECRET_KEY'])
        self.user_repository = user_repository

    def authenticate_user(self, username: str, password: str) -> dict:
        """Authenticate user credentials"""
        try:
            user = self.auth_manager.authenticate_user(username, password)
            if user:
                return {
                    'success': True,
                    'user': user,
                    'message': f'User {username} authenticated successfully'
                }
            else:
                return {
                    'success': False,
                    'error': 'Invalid credentials',
                    'message': f'Authentication failed for user: {username}'
                }
        except Exception as e:
            logger.error(f"Authentication error for user {username}: {e}")
            return {
                'success': False,
                'error': 'Authentication service unavailable',
                'message': 'Internal authentication error'
            }

    def generate_jwt_token(self, user, expires_hours: int = 24):
        """Generate JWT token for user"""
        try:
            return self.auth_manager.generate_jwt_token(user, expires_hours)
        except Exception as e:
            logger.error(f"JWT token generation error for user {user.username}: {e}")
            raise

    def verify_jwt_token(self, token: str):
        """Verify JWT token"""
        try:
            return self.auth_manager.verify_jwt_token(token)
        except Exception as e:
            logger.error(f"JWT token verification error: {e}")
            return None

    def log_auth_event(self, message: str, failed: bool = False):
        """Log authentication events"""
        level = logging.WARNING if failed else logging.INFO
        logger.log(level, f"🔐 AUTH: {message}")

    def render_login_page(self):
        """Render login template"""
        try:
            return render_template('login.html')
        except Exception as e:
            logger.error(f"Error rendering login page: {e}")
            return "Login page unavailable", 500

    def validate_password_strength(self, password: str) -> dict:
        """Validate password strength"""
        issues = []

        if len(password) < 8:
            issues.append("Password must be at least 8 characters long")
        if not any(c.isupper() for c in password):
            issues.append("Password must contain at least one uppercase letter")
        if not any(c.islower() for c in password):
            issues.append("Password must contain at least one lowercase letter")
        if not any(c.isdigit() for c in password):
            issues.append("Password must contain at least one number")

        return {
            'valid': len(issues) == 0,
            'issues': issues,
            'strength': self._calculate_password_strength(password)
        }

    def _calculate_password_strength(self, password: str) -> str:
        """Calculate password strength score"""
        score = 0

        if len(password) >= 8:
            score += 1
        if len(password) >= 12:
            score += 1
        if any(c.isupper() for c in password):
            score += 1
        if any(c.islower() for c in password):
            score += 1
        if any(c.isdigit() for c in password):
            score += 1
        if any(not c.isalnum() for c in password):
            score += 1

        if score <= 2:
            return 'weak'
        elif score <= 4:
            return 'medium'
        else:
            return 'strong'

# Global auth service instance
auth_service = AuthService()
