"""
Timeline Blueprint - Public API
GET /api/v1/timeline?year=N
Returns a snapshot of the galaxy at a given in-universe year:
  - active nations (era_start <= year <= era_end)
  - colonized star count (discovery_year <= year or NULL)
  - active trade route count (era_start <= year or NULL)
"""

from flask import Blueprint, request
from typing import Dict, Any
from app.utils.response_utils import success_response, error_response
from models.database import Database
import logging

logger = logging.getLogger(__name__)

timeline_bp = Blueprint('timeline', __name__, url_prefix='/api/v1')


@timeline_bp.route('/timeline')
def get_timeline() -> Dict[str, Any]:
    """Return a galaxy snapshot for a given year."""
    year = request.args.get('year', type=int)
    if year is None:
        return error_response("Missing required parameter: year (integer)", 400)

    try:
        db = Database()
        nations = db.get_nations()

        active_nations = []
        for n in nations:
            era_s = n.get('era_start')
            era_e = n.get('era_end')
            if (era_s is None or year >= era_s) and (era_e is None or year <= era_e):
                color = (n.get('appearance') or {}).get('color') or n.get('color') or '#888888'
                active_nations.append({
                    'id':         n.get('_id') or n.get('id'),
                    'name':       n.get('name', ''),
                    'color':      color,
                    'era_start':  era_s,
                    'era_end':    era_e,
                    'capital_star_id': n.get('capital', {}).get('star_id'),
                })

        colonized = db._one(
            "SELECT COUNT(*) AS c FROM stars WHERE is_fictional=0 AND (discovery_year IS NULL OR discovery_year <= ?)",
            (year,)
        )['c']

        active_routes = db._one(
            "SELECT COUNT(*) AS c FROM trade_routes WHERE (era_start IS NULL OR era_start <= ?) AND (era_end IS NULL OR era_end >= ?)",
            (year, year)
        )['c']

        return success_response({
            'year':           year,
            'active_nations': active_nations,
            'nation_count':   len(active_nations),
            'colonized_stars': colonized,
            'active_routes':  active_routes,
        })

    except Exception as e:
        logger.error(f"Error in get_timeline for year={year}: {e}")
        return error_response("Failed to compute timeline snapshot", 500)
