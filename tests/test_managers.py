"""
Unit tests for all manager classes (CRUD operations)
"""

import unittest
import os
import sys
from unittest.mock import patch, MagicMock, call

# Add project paths
project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, project_root)
sys.path.insert(0, os.path.join(project_root, 'managers'))
sys.path.insert(0, os.path.join(project_root, 'database'))

from tests import BaseTestCase


class TestDataManager(BaseTestCase):
    """Test the unified DataManager class"""
    
    @patch('managers.data_manager.StarManager')
    @patch('managers.data_manager.NationManager')
    @patch('managers.data_manager.TradeRouteManager')
    @patch('managers.data_manager.PlanetarySystemManager')
    @patch('managers.data_manager.FelgenlandCleanup')
    def setUp(self, mock_cleanup, mock_system, mock_trade, mock_nation, mock_star):
        super().setUp()
        
        # Mock all managers
        self.mock_star_manager = MagicMock()
        self.mock_nation_manager = MagicMock()
        self.mock_trade_manager = MagicMock()
        self.mock_system_manager = MagicMock()
        self.mock_cleanup_manager = MagicMock()
        
        mock_star.return_value = self.mock_star_manager
        mock_nation.return_value = self.mock_nation_manager
        mock_trade.return_value = self.mock_trade_manager
        mock_system.return_value = self.mock_system_manager
        mock_cleanup.return_value = self.mock_cleanup_manager
        
        try:
            from managers.data_manager import DataManager
            self.data_manager = DataManager()
        except ImportError:
            self.skipTest("DataManager not available")
    
    def test_data_manager_initialization(self):
        """Test DataManager initializes all sub-managers"""
        self.assertIsNotNone(self.data_manager.star_manager)
        self.assertIsNotNone(self.data_manager.nation_manager)
        self.assertIsNotNone(self.data_manager.trade_route_manager)
        self.assertIsNotNone(self.data_manager.system_manager)
        self.assertIsNotNone(self.data_manager.cleanup_manager)
    
    def test_add_star(self):
        """Test adding a star through DataManager"""
        star_data = {
            'id': 999001,
            'x': 12.34, 'y': 56.78, 'z': 90.12,
            'mag': 4.5, 'spect': 'G2V'
        }
        
        self.mock_star_manager.add_star.return_value = 999001
        
        result = self.data_manager.add_star(star_data)
        
        self.mock_star_manager.add_star.assert_called_once_with(star_data)
        self.assertEqual(result, 999001)
    
    def test_add_star_from_template(self):
        """Test adding star using template"""
        self.mock_star_manager.add_star.return_value = 999001
        
        result = self.data_manager.add_star_from_template(
            'fictional',
            star_id=999001,
            system_name='Test System',
            fictional_name='Test Star',
            x=12.34, y=56.78, z=90.12,
            magnitude=4.5,
            spectral_class='G2V'
        )
        
        self.mock_star_manager.add_star.assert_called_once()
        self.assertEqual(result, 999001)
    
    def test_get_comprehensive_statistics(self):
        """Test getting comprehensive statistics"""
        # Mock statistics from each manager
        self.mock_star_manager.get_star_statistics.return_value = {'total_stars': 1000}
        self.mock_nation_manager.get_nation_statistics.return_value = {'total_nations': 5}
        self.mock_trade_manager.get_trade_route_statistics.return_value = {'total_routes': 28}
        self.mock_system_manager.get_system_statistics.return_value = {'total_systems': 6}
        
        stats = self.data_manager.get_comprehensive_statistics()
        
        self.assertIn('stars', stats)
        self.assertIn('nations', stats)
        self.assertIn('trade_routes', stats)
        self.assertIn('planetary_systems', stats)
        self.assertIn('generated_at', stats)
        
        self.assertEqual(stats['stars']['total_stars'], 1000)
        self.assertEqual(stats['nations']['total_nations'], 5)
    
    def test_validation_methods(self):
        """Test data validation methods"""
        star_data = {'id': 999001, 'x': 12.34, 'y': 56.78, 'z': 90.12}
        
        self.mock_star_manager.validate_star_data.return_value = []
        
        errors = self.data_manager.validate_star_data(star_data)
        
        self.mock_star_manager.validate_star_data.assert_called_once_with(star_data)
        self.assertEqual(errors, [])


class TestStarManager(BaseTestCase):
    """Test StarManager CRUD operations"""
    
    @patch('database.config.get_collection')
    def setUp(self, mock_get_collection):
        super().setUp()
        
        # Mock database collection
        self.mock_collection = MagicMock()
        mock_get_collection.return_value = self.mock_collection
        
        try:
            from managers.star_manager import StarManager
            self.star_manager = StarManager()
        except ImportError:
            self.skipTest("StarManager not available")
    
    def test_add_star(self):
        """Test adding a new star"""
        star_data = {
            'id': 999001,
            'x': 12.34, 'y': 56.78, 'z': 90.12,
            'mag': 4.5, 'spect': 'G2V',
            'name': 'Test Star'
        }
        
        self.mock_collection.find_one.return_value = None  # Star doesn't exist
        self.mock_collection.insert_one.return_value = MagicMock()
        
        result = self.star_manager.add_star(star_data)
        
        self.mock_collection.insert_one.assert_called_once()
        self.assertEqual(result, 999001)
    
    def test_add_duplicate_star_fails(self):
        """Test that adding duplicate star fails"""
        star_data = {'id': 999001, 'name': 'Test Star'}
        
        # Mock existing star
        self.mock_collection.find_one.return_value = {'_id': 999001}
        
        with self.assertRaises(ValueError):
            self.star_manager.add_star(star_data)
    
    def test_get_star(self):
        """Test getting a star by ID"""
        mock_star = {'_id': 999001, 'name': 'Test Star'}
        self.mock_collection.find_one.return_value = mock_star
        
        result = self.star_manager.get_star(999001)
        
        self.mock_collection.find_one.assert_called_once_with({'_id': 999001})
        self.assertEqual(result, mock_star)
    
    def test_search_stars(self):
        """Test searching stars with filters"""
        mock_results = [
            {'_id': 999001, 'name': 'Test Star 1'},
            {'_id': 999002, 'name': 'Test Star 2'}
        ]
        self.mock_collection.find.return_value = mock_results
        
        results = self.star_manager.search_stars(
            query='Test',
            magnitude_range=(0, 6),
            limit=10
        )
        
        self.mock_collection.find.assert_called_once()
        self.assertEqual(len(results), 2)
    
    def test_update_star(self):
        """Test updating star information"""
        # Mock existing star
        self.mock_collection.find_one.return_value = {'_id': 999001}
        self.mock_collection.update_one.return_value = MagicMock(modified_count=1)
        
        update_data = {'fictional_name': 'Updated Name'}
        
        result = self.star_manager.update_star(999001, update_data)
        
        self.mock_collection.update_one.assert_called_once()
        self.assertTrue(result)
    
    def test_delete_star(self):
        """Test deleting a star"""
        # Mock existing star with no dependencies
        self.mock_collection.find_one.return_value = {'_id': 999001}
        self.mock_collection.delete_one.return_value = MagicMock(deleted_count=1)
        
        result = self.star_manager.delete_star(999001, force=True)
        
        self.mock_collection.delete_one.assert_called_once()
        self.assertTrue(result)
    
    def test_validate_star_data(self):
        """Test star data validation"""
        # Valid data
        valid_data = {
            'id': 999001,
            'x': 12.34, 'y': 56.78, 'z': 90.12,
            'mag': 4.5, 'spect': 'G2V'
        }
        
        errors = self.star_manager.validate_star_data(valid_data)
        self.assertEqual(len(errors), 0)
        
        # Invalid data
        invalid_data = {
            'id': 'not_an_int',
            'mag': 50.0,  # Out of range
            'spect': 'INVALID'  # Invalid spectral class
        }
        
        errors = self.star_manager.validate_star_data(invalid_data)
        self.assertGreater(len(errors), 0)


class TestNationManager(BaseTestCase):
    """Test NationManager CRUD operations"""
    
    @patch('database.config.get_collection')
    def setUp(self, mock_get_collection):
        super().setUp()
        
        self.mock_collection = MagicMock()
        mock_get_collection.return_value = self.mock_collection
        
        try:
            from managers.nation_manager import NationManager
            self.nation_manager = NationManager()
        except ImportError:
            self.skipTest("NationManager not available")
    
    def test_add_nation(self):
        """Test adding a new nation"""
        nation_data = {
            'id': 'test_nation',
            'name': 'Test Nation',
            'government_type': 'Republic',
            'capital_star_id': 999001
        }
        
        self.mock_collection.find_one.return_value = None
        self.mock_collection.insert_one.return_value = MagicMock()
        
        result = self.nation_manager.add_nation(nation_data)
        
        self.mock_collection.insert_one.assert_called_once()
        self.assertEqual(result, 'test_nation')
    
    def test_add_territory(self):
        """Test adding territory to a nation"""
        # Mock existing nation
        mock_nation = {
            '_id': 'test_nation',
            'territories': [999001]
        }
        self.mock_collection.find_one.return_value = mock_nation
        self.mock_collection.update_one.return_value = MagicMock(modified_count=1)
        
        result = self.nation_manager.add_territory('test_nation', 999002)
        
        self.mock_collection.update_one.assert_called_once()
        self.assertTrue(result)
    
    def test_remove_territory(self):
        """Test removing territory from a nation"""
        mock_nation = {
            '_id': 'test_nation',
            'territories': [999001, 999002]
        }
        self.mock_collection.find_one.return_value = mock_nation
        self.mock_collection.update_one.return_value = MagicMock(modified_count=1)
        
        result = self.nation_manager.remove_territory('test_nation', 999002)
        
        self.mock_collection.update_one.assert_called_once()
        self.assertTrue(result)
    
    def test_get_nation_statistics(self):
        """Test getting nation statistics"""
        mock_nations = [
            {'_id': 'nation1', 'territories': [1, 2, 3]},
            {'_id': 'nation2', 'territories': [4, 5]}
        ]
        self.mock_collection.find.return_value = mock_nations
        self.mock_collection.count_documents.return_value = 2
        
        stats = self.nation_manager.get_nation_statistics()
        
        self.assertIn('total_nations', stats)
        self.assertIn('territory_control', stats)
        self.assertEqual(stats['total_nations'], 2)


class TestTradeRouteManager(BaseTestCase):
    """Test TradeRouteManager CRUD operations"""
    
    @patch('database.config.get_collection')
    def setUp(self, mock_get_collection):
        super().setUp()
        
        self.mock_collection = MagicMock()
        mock_get_collection.return_value = self.mock_collection
        
        try:
            from managers.trade_route_manager import TradeRouteManager
            self.trade_manager = TradeRouteManager()
        except ImportError:
            self.skipTest("TradeRouteManager not available")
    
    def test_add_trade_route(self):
        """Test adding a new trade route"""
        route_data = {
            'id': 'test_route',
            'name': 'Test Route',
            'from_star_id': 999001,
            'to_star_id': 999002,
            'route_type': 'Commercial'
        }
        
        self.mock_collection.find_one.return_value = None
        self.mock_collection.insert_one.return_value = MagicMock()
        
        result = self.trade_manager.add_trade_route(route_data)
        
        self.mock_collection.insert_one.assert_called_once()
        self.assertEqual(result, 'test_route')
    
    def test_get_routes_by_nation(self):
        """Test getting routes controlled by a nation"""
        mock_routes = [
            {'_id': 'route1', 'controlling_nation': 'test_nation'},
            {'_id': 'route2', 'controlling_nation': 'test_nation'}
        ]
        self.mock_collection.find.return_value = mock_routes
        
        result = self.trade_manager.get_routes_by_nation('test_nation')
        
        self.mock_collection.find.assert_called_once_with({'control.controlling_nation': 'test_nation'})
        self.assertEqual(len(result), 2)
    
    def test_analyze_trade_network(self):
        """Test trade network analysis"""
        mock_routes = [
            {
                '_id': 'route1',
                'endpoints': {'from': {'star_id': 1}, 'to': {'star_id': 2}},
                'control': {'controlling_nation': 'nation1'}
            },
            {
                '_id': 'route2', 
                'endpoints': {'from': {'star_id': 2}, 'to': {'star_id': 3}},
                'control': {'controlling_nation': 'nation1'}
            }
        ]
        self.mock_collection.find.return_value = mock_routes
        
        analysis = self.trade_manager.analyze_trade_network()
        
        self.assertIn('summary', analysis)
        self.assertIn('total_routes', analysis['summary'])
        self.assertIn('hub_systems', analysis)


class TestPlanetarySystemManager(BaseTestCase):
    """Test PlanetarySystemManager CRUD operations"""
    
    @patch('database.config.get_collection')
    def setUp(self, mock_get_collection):
        super().setUp()
        
        self.mock_collection = MagicMock()
        mock_get_collection.return_value = self.mock_collection
        
        try:
            from managers.planetary_system_manager import PlanetarySystemManager
            self.system_manager = PlanetarySystemManager()
        except ImportError:
            self.skipTest("PlanetarySystemManager not available")
    
    def test_add_planetary_system(self):
        """Test adding a planetary system"""
        system_data = {
            'star_id': 999001,
            'system_name': 'Test System',
            'planets': [
                {
                    'name': 'Test Planet',
                    'type': 'Terrestrial',
                    'distance_au': 1.0
                }
            ]
        }
        
        self.mock_collection.find_one.return_value = None
        self.mock_collection.insert_one.return_value = MagicMock()
        
        result = self.system_manager.add_planetary_system(system_data)
        
        self.mock_collection.insert_one.assert_called_once()
        self.assertEqual(result, 999001)
    
    def test_add_planet_to_system(self):
        """Test adding a planet to existing system"""
        mock_system = {
            '_id': 999001,
            'planets': [{'name': 'Planet 1'}]
        }
        self.mock_collection.find_one.return_value = mock_system
        self.mock_collection.update_one.return_value = MagicMock(modified_count=1)
        
        planet_data = {
            'name': 'Planet 2',
            'type': 'Terrestrial',
            'distance_au': 2.0
        }
        
        result = self.system_manager.add_planet_to_system(999001, planet_data)
        
        self.mock_collection.update_one.assert_called_once()
        self.assertTrue(result)
    
    def test_get_system_statistics(self):
        """Test getting planetary system statistics"""
        mock_systems = [
            {'_id': 1, 'has_life': True, 'colonized': True},
            {'_id': 2, 'has_life': False, 'colonized': False}
        ]
        self.mock_collection.find.return_value = mock_systems
        self.mock_collection.count_documents.return_value = 2
        
        stats = self.system_manager.get_system_statistics()
        
        self.assertIn('total_systems', stats)
        self.assertIn('systems_with_life', stats)
        self.assertIn('colonized_systems', stats)


class TestFelgenlandCleanup(BaseTestCase):
    """Test Felgenland cleanup functionality"""
    
    @patch('managers.star_manager.StarManager')
    @patch('managers.nation_manager.NationManager')
    @patch('managers.trade_route_manager.TradeRouteManager')
    @patch('managers.planetary_system_manager.PlanetarySystemManager')
    def setUp(self, mock_system, mock_trade, mock_nation, mock_star):
        super().setUp()
        
        # Mock all managers
        self.mock_star_manager = MagicMock()
        self.mock_nation_manager = MagicMock()
        self.mock_trade_manager = MagicMock()
        self.mock_system_manager = MagicMock()
        
        mock_star.return_value = self.mock_star_manager
        mock_nation.return_value = self.mock_nation_manager
        mock_trade.return_value = self.mock_trade_manager
        mock_system.return_value = self.mock_system_manager
        
        try:
            from managers.felgenland_cleanup import FelgenlandCleanup
            self.cleanup_manager = FelgenlandCleanup()
        except ImportError:
            self.skipTest("FelgenlandCleanup not available")
    
    def test_preview_cleanup(self):
        """Test preview of what would be cleaned up"""
        # Mock data to be cleaned
        self.mock_nation_manager.get_nation.return_value = {
            'id': 'terran_directorate',
            'name': 'Terran Directorate',
            'territories': [0, 71456],
            'trade_routes': ['route1']
        }
        
        preview = self.cleanup_manager.preview_cleanup()
        
        self.assertIn('nations_to_remove', preview)
        self.assertIn('trade_routes_to_remove', preview)
        self.assertIn('planetary_systems_to_remove', preview)
    
    def test_selective_cleanup(self):
        """Test selective cleanup functionality"""
        # Mock successful cleanup operations
        self.mock_trade_manager.remove_all_felgenland_routes.return_value = 28
        self.mock_nation_manager.remove_all_felgenland_nations.return_value = ['terran_directorate']
        
        result = self.cleanup_manager.selective_cleanup(
            remove_nations=True,
            remove_trade_routes=True,
            remove_planetary_systems=False
        )
        
        self.assertIn('operations', result)
        self.assertIn('summary', result)
        self.assertTrue(result.get('success', False))
    
    def test_backup_creation(self):
        """Test backup creation before cleanup"""
        # Mock data for backup
        self.mock_nation_manager.get_nation.return_value = {
            'id': 'terran_directorate',
            'name': 'Terran Directorate'
        }
        
        with patch('builtins.open', create=True) as mock_open:
            mock_open.return_value.__enter__.return_value = MagicMock()
            
            result = self.cleanup_manager.create_backup('test_backup.json')
            
            self.assertIn('success', result)
            self.assertIn('backup_file', result)


if __name__ == '__main__':
    unittest.main()