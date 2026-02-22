#!/usr/bin/env python3
"""
Refactored Starmap Application - Clean Architecture
Routes -> Services -> Repositories with Authentication & Rate Limiting
"""

import sys
import os
sys.path.insert(0, os.path.abspath(os.path.dirname(__file__)))

from flask import Flask, redirect
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

# Singleton database instance shared across all repositories/services
_database: Database = None

def get_database() -> Database:
    """Return the application-wide Database singleton."""
    global _database
    if _database is None:
        _database = Database()
    return _database


def create_app():
    """Application factory pattern with clean architecture"""
    app = Flask(__name__)

    # Apply security configuration
    app.config.update(auth_config_module.auth_config)

    # Apply security headers to every response
    @app.after_request
    def apply_security_headers(response):
        for header, value in security_headers.items():
            response.headers[header] = value
        return response

    # Initialize Flask-Login
    login_manager = LoginManager()
    login_manager.init_app(app)
    login_manager.login_view = 'login'
    login_manager.login_message = 'Access to galactic data requires authentication.'
    login_manager.login_message_category = 'info'

    # User loader for Flask-Login
    from auth import AuthManager
    auth_manager = AuthManager(app.config['SECRET_KEY'])

    @login_manager.user_loader
    def load_user(user_id):
        return auth_manager.get_user(user_id)

    # Pre-load the database singleton so all services share it
    try:
        get_database()
    except FileNotFoundError as exc:
        print(f"❌ Cannot start: {exc}")
        print("Run 'python scripts/migrate_to_sqlite.py' first.")
        raise SystemExit(1)

    # ── Register route layers ────────────────────────────────────────────────
    print("Initializing Clean Architecture Routes with Blueprints...")

    # Authentication and web (HTML) routes
    init_auth_routes(app)
    init_web_routes(app)

    # Protected CRUD API routes (api_routes.py → api_bp)
    init_api_routes(app)

    # Public read-only star routes
    from app.routes.stars_blueprint import stars_bp
    app.register_blueprint(stars_bp)

    # Public read-only nation routes
    from app.routes.nations_blueprint import nations_bp
    app.register_blueprint(nations_bp)

    # Public fictional entity routes
    from app.routes.fictional_blueprint import fictional_bp
    app.register_blueprint(fictional_bp)

    # Public search routes
    from app.routes.search_blueprint import search_bp
    app.register_blueprint(search_bp)

    # Stats and galactic directions
    from app.routes.stats_blueprint import stats_bp
    app.register_blueprint(stats_bp)

    # Stellar regions
    from app.routes.stellar_regions_blueprint import stellar_regions_bp
    app.register_blueprint(stellar_regions_bp)

    # Trade routes
    from app.routes.trade_routes_blueprint import trade_routes_bp
    app.register_blueprint(trade_routes_bp)

    # Saved views (auth-protected)
    from app.routes.saved_views_blueprint import saved_views_bp
    app.register_blueprint(saved_views_bp)

    print("All blueprints registered successfully")

    # ── Error handlers ───────────────────────────────────────────────────────
    @app.errorhandler(404)
    def not_found(error):
        return {'success': False, 'error': 'Endpoint not found'}, 404

    @app.errorhandler(500)
    def server_error(error):
        logger.error(f"Internal server error: {error}")
        return {'success': False, 'error': 'Internal server error'}, 500

    # Backwards-compat: redirect /api/* → /api/v1/*
    @app.route('/api/<path:path>', methods=['GET', 'POST', 'PUT', 'DELETE', 'PATCH'])
    def api_legacy_redirect(path):
        return redirect(f'/api/v1/{path}', code=301)

    # Health check endpoint
    @app.route('/health')
    def health_check():
        return {
            'success': True,
            'status': 'healthy',
            'timestamp': datetime.now().isoformat()
        }

    return app


# Application entry point
app = create_app()

if __name__ == '__main__':
    print("Starting Refactored Starmap - Felgenland Saga")
    print("Clean Architecture: Routes -> Services -> Repositories")

    debug_mode = os.environ.get('FLASK_DEBUG', 'false').lower() == 'true'
    port = int(os.environ.get('PORT', 8080))

    if debug_mode:
        print("WARNING: Running in DEBUG mode - do not use in production")

    print(f"Access at: http://localhost:{port}")

    app.run(host='0.0.0.0', port=port, debug=debug_mode)
