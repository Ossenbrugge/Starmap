"""
Web Routes - HTML Template Serving
Handles web page requests and static file serving
"""

from flask import Blueprint, render_template, redirect, url_for
from flask_login import current_user

# Create blueprint for web routes
web_bp = Blueprint('web', __name__)

@web_bp.route('/')
def index():
    """Main starmap page - public for testing"""
    return render_template('starmap.html', user=current_user if current_user.is_authenticated else None)

@web_bp.route('/login', methods=['GET', 'POST'])
def login():
    """Login page - delegating to auth routes for actual handling"""
    # This will redirect to the auth blueprint
    return redirect(url_for('auth.login'))

def init_web_routes(app):
    """Initialize web routes blueprint"""
    app.register_blueprint(web_bp)
    print("✅ Web routes registered for HTML template serving")
