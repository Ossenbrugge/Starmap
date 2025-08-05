"""
Starmap Application with MontyDB Backend and Security
Enhanced version with Flask-Login authentication
"""

from flask import Flask, render_template, request, jsonify, redirect, url_for, flash, session
from flask_login import LoginManager, login_user, logout_user, login_required, current_user
import logging
from datetime import datetime
from functools import wraps
from typing import Optional

# Import MontyDB models
from database.config import initialize_database, get_collection_stats, get_database
from models.star_model_db import StarModelDB
from models.nation_model_db import NationModelDB
from models.trade_route_model_db import TradeRouteModelDB
from models.exoplanet_model_db import ExoplanetModelDB
# Import regular database for exoplanet data
from models.database import Database

# Import authentication
from auth import AuthManager, get_auth_config

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('starmap_secure.log'),
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

# Initialize models
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

def initialize_app():
    """Initialize the application with MontyDB"""
    global star_model, nation_model, trade_model, exoplanet_model, exoplanet_db
    
    logger.info("🚀 Starting Secure Starmap with MontyDB backend")
    
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
        logger.info(f"📊 Database loaded: {stats}")
        logger.info(f"📊 Exoplanet stats: {exoplanet_db.get_stats()}")
        
        return True
        
    except Exception as e:
        logger.error(f"❌ Failed to initialize models: {e}")
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
            return redirect(next_page) if next_page else redirect(url_for('starmap'))
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

# Protected routes
@app.route('/')
@login_required
def starmap():
    """Main starmap view - requires authentication"""
    logger.info(f"🌟 Starmap accessed by user: {current_user.username}")
    return render_template('starmap.html', user=current_user)

# Protected API endpoints
@app.route('/api/stars')
@api_auth_required
def api_stars():
    """Enhanced star data API - protected"""
    try:
        if not star_model:
            return jsonify({'error': 'Star model not initialized'}), 500
            
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
        
        logger.info(f"🔐 API: Served {len(client_stars)} stars to {current_user.username if current_user.is_authenticated else 'JWT user'}")
        return jsonify({
            'success': True,
            'data': client_stars,
            'count': len(client_stars)
        })
        
    except Exception as e:
        logger.error(f"Error in /api/stars: {e}")
        return jsonify({'error': str(e)}), 500

@app.route('/api/nations')
@api_auth_required
def api_nations():
    """Get all nations - protected"""
    try:
        if not nation_model:
            return jsonify({'error': 'Nation model not initialized'}), 500
            
        nations = nation_model.get_nations()
        logger.info(f"🔐 API: Served {len(nations)} nations to authenticated user")
        return jsonify({
            'success': True,
            'data': nations,
            'count': len(nations)
        })
        
    except Exception as e:
        logger.error(f"Error in /api/nations: {e}")
        return jsonify({'error': str(e)}), 500

# Keep some endpoints public for basic functionality
@app.route('/api/stats')
def api_stats():
    """Get comprehensive database statistics - public for monitoring"""
    try:
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
        
    except Exception as e:
        logger.error(f"Error in /api/stats: {e}")
        return jsonify({'error': str(e)}), 500

# Additional protected endpoints
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

@app.route('/api/search')
@api_auth_required
def api_search():
    """Enhanced search API - protected"""
    try:
        query = request.args.get('q', '').strip()
        limit = min(int(request.args.get('limit', 20)), 100)
        spectral_type = request.args.get('spectral_type', '').strip()
        
        if not star_model:
            return jsonify({'error': 'Star model not initialized'}), 500
            
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
        
    except Exception as e:
        logger.error(f"Error in /api/search: {e}")
        return jsonify({'error': str(e)}), 500

# Star details endpoint
@app.route('/api/star/<int:star_id>')
@api_auth_required
def api_star_detail(star_id):
    """Get detailed information about a specific star - protected"""
    try:
        if not star_model or not trade_model:
            return jsonify({'error': 'Models not initialized'}), 500
            
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
        
    except Exception as e:
        logger.error(f"Error in /api/star/{star_id}: {e}")
        return jsonify({'error': str(e)}), 500

# Copy remaining endpoints with protection
@app.route('/api/trade-routes')
@api_auth_required
def api_trade_routes():
    """Get all trade routes - protected"""
    try:
        if not trade_model:
            return jsonify({'error': 'Trade model not initialized'}), 500
            
        routes = trade_model.get_trade_routes()
        logger.info(f"🔐 API: Served {len(routes)} trade routes")
        return jsonify({
            'success': True,
            'data': routes,
            'count': len(routes)
        })
        
    except Exception as e:
        logger.error(f"Error in /api/trade-routes: {e}")
        return jsonify({'error': str(e)}), 500

# Exoplanet endpoints (public for now, can be protected if needed)
@app.route('/api/exoplanets')
def api_exoplanets():
    """Get all real exoplanets - public"""
    try:
        if not exoplanet_db:
            return jsonify({'success': True, 'data': [], 'count': 0})
            
        exoplanets = exoplanet_db.get_exoplanets()
        logger.info(f"📡 API: Served {len(exoplanets)} real exoplanets")
        
        return jsonify({
            'success': True,
            'data': exoplanets,
            'count': len(exoplanets)
        })
        
    except Exception as e:
        logger.error(f"Error in /api/exoplanets: {e}")
        return jsonify({'error': str(e)}), 500

@app.route('/api/fictional-exoplanets')
def api_fictional_exoplanets():
    """Get all fictional exoplanets (including Sol system) - public"""
    try:
        if not exoplanet_db:
            return jsonify({'success': True, 'data': [], 'count': 0})
            
        fictional_exoplanets = exoplanet_db.get_fictional_exoplanets()
        logger.info(f"🌍 API: Served {len(fictional_exoplanets)} fictional exoplanets (including Sol system)")
        
        return jsonify({
            'success': True,
            'data': fictional_exoplanets,
            'count': len(fictional_exoplanets)
        })
        
    except Exception as e:
        logger.error(f"Error in /api/fictional-exoplanets: {e}")
        return jsonify({'error': str(e)}), 500

# Keep utility endpoints (add more as needed)
@app.route('/api/stellar-regions')
def api_stellar_regions():
    """Get all stellar regions - public for display"""
    try:
        db = get_database()
        if not db:
            return jsonify({'error': 'Database not initialized'}), 500
            
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

@app.errorhandler(401)
def unauthorized(error):
    return jsonify({
        'error': 'Unauthorized',
        'message': 'Felgenland Security: Authentication required for galactic data access'
    }), 401

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
    
    logger.info("✅ Secure Starmap application ready")
    logger.info("🔐 Authentication: Flask-Login + JWT tokens")
    logger.info("👤 Default users: admin, starmap_admin")
    logger.info("🌐 Starting Flask server...")
    
    # Run Flask app
    app.run(
        host='0.0.0.0',
        port=5001,
        debug=True,
        use_reloader=False
    )