"""
Web Routes - HTML Template Serving
Handles web page requests and static file serving
"""

import os

from flask import (Blueprint, render_template, redirect, url_for,
                   send_from_directory, current_app, abort)
from flask_login import current_user

# Create blueprint for web routes
web_bp = Blueprint('web', __name__)

@web_bp.route('/')
def index():
    """Main starmap page - public for testing"""
    return render_template('starmap.html', user=current_user if current_user.is_authenticated else None)

@web_bp.route('/favicon.ico')
def favicon():
    """Serve the favicon for the browser's default /favicon.ico request.
    Points at the same PNG the page <head> links use — drop the file at
    static/img/favicon.png and both paths resolve. 404s harmlessly if absent."""
    img_dir = os.path.join(current_app.static_folder, 'img')
    if not os.path.exists(os.path.join(img_dir, 'favicon.png')):
        abort(404)
    return send_from_directory(img_dir, 'favicon.png', mimetype='image/png')

@web_bp.route('/login', methods=['GET', 'POST'])
def login():
    """Login page - delegating to auth routes for actual handling"""
    # This will redirect to the auth blueprint
    return redirect(url_for('auth.login'))

def init_web_routes(app):
    """Initialize web routes blueprint"""
    app.register_blueprint(web_bp)
    print("✅ Web routes registered for HTML template serving")
