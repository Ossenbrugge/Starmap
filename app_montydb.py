"""
Starmap Application with MontyDB Backend
Enhanced version using MontyDB for improved performance and scalability
"""

from flask import Flask, render_template, request, jsonify
import json
import logging
from datetime import datetime

# Import MontyDB models
from database.config import initialize_database, get_collection_stats, get_database
from models.star_model_db import StarModelDB
from models.nation_model_db import NationModelDB
from models.trade_route_model_db import TradeRouteModelDB

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('starmap_montydb.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

app = Flask(__name__)

# Initialize models
star_model = None
nation_model = None
trade_model = None

def initialize_app():
    """Initialize the application with MontyDB"""
    global star_model, nation_model, trade_model
    
    logger.info("🚀 Starting Starmap with MontyDB backend")
    
    # Initialize database
    if not initialize_database():
        logger.error("❌ Failed to initialize MontyDB")
        return False
    
    # Initialize models
    try:
        star_model = StarModelDB()
        nation_model = NationModelDB()
        trade_model = TradeRouteModelDB()
        
        # Log statistics
        stats = get_collection_stats()
        logger.info(f"📊 Database loaded: {stats}")
        
        return True
        
    except Exception as e:
        logger.error(f"❌ Failed to initialize models: {e}")
        return False

@app.route('/')
def starmap():
    """Main starmap view"""
    return render_template('starmap.html')

@app.route('/api/stars')
def api_stars():
    """Enhanced star data API with improved filtering"""
    try:
        # Get parameters
        limit = min(int(request.args.get('count_limit', 1000)), 2000)
        mag_limit = float(request.args.get('mag_limit', 8.0))
        spectral_type = request.args.get('spectral_type', '').strip()
        
        # Get filtered stars
        stars = star_model.get_stars(limit=limit, mag_limit=mag_limit, spectral_type=spectral_type)
        
        # Convert to client format
        client_stars = []
        for star in stars:
            client_star = {
                'id': star['_id'],
                'name': star['names']['primary_name'],
                'fictional_name': star['names'].get('fictional_name'),
                'fictional_description': star['names'].get('fictional_description'),
                'x': star['coordinates']['x'],
                'y': star['coordinates']['y'],
                'z': star['coordinates']['z'],
                'distance': star['coordinates']['dist'],
                'magnitude': star['physical_properties']['magnitude'],
                'spectral_class': star['physical_properties']['spectral_class'],
                'constellation': star['classification']['constellation'],
                'exoplanet_count': star['exoplanets']['count'],
                'has_planets': star['exoplanets']['has_planets']
            }
            
            # Add political data if available
            if 'political' in star:
                client_star['nation'] = {
                    'id': star['political']['nation_id'],
                    'name': star['political']['nation_name']
                }
            
            client_stars.append(client_star)
        
        logger.info(f"API: Served {len(client_stars)} stars (limit: {limit}, mag: {mag_limit}, spectral: {spectral_type})")
        return jsonify({
            'success': True,
            'data': client_stars,
            'count': len(client_stars)
        })
        
    except Exception as e:
        logger.error(f"Error in /api/stars: {e}")
        return jsonify({'error': str(e)}), 500

@app.route('/api/search')
def api_search():
    """Enhanced search API"""
    try:
        query = request.args.get('q', '').strip()
        limit = min(int(request.args.get('limit', 20)), 100)
        spectral_type = request.args.get('spectral_type', '').strip()
        
        if not query:
            return jsonify([])
        
        # Search stars
        results = star_model.search_stars(query, limit)
        
        # Apply spectral type filter if specified
        if spectral_type:
            results = [star for star in results 
                      if star['physical_properties']['spectral_class'].startswith(spectral_type)]
        
        # Convert to client format
        client_results = []
        for star in results:
            client_result = {
                'id': star['_id'],
                'name': star['names']['primary_name'],
                'fictional_name': star['names'].get('fictional_name'),
                'distance': star['coordinates']['dist'],
                'magnitude': star['physical_properties']['magnitude'],
                'spectral_class': star['physical_properties']['spectral_class']
            }
            client_results.append(client_result)
        
        logger.info(f"API: Search '{query}' returned {len(client_results)} results")
        return jsonify({
            'success': True,
            'data': client_results,
            'count': len(client_results)
        })
        
    except Exception as e:
        logger.error(f"Error in /api/search: {e}")
        return jsonify({'error': str(e)}), 500

@app.route('/api/star/<int:star_id>')
def api_star_detail(star_id):
    """Get detailed information about a specific star"""
    try:
        star = star_model.get_star_by_id(star_id)
        if not star:
            return jsonify({'error': 'Star not found'}), 404
        
        # Get connected trade routes
        trade_routes = trade_model.get_routes_by_star(star_id)
        
        # Format detailed response
        detail = {
            'id': star['_id'],
            'names': star['names'],
            'coordinates': star['coordinates'],
            'physical_properties': star['physical_properties'],
            'classification': star['classification'],
            'exoplanets': star['exoplanets'],
            'political': star.get('political'),
            'trade_routes': [
                {
                    'id': route['_id'],
                    'name': route['name'],
                    'route_type': route['route_type'],
                    'connected_to': route['endpoints']['to']['system'] if route['endpoints']['from']['star_id'] == star_id else route['endpoints']['from']['system']
                }
                for route in trade_routes
            ],
            'is_fictional': star.get('is_fictional', False)
        }
        
        return jsonify(detail)
        
    except Exception as e:
        logger.error(f"Error in /api/star/{star_id}: {e}")
        return jsonify({'error': str(e)}), 500

@app.route('/api/nations')
def api_nations():
    """Get all nations"""
    try:
        nations = nation_model.get_nations()
        logger.info(f"API: Served {len(nations)} nations")
        return jsonify({
            'success': True,
            'data': nations,
            'count': len(nations)
        })
        
    except Exception as e:
        logger.error(f"Error in /api/nations: {e}")
        return jsonify({'error': str(e)}), 500

@app.route('/api/trade-routes')
def api_trade_routes():
    """Get all trade routes"""
    try:
        routes = trade_model.get_trade_routes()
        logger.info(f"API: Served {len(routes)} trade routes")
        return jsonify({
            'success': True,
            'data': routes,
            'count': len(routes)
        })
        
    except Exception as e:
        logger.error(f"Error in /api/trade-routes: {e}")
        return jsonify({'error': str(e)}), 500

@app.route('/api/stats')
def api_stats():
    """Get comprehensive database statistics"""
    try:
        stats = {
            'database': get_collection_stats(),
            'nations': nation_model.get_nation_stats(),
            'trade_network': trade_model.get_trade_network_analysis(),
            'performance': {
                'star_cache': star_model.get_cache_stats(),
                'nation_cache': nation_model.get_cache_stats(),
                'trade_cache': trade_model.get_cache_stats()
            },
            'timestamp': datetime.now().isoformat()
        }
        
        return jsonify({
            'success': True,
            'data': stats
        })
        
    except Exception as e:
        logger.error(f"Error in /api/stats: {e}")
        return jsonify({'error': str(e)}), 500

@app.route('/api/stars/nation/<nation_id>')
def api_stars_by_nation(nation_id):
    """Get all stars controlled by a nation"""
    try:
        stars = star_model.get_stars_by_nation(nation_id)
        
        client_stars = []
        for star in stars:
            client_star = {
                'id': star['_id'],
                'name': star['names']['primary_name'],
                'fictional_name': star['names'].get('fictional_name'),
                'coordinates': star['coordinates'],
                'magnitude': star['physical_properties']['magnitude'],
                'spectral_class': star['physical_properties']['spectral_class']
            }
            client_stars.append(client_star)
        
        logger.info(f"API: Served {len(client_stars)} stars for nation {nation_id}")
        return jsonify(client_stars)
        
    except Exception as e:
        logger.error(f"Error in /api/stars/nation/{nation_id}: {e}")
        return jsonify({'error': str(e)}), 500

@app.route('/api/network-analysis')
def api_network_analysis():
    """Get trade network analysis"""
    try:
        analysis = trade_model.get_trade_network_analysis()
        return jsonify(analysis)
        
    except Exception as e:
        logger.error(f"Error in /api/network-analysis: {e}")
        return jsonify({'error': str(e)}), 500

@app.route('/api/exoplanets')
def api_exoplanets():
    """Get all real exoplanets"""
    try:
        # For now, return empty array since we don't have exoplanet models implemented yet
        return jsonify({
            'success': True,
            'data': [],
            'count': 0
        })
        
    except Exception as e:
        logger.error(f"Error in /api/exoplanets: {e}")
        return jsonify({'error': str(e)}), 500

@app.route('/api/fictional-exoplanets')
def api_fictional_exoplanets():
    """Get all fictional exoplanets"""
    try:
        # For now, return empty array since we don't have exoplanet models implemented yet
        return jsonify({
            'success': True,
            'data': [],
            'count': 0
        })
        
    except Exception as e:
        logger.error(f"Error in /api/fictional-exoplanets: {e}")
        return jsonify({'error': str(e)}), 500

@app.route('/api/stellar-regions')
def api_stellar_regions():
    """Get all stellar regions"""
    try:
        db = get_database()
        stellar_regions = db.stellar_regions
        regions = list(stellar_regions.find())
        
        return jsonify({
            'success': True,
            'data': regions,
            'count': len(regions)
        })
        
    except Exception as e:
        logger.error(f"Error in /api/stellar-regions: {e}")
        return jsonify({'error': str(e)}), 500

@app.route('/api/galactic-directions')
def api_galactic_directions():
    """Get galactic directions data"""
    try:
        import math
        
        def ra_dec_to_xyz(ra, dec, distance):
            """Convert RA/Dec coordinates to Cartesian coordinates"""
            ra_rad = math.radians(ra)
            dec_rad = math.radians(dec)
            
            x = distance * math.cos(dec_rad) * math.cos(ra_rad)
            y = distance * math.cos(dec_rad) * math.sin(ra_rad)
            z = distance * math.sin(dec_rad)
            
            return [x, y, z]
        
        # Return static galactic directions data with 3D positions
        # Position them at the edge of the visible star field (~25 parsecs)
        directions = [
            {
                'name': 'Galactic Center',
                'position': ra_dec_to_xyz(266.4, -29.0, 25),  # Within visible range
                'color': '#ff6b6b',
                'description': 'Direction toward the center of the Milky Way'
            },
            {
                'name': 'Galactic North',
                'position': ra_dec_to_xyz(192.9, 27.1, 25),
                'color': '#4ecdc4',
                'description': 'Direction toward the galactic north pole'
            },
            {
                'name': 'Galactic South',
                'position': ra_dec_to_xyz(12.9, -27.1, 25),
                'color': '#45b7d1',
                'description': 'Direction toward the galactic south pole'
            },
            {
                'name': 'Galactic Anticenter',
                'position': ra_dec_to_xyz(86.4, 29.0, 25),
                'color': '#f9ca24',
                'description': 'Direction opposite to the galactic center'
            },
            {
                'name': 'Sol',
                'position': [0.0, 0.0, 0.0],  # Origin point
                'color': '#ffeb3b',
                'description': 'Solar system - our reference point'
            }
        ]
        
        return jsonify({
            'success': True,
            'data': directions,
            'count': len(directions)
        })
        
    except Exception as e:
        logger.error(f"Error in /api/galactic-directions: {e}")
        return jsonify({'error': str(e)}), 500

@app.errorhandler(404)
def not_found(error):
    return jsonify({'error': 'Not found'}), 404

@app.errorhandler(500)
def internal_error(error):
    logger.error(f"Internal server error: {error}")
    return jsonify({'error': 'Internal server error'}), 500

if __name__ == '__main__':
    # Initialize application
    if not initialize_app():
        logger.error("❌ Failed to initialize application")
        exit(1)
    
    logger.info("✅ Starmap MontyDB application ready")
    logger.info("🌐 Starting Flask server...")
    
    # Run Flask app
    app.run(
        host='0.0.0.0',
        port=5001,
        debug=True,
        use_reloader=False  # Disable reloader to prevent double initialization
    )