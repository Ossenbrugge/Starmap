"""
Authentication route handlers
Handles login, logout, and JWT token operations
"""

from flask import request, redirect, url_for, flash
from flask_login import login_user, logout_user, current_user
from app.services.auth_service import auth_service
from app.middleware.auth_middleware import api_auth_required
from app.utils.response_utils import success_response, error_response

def init_auth_routes(app):
    """Initialize authentication routes"""

    @app.route('/login', methods=['GET', 'POST'])
    def login():
        """Login page and handler"""
        if request.method == 'POST':
            username = request.form.get('username') or ''
            password = request.form.get('password') or ''
            remember = bool(request.form.get('remember'))

            result = auth_service.authenticate_user(username, password)
            if result['success']:
                user = result['user']
                login_user(user, remember=remember)
                auth_service.log_auth_event(f"User {username} authenticated successfully")

                # Redirect to next page or dashboard
                next_page = request.args.get('next')
                return redirect(next_page) if next_page else redirect(url_for('web.index'))
            else:
                auth_service.log_auth_event(f"Failed authentication attempt for user: {username}", failed=True)
                flash('Invalid credentials. Access denied.', 'danger')

        return auth_service.render_login_page()

    @app.route('/logout')
    def logout():
        """Logout handler"""
        username = current_user.username if current_user.is_authenticated else 'Unknown'
        logout_user()
        auth_service.log_auth_event(f"User {username} logged out")
        flash('Logged out successfully. Safe travels!', 'success')
        return redirect(url_for('login'))

    @app.route('/api/auth/token', methods=['POST'])
    def get_auth_token():
        """Generate JWT token for API access"""
        if not current_user.is_authenticated:
            return error_response('Authentication required', 401)

        try:
            expires_hours = request.json.get('expires_hours', 24) if request.is_json else 24
            token = auth_service.generate_jwt_token(current_user, expires_hours)

            auth_service.log_auth_event(f"JWT token generated for user {current_user.username}")

            return success_response({
                'token': token,
                'expires_in_hours': expires_hours,
                'user': current_user.username
            })

        except Exception as e:
            auth_service.log_auth_event(f"Error generating token: {e}", failed=True)
            return error_response('Failed to generate token', 500)
