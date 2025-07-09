"""
Unit tests for all model classes
"""

import unittest
import os
import sys
from unittest.mock import patch, MagicMock
import pandas as pd

# Add project paths
project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, project_root)
sys.path.insert(0, os.path.join(project_root, 'models'))

from tests import BaseTestCase


class TestBaseModel(BaseTestCase):
    """Test base model functionality"""
    
    def test_base_model_import(self):
        """Test that base model can be imported"""
        try:
            from models.base_model import BaseModel
            self.assertTrue(hasattr(BaseModel, '__init__'))
        except ImportError:
            self.skipTest("BaseModel not available")
    
    @patch('pandas.read_csv')
    def test_base_model_caching(self, mock_read_csv):
        """Test model caching functionality"""
        try:
            from models.base_model import BaseModel
            
            # Mock CSV data
            mock_data = pd.DataFrame({
                'id': [1, 2, 3],
                'name': ['Star 1', 'Star 2', 'Star 3']
            })
            mock_read_csv.return_value = mock_data
            
            model = BaseModel('test.csv')
            
            # First call should read from CSV
            data1 = model.get_data()
            self.assertEqual(len(data1), 3)
            
            # Second call should use cache
            data2 = model.get_data()
            self.assertEqual(len(data2), 3)
            
            # Should only read CSV once
            mock_read_csv.assert_called_once()
            
        except ImportError:
            self.skipTest("BaseModel not available")


class TestStarModel(BaseTestCase):
    """Test star model functionality"""
    
    @patch('pandas.read_csv')
    def setUp(self, mock_read_csv):
        super().setUp()
        
        # Mock star data
        self.mock_star_data = pd.DataFrame({
            'id': [0, 71456, 32263],
            'hip': [0, 71456, 32263],
            'x': [0.0, -1.34, -2.64],
            'y': [0.0, -0.20, -7.31],
            'z': [0.0, -1.17, -1.35],
            'mag': [-26.7, -0.27, -1.46],
            'spect': ['G2V', 'G2V', 'A1V'],
            'proper': ['Sol', 'Alpha Centauri A', 'Sirius']
        })
        mock_read_csv.return_value = self.mock_star_data
        
        try:
            from models.star_model import StarModel
            self.star_model = StarModel()
        except ImportError:
            self.skipTest("StarModel not available")
    
    def test_get_all_stars(self):
        """Test getting all stars"""
        stars = self.star_model.get_all_stars()
        self.assertEqual(len(stars), 3)
        self.assertIn('Sol', [star['proper'] for star in stars])
    
    def test_get_star_by_id(self):
        """Test getting a specific star by ID"""
        star = self.star_model.get_star_by_id(0)
        self.assertIsNotNone(star)
        self.assertEqual(star['proper'], 'Sol')
        self.assertEqual(star['mag'], -26.7)
    
    def test_get_star_by_id_not_found(self):
        """Test getting non-existent star returns None"""
        star = self.star_model.get_star_by_id(999999)
        self.assertIsNone(star)
    
    def test_search_stars_by_name(self):
        """Test searching stars by name"""
        results = self.star_model.search_stars('Sirius')
        self.assertEqual(len(results), 1)
        self.assertEqual(results[0]['proper'], 'Sirius')
    
    def test_filter_by_magnitude(self):
        """Test filtering stars by magnitude"""
        bright_stars = self.star_model.filter_by_magnitude(max_mag=0.0)
        # Should include Sol and Alpha Centauri A and Sirius
        self.assertEqual(len(bright_stars), 3)
    
    def test_filter_by_spectral_type(self):
        """Test filtering stars by spectral type"""
        g_stars = self.star_model.filter_by_spectral_type(['G'])
        self.assertEqual(len(g_stars), 2)  # Sol and Alpha Centauri A
        
        a_stars = self.star_model.filter_by_spectral_type(['A'])
        self.assertEqual(len(a_stars), 1)  # Sirius
    
    def test_get_stars_in_range(self):
        """Test getting stars within coordinate range"""
        nearby_stars = self.star_model.get_stars_in_range(
            center_x=0, center_y=0, center_z=0, radius=10
        )
        self.assertGreaterEqual(len(nearby_stars), 1)  # At least Sol
    
    def test_calculate_distance(self):
        """Test distance calculation between stars"""
        distance = self.star_model.calculate_distance(0, 71456)  # Sol to Alpha Centauri
        self.assertGreater(distance, 0)
        self.assertLess(distance, 10)  # Should be about 4.37 light years


class TestStarModelDB(BaseTestCase):
    """Test MontyDB-based star model"""
    
    @patch('database.config.get_collection')
    def setUp(self, mock_get_collection):
        super().setUp()
        
        # Mock database collection
        self.mock_collection = MagicMock()
        mock_get_collection.return_value = self.mock_collection
        
        try:
            from models.star_model_db import StarModelDB
            self.star_model_db = StarModelDB()
        except ImportError:
            self.skipTest("StarModelDB not available")
    
    def test_find_stars(self):
        """Test finding stars with query"""
        mock_stars = [
            {'_id': 0, 'names': {'primary_name': 'Sol'}},
            {'_id': 71456, 'names': {'primary_name': 'Alpha Centauri A'}}
        ]
        self.mock_collection.find.return_value = mock_stars
        
        results = self.star_model_db.find({'coordinates.x': {'$lt': 10}})
        
        self.mock_collection.find.assert_called_once()
        self.assertEqual(len(results), 2)
    
    def test_get_star_by_id_db(self):
        """Test getting star by ID from database"""
        mock_star = {'_id': 0, 'names': {'primary_name': 'Sol'}}
        self.mock_collection.find_one.return_value = mock_star
        
        star = self.star_model_db.get_star_by_id(0)
        
        self.mock_collection.find_one.assert_called_once_with({'_id': 0})
        self.assertEqual(star, mock_star)
    
    def test_search_by_name_db(self):
        """Test searching stars by name in database"""
        mock_results = [{'_id': 32263, 'names': {'primary_name': 'Sirius'}}]
        self.mock_collection.find.return_value = mock_results
        
        results = self.star_model_db.search_by_name('Sirius')
        
        self.mock_collection.find.assert_called_once()
        self.assertEqual(len(results), 1)
    
    def test_get_stars_by_nation_db(self):
        """Test getting stars controlled by a nation"""
        mock_stars = [
            {'_id': 0, 'political': {'nation_id': 'terran_directorate'}},
            {'_id': 71456, 'political': {'nation_id': 'terran_directorate'}}
        ]
        self.mock_collection.find.return_value = mock_stars
        
        results = self.star_model_db.get_stars_by_nation('terran_directorate')
        
        self.mock_collection.find.assert_called_once_with(
            {'political.nation_id': 'terran_directorate'}
        )
        self.assertEqual(len(results), 2)
    
    def test_add_star_db(self):
        """Test adding star to database"""
        star_data = {
            'id': 999001,
            'x': 12.34, 'y': 56.78, 'z': 90.12,
            'mag': 4.5, 'spect': 'G2V'
        }
        
        self.mock_collection.insert_one.return_value = MagicMock()
        
        self.star_model_db.add_star(star_data)
        
        self.mock_collection.insert_one.assert_called_once()
    
    def test_update_star_db(self):
        """Test updating star in database"""
        update_data = {'fictional_name': 'New Name'}
        
        self.mock_collection.update_one.return_value = MagicMock(modified_count=1)
        
        result = self.star_model_db.update_star(999001, update_data)
        
        self.mock_collection.update_one.assert_called_once()
        self.assertTrue(result)


class TestNationModel(BaseTestCase):
    """Test nation model functionality"""
    
    @patch('builtins.open')
    @patch('json.load')
    def setUp(self, mock_json_load, mock_open):
        super().setUp()
        
        # Mock nation data
        self.mock_nation_data = {
            'terran_directorate': {
                'name': 'Terran Directorate',
                'government_type': 'Authoritarian Republic',
                'capital_star_id': 0,
                'territories': [0, 71456, 32263]
            },
            'felgenland_union': {
                'name': 'Felgenland Union',
                'government_type': 'Personal Federal Republic',
                'capital_star_id': 48941,
                'territories': [48941]
            }
        }
        mock_json_load.return_value = self.mock_nation_data
        
        try:
            from models.nation_model import NationModel
            self.nation_model = NationModel()
        except ImportError:
            self.skipTest("NationModel not available")
    
    def test_get_all_nations(self):
        """Test getting all nations"""
        nations = self.nation_model.get_all_nations()
        self.assertEqual(len(nations), 2)
        self.assertIn('terran_directorate', [n['id'] for n in nations])
    
    def test_get_nation_by_id(self):
        """Test getting specific nation by ID"""
        nation = self.nation_model.get_nation_by_id('terran_directorate')
        self.assertIsNotNone(nation)
        self.assertEqual(nation['name'], 'Terran Directorate')
    
    def test_get_nation_territories(self):
        """Test getting nation territories"""
        territories = self.nation_model.get_nation_territories('terran_directorate')
        self.assertEqual(len(territories), 3)
        self.assertIn(0, territories)  # Sol
    
    def test_find_nation_by_star(self):
        """Test finding which nation controls a star"""
        nation = self.nation_model.find_nation_by_star(0)  # Sol
        self.assertEqual(nation['id'], 'terran_directorate')
        
        # Test uncontrolled star
        nation = self.nation_model.find_nation_by_star(999999)
        self.assertIsNone(nation)


class TestNationModelDB(BaseTestCase):
    """Test MontyDB-based nation model"""
    
    @patch('database.config.get_collection')
    def setUp(self, mock_get_collection):
        super().setUp()
        
        self.mock_collection = MagicMock()
        mock_get_collection.return_value = self.mock_collection
        
        try:
            from models.nation_model_db import NationModelDB
            self.nation_model_db = NationModelDB()
        except ImportError:
            self.skipTest("NationModelDB not available")
    
    def test_get_all_nations_db(self):
        """Test getting all nations from database"""
        mock_nations = [
            {'_id': 'terran_directorate', 'name': 'Terran Directorate'},
            {'_id': 'felgenland_union', 'name': 'Felgenland Union'}
        ]
        self.mock_collection.find.return_value = mock_nations
        
        nations = self.nation_model_db.get_all_nations()
        
        self.mock_collection.find.assert_called_once()
        self.assertEqual(len(nations), 2)
    
    def test_add_nation_db(self):
        """Test adding nation to database"""
        nation_data = {
            'id': 'test_nation',
            'name': 'Test Nation',
            'government_type': 'Republic'
        }
        
        self.mock_collection.insert_one.return_value = MagicMock()
        
        self.nation_model_db.add_nation(nation_data)
        
        self.mock_collection.insert_one.assert_called_once()


class TestTradeRouteModelDB(BaseTestCase):
    """Test MontyDB-based trade route model"""
    
    @patch('database.config.get_collection')
    def setUp(self, mock_get_collection):
        super().setUp()
        
        self.mock_collection = MagicMock()
        mock_get_collection.return_value = self.mock_collection
        
        try:
            from models.trade_route_model_db import TradeRouteModelDB
            self.trade_model_db = TradeRouteModelDB()
        except ImportError:
            self.skipTest("TradeRouteModelDB not available")
    
    def test_get_all_routes_db(self):
        """Test getting all trade routes from database"""
        mock_routes = [
            {'_id': 'route1', 'name': 'Test Route 1'},
            {'_id': 'route2', 'name': 'Test Route 2'}
        ]
        self.mock_collection.find.return_value = mock_routes
        
        routes = self.trade_model_db.get_all_trade_routes()
        
        self.mock_collection.find.assert_called_once()
        self.assertEqual(len(routes), 2)
    
    def test_get_routes_by_nation_db(self):
        """Test getting routes by controlling nation"""
        mock_routes = [{'_id': 'route1', 'control': {'controlling_nation': 'test_nation'}}]
        self.mock_collection.find.return_value = mock_routes
        
        routes = self.trade_model_db.get_routes_by_nation('test_nation')
        
        self.mock_collection.find.assert_called_once_with(
            {'control.controlling_nation': 'test_nation'}
        )
        self.assertEqual(len(routes), 1)
    
    def test_add_trade_route_db(self):
        """Test adding trade route to database"""
        route_data = {
            'id': 'test_route',
            'name': 'Test Route',
            'from_star_id': 1,
            'to_star_id': 2
        }
        
        self.mock_collection.insert_one.return_value = MagicMock()
        
        self.trade_model_db.add_trade_route(route_data)
        
        self.mock_collection.insert_one.assert_called_once()


class TestPlanetModel(BaseTestCase):
    """Test planet model functionality"""
    
    def setUp(self):
        super().setUp()
        
        try:
            from models.planet_model import PlanetModel
            self.planet_model = PlanetModel()
        except ImportError:
            self.skipTest("PlanetModel not available")
    
    @patch('fictional_planets.fictional_planet_systems', {
        999001: [
            {
                'name': 'Test Planet',
                'type': 'Terrestrial',
                'distance_au': 1.0,
                'mass_earth': 1.0,
                'habitable': True
            }
        ]
    })
    def test_get_planetary_system(self):
        """Test getting planetary system"""
        system = self.planet_model.get_planetary_system(999001)
        self.assertIsNotNone(system)
        self.assertEqual(len(system['planets']), 1)
        self.assertEqual(system['planets'][0]['name'], 'Test Planet')
    
    def test_get_nonexistent_system(self):
        """Test getting non-existent planetary system"""
        system = self.planet_model.get_planetary_system(999999)
        self.assertIsNone(system)
    
    @patch('fictional_planets.fictional_planet_systems', {
        999001: [
            {'name': 'Planet 1', 'habitable': True},
            {'name': 'Planet 2', 'habitable': False}
        ]
    })
    def test_get_habitable_planets(self):
        """Test getting habitable planets in a system"""
        habitable = self.planet_model.get_habitable_planets(999001)
        self.assertEqual(len(habitable), 1)
        self.assertEqual(habitable[0]['name'], 'Planet 1')


class TestStellarRegionModel(BaseTestCase):
    """Test stellar region model functionality"""
    
    @patch('builtins.open')
    @patch('json.load')
    def setUp(self, mock_json_load, mock_open):
        super().setUp()
        
        # Mock stellar region data
        self.mock_region_data = {
            'regions': [
                {
                    'name': 'Sol Region',
                    'x_min': -50, 'x_max': 50,
                    'y_min': -50, 'y_max': 50,
                    'z_min': -50, 'z_max': 50,
                    'color': '#FF0000'
                }
            ]
        }
        mock_json_load.return_value = self.mock_region_data
        
        try:
            from models.stellar_region_model import StellarRegionModel
            self.region_model = StellarRegionModel()
        except ImportError:
            self.skipTest("StellarRegionModel not available")
    
    def test_get_all_regions(self):
        """Test getting all stellar regions"""
        regions = self.region_model.get_all_regions()
        self.assertEqual(len(regions), 1)
        self.assertEqual(regions[0]['name'], 'Sol Region')
    
    def test_find_region_for_coordinates(self):
        """Test finding region for given coordinates"""
        region = self.region_model.find_region_for_coordinates(0, 0, 0)
        self.assertIsNotNone(region)
        self.assertEqual(region['name'], 'Sol Region')
        
        # Test coordinates outside region
        region = self.region_model.find_region_for_coordinates(100, 100, 100)
        self.assertIsNone(region)


class TestModelPerformance(BaseTestCase):
    """Test model performance characteristics"""
    
    @patch('pandas.read_csv')
    def test_star_model_performance(self, mock_read_csv):
        """Test star model query performance"""
        # Create large mock dataset
        import pandas as pd
        large_dataset = pd.DataFrame({
            'id': range(25000),
            'x': [i * 0.1 for i in range(25000)],
            'y': [i * 0.1 for i in range(25000)],
            'z': [i * 0.1 for i in range(25000)],
            'mag': [5.0] * 25000,
            'spect': ['G2V'] * 25000,
            'proper': [f'Star {i}' for i in range(25000)]
        })
        mock_read_csv.return_value = large_dataset
        
        try:
            from models.star_model import StarModel
            star_model = StarModel()
            
            # Test search performance
            def search_test():
                return star_model.search_stars('Star 1000')
            
            result = self.assertPerformance(search_test, max_time_ms=1000)
            
        except ImportError:
            self.skipTest("StarModel not available")
    
    @patch('database.config.get_collection')
    def test_db_model_performance(self, mock_get_collection):
        """Test database model query performance"""
        mock_collection = MagicMock()
        mock_collection.find.return_value = [{'_id': i} for i in range(1000)]
        mock_get_collection.return_value = mock_collection
        
        try:
            from models.star_model_db import StarModelDB
            star_model_db = StarModelDB()
            
            def db_query_test():
                return star_model_db.find({'coordinates.x': {'$lt': 100}})
            
            result = self.assertPerformance(db_query_test, max_time_ms=500)
            
        except ImportError:
            self.skipTest("StarModelDB not available")


if __name__ == '__main__':
    unittest.main()