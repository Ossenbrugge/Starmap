#!/usr/bin/env python3
"""
Starmap Application - MVC Refactored Version
Interactive 3D starmap for science fiction novels with clean MVC architecture
"""

from flask import Flask, request
from models.star_model import StarModel
from models.planet_model import PlanetModel
from models.nation_model import NationModel
from views.api_views import ApiView, TemplateView
from controllers.star_controller import StarController
from controllers.planet_controller import PlanetController
from controllers.nation_controller import NationController
from controllers.map_controller import MapController


class StarmapApplication:
    """Main application class using MVC architecture"""
    
    def __init__(self):
        self.app = Flask(__name__)
        self._initialize_mvc_components()
        self._register_routes()
    
    def _initialize_mvc_components(self):
        """Initialize Models, Views, and Controllers"""
        print("🏗️  Initializing MVC components...")
        
        # Initialize Models
        print("📊 Loading models...")
        self.star_model = StarModel()
        self.planet_model = PlanetModel()
        self.nation_model = NationModel()
        
        # Add planets to star model for compatibility
        self._integrate_planet_data()
        
        # Initialize Views
        self.api_view = ApiView()
        self.template_view = TemplateView()
        
        # Initialize Controllers
        print("🎮 Setting up controllers...")
        self.star_controller = StarController(self.star_model, self.api_view)
        self.planet_controller = PlanetController(
            self.planet_model, self.star_model, self.api_view
        )
        self.nation_controller = NationController(
            self.nation_model, self.star_model, self.api_view
        )
        self.map_controller = MapController(
            self.star_model, self.planet_model, self.api_view
        )
        
        print("✅ MVC components initialized successfully")
    
    def _integrate_planet_data(self):
        """Add planetary data to the star model for backward compatibility"""
        if self.star_model.data is not None and not self.star_model.data.empty:
            # Add planets column to star data
            self.star_model.data['planets'] = self.star_model.data['id'].map(
                lambda star_id: self.planet_model.get_planets_for_star(star_id)
            ).fillna('').apply(list)
    
    def _register_routes(self):
        """Register all application routes"""
        print("🛣️  Registering routes...")
        
        # Main page route
        self.app.route('/')(self._handle_index)
        
        # Star routes
        self.app.route('/api/stars')(self.star_controller.get_stars)
        self.app.route('/api/star/<int:star_id>')(self.star_controller.get_star_details)
        self.app.route('/api/search')(self.star_controller.search_stars)
        self.app.route('/api/distance')(self.star_controller.calculate_distance)
        self.app.route('/api/spectral-types')(self.star_controller.get_spectral_types)
        self.app.route('/export/csv')(self.star_controller.export_csv)
        
        # Planet routes
        self.app.route('/api/planet/add', methods=['POST'])(self.planet_controller.add_planet)
        self.app.route('/api/systems')(self.planet_controller.get_planetary_systems)
        self.app.route('/api/system/<int:star_id>')(self.planet_controller.get_star_system)
        
        # Nation routes
        self.app.route('/api/nations')(self.nation_controller.get_nations)
        self.app.route('/api/nation/<nation_id>')(self.nation_controller.get_nation_details)
        self.app.route('/api/trade-routes')(self.nation_controller.get_trade_routes)
        
        # Map routes
        self.app.route('/api/galactic-directions')(self.map_controller.get_galactic_directions)
        
        # Additional API routes for enhanced functionality
        self._register_extended_routes()
        
        print("✅ Routes registered successfully")
    
    def _register_extended_routes(self):
        """Register additional routes for extended functionality"""
        
        # Extended star routes
        @self.app.route('/api/stars/brightest')
        def get_brightest_stars():
            return self.star_controller.get_brightest_stars()
        
        @self.app.route('/api/stars/nearest')
        def get_nearest_stars():
            return self.star_controller.get_nearest_stars()
        
        @self.app.route('/api/stars/constellation/<constellation>')
        def get_stars_by_constellation(constellation):
            return self.star_controller.get_stars_by_constellation(constellation)
        
        # Extended planet routes
        @self.app.route('/api/planets/habitable')
        def get_habitable_planets():
            return self.planet_controller.get_habitable_planets()
        
        @self.app.route('/api/planets/confirmed')
        def get_confirmed_exoplanets():
            return self.planet_controller.get_confirmed_exoplanets()
        
        @self.app.route('/api/planets/statistics')
        def get_planet_statistics():
            return self.planet_controller.get_planet_statistics()
        
        @self.app.route('/api/planets/type/<planet_type>')
        def get_systems_by_planet_type(planet_type):
            return self.planet_controller.get_systems_by_planet_type(planet_type)
        
        # Extended nation routes
        @self.app.route('/api/nations/largest')
        def get_largest_nations():
            return self.nation_controller.get_largest_nations()
        
        @self.app.route('/api/nations/government/<government_type>')
        def get_nations_by_government_type(government_type):
            return self.nation_controller.get_nations_by_government_type(government_type)
        
        @self.app.route('/api/nation/<nation_id>/routes')
        def get_nation_trade_routes(nation_id):
            return self.nation_controller.get_nation_trade_routes(nation_id)
        
        @self.app.route('/api/nation/<nation_id>/stats')
        def get_nation_statistics(nation_id):
            return self.nation_controller.get_nation_statistics(nation_id)
        
        @self.app.route('/api/trade-route/<int:star1_id>/<int:star2_id>')
        def get_trade_route_between_stars(star1_id, star2_id):
            return self.nation_controller.get_trade_route_between_stars(star1_id, star2_id)
        
        # Map analysis routes
        @self.app.route('/api/map/bounds')
        def get_map_bounds():
            return self.map_controller.get_map_bounds()
        
        @self.app.route('/api/map/density')
        def get_star_density_map():
            return self.map_controller.get_star_density_map()
        
        @self.app.route('/api/map/constellations')
        def get_constellation_boundaries():
            return self.map_controller.get_constellation_boundaries()
        
        @self.app.route('/api/map/coordinate-info')
        def get_coordinate_system_info():
            return self.map_controller.get_coordinate_system_info()
        
        @self.app.route('/api/map/settings')
        def get_visualization_settings():
            return self.map_controller.get_visualization_settings()
    
    def _handle_index(self):
        """Handle main page request"""
        return self.map_controller.render_main_page()
    
    def get_app(self):
        """Get the Flask application instance"""
        return self.app
    
    def get_models(self):
        """Get all model instances for testing"""
        return {
            'star_model': self.star_model,
            'planet_model': self.planet_model,
            'nation_model': self.nation_model
        }
    
    def get_controllers(self):
        """Get all controller instances for testing"""
        return {
            'star_controller': self.star_controller,
            'planet_controller': self.planet_controller,
            'nation_controller': self.nation_controller,
            'map_controller': self.map_controller
        }


def create_app():
    """Application factory function"""
    starmap_app = StarmapApplication()
    return starmap_app.get_app()


# For backward compatibility and direct execution
app = create_app()


if __name__ == '__main__':
    print("🌟 Starting Starmap Application (MVC Architecture)")
    
    # Get the StarmapApplication instance to check data loading
    starmap_instance = StarmapApplication()
    models = starmap_instance.get_models()
    
    # Check data loading status
    star_data_loaded = (models['star_model'].data is not None and 
                       not models['star_model'].data.empty)
    planet_data_loaded = len(models['planet_model'].data) > 0
    nation_data_loaded = len(models['nation_model'].data) > 0
    
    print(f"📊 Star data loaded: {'✅' if star_data_loaded else '❌'}")
    print(f"🪐 Planet data loaded: {'✅' if planet_data_loaded else '❌'}")
    print(f"🏛️  Nation data loaded: {'✅' if nation_data_loaded else '❌'}")
    
    if star_data_loaded:
        star_count = len(models['star_model'].data)
        print(f"   └─ {star_count} stars loaded")
    
    if planet_data_loaded:
        system_count = len([s for s in models['planet_model'].data.values() if s])
        total_planets = sum(len(planets) for planets in models['planet_model'].data.values())
        print(f"   └─ {system_count} planetary systems with {total_planets} planets")
    
    if nation_data_loaded:
        nation_count = len(models['nation_model'].data)
        print(f"   └─ {nation_count} nations loaded")
    
    print("\n🌐 Server Information:")
    print("   Local:  http://localhost:8080")
    print("   LAN:    http://[your-ip]:8080")
    print("\n🎮 API Endpoints Available:")
    print("   /api/stars - Get star data")
    print("   /api/search - Search stars")
    print("   /api/systems - Planetary systems")
    print("   /api/nations - Political data")
    print("   /api/map/settings - Visualization settings")
    print("\n🚀 Press Ctrl+C to stop")
    
    app.run(host='0.0.0.0', port=8080, debug=True)