"""
Saved Views Blueprint — allows authenticated users to persist named map views.
"""
import json
import logging
from flask import Blueprint, request
from flask_login import current_user
from app.middleware.auth_middleware import api_auth_required
from app.utils.response_utils import success_response, error_response

logger = logging.getLogger(__name__)

saved_views_bp = Blueprint('saved_views', __name__, url_prefix='/api/v1')


def _db():
    from app_refactored import get_database
    return get_database()


@saved_views_bp.route('/views', methods=['GET'])
@api_auth_required
def list_views():
    """Return all saved views for the authenticated user."""
    try:
        views = _db().get_saved_views(current_user.id)
        # Parse params back to dict for the client
        for v in views:
            try:
                v['params'] = json.loads(v['params'])
            except Exception:
                v['params'] = {}
        return success_response(views, count=len(views))
    except Exception as e:
        logger.error(f"list_views error: {e}")
        return error_response("Failed to retrieve saved views", 500)


@saved_views_bp.route('/views', methods=['POST'])
@api_auth_required
def create_view():
    """Save a new named view for the authenticated user."""
    try:
        data = request.get_json(silent=True) or {}
        name = str(data.get('name', '')).strip()
        params = data.get('params', {})
        if not name:
            return error_response("View name is required", 400)
        params_json = json.dumps(params)
        view_id = _db().save_view(current_user.id, name, params_json)
        if view_id:
            return success_response({'id': view_id, 'name': name}, 201)
        return error_response("Failed to save view", 500)
    except Exception as e:
        logger.error(f"create_view error: {e}")
        return error_response("Failed to save view", 500)


@saved_views_bp.route('/views/<int:view_id>', methods=['DELETE'])
@api_auth_required
def delete_view(view_id: int):
    """Delete a saved view (only if it belongs to the current user)."""
    try:
        deleted = _db().delete_saved_view(view_id, current_user.id)
        if deleted:
            return success_response({'deleted': view_id})
        return error_response("View not found", 404)
    except Exception as e:
        logger.error(f"delete_view error: {e}")
        return error_response("Failed to delete view", 500)
