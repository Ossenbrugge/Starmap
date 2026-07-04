"""
Timeline Blueprint - Public API
GET /api/v1/timeline?year=N
Returns a snapshot of the galaxy at a given in-universe year:
  - active nations (era_start <= year <= era_end)
  - colonized star count (discovery_year <= year or NULL)
  - active trade route count (era_start <= year or NULL)
  - events: historical events at that exact year (or spanning it)

GET /api/v1/events?start=N&end=N&type=T
All historical events, optionally filtered by year range / event type.

GET /api/v1/star-ownership
Era ownership intervals: which nation holds which star during which years.
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
            'events':         db.get_historical_events(start=year, end=year),
        })

    except Exception as e:
        logger.error(f"Error in get_timeline for year={year}: {e}")
        return error_response("Failed to compute timeline snapshot", 500)


@timeline_bp.route('/events')
def get_events() -> Dict[str, Any]:
    """Return historical events, optionally filtered by year range / type."""
    start = request.args.get('start', type=int)
    end = request.args.get('end', type=int)
    event_type = request.args.get('type')

    try:
        db = Database()
        events = db.get_historical_events(start=start, end=end)
        if event_type:
            events = [e for e in events if e.get('event_type') == event_type]
        return success_response(events, count=len(events))
    except Exception as e:
        logger.error(f"Error in get_events: {e}")
        return error_response("Failed to retrieve historical events", 500)


@timeline_bp.route('/star-ownership')
def get_star_ownership() -> Dict[str, Any]:
    """Return era ownership intervals for all stars that have them."""
    try:
        db = Database()
        rows = db.get_star_ownership()
        return success_response(rows, count=len(rows))
    except Exception as e:
        logger.error(f"Error in get_star_ownership: {e}")
        return error_response("Failed to retrieve star ownership", 500)
