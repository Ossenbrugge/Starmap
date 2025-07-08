# Trade Routes for the Starmap Application
# Economic networks and shipping routes in the galaxy

import json
import os

# Load trade routes data from JSON file
def load_trade_routes_data():
    """Load trade routes data from JSON file"""
    try:
        data_file = os.path.join(os.path.dirname(__file__), 'trade_routes_data.json')
        with open(data_file, 'r', encoding='utf-8') as f:
            data = json.load(f)
        return data
    except FileNotFoundError:
        print("Warning: trade_routes_data.json not found, using empty data")
        return {"trade_routes": {}}
    except json.JSONDecodeError as e:
        print(f"Error parsing trade_routes_data.json: {e}")
        return {"trade_routes": {}}

def get_fallback_trade_routes():
    """Fallback trade routes data in case JSON file is not available"""
    return {
        "trade_routes": {
            "terran_primary_routes": [
                {
                    "name": "Earth-Lalande Trade Corridor",
                    "from_star_id": 0,
                    "to_star_id": 53879,
                    "from_system": "Sol",
                    "to_system": "Lalande 21185",
                    "route_type": "Primary Trade",
                    "established": 2181,
                    "cargo_types": ["Technology", "Manufactured Goods", "Rare Earth Elements"],
                    "travel_time_days": 28,
                    "frequency": "Daily",
                    "controlling_nation": "terran_directorate",
                    "security_level": "High",
                    "description": "Major industrial supply route connecting Earth's manufacturing to Lalande's mining operations"
                }
            ]
        }
    }

# Load the data
trade_routes_data = load_trade_routes_data()
all_trade_routes = trade_routes_data.get('trade_routes', {})

def get_all_trade_routes():
    """Get all trade routes"""
    return all_trade_routes

def get_trade_routes_by_nation(nation_id):
    """Get trade routes controlled by a specific nation"""
    nation_routes = []
    for route_category, routes in all_trade_routes.items():
        for route in routes:
            if route.get('controlling_nation') == nation_id:
                nation_routes.append(route)
    return nation_routes

def get_trade_routes_for_star(star_id):
    """Get all trade routes that connect to a specific star"""
    star_routes = []
    for route_category, routes in all_trade_routes.items():
        for route in routes:
            if route.get('from_star_id') == star_id or route.get('to_star_id') == star_id:
                star_routes.append(route)
    return star_routes

def get_trade_route_by_name(route_name):
    """Get a specific trade route by name"""
    for route_category, routes in all_trade_routes.items():
        for route in routes:
            if route.get('name') == route_name:
                return route
    return None

def get_trade_routes_summary():
    """Get a summary of all trade routes"""
    summary = {
        'total_routes': 0,
        'routes_by_nation': {},
        'routes_by_type': {},
        'total_categories': len(all_trade_routes)
    }
    
    for route_category, routes in all_trade_routes.items():
        summary['total_routes'] += len(routes)
        
        for route in routes:
            nation = route.get('controlling_nation', 'unknown')
            route_type = route.get('route_type', 'unknown')
            
            # Count by nation
            if nation not in summary['routes_by_nation']:
                summary['routes_by_nation'][nation] = 0
            summary['routes_by_nation'][nation] += 1
            
            # Count by type
            if route_type not in summary['routes_by_type']:
                summary['routes_by_type'][route_type] = 0
            summary['routes_by_type'][route_type] += 1
    
    return summary