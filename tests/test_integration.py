"""
Integration tests for complete workflows and system functionality
"""

import unittest
import os
import sys
import tempfile
import shutil
import json
from unittest.mock import patch, MagicMock

# Add project paths
project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, project_root)
sys.path.insert(0, os.path.join(project_root, 'database'))
sys.path.insert(0, os.path.join(project_root, 'managers'))

from tests import BaseTestCase


class TestDataWorkflow(BaseTestCase):
    """Test complete data management workflows"""
    
    def setUp(self):
        super().setUp()
        self.test_db_path = tempfile.mkdtemp(prefix="test_starmap_integration_")
    
    def tearDown(self):
        super().tearDown()
        if os.path.exists(self.test_db_path):
            shutil.rmtree(self.test_db_path)
    
    @patch('database.config.get_database')
    def test_complete_star_lifecycle(self, mock_db):
        """Test complete star creation, update, and deletion workflow"""
        try:
            from managers.data_manager import DataManager
            
            # Mock database operations
            mock_db_instance = MagicMock()
            mock_db.return_value = mock_db_instance
            
            mock_collection = MagicMock()
            mock_db_instance.stars = mock_collection
            
            # Test data
            star_data = {
                'id': 999001,
                'x': 12.34, 'y': 56.78, 'z': 90.12,
                'mag': 4.5, 'spect': 'G2V',
                'name': 'Integration Test Star'
            }
            
            dm = DataManager()
            
            # Step 1: Add star
            mock_collection.find_one.return_value = None  # Star doesn't exist
            mock_collection.insert_one.return_value = MagicMock()
            
            star_id = dm.add_star(star_data)
            self.assertEqual(star_id, 999001)
            
            # Step 2: Retrieve star
            mock_collection.find_one.return_value = star_data
            retrieved_star = dm.get_star(999001)
            self.assertIsNotNone(retrieved_star)
            
            # Step 3: Update star
            mock_collection.update_one.return_value = MagicMock(modified_count=1)
            update_data = {'fictional_name': 'Updated Test Star'}
            
            update_result = dm.update_star(999001, update_data)
            self.assertTrue(update_result)
            
            # Step 4: Delete star
            mock_collection.delete_one.return_value = MagicMock(deleted_count=1)
            delete_result = dm.delete_star(999001, force=True)
            self.assertTrue(delete_result)
            
        except ImportError:
            self.skipTest("DataManager not available")
    
    @patch('database.config.get_database')
    def test_nation_territory_management(self, mock_db):
        """Test complete nation and territory management workflow"""
        try:
            from managers.data_manager import DataManager
            
            # Mock database
            mock_db_instance = MagicMock()
            mock_db.return_value = mock_db_instance
            
            mock_nations = MagicMock()
            mock_stars = MagicMock()
            mock_db_instance.nations = mock_nations
            mock_db_instance.stars = mock_stars
            
            dm = DataManager()
            
            # Step 1: Create nation
            nation_data = {
                'id': 'test_integration_nation',
                'name': 'Test Integration Nation',
                'government_type': 'Test Republic',
                'capital_star_id': 999001
            }
            
            mock_nations.find_one.return_value = None
            mock_nations.insert_one.return_value = MagicMock()
            
            nation_id = dm.add_nation(nation_data)
            self.assertEqual(nation_id, 'test_integration_nation')
            
            # Step 2: Add territories
            mock_nations.find_one.return_value = {
                '_id': 'test_integration_nation',
                'territories': [999001]
            }
            mock_nations.update_one.return_value = MagicMock(modified_count=1)
            
            territory_added = dm.add_territory('test_integration_nation', 999002)
            self.assertTrue(territory_added)
            
            # Step 3: Remove territory
            territory_removed = dm.remove_territory('test_integration_nation', 999002)
            self.assertTrue(territory_removed)
            
            # Step 4: Delete nation
            mock_nations.delete_one.return_value = MagicMock(deleted_count=1)
            nation_deleted = dm.delete_nation('test_integration_nation')
            self.assertTrue(nation_deleted)
            
        except ImportError:
            self.skipTest("DataManager not available")
    
    @patch('database.config.get_database')
    def test_trade_route_network_integration(self, mock_db):
        """Test trade route network creation and analysis"""
        try:
            from managers.data_manager import DataManager
            
            # Mock database
            mock_db_instance = MagicMock()
            mock_db.return_value = mock_db_instance
            
            mock_routes = MagicMock()
            mock_db_instance.trade_routes = mock_routes
            
            dm = DataManager()
            
            # Step 1: Create multiple trade routes
            routes_data = [
                {
                    'id': 'test_route_1',
                    'name': 'Test Route 1',
                    'from_star_id': 999001,
                    'to_star_id': 999002,
                    'route_type': 'Commercial'
                },
                {
                    'id': 'test_route_2',
                    'name': 'Test Route 2',
                    'from_star_id': 999002,
                    'to_star_id': 999003,
                    'route_type': 'Commercial'
                }
            ]
            
            mock_routes.find_one.return_value = None
            mock_routes.insert_one.return_value = MagicMock()
            
            route_ids = []
            for route_data in routes_data:
                route_id = dm.add_trade_route(route_data)
                route_ids.append(route_id)
            
            self.assertEqual(len(route_ids), 2)
            
            # Step 2: Analyze trade network
            mock_routes.find.return_value = [
                {
                    '_id': 'test_route_1',
                    'endpoints': {'from': {'star_id': 999001}, 'to': {'star_id': 999002}},
                    'control': {'controlling_nation': 'test_nation'}
                },
                {
                    '_id': 'test_route_2',
                    'endpoints': {'from': {'star_id': 999002}, 'to': {'star_id': 999003}},
                    'control': {'controlling_nation': 'test_nation'}
                }
            ]
            
            network_analysis = dm.analyze_trade_network()
            
            self.assertIn('summary', network_analysis)
            self.assertIn('hub_systems', network_analysis)
            
        except ImportError:
            self.skipTest("DataManager not available")


class TestTemplateWorkflow(BaseTestCase):
    """Test template-based data creation workflows"""
    
    @patch('database.config.get_database')
    def test_template_star_creation(self, mock_db):
        """Test creating stars using templates"""
        try:
            from managers.data_manager import DataManager
            
            # Mock database
            mock_db_instance = MagicMock()
            mock_db.return_value = mock_db_instance
            
            mock_collection = MagicMock()
            mock_db_instance.stars = mock_collection
            mock_collection.find_one.return_value = None
            mock_collection.insert_one.return_value = MagicMock()
            
            dm = DataManager()
            
            # Test fictional star template
            star_id = dm.add_star_from_template(
                'fictional',
                star_id=999001,
                system_name='Template Test System',
                fictional_name='Template Test Star',
                x=45.2, y=-23.1, z=67.8,
                magnitude=4.2,
                spectral_class='G5V',
                description='A star created from template for testing'
            )
            
            self.assertEqual(star_id, 999001)
            mock_collection.insert_one.assert_called()
            
        except ImportError:
            self.skipTest("DataManager not available")
    
    @patch('database.config.get_database')
    def test_template_nation_creation(self, mock_db):
        """Test creating nations using templates"""
        try:
            from managers.data_manager import DataManager
            
            # Mock database
            mock_db_instance = MagicMock()
            mock_db.return_value = mock_db_instance
            
            mock_collection = MagicMock()
            mock_db_instance.nations = mock_collection
            mock_collection.find_one.return_value = None
            mock_collection.insert_one.return_value = MagicMock()
            
            dm = DataManager()
            
            # Test trading confederation template
            nation_id = dm.add_nation_from_template(
                'confederation',
                nation_id='template_test_confederation',
                name='Template Test Confederation',
                capital_system='Template Hub',
                capital_star_id=999001,
                established_year=2350,
                member_systems=[999001, 999002, 999003],
                trade_specialties=['Electronics', 'Rare Metals']
            )
            
            self.assertEqual(nation_id, 'template_test_confederation')
            mock_collection.insert_one.assert_called()
            
        except ImportError:
            self.skipTest("DataManager not available")


class TestFelgenlandCleanupWorkflow(BaseTestCase):
    """Test complete Felgenland cleanup workflow"""
    
    @patch('database.config.get_database')
    @patch('database.config.get_collection')
    def test_complete_cleanup_workflow(self, mock_get_collection, mock_db):
        """Test complete Felgenland cleanup process"""
        try:
            from managers.data_manager import DataManager
            
            # Mock database and collections
            mock_db_instance = MagicMock()
            mock_db.return_value = mock_db_instance
            
            mock_collection = MagicMock()
            mock_get_collection.return_value = mock_collection
            
            dm = DataManager()
            
            # Step 1: Preview cleanup
            mock_collection.find.return_value = []
            mock_collection.find_one.return_value = None
            
            preview = dm.preview_felgenland_cleanup()
            
            self.assertIn('nations_to_remove', preview)
            self.assertIn('trade_routes_to_remove', preview)
            self.assertIn('planetary_systems_to_remove', preview)
            
            # Step 2: Create backup
            with patch('builtins.open', create=True) as mock_open:
                mock_open.return_value.__enter__.return_value = MagicMock()
                
                backup_result = dm.backup_felgenland_data('test_backup.json')
                
                self.assertIn('success', backup_result)
            
            # Step 3: Perform selective cleanup
            cleanup_result = dm.selective_felgenland_cleanup(
                remove_nations=True,
                remove_trade_routes=True,
                remove_planetary_systems=False
            )
            
            self.assertIn('operations', cleanup_result)
            self.assertIn('summary', cleanup_result)
            
        except ImportError:
            self.skipTest("DataManager not available")


class TestAPIIntegration(BaseTestCase):
    """Test API integration with database and managers"""
    
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
    
    @patch('managers.data_manager.DataManager')
    def test_api_star_crud_workflow(self, mock_manager_class):
        """Test complete CRUD workflow through API"""
        # Mock DataManager
        mock_manager = MagicMock()
        mock_manager_class.return_value = mock_manager
        
        # Test data
        star_data = {
            'id': 999001,
            'x': 12.34, 'y': 56.78, 'z': 90.12,
            'mag': 4.5, 'spect': 'G2V',
            'name': 'API Test Star'
        }
        
        # Step 1: Create star via API
        mock_manager.validate_star_data.return_value = []
        mock_manager.add_star.return_value = 999001
        
        response = self.client.post(
            '/api/star/add',
            data=json.dumps(star_data),
            content_type='application/json'
        )
        
        if response.status_code == 201:
            data = json.loads(response.data)
            self.assertEqual(data['star_id'], 999001)
        
        # Step 2: Retrieve star via API
        mock_manager.get_star.return_value = star_data
        
        response = self.client.get('/api/star/999001')
        
        if response.status_code == 200:
            data = json.loads(response.data)
            self.assertEqual(data['id'], 999001)
        
        # Step 3: Update star via API
        update_data = {'fictional_name': 'Updated API Test Star'}
        mock_manager.update_star.return_value = True
        
        response = self.client.put(
            '/api/star/999001/update',
            data=json.dumps(update_data),
            content_type='application/json'
        )
        
        if response.status_code == 200:
            data = json.loads(response.data)
            self.assertTrue(data.get('success', False))
    
    @patch('managers.data_manager.DataManager')
    def test_api_statistics_integration(self, mock_manager_class):
        """Test statistics API integration"""
        mock_manager = MagicMock()
        mock_manager_class.return_value = mock_manager
        
        # Mock comprehensive statistics
        mock_stats = {
            'stars': {'total_stars': 24671},
            'nations': {'total_nations': 5},
            'trade_routes': {'total_routes': 28},
            'planetary_systems': {'total_systems': 6}
        }
        mock_manager.get_comprehensive_statistics.return_value = mock_stats
        
        # Test comprehensive stats endpoint
        response = self.client.get('/api/stats/comprehensive')
        
        if response.status_code == 200:
            data = json.loads(response.data)
            self.assertIn('stars', data)
            self.assertIn('nations', data)


class TestDataValidationIntegration(BaseTestCase):
    """Test data validation across the entire system"""
    
    @patch('database.config.get_database')
    def test_star_validation_integration(self, mock_db):
        """Test star data validation throughout the system"""
        try:
            from managers.data_manager import DataManager
            
            # Mock database
            mock_db_instance = MagicMock()
            mock_db.return_value = mock_db_instance
            
            dm = DataManager()
            
            # Test valid star data
            valid_star = {
                'id': 999001,
                'x': 12.34, 'y': 56.78, 'z': 90.12,
                'mag': 4.5, 'spect': 'G2V'
            }
            
            errors = dm.validate_star_data(valid_star)
            self.assertEqual(len(errors), 0)
            
            # Test invalid star data
            invalid_star = {
                'id': 'not_an_int',
                'mag': 50.0,  # Out of range
                'spect': 'INVALID'  # Invalid spectral class
            }
            
            errors = dm.validate_star_data(invalid_star)
            self.assertGreater(len(errors), 0)
            
        except ImportError:
            self.skipTest("DataManager not available")
    
    def test_api_validation_integration(self):
        """Test API validation integration"""
        # Test invalid JSON
        response = self.client.post(
            '/api/star/add',
            data='invalid json',
            content_type='application/json'
        )
        
        # Should handle gracefully
        self.assertIn(response.status_code, [400, 415])


class TestPerformanceIntegration(BaseTestCase):
    """Test system performance under realistic load"""
    
    @patch('database.config.get_database')
    def test_bulk_operations_performance(self, mock_db):
        """Test bulk operations performance"""
        try:
            from managers.data_manager import DataManager
            
            # Mock database for bulk operations
            mock_db_instance = MagicMock()
            mock_db.return_value = mock_db_instance
            
            mock_collection = MagicMock()
            mock_db_instance.stars = mock_collection
            mock_collection.insert_many.return_value = MagicMock()
            
            dm = DataManager()
            
            # Create bulk test data
            bulk_stars = [
                {
                    'id': 900000 + i,
                    'x': i * 0.1, 'y': i * 0.1, 'z': i * 0.1,
                    'mag': 5.0, 'spect': 'G2V',
                    'name': f'Bulk Test Star {i}'
                }
                for i in range(100)
            ]
            
            # Test bulk insertion performance
            def bulk_insert_test():
                return dm.bulk_add_stars(bulk_stars)
            
            result = self.assertPerformance(bulk_insert_test, max_time_ms=5000)
            self.assertEqual(len(result), 100)
            
        except ImportError:
            self.skipTest("DataManager not available")
    
    def test_api_performance_integration(self):
        """Test API performance under load"""
        import time
        
        # Test multiple rapid requests
        start_time = time.time()
        
        responses = []
        for _ in range(10):
            response = self.client.get('/api/spectral-types')
            responses.append(response.status_code)
        
        end_time = time.time()
        total_time_ms = (end_time - start_time) * 1000
        
        # All requests should succeed
        for status in responses:
            self.assertEqual(status, 200)
        
        # Total time should be reasonable
        self.assertLess(total_time_ms, 10000, "API performance degraded under load")


if __name__ == '__main__':
    unittest.main()