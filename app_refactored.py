#!/usr/bin/env python3
"""
Refactored Starmap Application - Clean Architecture
Phase 2 Complete: API Routes -> Services -> Repositories with Authentication & Rate Limiting
"""

import sys
import os
# Add current directory to Python path
sys.path.insert(0, os.path.abspath(os.path.dirname(__file__)))

from flask import Flask
from flask_login import LoginManager
import logging
from datetime import datetime
import app.config.auth_config as auth_config_module
from app.config.auth_config import security_headers
from app.routes.auth_routes import init_auth_routes
from app.routes.api_routes import init_api_routes
from app.routes.web_routes import init_web_routes
from models.database import Database

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('starmap.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

def create_app():
    """Application factory pattern with clean architecture"""
    app = Flask(__name__)

    # Apply security configuration
    app.config.update(auth_config_module.auth_config)

    # Initialize Flask-Login
    login_manager = LoginManager()
    login_manager.init_app(app)
    login_manager.login_view = 'login'
    login_manager.login_message = '🔒 Felgenland Security: Access to galactic data requires authentication.'
    login_manager.login_message_category = 'info'

    # User loader for Flask-Login
    from auth import AuthManager
    auth_manager = AuthManager(app.config['SECRET_KEY'])

    @login_manager.user_loader
    def load_user(user_id):
        """Load user for Flask-Login"""
        return auth_manager.get_user(user_id)

    # Initialize database
    database = Database()

    # Register route blueprints - Clean Architecture Order
    print("🚀 Initializing Clean Architecture Routes...")
    init_auth_routes(app)  # Phase 1: Authentication
    init_web_routes(app)   # Phase 2.1: Web Routes (HTML templates)
    init_api_routes(app)   # Phase 2.2: API Endpoints

    # Add security headers to all responses
    @app.after_request
    def add_security_headers(response):
        """Apply comprehensive security headers"""
        for header, value in security_headers.items():
            response.headers[header] = value
        return response

    # Error handlers with consistent JSON format
    @app.errorhandler(401)
    def unauthorized(error):
        return {
            'success': False,
            'error': 'Unauthorized',
            'message': 'Felgenland Security: Authentication required for galactic data access'
        }, 401

    @app.errorhandler(404)
    def not_found(error):
        return {
            'success': False,
            'error': 'Endpoint not found'
        }, 404

    @app.errorhandler(500)
    def server_error(error):
        logger.error(f"Internal server error: {error}")
        return {
            'success': False,
            'error': 'Internal server error'
        }, 500

    # Health check endpoint
    @app.route('/health')
    def health_check():
        """Application health check"""
        return {
            'success': True,
            'status': 'healthy',
            'architecture': 'Clean Architecture - Phase 2 Complete',
            'layers': ['Routes', 'Services', 'Repositories'],
            'features': ['Authentication', 'Authorization', 'Rate Limiting'],
            'timestamp': datetime.now().isoformat()
        }

    return app

# Keep the original access for backwards compatibility
app = create_app()

if __name__ == '__main__':
    print("🚀 Starting Refactored Starmap - Felgenland Saga")
    print("✨ Clean Architecture: Routes → Services → Repositories")
    print("🔐 Enhanced Authentication: Flask-Login + JWT + Rate Limiting")
    print("🛡️ Security: Input Validation + Security Headers")

    print("🌐 Access at: http://localhost:8080")
    print("🔑 Login required - use /login endpoint")

    app.run(host='0.0.0.0', port=8080, debug=True)
