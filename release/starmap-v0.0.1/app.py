#!/usr/bin/env python3
"""
Starmap - Felgenland Saga
3D Interactive starmap for the Felgenland Saga universe
Features real astronomical data enhanced with fictional political entities and trade networks
Includes Flask-Login authentication and JWT support for secure access
"""

from flask import Flask, request, jsonify, render_template, redirect, url_for, flash, session
from flask_login import LoginManager, login_user, logout_user, login_required, current_user
import json
import os
import logging
from datetime import datetime
from functools import wraps
from typing import Optional
from models.database import Database
from controllers.api_controller import APIController

# Import MontyDB models for enhanced features
try:
    from database.config import initialize_database, get_collection_stats, get_database
    from models.star_model_db import StarModelDB
    from models.nation_model_db import NationModelDB
    from models.trade_route_model_db import TradeRouteModelDB
    from models.exoplanet_model_db import ExoplanetModelDB
    MONTYDB_AVAILABLE = True
except ImportError:
    MONTYDB_AVAILABLE = False

# Import authentication
from auth import AuthManager, get_auth_config

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

app = Flask(__name__)

# Security configuration
auth_config = get_auth_config()
app.config.update(auth_config)

# Initialize Flask-Login
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'
login_manager.login_message = '🔒 Felgenland Security: Access to galactic data requires authentication.'
login_manager.login_message_category = 'info'

# Initialize authentication manager
auth_manager = AuthManager(app.config['SECRET_KEY'])

# Initialize database and controllers
db = Database()
api = APIController(db)

# Initialize enhanced models if MontyDB is available
star_model: Optional[StarModelDB] = None
nation_model: Optional[NationModelDB] = None
trade_model: Optional[TradeRouteModelDB] = None
exoplanet_model: Optional[ExoplanetModelDB] = None
exoplanet_db: Optional[Database] = None

@login_manager.user_loader
def load_user(user_id):
    """Load user for Flask-Login"""
    return auth_manager.get_user(user_id)

def api_auth_required(f):
    """Custom decorator for API authentication (supports both session and JWT)"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        # Check for JWT token in Authorization header
        auth_header = request.headers.get('Authorization')
        if auth_header and auth_header.startswith('Bearer '):
            token = auth_header.split(' ')[1]
            user = auth_manager.verify_jwt_token(token)
            if user:
                # Set current_user for the request
                session['_user_id'] = str(user.id)
                return f(*args, **kwargs)
        
        # Fall back to Flask-Login session authentication
        if current_user.is_authenticated:
            return f(*args, **kwargs)
        
        return jsonify({
            'error': 'Authentication required',
            'message': 'Please provide valid credentials via session login or JWT token'
        }), 401
    
    return decorated_function

def initialize_enhanced_features():
    """Initialize enhanced MontyDB features if available"""
    global star_model, nation_model, trade_model, exoplanet_model, exoplanet_db
    
    if not MONTYDB_AVAILABLE:
        logger.info("MontyDB features not available - using basic mode")
        return False
    
    logger.info("🚀 Initializing enhanced features with MontyDB backend")
    
    # Initialize database
    if not initialize_database():
        logger.error("❌ Failed to initialize MontyDB")
        return False
    
    # Initialize models
    try:
        star_model = StarModelDB()
        nation_model = NationModelDB()
        trade_model = TradeRouteModelDB()
        exoplanet_model = ExoplanetModelDB()
        
        # Initialize exoplanet database with working data
        exoplanet_db = Database()
        
        # Log statistics
        stats = get_collection_stats()
        logger.info(f"📊 Enhanced database loaded: {stats}")
        logger.info(f"📊 Exoplanet stats: {exoplanet_db.get_stats()}")
        
        return True
        
    except Exception as e:
        logger.error(f"❌ Failed to initialize enhanced models: {e}")
        return False

# Authentication routes
@app.route('/login', methods=['GET', 'POST'])
def login():
    """Login page and handler"""
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        remember = bool(request.form.get('remember'))
        
        user = auth_manager.authenticate_user(username, password)
        if user:
            login_user(user, remember=remember)
            logger.info(f"🔓 User {username} authenticated successfully")
            
            # Redirect to next page or dashboard
            next_page = request.args.get('next')
            return redirect(next_page) if next_page else redirect(url_for('index'))
        else:
            logger.warning(f"🔒 Failed authentication attempt for user: {username}")
            flash('Invalid credentials. Access denied.', 'danger')
    
    return render_template('login.html')

@app.route('/logout')
@login_required
def logout():
    """Logout handler"""
    username = current_user.username if current_user.is_authenticated else 'Unknown'
    logout_user()
    logger.info(f"🔓 User {username} logged out")
    flash('Logged out successfully. Safe travels!', 'success')
    return redirect(url_for('login'))

@app.route('/api/auth/token', methods=['POST'])
@login_required
def get_auth_token():
    """Generate JWT token for API access"""
    try:
        expires_hours = request.json.get('expires_hours', 24) if request.is_json else 24
        token = auth_manager.generate_jwt_token(current_user, expires_hours)
        
        logger.info(f"🎫 JWT token generated for user {current_user.username}")
        
        return jsonify({
            'success': True,
            'token': token,
            'expires_in_hours': expires_hours,
            'user': current_user.username
        })
        
    except Exception as e:
        logger.error(f"❌ Error generating token: {e}")
        return jsonify({'error': 'Failed to generate token'}), 500

@app.route('/')
@login_required
def index():
    """Main starmap page - requires authentication"""
    logger.info(f"🌟 Starmap accessed by user: {current_user.username}")
    return render_template('starmap.html', user=current_user)

@app.route('/api/stars')
@api_auth_required
def get_stars():
    """Get star data with optional filtering - protected"""
    try:
        # Use enhanced star model if available, otherwise fallback to basic
        if star_model:
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
            
            logger.info(f"🔐 API: Served {len(client_stars)} stars to {current_user.username if current_user.is_authenticated else 'JWT user'}")
            return jsonify({
                'success': True,
                'data': client_stars,
                'count': len(client_stars)
            })
        else:
            # Fallback to basic API controller
            limit = request.args.get('limit', 1000, type=int)
            mag_limit = request.args.get('mag_limit', 8.0, type=float)
            spectral_type = request.args.get('spectral_type', '')
            
            result = api.get_stars(limit, mag_limit, spectral_type)
            logger.info(f"🔐 API: Served stars via basic controller to authenticated user")
            return result
            
    except Exception as e:
        logger.error(f"Error in /api/stars: {e}")
        return jsonify({'error': str(e)}), 500

@app.route('/api/star/<int:star_id>')
@api_auth_required
def get_star_details(star_id):
    """Get detailed information for a specific star - protected"""
    try:
        if star_model and trade_model:
            star = star_model.get_star_by_id(star_id)
            if not star:
                return jsonify({'error': 'Star not found'}), 404
            
            # Get connected trade routes
            trade_routes = trade_model.get_routes_by_star(star_id)
            
            # Format detailed response
            detail = {
                'success': True,
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
            
            logger.info(f"🔐 API: Served star details for {star_id}")
            return jsonify(detail)
        else:
            # Fallback to basic API controller
            result = api.get_star_details(star_id)
            logger.info(f"🔐 API: Served star details via basic controller")
            return result
            
    except Exception as e:
        logger.error(f"Error in /api/star/{star_id}: {e}")
        return jsonify({'error': str(e)}), 500

@app.route('/api/nations')
@api_auth_required
def get_nations():
    """Get all nations - protected"""
    try:
        if nation_model:
            nations = nation_model.get_nations()
            logger.info(f"🔐 API: Served {len(nations)} nations to authenticated user")
            return jsonify({
                'success': True,
                'data': nations,
                'count': len(nations)
            })
        else:
            # Fallback to basic API controller
            result = api.get_nations()
            logger.info(f"🔐 API: Served nations via basic controller")
            return result
            
    except Exception as e:
        logger.error(f"Error in /api/nations: {e}")
        return jsonify({'error': str(e)}), 500

@app.route('/api/trade-routes')
@api_auth_required
def get_trade_routes():
    """Get all trade routes - protected"""
    try:
        if trade_model:
            routes = trade_model.get_trade_routes()
            logger.info(f"🔐 API: Served {len(routes)} trade routes")
            return jsonify({
                'success': True,
                'data': routes,
                'count': len(routes)
            })
        else:
            # Fallback to basic API controller
            result = api.get_trade_routes()
            logger.info(f"🔐 API: Served trade routes via basic controller")
            return result
            
    except Exception as e:
        logger.error(f"Error in /api/trade-routes: {e}")
        return jsonify({'error': str(e)}), 500

@app.route('/api/search')
@api_auth_required
def search_stars():
    """Search stars by name - protected"""
    try:
        query = request.args.get('q', '').strip()
        limit = min(int(request.args.get('limit', 20)), 100)
        spectral_type = request.args.get('spectral_type', '').strip()
        
        if star_model:
            if not query:
                return jsonify({'success': True, 'data': [], 'count': 0})
            
            results = star_model.search_stars(query, limit)
            
            if spectral_type:
                results = [star for star in results 
                          if star['physical_properties']['spectral_class'].startswith(spectral_type)]
            
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
            
            logger.info(f"🔐 API: Search '{query}' returned {len(client_results)} results")
            return jsonify({
                'success': True,
                'data': client_results,
                'count': len(client_results)
            })
        else:
            # Fallback to basic API controller
            result = api.search_stars(query, limit)
            logger.info(f"🔐 API: Search via basic controller")
            return result
            
    except Exception as e:
        logger.error(f"Error in /api/search: {e}")
        return jsonify({'error': str(e)}), 500

@app.route('/api/stats')
def get_stats():
    """Get application statistics - public for monitoring"""
    try:
        if MONTYDB_AVAILABLE and get_database:
            stats = {
                'database': get_collection_stats(),
                'timestamp': datetime.now().isoformat(),
                'authenticated': current_user.is_authenticated if hasattr(current_user, 'is_authenticated') else False
            }
            
            # Add detailed stats only for authenticated users
            if current_user.is_authenticated and nation_model and trade_model and star_model:
                stats.update({
                    'nations': nation_model.get_nation_stats(),
                    'trade_network': trade_model.get_trade_network_analysis(),
                    'performance': {
                        'star_cache': star_model.get_cache_stats(),
                        'nation_cache': nation_model.get_cache_stats(),
                        'trade_cache': trade_model.get_cache_stats()
                    }
                })
            
            return jsonify({
                'success': True,
                'data': stats
            })
        else:
            # Fallback to basic API controller
            return api.get_stats()
            
    except Exception as e:
        logger.error(f"Error in /api/stats: {e}")
        return jsonify({'error': str(e)}), 500

# Public utility endpoints (keep some public for basic functionality)
@app.route('/api/stellar-regions')
def get_stellar_regions():
    """Get stellar regions data - public for display"""
    try:
        if MONTYDB_AVAILABLE and get_database:
            db_conn = get_database()
            if not db_conn:
                return jsonify({'error': 'Database not initialized'}), 500
                
            stellar_regions = db_conn.stellar_regions
            regions = list(stellar_regions.find())
            
            return jsonify({
                'success': True,
                'data': regions,
                'count': len(regions)
            })
        else:
            # Fallback to basic API controller
            return api.get_stellar_regions()
            
    except Exception as e:
        logger.error(f"Error in /api/stellar-regions: {e}")
        return jsonify({'error': str(e)}), 500

@app.route('/api/galactic-directions')
def get_galactic_directions():
    """Get galactic directions data - public for navigation"""
    try:
        import math
        
        def ra_dec_to_xyz(ra, dec, distance):
            ra_rad = math.radians(ra)
            dec_rad = math.radians(dec)
            x = distance * math.cos(dec_rad) * math.cos(ra_rad)
            y = distance * math.cos(dec_rad) * math.sin(ra_rad)
            z = distance * math.sin(dec_rad)
            return [x, y, z]
        
        directions = [
            {
                'name': 'Galactic Center',
                'position': ra_dec_to_xyz(266.4, -29.0, 25),
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
                'position': [0.0, 0.0, 0.0],
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

@app.route('/api/fictional-exoplanets')
def get_fictional_exoplanets():
    """Get fictional exoplanets data - public"""
    try:
        if exoplanet_db:
            fictional_exoplanets = exoplanet_db.get_fictional_exoplanets()
            logger.info(f"🌍 API: Served {len(fictional_exoplanets)} fictional exoplanets (including Sol system)")
            
            return jsonify({
                'success': True,
                'data': fictional_exoplanets,
                'count': len(fictional_exoplanets)
            })
        else:
            # Fallback to basic API controller
            return api.get_fictional_exoplanets()
            
    except Exception as e:
        logger.error(f"Error in /api/fictional-exoplanets: {e}")
        return jsonify({'error': str(e)}), 500

@app.route('/api/exoplanets')
def get_exoplanets():
    """Get exoplanets data - public"""
    try:
        if exoplanet_db:
            exoplanets = exoplanet_db.get_exoplanets()
            logger.info(f"📡 API: Served {len(exoplanets)} real exoplanets")
            
            return jsonify({
                'success': True,
                'data': exoplanets,
                'count': len(exoplanets)
            })
        else:
            # Fallback to basic API controller
            return api.get_exoplanets()
            
    except Exception as e:
        logger.error(f"Error in /api/exoplanets: {e}")
        return jsonify({'error': str(e)}), 500

# Enhanced API endpoints (protected)
@app.route('/api/stars/nation/<nation_id>')
@api_auth_required
def api_stars_by_nation(nation_id):
    """Get all stars controlled by a nation - protected"""
    try:
        if not star_model:
            return jsonify({'error': 'Star model not initialized'}), 500
            
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
        
        logger.info(f"🔐 API: Served {len(client_stars)} stars for nation {nation_id}")
        return jsonify({
            'success': True,
            'data': client_stars,
            'count': len(client_stars)
        })
        
    except Exception as e:
        logger.error(f"Error in /api/stars/nation/{nation_id}: {e}")
        return jsonify({'error': str(e)}), 500

@app.route('/api/network-analysis')
@api_auth_required
def api_network_analysis():
    """Get trade network analysis - protected"""
    try:
        if not trade_model:
            return jsonify({'error': 'Trade model not initialized'}), 500
            
        analysis = trade_model.get_trade_network_analysis()
        logger.info(f"🔐 API: Served network analysis")
        return jsonify({
            'success': True,
            'data': analysis
        })
        
    except Exception as e:
        logger.error(f"Error in /api/network-analysis: {e}")
        return jsonify({'error': str(e)}), 500

# Fictional entity management endpoints (protected)
@app.route('/api/fictional/stars', methods=['GET'])
@api_auth_required
def get_fictional_stars():
    """Get all fictional stars - protected"""
    return api.get_fictional_stars()

@app.route('/api/fictional/stars', methods=['POST'])
@api_auth_required
def add_fictional_star():
    """Add a new fictional star - protected"""
    return api.add_fictional_star()

@app.route('/api/fictional/stars/<int:star_id>', methods=['DELETE'])
@api_auth_required
def delete_fictional_star(star_id):
    """Delete a fictional star - protected"""
    return api.delete_fictional_star(star_id)

@app.route('/api/fictional/exoplanets', methods=['GET'])
@api_auth_required
def get_fictional_exoplanets_new():
    """Get all fictional exoplanets - protected"""
    return api.get_fictional_exoplanets()

@app.route('/api/fictional/exoplanets', methods=['POST'])
@api_auth_required
def add_fictional_exoplanet():
    """Add a new fictional exoplanet - protected"""
    return api.add_fictional_exoplanet()

@app.route('/api/fictional/nations', methods=['GET'])
@api_auth_required
def get_fictional_nations():
    """Get all fictional nations - protected"""
    return api.get_fictional_nations()

@app.route('/api/fictional/nations', methods=['POST'])
@api_auth_required
def add_fictional_nation():
    """Add a new fictional nation - protected"""
    return api.add_fictional_nation()

@app.route('/api/fictional/nations/<string:nation_id>', methods=['DELETE'])
@api_auth_required
def delete_fictional_nation(nation_id):
    """Delete a fictional nation - protected"""
    return api.delete_fictional_nation(nation_id)

@app.route('/api/fictional/trade-routes', methods=['GET'])
@api_auth_required
def get_fictional_trade_routes():
    """Get all fictional trade routes - protected"""
    return api.get_fictional_trade_routes()

@app.route('/api/fictional/trade-routes', methods=['POST'])
@api_auth_required
def add_fictional_trade_route():
    """Add a new fictional trade route - protected"""
    return api.add_fictional_trade_route()

@app.route('/api/fictional/trade-routes/<string:route_id>', methods=['DELETE'])
@api_auth_required
def delete_fictional_trade_route(route_id):
    """Delete a fictional trade route - protected"""
    return api.delete_fictional_trade_route(route_id)

@app.errorhandler(401)
def unauthorized(error):
    return jsonify({
        'error': 'Unauthorized',
        'message': 'Felgenland Security: Authentication required for galactic data access'
    }), 401

@app.errorhandler(404)
def not_found(error):
    return jsonify({'success': False, 'error': 'Endpoint not found'}), 404

@app.errorhandler(500)
def server_error(error):
    logger.error(f"Internal server error: {error}")
    return jsonify({'success': False, 'error': 'Internal server error'}), 500

if __name__ == '__main__':
    print("🚀 Starting Starmap - Felgenland Saga")
    print(f"📊 Database Stats: {db.get_stats()}")
    
    # Initialize enhanced features if available
    enhanced_features = initialize_enhanced_features()
    if enhanced_features:
        logger.info("✅ Enhanced features initialized with MontyDB")
        logger.info("🔐 Authentication: Flask-Login + JWT tokens")
        logger.info("👤 Default users: admin, starmap_admin")
    else:
        logger.info("✅ Basic features initialized")
        logger.info("🔐 Authentication: Flask-Login (MontyDB features unavailable)")
    
    print("🌐 Access at: http://localhost:8080")
    print("🔑 Login required - see auth.py for default credentials")
    app.run(host='0.0.0.0', port=8080, debug=True)