"""
Unit tests for API endpoints and Flask application
"""

import unittest
import json
import os
import sys
from unittest.mock import patch, MagicMock

# Add project paths
project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, project_root)

from tests import BaseTestCase


class TestAPIEndpoints(BaseTestCase):
    """Test Flask API endpoints"""
    
    def setUp(self):
        super().setUp()
        
        try:
            # Try to import the MontyDB version first
            import app_montydb
            self.app = app_montydb.app
        except ImportError:
            try:
                # Fall back to regular version
                import app
                self.app = app.app
            except ImportError:
                self.skipTest("Flask app not available")
        
        self.app.config['TESTING'] = True
        self.app.config['WTF_CSRF_ENABLED'] = False
        self.client = self.app.test_client()
    
    def test_home_page(self):
        """Test home page loads"""
        response = self.client.get('/')
        self.assertEqual(response.status_code, 200)
        # Should contain the starmap HTML
        self.assertIn(b'starmap', response.data.lower())
    
    def test_api_stars_endpoint(self):
        """Test /api/stars endpoint"""
        with patch('controllers.star_controller.StarController') as mock_controller:
            mock_instance = MagicMock()
            mock_instance.get_all_stars.return_value = [
                {'id': 0, 'name': 'Sol', 'x': 0, 'y': 0, 'z': 0, 'mag': -26.7},
                {'id': 71456, 'name': 'Alpha Centauri A', 'x': -1.34, 'y': -0.20, 'z': -1.17, 'mag': -0.27}
            ]
            mock_controller.return_value = mock_instance
            
            response = self.client.get('/api/stars')
            
            self.assertEqual(response.status_code, 200)
            data = json.loads(response.data)
            self.assertIn('stars', data)
            self.assertEqual(len(data['stars']), 2)
            self.assertEqual(data['stars'][0]['name'], 'Sol')
    
    def test_api_stars_with_filters(self):
        """Test /api/stars endpoint with filters"""
        with patch('controllers.star_controller.StarController') as mock_controller:
            mock_instance = MagicMock()
            mock_instance.get_all_stars.return_value = [
                {'id': 0, 'name': 'Sol', 'mag': 4.8}
            ]
            mock_controller.return_value = mock_instance
            
            response = self.client.get('/api/stars?mag_limit=5.0&count_limit=100')
            
            self.assertEqual(response.status_code, 200)
            data = json.loads(response.data)
            self.assertIn('stars', data)
    
    def test_api_star_by_id(self):
        """Test /api/star/<id> endpoint"""
        with patch('controllers.star_controller.StarController') as mock_controller:
            mock_instance = MagicMock()
            mock_instance.get_star_by_id.return_value = {
                'id': 0,
                'name': 'Sol',
                'mag': -26.7,
                'spect': 'G2V'
            }
            mock_controller.return_value = mock_instance
            
            response = self.client.get('/api/star/0')
            
            self.assertEqual(response.status_code, 200)
            data = json.loads(response.data)
            self.assertEqual(data['id'], 0)
            self.assertEqual(data['name'], 'Sol')
    
    def test_api_star_not_found(self):
        """Test /api/star/<id> endpoint with non-existent star"""
        with patch('controllers.star_controller.StarController') as mock_controller:
            mock_instance = MagicMock()
            mock_instance.get_star_by_id.return_value = None
            mock_controller.return_value = mock_instance
            
            response = self.client.get('/api/star/999999')
            
            self.assertEqual(response.status_code, 404)
            data = json.loads(response.data)
            self.assertIn('error', data)
    
    def test_api_search_endpoint(self):
        """Test /api/search endpoint"""
        with patch('controllers.star_controller.StarController') as mock_controller:
            mock_instance = MagicMock()
            mock_instance.search_stars.return_value = [
                {'id': 32263, 'name': 'Sirius', 'mag': -1.46}
            ]
            mock_controller.return_value = mock_instance
            
            response = self.client.get('/api/search?q=Sirius')
            
            self.assertEqual(response.status_code, 200)
            data = json.loads(response.data)
            self.assertIn('results', data)
            self.assertEqual(len(data['results']), 1)
            self.assertEqual(data['results'][0]['name'], 'Sirius')
    
    def test_api_search_empty_query(self):
        """Test /api/search endpoint with empty query"""
        response = self.client.get('/api/search?q=')
        
        self.assertEqual(response.status_code, 400)
        data = json.loads(response.data)
        self.assertIn('error', data)
    
    def test_api_nations_endpoint(self):
        """Test /api/nations endpoint"""
        with patch('controllers.nation_controller.NationController') as mock_controller:
            mock_instance = MagicMock()
            mock_instance.get_all_nations.return_value = [
                {
                    'id': 'terran_directorate',
                    'name': 'Terran Directorate',
                    'government_type': 'Authoritarian Republic'
                }
            ]
            mock_controller.return_value = mock_instance
            
            response = self.client.get('/api/nations')
            
            self.assertEqual(response.status_code, 200)
            data = json.loads(response.data)
            self.assertIn('nations', data)
            self.assertEqual(len(data['nations']), 1)
            self.assertEqual(data['nations'][0]['name'], 'Terran Directorate')
    
    def test_api_nation_by_id(self):
        """Test /api/nation/<id> endpoint"""
        with patch('controllers.nation_controller.NationController') as mock_controller:
            mock_instance = MagicMock()
            mock_instance.get_nation_by_id.return_value = {
                'id': 'terran_directorate',
                'name': 'Terran Directorate',
                'territories': [0, 71456, 32263]
            }
            mock_controller.return_value = mock_instance
            
            response = self.client.get('/api/nation/terran_directorate')
            
            self.assertEqual(response.status_code, 200)
            data = json.loads(response.data)
            self.assertEqual(data['id'], 'terran_directorate')
            self.assertEqual(len(data['territories']), 3)
    
    def test_api_nation_territories(self):
        """Test /api/nation/<id>/territories endpoint"""
        with patch('controllers.nation_controller.NationController') as mock_controller:
            mock_instance = MagicMock()
            mock_instance.get_nation_territories.return_value = [0, 71456, 32263]
            mock_controller.return_value = mock_instance
            
            response = self.client.get('/api/nation/terran_directorate/territories')
            
            self.assertEqual(response.status_code, 200)
            data = json.loads(response.data)
            self.assertIn('territories', data)
            self.assertEqual(len(data['territories']), 3)
    
    def test_api_trade_routes_endpoint(self):
        """Test /api/trade-routes endpoint"""
        with patch('trade_routes.get_all_trade_routes') as mock_routes:
            mock_routes.return_value = [
                {
                    'id': 'earth_centauri_express',
                    'name': 'Earth-Centauri Express',
                    'from_star_id': 0,
                    'to_star_id': 71456
                }
            ]
            
            response = self.client.get('/api/trade-routes')
            
            self.assertEqual(response.status_code, 200)
            data = json.loads(response.data)
            self.assertIn('trade_routes', data)
    
    def test_api_planetary_systems_endpoint(self):
        """Test /api/systems endpoint"""
        with patch('controllers.planet_controller.PlanetController') as mock_controller:
            mock_instance = MagicMock()
            mock_instance.get_all_systems.return_value = [
                {
                    'star_id': 48941,
                    'system_name': 'Holsten Tor',
                    'total_planets': 5
                }
            ]
            mock_controller.return_value = mock_instance
            
            response = self.client.get('/api/systems')
            
            self.assertEqual(response.status_code, 200)
            data = json.loads(response.data)
            self.assertIn('systems', data)
    
    def test_api_system_by_star_id(self):
        """Test /api/system/<star_id> endpoint"""
        with patch('controllers.planet_controller.PlanetController') as mock_controller:
            mock_instance = MagicMock()
            mock_instance.get_planetary_system.return_value = {
                'star_id': 48941,
                'system_name': 'Holsten Tor',
                'planets': [
                    {'name': 'Stahlburgh', 'type': 'Terrestrial'}
                ]
            }
            mock_controller.return_value = mock_instance
            
            response = self.client.get('/api/system/48941')
            
            self.assertEqual(response.status_code, 200)
            data = json.loads(response.data)
            self.assertEqual(data['star_id'], 48941)
            self.assertEqual(len(data['planets']), 1)
    
    def test_api_galactic_directions(self):
        """Test /api/galactic-directions endpoint"""
        with patch('galactic_directions.get_galactic_directions') as mock_directions:
            mock_directions.return_value = [
                {'name': 'Coreward', 'x': 50, 'y': 0, 'z': 0}
            ]
            
            response = self.client.get('/api/galactic-directions')
            
            self.assertEqual(response.status_code, 200)
            data = json.loads(response.data)
            self.assertIn('directions', data)
    
    def test_api_stellar_regions(self):
        """Test /api/stellar-regions endpoint"""
        with patch('controllers.stellar_region_controller.StellarRegionController') as mock_controller:
            mock_instance = MagicMock()
            mock_instance.get_all_regions.return_value = [
                {'name': 'Sol Region', 'color': '#FF0000'}
            ]
            mock_controller.return_value = mock_instance
            
            response = self.client.get('/api/stellar-regions')
            
            self.assertEqual(response.status_code, 200)
            data = json.loads(response.data)
            self.assertIn('regions', data)
    
    def test_api_distance_calculation(self):
        """Test /api/distance endpoint"""
        with patch('controllers.star_controller.StarController') as mock_controller:
            mock_instance = MagicMock()
            mock_instance.calculate_distance.return_value = 4.37
            mock_controller.return_value = mock_instance
            
            response = self.client.get('/api/distance?star1=0&star2=71456')
            
            self.assertEqual(response.status_code, 200)
            data = json.loads(response.data)
            self.assertIn('distance', data)
            self.assertEqual(data['distance'], 4.37)
    
    def test_api_distance_missing_parameters(self):
        """Test /api/distance endpoint with missing parameters"""
        response = self.client.get('/api/distance?star1=0')
        
        self.assertEqual(response.status_code, 400)
        data = json.loads(response.data)
        self.assertIn('error', data)
    
    def test_api_spectral_types(self):
        """Test /api/spectral-types endpoint"""
        response = self.client.get('/api/spectral-types')
        
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.data)
        self.assertIn('spectral_types', data)
        self.assertIn('O', data['spectral_types'])
        self.assertIn('G', data['spectral_types'])
    
    def test_export_csv_endpoint(self):
        """Test /export/csv endpoint"""
        with patch('controllers.star_controller.StarController') as mock_controller:
            mock_instance = MagicMock()
            mock_instance.get_all_stars.return_value = [
                {'id': 0, 'name': 'Sol', 'x': 0, 'y': 0, 'z': 0}
            ]
            mock_controller.return_value = mock_instance
            
            response = self.client.get('/export/csv')
            
            self.assertEqual(response.status_code, 200)
            self.assertEqual(response.headers['Content-Type'], 'text/csv; charset=utf-8')
            self.assertIn(b'Sol', response.data)


class TestAPIValidation(BaseTestCase):
    """Test API input validation and error handling"""
    
    def setUp(self):
        super().setUp()
        
        try:
            import app_montydb
            self.app = app_montydb.app
        except ImportError:
            try:
                import app
                self.app = app.app
            except ImportError:
                self.skipTest("Flask app not available")
        
        self.app.config['TESTING'] = True
        self.client = self.app.test_client()
    
    def test_invalid_star_id_format(self):
        """Test API with invalid star ID format"""
        response = self.client.get('/api/star/invalid_id')
        
        # Should handle gracefully
        self.assertIn(response.status_code, [400, 404])
    
    def test_negative_star_id(self):
        """Test API with negative star ID"""
        response = self.client.get('/api/star/-1')
        
        # Should handle gracefully
        self.assertIn(response.status_code, [400, 404])
    
    def test_invalid_magnitude_parameters(self):
        """Test API with invalid magnitude parameters"""
        response = self.client.get('/api/stars?mag_limit=invalid')
        
        # Should handle gracefully or use defaults
        self.assertIn(response.status_code, [200, 400])
    
    def test_invalid_count_limit(self):
        """Test API with invalid count limit"""
        response = self.client.get('/api/stars?count_limit=-1')
        
        # Should handle gracefully or use defaults
        self.assertIn(response.status_code, [200, 400])
    
    def test_sql_injection_attempt(self):
        """Test API protection against SQL injection"""
        malicious_query = "'; DROP TABLE stars; --"
        response = self.client.get(f'/api/search?q={malicious_query}')
        
        # Should handle safely
        self.assertIn(response.status_code, [200, 400])
    
    def test_xss_attempt(self):
        """Test API protection against XSS"""
        xss_payload = "<script>alert('xss')</script>"
        response = self.client.get(f'/api/search?q={xss_payload}')
        
        # Should handle safely
        self.assertIn(response.status_code, [200, 400])
        # Response should not contain unescaped script tags
        if response.status_code == 200:
            self.assertNotIn(b'<script>', response.data)


class TestAPIPerformance(BaseTestCase):
    """Test API performance characteristics"""
    
    def setUp(self):
        super().setUp()
        
        try:
            import app_montydb
            self.app = app_montydb.app
        except ImportError:
            try:
                import app
                self.app = app.app
            except ImportError:
                self.skipTest("Flask app not available")
        
        self.app.config['TESTING'] = True
        self.client = self.app.test_client()
    
    def test_api_response_time(self):
        """Test API response times are reasonable"""
        import time
        
        with patch('controllers.star_controller.StarController') as mock_controller:
            mock_instance = MagicMock()
            mock_instance.get_all_stars.return_value = [
                {'id': i, 'name': f'Star {i}'} for i in range(1000)
            ]
            mock_controller.return_value = mock_instance
            
            start_time = time.time()
            response = self.client.get('/api/stars')
            end_time = time.time()
            
            response_time_ms = (end_time - start_time) * 1000
            
            self.assertEqual(response.status_code, 200)
            self.assertLess(response_time_ms, 2000, "API response too slow")
    
    def test_concurrent_requests(self):
        """Test handling of concurrent requests"""
        import threading
        import queue
        
        results = queue.Queue()
        
        def make_request():
            try:
                response = self.client.get('/api/spectral-types')
                results.put(response.status_code)
            except Exception as e:
                results.put(str(e))
        
        # Create multiple threads
        threads = []
        for _ in range(10):
            thread = threading.Thread(target=make_request)
            threads.append(thread)
            thread.start()
        
        # Wait for all threads
        for thread in threads:
            thread.join()
        
        # Check results
        status_codes = []
        while not results.empty():
            status_codes.append(results.get())
        
        # All requests should succeed
        self.assertEqual(len(status_codes), 10)
        for status in status_codes:
            self.assertEqual(status, 200)


class TestAPIMontyDBFeatures(BaseTestCase):
    """Test MontyDB-specific API features"""
    
    def setUp(self):
        super().setUp()
        
        try:
            import app_montydb
            self.app = app_montydb.app
            self.app.config['TESTING'] = True
            self.client = self.app.test_client()
        except ImportError:
            self.skipTest("MontyDB app not available")
    
    def test_api_stats_stars(self):
        """Test /api/stats/stars endpoint"""
        with patch('managers.data_manager.DataManager') as mock_manager:
            mock_instance = MagicMock()
            mock_instance.get_star_statistics.return_value = {
                'total_stars': 24671,
                'real_stars': 24658,
                'fictional_stars': 13
            }
            mock_manager.return_value = mock_instance
            
            response = self.client.get('/api/stats/stars')
            
            self.assertEqual(response.status_code, 200)
            data = json.loads(response.data)
            self.assertIn('total_stars', data)
    
    def test_api_stars_region(self):
        """Test /api/stars/region/<region_name> endpoint"""
        with patch('managers.data_manager.DataManager') as mock_manager:
            mock_instance = MagicMock()
            mock_instance.search_stars.return_value = [
                {'id': 0, 'name': 'Sol'}
            ]
            mock_manager.return_value = mock_instance
            
            response = self.client.get('/api/stars/region/sol_region')
            
            self.assertEqual(response.status_code, 200)
            data = json.loads(response.data)
            self.assertIn('stars', data)
    
    def test_api_stars_nation(self):
        """Test /api/stars/nation/<nation_id> endpoint"""
        with patch('managers.data_manager.DataManager') as mock_manager:
            mock_instance = MagicMock()
            mock_instance.search_stars.return_value = [
                {'id': 0, 'name': 'Sol', 'nation_id': 'terran_directorate'}
            ]
            mock_manager.return_value = mock_instance
            
            response = self.client.get('/api/stars/nation/terran_directorate')
            
            self.assertEqual(response.status_code, 200)
            data = json.loads(response.data)
            self.assertIn('stars', data)
    
    def test_api_network_analysis(self):
        """Test /api/network-analysis endpoint"""
        with patch('managers.data_manager.DataManager') as mock_manager:
            mock_instance = MagicMock()
            mock_instance.analyze_trade_network.return_value = {
                'summary': {'total_routes': 28, 'network_density': 0.75},
                'hub_systems': []
            }
            mock_manager.return_value = mock_instance
            
            response = self.client.get('/api/network-analysis')
            
            self.assertEqual(response.status_code, 200)
            data = json.loads(response.data)
            self.assertIn('summary', data)
    
    def test_post_star_add(self):
        """Test POST /api/star/add endpoint"""
        star_data = {
            'id': 999001,
            'x': 12.34, 'y': 56.78, 'z': 90.12,
            'mag': 4.5, 'spect': 'G2V',
            'name': 'Test Star'
        }
        
        with patch('managers.data_manager.DataManager') as mock_manager:
            mock_instance = MagicMock()
            mock_instance.add_star.return_value = 999001
            mock_instance.validate_star_data.return_value = []
            mock_manager.return_value = mock_instance
            
            response = self.client.post(
                '/api/star/add',
                data=json.dumps(star_data),
                content_type='application/json'
            )
            
            self.assertEqual(response.status_code, 201)
            data = json.loads(response.data)
            self.assertIn('star_id', data)
            self.assertEqual(data['star_id'], 999001)
    
    def test_put_star_update(self):
        """Test PUT /api/star/<id>/update endpoint"""
        update_data = {
            'fictional_name': 'Updated Name',
            'fictional_description': 'Updated description'
        }
        
        with patch('managers.data_manager.DataManager') as mock_manager:
            mock_instance = MagicMock()
            mock_instance.update_star.return_value = True
            mock_manager.return_value = mock_instance
            
            response = self.client.put(
                '/api/star/999001/update',
                data=json.dumps(update_data),
                content_type='application/json'
            )
            
            self.assertEqual(response.status_code, 200)
            data = json.loads(response.data)
            self.assertIn('success', data)
            self.assertTrue(data['success'])


if __name__ == '__main__':
    unittest.main()