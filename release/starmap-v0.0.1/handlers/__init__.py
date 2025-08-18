"""
Handlers package for managing fictional entities in the Starmap application.
Contains handlers for adding new fictional stars, exoplanets, nations, and trade routes.
"""

from .star_handler import StarHandler
from .exoplanet_handler import ExoplanetHandler
from .nation_handler import NationHandler
from .trade_route_handler import TradeRouteHandler

__all__ = ['StarHandler', 'ExoplanetHandler', 'NationHandler', 'TradeRouteHandler']