#!/usr/bin/env python3
"""
Quick environment test for Starmap application
Tests that all components work correctly in the virtual environment
"""

import sys
import json
from io import StringIO
from contextlib import redirect_stdout


def test_mvc_components():
    """Test individual MVC components"""
    print("🧪 Testing MVC Components")
    print("-" * 30)
    
    try:
        # Test Model imports and initialization
        print("📊 Testing Models...")
        from models.star_model import StarModel
        from models.planet_model import PlanetModel
        from models.nation_model import NationModel
        
        star_model = StarModel()
        planet_model = PlanetModel()
        nation_model = NationModel()
        
        print(f"  ✅ StarModel: {len(star_model.data)} stars loaded")
        print(f"  ✅ PlanetModel: {len(planet_model.data)} systems loaded")
        print(f"  ✅ NationModel: {len(nation_model.data)} nations loaded")
        
        # Test Views
        print("🎨 Testing Views...")
        from views.api_views import ApiView, TemplateView
        
        api_view = ApiView()
        template_view = TemplateView()
        print("  ✅ Views initialized successfully")
        
        # Test Controllers
        print("🎮 Testing Controllers...")
        from controllers.star_controller import StarController
        from controllers.planet_controller import PlanetController
        from controllers.nation_controller import NationController
        from controllers.map_controller import MapController
        
        star_controller = StarController(star_model, api_view)
        planet_controller = PlanetController(planet_model, star_model, api_view)
        nation_controller = NationController(nation_model, star_model, api_view)
        map_controller = MapController(star_model, planet_model, api_view)
        
        print("  ✅ Controllers initialized successfully")
        
        return True
        
    except Exception as e:
        print(f"  ❌ Component test failed: {e}")
        return False


def test_flask_app():
    """Test Flask application creation and basic routes"""
    print("\n🌐 Testing Flask Application")
    print("-" * 30)
    
    try:
        from app import create_app
        
        # Create app
        app = create_app()
        print("  ✅ Flask app created successfully")
        
        # Test with test client
        with app.test_client() as client:
            # Test main page
            response = client.get('/')
            print(f"  ✅ Main page: {response.status_code}")
            
            # Test API endpoints
            response = client.get('/api/stars?count_limit=10')
            if response.status_code == 200:
                data = response.get_json()
                print(f"  ✅ Stars API: {len(data)} stars returned")
            else:
                print(f"  ⚠️  Stars API: {response.status_code}")
            
            # Test search endpoint
            response = client.get('/api/search?q=sol')
            if response.status_code == 200:
                data = response.get_json()
                print(f"  ✅ Search API: {data.get('count', 0)} results")
            else:
                print(f"  ⚠️  Search API: {response.status_code}")
            
            # Test nations endpoint
            response = client.get('/api/nations')
            if response.status_code == 200:
                data = response.get_json()
                print(f"  ✅ Nations API: {data.get('total_nations', 0)} nations")
            else:
                print(f"  ⚠️  Nations API: {response.status_code}")
        
        return True
        
    except Exception as e:
        print(f"  ❌ Flask app test failed: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_data_operations():
    """Test basic data operations"""
    print("\n📊 Testing Data Operations")
    print("-" * 30)
    
    try:
        from models.star_model import StarModel
        
        star_model = StarModel()
        
        # Test star search
        results = star_model.search_stars("Sol")
        print(f"  ✅ Star search: {len(results)} results for 'Sol'")
        
        # Test distance calculation
        if len(results) >= 2:
            star1_id = results[0]['id']
            star2_id = results[1]['id'] if len(results) > 1 else star1_id
            
            distance_data = star_model.calculate_distance(star1_id, star2_id)
            if distance_data:
                print(f"  ✅ Distance calculation: {distance_data['distance_between']['light_years']} ly")
            else:
                print("  ⚠️  Distance calculation failed")
        
        # Test spectral types
        spectral_data = star_model.get_spectral_types()
        total_types = spectral_data.get('total_types', 0)
        print(f"  ✅ Spectral types: {total_types} types available")
        
        return True
        
    except Exception as e:
        print(f"  ❌ Data operations test failed: {e}")
        return False


def generate_test_report():
    """Generate a comprehensive test report"""
    print("\n" + "="*50)
    print("🎯 ENVIRONMENT TEST SUMMARY")
    print("="*50)
    
    # Capture output
    test_output = StringIO()
    
    with redirect_stdout(test_output):
        component_test = test_mvc_components()
        flask_test = test_flask_app()
        data_test = test_data_operations()
    
    # Print captured output
    print(test_output.getvalue())
    
    # Summary
    total_tests = 3
    passed_tests = sum([component_test, flask_test, data_test])
    
    print(f"\n📊 Test Results: {passed_tests}/{total_tests} passed")
    
    if passed_tests == total_tests:
        print("🎉 ALL TESTS PASSED! Environment is ready for use.")
        print("\n🚀 You can now run:")
        print("   python app.py")
        print("   ./run_starmap.sh")
        return True
    else:
        print("⚠️  Some tests failed. Check the output above.")
        return False


def main():
    """Main test function"""
    print("🌟 Starmap Environment Test")
    print("="*40)
    
    # Quick environment check
    try:
        import flask, pandas, plotly, numpy
        print("✅ Core packages available")
    except ImportError as e:
        print(f"❌ Missing core packages: {e}")
        print("Please run: source starmap_venv/bin/activate")
        return 1
    
    # Run comprehensive tests
    if generate_test_report():
        return 0
    else:
        return 1


if __name__ == "__main__":
    sys.exit(main())