#!/usr/bin/env python3
"""
Starmap Application - MontyDB Version
Interactive 3D starmap with MontyDB backend for enhanced performance and scalability
"""

import os
import sys
from flask import Flask, request, jsonify, render_template, send_from_directory

# Add database path
sys.path.append('database')
from database.config import initialize_database, get_database, close_database

# Import MontyDB models
from models.star_model_db import StarModelDB
from models.nation_model_db import NationModelDB
from models.trade_route_model_db import TradeRouteModelDB
from models.exoplanet_model_db import ExoplanetModelDB

# Import existing views (will work with new models)
from views.api_views import ApiView, TemplateView


class StarmapMontyDBApplication:
    """Main application class using MontyDB backend"""
    
    def __init__(self):
        self.app = Flask(__name__)
        self.app.secret_key = 'starmap_secret_key_2024'
        
        # Initialize database
        self._initialize_database()
        
        # Initialize models
        self._initialize_models()
        
        # Initialize views
        self._initialize_views()
        
        # Register routes
        self._register_routes()
        
        # Register error handlers
        self._register_error_handlers()
    
    def _initialize_database(self):
        """Initialize MontyDB connection"""
        print("🔌 Initializing MontyDB connection...")
        
        if not initialize_database():
            print("❌ Failed to initialize database!")
            sys.exit(1)
        
        self.db = get_database()
        print(f"✅ Connected to MontyDB with {self.db.list_collection_names()} collections")
    
    def _initialize_models(self):
        """Initialize MontyDB models"""
        print("📊 Initializing MontyDB models...")
        
        self.star_model = StarModelDB()
        self.nation_model = NationModelDB()
        self.trade_route_model = TradeRouteModelDB()
        self.exoplanet_model = ExoplanetModelDB()
        
        print("✅ Models initialized successfully")
    
    def _initialize_views(self):
        """Initialize views"""
        self.api_view = ApiView()
        self.template_view = TemplateView()
    
    def _register_routes(self):
        """Register application routes"""
        print("🛣️  Registering application routes...")
        
        # Main application route
        @self.app.route('/')
        def index():
            return render_template('starmap.html')
        
        # Static files
        @self.app.route('/static/<path:filename>')
        def serve_static(filename):
            return send_from_directory('static', filename)
        
        # API Routes - Stars
        @self.app.route('/api/stars')
        def get_stars():
            try:
                # Get query parameters
                mag_limit = request.args.get('mag_limit', 6.0, type=float)
                count_limit = request.args.get('count_limit', 1000, type=int)
                spectral_filter = request.args.get('spectral_type')
                
                # Get stars from database
                stars = self.star_model.get_stars_for_display(
                    mag_limit=mag_limit,
                    count_limit=count_limit,
                    spectral_filter=spectral_filter
                )
                
                return self.api_view.success_response(stars, {
                    'total_count': len(stars),
                    'mag_limit': mag_limit,
                    'count_limit': count_limit,
                    'spectral_filter': spectral_filter
                })
                
            except Exception as e:
                return self.api_view.error_response(str(e), 500)
        
        @self.app.route('/api/star/<int:star_id>')
        def get_star_details(star_id):
            try:
                star = self.star_model.get_star_details(star_id)
                if not star:
                    return self.api_view.error_response(f"Star {star_id} not found", 404)
                
                return self.api_view.success_response(star)
                
            except Exception as e:
                return self.api_view.error_response(str(e), 500)
        
        @self.app.route('/api/search')
        def search_stars():
            try:
                query = request.args.get('q', '')
                spectral_type = request.args.get('spectral_type')
                limit = request.args.get('limit', 50, type=int)
                
                if not query and not spectral_type:
                    return self.api_view.error_response("Query or spectral type required", 400)
                
                results = self.star_model.search_stars(
                    query=query,
                    spectral_type=spectral_type,
                    limit=limit
                )
                
                return self.api_view.success_response(results, {
                    'query': query,
                    'spectral_type': spectral_type,
                    'result_count': len(results)
                })
                
            except Exception as e:
                return self.api_view.error_response(str(e), 500)
        
        @self.app.route('/api/distance')
        def calculate_distance():
            try:
                star1_id = request.args.get('star1', type=int)
                star2_id = request.args.get('star2', type=int)
                
                if not star1_id or not star2_id:
                    return self.api_view.error_response("Both star1 and star2 IDs required", 400)
                
                distance_data = self.star_model.calculate_distance(star1_id, star2_id)
                if not distance_data:
                    return self.api_view.error_response("Could not calculate distance", 404)
                
                return self.api_view.success_response(distance_data)
                
            except Exception as e:
                return self.api_view.error_response(str(e), 500)
        
        @self.app.route('/api/spectral-types')
        def get_spectral_types():
            try:
                spectral_types = self.star_model.get_spectral_types()
                return self.api_view.success_response(spectral_types)
                
            except Exception as e:
                return self.api_view.error_response(str(e), 500)
        
        # API Routes - Nations
        @self.app.route('/api/nations')
        def get_nations():
            try:
                nations = self.nation_model.get_all_nations()
                return self.api_view.success_response(nations)
                
            except Exception as e:
                return self.api_view.error_response(str(e), 500)
        
        @self.app.route('/api/nation/<nation_id>')
        def get_nation_details(nation_id):
            try:
                nation = self.nation_model.get_nation_details(nation_id)
                if not nation:
                    return self.api_view.error_response(f"Nation {nation_id} not found", 404)
                
                return self.api_view.success_response(nation)
                
            except Exception as e:
                return self.api_view.error_response(str(e), 500)
        
        @self.app.route('/api/nation/<nation_id>/territories')
        def get_nation_territories(nation_id):
            try:
                territories = self.nation_model.get_nation_territories(nation_id)
                return self.api_view.success_response(territories)
                
            except Exception as e:
                return self.api_view.error_response(str(e), 500)
        
        # API Routes - Trade Routes
        @self.app.route('/api/trade-routes')
        def get_trade_routes():
            try:
                route_type = request.args.get('type')
                nation_id = request.args.get('nation')
                
                if route_type:
                    routes = self.trade_route_model.get_routes_by_type(route_type)
                elif nation_id:
                    routes = self.trade_route_model.get_routes_by_nation(nation_id)
                else:
                    routes = self.trade_route_model.get_all_trade_routes()
                
                return self.api_view.success_response(routes)
                
            except Exception as e:
                return self.api_view.error_response(str(e), 500)
        
        @self.app.route('/api/trade-route/<route_id>')
        def get_trade_route_details(route_id):
            try:
                route = self.trade_route_model.get_route_details(route_id)
                if not route:
                    return self.api_view.error_response(f"Trade route {route_id} not found", 404)
                
                return self.api_view.success_response(route)
                
            except Exception as e:
                return self.api_view.error_response(str(e), 500)
        
        # API Routes - Statistics and Analytics
        @self.app.route('/api/stats/stars')
        def get_star_stats():
            try:
                stats = self.star_model.get_stats()
                return self.api_view.success_response(stats)
                
            except Exception as e:
                return self.api_view.error_response(str(e), 500)
        
        @self.app.route('/api/stats/nations')
        def get_nation_stats():
            try:
                stats = self.nation_model.get_nation_statistics()
                return self.api_view.success_response(stats)
                
            except Exception as e:
                return self.api_view.error_response(str(e), 500)
        
        @self.app.route('/api/stats/trade-routes')
        def get_trade_route_stats():
            try:
                stats = self.trade_route_model.get_route_statistics()
                return self.api_view.success_response(stats)
                
            except Exception as e:
                return self.api_view.error_response(str(e), 500)
        
        @self.app.route('/api/network-analysis')
        def get_network_analysis():
            try:
                analysis = self.trade_route_model.get_trade_network_analysis()
                return self.api_view.success_response(analysis)
                
            except Exception as e:
                return self.api_view.error_response(str(e), 500)
        
        # API Routes - Advanced Queries
        @self.app.route('/api/stars/region/<region_name>')
        def get_stars_by_region(region_name):
            try:
                limit = request.args.get('limit', type=int)
                stars = self.star_model.get_stars_by_region(region_name, limit)
                
                return self.api_view.success_response(stars, {
                    'region': region_name,
                    'star_count': len(stars)
                })
                
            except Exception as e:
                return self.api_view.error_response(str(e), 500)
        
        @self.app.route('/api/stars/nation/<nation_id>')
        def get_stars_by_nation(nation_id):
            try:
                limit = request.args.get('limit', type=int)
                stars = self.star_model.get_stars_by_nation(nation_id, limit)
                
                return self.api_view.success_response(stars, {
                    'nation_id': nation_id,
                    'star_count': len(stars)
                })
                
            except Exception as e:
                return self.api_view.error_response(str(e), 500)
        
        @self.app.route('/api/stars/habitable')
        def get_habitable_stars():
            try:
                min_score = request.args.get('min_score', 0.5, type=float)
                limit = request.args.get('limit', type=int)
                
                stars = self.star_model.get_habitable_stars(min_score, limit)
                
                return self.api_view.success_response(stars, {
                    'min_habitability_score': min_score,
                    'star_count': len(stars)
                })
                
            except Exception as e:
                return self.api_view.error_response(str(e), 500)
        
        # API Routes - Exoplanets
        @self.app.route('/api/exoplanets')
        def get_exoplanets():
            try:
                limit = request.args.get('limit', 50, type=int)
                method = request.args.get('method')
                habitable_only = request.args.get('habitable', 'false').lower() == 'true'
                
                if habitable_only:
                    exoplanets = self.exoplanet_model.get_habitable_planets(limit=limit)
                elif method:
                    exoplanets = self.exoplanet_model.get_planets_by_discovery_method(method, limit=limit)
                else:
                    exoplanets = self.exoplanet_model.get_recent_discoveries(limit=limit)
                
                return self.api_view.success_response(exoplanets)
                
            except Exception as e:
                return self.api_view.error_response(str(e), 500)
        
        @self.app.route('/api/star/<int:star_id>/exoplanets')
        def get_star_exoplanets(star_id):
            try:
                star = self.star_model.get_star_details(star_id)
                if not star:
                    return self.api_view.error_response(f"Star {star_id} not found", 404)
                
                # Get exoplanets from star data or by HIP ID lookup
                planets = star.get('planets', [])
                if not planets and star.get('catalog_data', {}).get('hip'):
                    hip_id = star['catalog_data']['hip']
                    planets = self.exoplanet_model.get_planets_by_hip_id(hip_id)
                
                return self.api_view.success_response(planets)
                
            except Exception as e:
                return self.api_view.error_response(str(e), 500)
        
        @self.app.route('/api/exoplanets/stats')
        def get_exoplanet_stats():
            try:
                stats = self.exoplanet_model.get_system_statistics()
                return self.api_view.success_response(stats)
                
            except Exception as e:
                return self.api_view.error_response(str(e), 500)
        
        @self.app.route('/api/exoplanets/search')
        def search_exoplanets():
            try:
                query = request.args.get('q', '')
                limit = request.args.get('limit', 50, type=int)
                
                if not query:
                    return self.api_view.error_response("Query parameter required", 400)
                
                results = self.exoplanet_model.search_planets(query, limit=limit)
                
                return self.api_view.success_response(results, {
                    'query': query,
                    'result_count': len(results)
                })
                
            except Exception as e:
                return self.api_view.error_response(str(e), 500)
        
        # Data Management Routes
        @self.app.route('/api/star/add', methods=['POST'])
        def add_star():
            try:
                star_data = request.get_json()
                if not star_data:
                    return self.api_view.error_response("No data provided", 400)
                
                star_id = self.star_model.add_star(star_data)
                return self.api_view.success_response({'star_id': star_id}, message="Star added successfully")
                
            except Exception as e:
                return self.api_view.error_response(str(e), 500)
        
        @self.app.route('/api/star/<int:star_id>/update', methods=['PUT'])
        def update_star(star_id):
            try:
                update_data = request.get_json()
                if not update_data:
                    return self.api_view.error_response("No data provided", 400)
                
                result = self.star_model.update_star(star_id, update_data)
                if result:
                    return self.api_view.success_response({'modified_count': result.modified_count}, message="Star updated successfully")
                else:
                    return self.api_view.error_response("No fields to update", 400)
                
            except Exception as e:
                return self.api_view.error_response(str(e), 500)
        
        # API Routes - Overlays and UI Features
        @self.app.route('/api/galactic-directions')
        def get_galactic_directions():
            try:
                distance = request.args.get('distance', 50, type=int)
                grid = request.args.get('grid', 'false').lower() == 'true'
                
                # Generate galactic directions data
                directions_data = {
                    'directions': [
                        {'name': 'Galactic North', 'x': 0, 'y': 0, 'z': distance, 'color': '#ff6b6b'},
                        {'name': 'Galactic South', 'x': 0, 'y': 0, 'z': -distance, 'color': '#4ecdc4'},
                        {'name': 'Galactic Center', 'x': 0, 'y': -distance, 'z': 0, 'color': '#45b7d1'},
                        {'name': 'Galactic Anticenter', 'x': 0, 'y': distance, 'z': 0, 'color': '#f39c12'}
                    ],
                    'grid_enabled': grid,
                    'distance': distance
                }
                
                return self.api_view.success_response(directions_data)
                
            except Exception as e:
                return self.api_view.error_response(str(e), 500)
        
        @self.app.route('/api/stellar-regions')
        def get_stellar_regions():
            try:
                # Generate octant regions extending from Sol (0,0,0) to map boundaries
                # Map extends roughly -95 to +95 in each direction
                map_extent = 95
                
                regions_data = [
                    {
                        'id': 'octant_ppp',
                        'name': 'Capella Region',
                        'short_name': 'Capella',
                        'description': 'Galactic region centered on Capella (magnitude 0.08), the brightest star in this octant. Coreward Spinward Above - The first galactic octant extending in positive X, Y, and Z directions from Sol.',
                        'type': 'octant',
                        'center_point': [map_extent/2, map_extent/2, map_extent/2],
                        'x_range': [0, map_extent],
                        'y_range': [0, map_extent],
                        'z_range': [0, map_extent],
                        'color_rgb': [255, 99, 132],
                        'brightest_star': 'Capella',
                        'brightest_star_id': 24549,
                        'brightest_star_magnitude': 0.08,
                        'octant_number': 1
                    },
                    {
                        'id': 'octant_ppn',
                        'name': 'Achernar Region',
                        'short_name': 'Achernar',
                        'description': 'Galactic region centered on Achernar (magnitude 0.45), the brightest star in this octant. Coreward Spinward Below - The fifth galactic octant extending in positive X and Y, negative Z directions from Sol.',
                        'type': 'octant',
                        'center_point': [map_extent/2, map_extent/2, -map_extent/2],
                        'x_range': [0, map_extent],
                        'y_range': [0, map_extent],
                        'z_range': [-map_extent, 0],
                        'color_rgb': [153, 102, 255],
                        'brightest_star': 'Achernar',
                        'brightest_star_id': 7574,
                        'brightest_star_magnitude': 0.45,
                        'octant_number': 5
                    },
                    {
                        'id': 'octant_pnp',
                        'name': 'Vega Region',
                        'short_name': 'Vega',
                        'description': 'Galactic region centered on Vega (magnitude 0.03), the brightest star in this octant. Coreward Anti-Spinward Above - The fourth galactic octant extending in positive X, negative Y, positive Z directions from Sol.',
                        'type': 'octant',
                        'center_point': [map_extent/2, -map_extent/2, map_extent/2],
                        'x_range': [0, map_extent],
                        'y_range': [-map_extent, 0],
                        'z_range': [0, map_extent],
                        'color_rgb': [75, 192, 192],
                        'brightest_star': 'Vega',
                        'brightest_star_id': 90979,
                        'brightest_star_magnitude': 0.03,
                        'octant_number': 4
                    },
                    {
                        'id': 'octant_pnn',
                        'name': 'Fomalhaut Region',
                        'short_name': 'Fomalhaut',
                        'description': 'Galactic region centered on Fomalhaut (magnitude 1.17), the brightest star in this octant. Coreward Anti-Spinward Below - The eighth galactic octant extending in positive X, negative Y and Z directions from Sol.',
                        'type': 'octant',
                        'center_point': [map_extent/2, -map_extent/2, -map_extent/2],
                        'x_range': [0, map_extent],
                        'y_range': [-map_extent, 0],
                        'z_range': [-map_extent, 0],
                        'color_rgb': [255, 99, 255],
                        'brightest_star': 'Fomalhaut',
                        'brightest_star_id': 113008,
                        'brightest_star_magnitude': 1.17,
                        'octant_number': 8
                    },
                    {
                        'id': 'octant_npp',
                        'name': 'Procyon Region',
                        'short_name': 'Procyon',
                        'description': 'Galactic region centered on Procyon (magnitude 0.40), the brightest star in this octant. Rimward Spinward Above - The second galactic octant extending in negative X, positive Y and Z directions from Sol.',
                        'type': 'octant',
                        'center_point': [-map_extent/2, map_extent/2, map_extent/2],
                        'x_range': [-map_extent, 0],
                        'y_range': [0, map_extent],
                        'z_range': [0, map_extent],
                        'color_rgb': [54, 162, 235],
                        'brightest_star': 'Procyon',
                        'brightest_star_id': 37173,
                        'brightest_star_magnitude': 0.4,
                        'octant_number': 2
                    },
                    {
                        'id': 'octant_npn',
                        'name': 'Sirius Region',
                        'short_name': 'Sirius',
                        'description': 'Galactic region centered on Sirius (magnitude -1.44), the brightest star in this octant. Rimward Spinward Below - The sixth galactic octant extending in negative X, positive Y, negative Z directions from Sol.',
                        'type': 'octant',
                        'center_point': [-map_extent/2, map_extent/2, -map_extent/2],
                        'x_range': [-map_extent, 0],
                        'y_range': [0, map_extent],
                        'z_range': [-map_extent, 0],
                        'color_rgb': [255, 159, 64],
                        'brightest_star': 'Sirius',
                        'brightest_star_id': 32263,
                        'brightest_star_magnitude': -1.44,
                        'octant_number': 6
                    },
                    {
                        'id': 'octant_nnp',
                        'name': 'Arcturus Region',
                        'short_name': 'Arcturus',
                        'description': 'Galactic region centered on Arcturus (magnitude -0.05), the brightest star in this octant. Rimward Anti-Spinward Above - The third galactic octant extending in negative X and Y, positive Z directions from Sol.',
                        'type': 'octant',
                        'center_point': [-map_extent/2, -map_extent/2, map_extent/2],
                        'x_range': [-map_extent, 0],
                        'y_range': [-map_extent, 0],
                        'z_range': [0, map_extent],
                        'color_rgb': [255, 205, 86],
                        'brightest_star': 'Arcturus',
                        'brightest_star_id': 69451,
                        'brightest_star_magnitude': -0.05,
                        'octant_number': 3
                    },
                    {
                        'id': 'octant_nnn',
                        'name': 'Rigil Kentaurus Region',
                        'short_name': 'Rigil Kentaurus',
                        'description': 'Galactic region centered on Rigil Kentaurus (magnitude -0.01), the brightest star in this octant. Rimward Anti-Spinward Below - The seventh galactic octant extending in negative X, Y, and Z directions from Sol.',
                        'type': 'octant',
                        'center_point': [-map_extent/2, -map_extent/2, -map_extent/2],
                        'x_range': [-map_extent, 0],
                        'y_range': [-map_extent, 0],
                        'z_range': [-map_extent, 0],
                        'color_rgb': [201, 203, 207],
                        'brightest_star': 'Rigil Kentaurus',
                        'brightest_star_id': 71456,
                        'brightest_star_magnitude': -0.01,
                        'octant_number': 7
                    }
                ]
                
                return self.api_view.success_response(regions_data)
                
            except Exception as e:
                return self.api_view.error_response(str(e), 500)
        
        print("✅ Routes registered successfully")
    
    def _register_error_handlers(self):
        """Register error handlers"""
        @self.app.errorhandler(404)
        def not_found(error):
            return self.api_view.error_response("Resource not found", 404)
        
        @self.app.errorhandler(500)
        def internal_error(error):
            return self.api_view.error_response("Internal server error", 500)
    
    def run(self, host='0.0.0.0', port=8080, debug=False):
        """Run the application"""
        try:
            print(f"🚀 Starting Starmap MontyDB Application on {host}:{port}")
            print(f"📊 Database collections: {self.db.list_collection_names()}")
            
            # Print some quick stats
            star_count = self.star_model.count_documents()
            nation_count = self.nation_model.count_documents()
            route_count = self.trade_route_model.count_documents()
            exoplanet_count = self.exoplanet_model.count_documents()
            
            print(f"⭐ Stars: {star_count}")
            print(f"🏛️  Nations: {nation_count}")
            print(f"🛣️  Trade routes: {route_count}")
            print(f"🪐 Exoplanets: {exoplanet_count}")
            print(f"🌐 Access URL: http://{host}:{port}")
            print("="*50)
            
            self.app.run(host=host, port=port, debug=debug)
            
        except KeyboardInterrupt:
            print("\n🛑 Application stopped by user")
        except Exception as e:
            print(f"❌ Application error: {e}")
        finally:
            self._cleanup()
    
    def _cleanup(self):
        """Cleanup resources"""
        print("🧹 Cleaning up resources...")
        
        # Clear model caches
        self.star_model.clear_cache()
        self.nation_model.clear_cache()
        self.trade_route_model.clear_cache()
        self.exoplanet_model.clear_cache()
        
        # Close database connection
        close_database()
        
        print("✅ Cleanup completed")


def main():
    """Main application entry point"""
    app = StarmapMontyDBApplication()
    app.run(debug=True)


if __name__ == "__main__":
    main()