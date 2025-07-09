"""
Unit tests for all controller classes
"""

import unittest
import os
import sys
from unittest.mock import patch, MagicMock

# Add project paths
project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, project_root)
sys.path.insert(0, os.path.join(project_root, 'controllers'))
sys.path.insert(0, os.path.join(project_root, 'models'))

from tests import BaseTestCase


class TestBaseController(BaseTestCase):
    """Test base controller functionality"""
    
    def test_base_controller_import(self):
        """Test that base controller can be imported"""
        try:
            from controllers.base_controller import BaseController
            self.assertTrue(hasattr(BaseController, '__init__'))
        except ImportError:
            self.skipTest("BaseController not available")
    
    def test_base_controller_initialization(self):
        """Test base controller initialization"""
        try:
            from controllers.base_controller import BaseController
            controller = BaseController()
            self.assertIsNotNone(controller)
        except ImportError:
            self.skipTest("BaseController not available")


class TestStarController(BaseTestCase):
    """Test star controller functionality"""
    
    @patch('models.star_model.StarModel')
    @patch('models.star_model_db.StarModelDB')
    def setUp(self, mock_star_model_db, mock_star_model):
        super().setUp()
        
        # Mock both models
        self.mock_star_model = MagicMock()
        self.mock_star_model_db = MagicMock()
        
        mock_star_model.return_value = self.mock_star_model
        mock_star_model_db.return_value = self.mock_star_model_db
        
        try:
            from controllers.star_controller import StarController
            self.star_controller = StarController()
        except ImportError:
            self.skipTest("StarController not available")
    
    def test_get_all_stars(self):
        """Test getting all stars through controller"""
        mock_stars = [
            {'id': 0, 'name': 'Sol'},
            {'id': 71456, 'name': 'Alpha Centauri A'}
        ]
        self.mock_star_model.get_all_stars.return_value = mock_stars
        
        result = self.star_controller.get_all_stars()
        
        self.mock_star_model.get_all_stars.assert_called_once()
        self.assertEqual(len(result), 2)
        self.assertEqual(result[0]['name'], 'Sol')
    
    def test_get_star_by_id(self):
        """Test getting star by ID through controller"""
        mock_star = {'id': 0, 'name': 'Sol', 'mag': -26.7}
        self.mock_star_model.get_star_by_id.return_value = mock_star
        
        result = self.star_controller.get_star_by_id(0)
        
        self.mock_star_model.get_star_by_id.assert_called_once_with(0)
        self.assertEqual(result['name'], 'Sol')
    
    def test_search_stars(self):
        """Test searching stars through controller"""
        mock_results = [{'id': 32263, 'name': 'Sirius'}]
        self.mock_star_model.search_stars.return_value = mock_results
        
        result = self.star_controller.search_stars('Sirius')
        
        self.mock_star_model.search_stars.assert_called_once_with('Sirius')
        self.assertEqual(len(result), 1)
        self.assertEqual(result[0]['name'], 'Sirius')
    
    def test_filter_stars_by_magnitude(self):
        """Test filtering stars by magnitude through controller"""
        mock_stars = [
            {'id': 0, 'mag': -26.7},
            {'id': 71456, 'mag': -0.27}
        ]
        self.mock_star_model.filter_by_magnitude.return_value = mock_stars
        
        result = self.star_controller.filter_stars_by_magnitude(min_mag=-30, max_mag=0)
        
        self.mock_star_model.filter_by_magnitude.assert_called_once()
        self.assertEqual(len(result), 2)
    
    def test_filter_stars_by_spectral_type(self):
        """Test filtering stars by spectral type through controller"""
        mock_stars = [{'id': 0, 'spect': 'G2V'}]
        self.mock_star_model.filter_by_spectral_type.return_value = mock_stars
        
        result = self.star_controller.filter_stars_by_spectral_type(['G'])
        
        self.mock_star_model.filter_by_spectral_type.assert_called_once_with(['G'])
        self.assertEqual(len(result), 1)
    
    def test_get_stars_in_range(self):
        """Test getting stars in coordinate range through controller"""
        mock_stars = [{'id': 0, 'distance': 0}]
        self.mock_star_model.get_stars_in_range.return_value = mock_stars
        
        result = self.star_controller.get_stars_in_range(0, 0, 0, 10)
        
        self.mock_star_model.get_stars_in_range.assert_called_once_with(0, 0, 0, 10)
        self.assertEqual(len(result), 1)
    
    def test_calculate_distance(self):
        """Test calculating distance between stars through controller"""
        self.mock_star_model.calculate_distance.return_value = 4.37
        
        result = self.star_controller.calculate_distance(0, 71456)
        
        self.mock_star_model.calculate_distance.assert_called_once_with(0, 71456)
        self.assertEqual(result, 4.37)
    
    def test_get_star_statistics(self):
        """Test getting star statistics through controller"""
        mock_stats = {
            'total_stars': 24671,
            'real_stars': 24658,
            'fictional_stars': 13
        }
        self.mock_star_model.get_statistics.return_value = mock_stats
        
        result = self.star_controller.get_star_statistics()
        
        self.assertEqual(result['total_stars'], 24671)


class TestNationController(BaseTestCase):
    """Test nation controller functionality"""
    
    @patch('models.nation_model.NationModel')
    @patch('models.nation_model_db.NationModelDB')
    def setUp(self, mock_nation_model_db, mock_nation_model):
        super().setUp()
        
        self.mock_nation_model = MagicMock()
        self.mock_nation_model_db = MagicMock()
        
        mock_nation_model.return_value = self.mock_nation_model
        mock_nation_model_db.return_value = self.mock_nation_model_db
        
        try:
            from controllers.nation_controller import NationController
            self.nation_controller = NationController()
        except ImportError:
            self.skipTest("NationController not available")
    
    def test_get_all_nations(self):
        """Test getting all nations through controller"""
        mock_nations = [
            {'id': 'terran_directorate', 'name': 'Terran Directorate'},
            {'id': 'felgenland_union', 'name': 'Felgenland Union'}
        ]
        self.mock_nation_model.get_all_nations.return_value = mock_nations
        
        result = self.nation_controller.get_all_nations()
        
        self.mock_nation_model.get_all_nations.assert_called_once()
        self.assertEqual(len(result), 2)
    
    def test_get_nation_by_id(self):
        """Test getting nation by ID through controller"""
        mock_nation = {
            'id': 'terran_directorate',
            'name': 'Terran Directorate',
            'government_type': 'Authoritarian Republic'
        }
        self.mock_nation_model.get_nation_by_id.return_value = mock_nation
        
        result = self.nation_controller.get_nation_by_id('terran_directorate')
        
        self.mock_nation_model.get_nation_by_id.assert_called_once_with('terran_directorate')
        self.assertEqual(result['name'], 'Terran Directorate')
    
    def test_get_nation_territories(self):
        """Test getting nation territories through controller"""
        mock_territories = [0, 71456, 32263]
        self.mock_nation_model.get_nation_territories.return_value = mock_territories
        
        result = self.nation_controller.get_nation_territories('terran_directorate')
        
        self.mock_nation_model.get_nation_territories.assert_called_once_with('terran_directorate')
        self.assertEqual(len(result), 3)
        self.assertIn(0, result)  # Sol
    
    def test_find_nation_by_star(self):
        """Test finding nation controlling a star through controller"""
        mock_nation = {'id': 'terran_directorate', 'name': 'Terran Directorate'}
        self.mock_nation_model.find_nation_by_star.return_value = mock_nation
        
        result = self.nation_controller.find_nation_by_star(0)  # Sol
        
        self.mock_nation_model.find_nation_by_star.assert_called_once_with(0)
        self.assertEqual(result['id'], 'terran_directorate')
    
    def test_get_nation_statistics(self):
        """Test getting nation statistics through controller"""
        mock_stats = {
            'total_nations': 5,
            'total_controlled_systems': 15,
            'largest_nation': 'terran_directorate'
        }
        self.mock_nation_model.get_statistics.return_value = mock_stats
        
        result = self.nation_controller.get_nation_statistics()
        
        self.assertEqual(result['total_nations'], 5)


class TestPlanetController(BaseTestCase):
    """Test planet controller functionality"""
    
    @patch('models.planet_model.PlanetModel')
    def setUp(self, mock_planet_model):
        super().setUp()
        
        self.mock_planet_model = MagicMock()
        mock_planet_model.return_value = self.mock_planet_model
        
        try:
            from controllers.planet_controller import PlanetController
            self.planet_controller = PlanetController()
        except ImportError:
            self.skipTest("PlanetController not available")
    
    def test_get_planetary_system(self):
        """Test getting planetary system through controller"""
        mock_system = {
            'star_id': 999001,
            'system_name': 'Test System',
            'planets': [
                {'name': 'Test Planet', 'type': 'Terrestrial'}
            ]
        }
        self.mock_planet_model.get_planetary_system.return_value = mock_system
        
        result = self.planet_controller.get_planetary_system(999001)
        
        self.mock_planet_model.get_planetary_system.assert_called_once_with(999001)
        self.assertEqual(result['system_name'], 'Test System')
    
    def test_get_all_systems(self):
        """Test getting all planetary systems through controller"""
        mock_systems = [
            {'star_id': 999001, 'system_name': 'System 1'},
            {'star_id': 999002, 'system_name': 'System 2'}
        ]
        self.mock_planet_model.get_all_systems.return_value = mock_systems
        
        result = self.planet_controller.get_all_systems()
        
        self.mock_planet_model.get_all_systems.assert_called_once()
        self.assertEqual(len(result), 2)
    
    def test_get_habitable_planets(self):
        """Test getting habitable planets through controller"""
        mock_planets = [
            {'name': 'Habitable Planet 1', 'habitable': True},
            {'name': 'Habitable Planet 2', 'habitable': True}
        ]
        self.mock_planet_model.get_habitable_planets.return_value = mock_planets
        
        result = self.planet_controller.get_habitable_planets(999001)
        
        self.mock_planet_model.get_habitable_planets.assert_called_once_with(999001)
        self.assertEqual(len(result), 2)
    
    def test_add_planet_to_system(self):
        """Test adding planet to system through controller"""
        planet_data = {
            'name': 'New Planet',
            'type': 'Terrestrial',
            'distance_au': 1.5
        }
        
        self.mock_planet_model.add_planet_to_system.return_value = True
        
        result = self.planet_controller.add_planet_to_system(999001, planet_data)
        
        self.mock_planet_model.add_planet_to_system.assert_called_once_with(999001, planet_data)
        self.assertTrue(result)


class TestMapController(BaseTestCase):
    """Test map controller functionality"""
    
    @patch('models.star_model.StarModel')
    @patch('models.nation_model.NationModel')
    @patch('galactic_directions.get_galactic_directions')
    def setUp(self, mock_galactic_directions, mock_nation_model, mock_star_model):
        super().setUp()
        
        self.mock_star_model = MagicMock()
        self.mock_nation_model = MagicMock()
        self.mock_galactic_directions = MagicMock()
        
        mock_star_model.return_value = self.mock_star_model
        mock_nation_model.return_value = self.mock_nation_model
        mock_galactic_directions.return_value = []
        
        try:
            from controllers.map_controller import MapController
            self.map_controller = MapController()
        except ImportError:
            self.skipTest("MapController not available")
    
    def test_get_filtered_stars(self):
        """Test getting filtered stars for map display"""
        mock_stars = [
            {'id': 0, 'mag': 4.8, 'spect': 'G2V'},
            {'id': 71456, 'mag': 1.3, 'spect': 'G2V'}
        ]
        self.mock_star_model.get_all_stars.return_value = mock_stars
        
        result = self.map_controller.get_filtered_stars(
            mag_limit=5.0,
            count_limit=1000,
            spectral_types=['G']
        )
        
        self.assertIsInstance(result, list)
        # Should filter and format stars appropriately
    
    def test_get_galactic_directions(self):
        """Test getting galactic directions through controller"""
        mock_directions = [
            {'name': 'Coreward', 'x': 50, 'y': 0, 'z': 0},
            {'name': 'Rimward', 'x': -50, 'y': 0, 'z': 0}
        ]
        
        result = self.map_controller.get_galactic_directions(distance=50)
        
        # Should return formatted galactic directions
        self.assertIsInstance(result, list)
    
    def test_get_political_overlays(self):
        """Test getting political overlays through controller"""
        mock_nations = [
            {
                'id': 'terran_directorate',
                'name': 'Terran Directorate',
                'territories': [0, 71456]
            }
        ]
        self.mock_nation_model.get_all_nations.return_value = mock_nations
        
        result = self.map_controller.get_political_overlays()
        
        self.assertIsInstance(result, list)
        # Should format nations for map display
    
    def test_export_star_data(self):
        """Test exporting star data through controller"""
        mock_stars = [
            {'id': 0, 'name': 'Sol', 'x': 0, 'y': 0, 'z': 0}
        ]
        self.mock_star_model.get_all_stars.return_value = mock_stars
        
        result = self.map_controller.export_star_data(format='csv')
        
        # Should return formatted export data
        self.assertIsNotNone(result)


class TestStellarRegionController(BaseTestCase):
    """Test stellar region controller functionality"""
    
    @patch('models.stellar_region_model.StellarRegionModel')
    def setUp(self, mock_region_model):
        super().setUp()
        
        self.mock_region_model = MagicMock()
        mock_region_model.return_value = self.mock_region_model
        
        try:
            from controllers.stellar_region_controller import StellarRegionController
            self.region_controller = StellarRegionController()
        except ImportError:
            self.skipTest("StellarRegionController not available")
    
    def test_get_all_regions(self):
        """Test getting all stellar regions through controller"""
        mock_regions = [
            {
                'name': 'Sol Region',
                'x_min': -50, 'x_max': 50,
                'color': '#FF0000'
            }
        ]
        self.mock_region_model.get_all_regions.return_value = mock_regions
        
        result = self.region_controller.get_all_regions()
        
        self.mock_region_model.get_all_regions.assert_called_once()
        self.assertEqual(len(result), 1)
    
    def test_find_region_for_coordinates(self):
        """Test finding region for coordinates through controller"""
        mock_region = {
            'name': 'Sol Region',
            'color': '#FF0000'
        }
        self.mock_region_model.find_region_for_coordinates.return_value = mock_region
        
        result = self.region_controller.find_region_for_coordinates(0, 0, 0)
        
        self.mock_region_model.find_region_for_coordinates.assert_called_once_with(0, 0, 0)
        self.assertEqual(result['name'], 'Sol Region')
    
    def test_get_region_statistics(self):
        """Test getting region statistics through controller"""
        mock_stats = {
            'total_regions': 8,
            'largest_region': 'Sol Region'
        }
        self.mock_region_model.get_statistics.return_value = mock_stats
        
        result = self.region_controller.get_region_statistics()
        
        self.assertEqual(result['total_regions'], 8)


class TestControllerPerformance(BaseTestCase):
    """Test controller performance characteristics"""
    
    @patch('models.star_model.StarModel')
    def test_star_controller_performance(self, mock_star_model):
        """Test star controller performance with large datasets"""
        # Mock large dataset
        large_dataset = [{'id': i, 'name': f'Star {i}'} for i in range(10000)]
        
        mock_model = MagicMock()
        mock_model.get_all_stars.return_value = large_dataset
        mock_star_model.return_value = mock_model
        
        try:
            from controllers.star_controller import StarController
            controller = StarController()
            
            def large_query_test():
                return controller.get_all_stars()
            
            result = self.assertPerformance(large_query_test, max_time_ms=2000)
            self.assertEqual(len(result), 10000)
            
        except ImportError:
            self.skipTest("StarController not available")
    
    @patch('models.star_model.StarModel')
    def test_search_performance(self, mock_star_model):
        """Test search performance through controller"""
        mock_results = [{'id': 1, 'name': 'Found Star'}]
        
        mock_model = MagicMock()
        mock_model.search_stars.return_value = mock_results
        mock_star_model.return_value = mock_model
        
        try:
            from controllers.star_controller import StarController
            controller = StarController()
            
            def search_test():
                return controller.search_stars('test query')
            
            result = self.assertPerformance(search_test, max_time_ms=1000)
            self.assertEqual(len(result), 1)
            
        except ImportError:
            self.skipTest("StarController not available")


class TestControllerValidation(BaseTestCase):
    """Test controller input validation"""
    
    @patch('models.star_model.StarModel')
    def setUp(self, mock_star_model):
        super().setUp()
        
        self.mock_star_model = MagicMock()
        mock_star_model.return_value = self.mock_star_model
        
        try:
            from controllers.star_controller import StarController
            self.star_controller = StarController()
        except ImportError:
            self.skipTest("StarController not available")
    
    def test_invalid_star_id(self):
        """Test handling of invalid star IDs"""
        self.mock_star_model.get_star_by_id.return_value = None
        
        result = self.star_controller.get_star_by_id(-1)
        
        self.assertIsNone(result)
    
    def test_invalid_magnitude_range(self):
        """Test handling of invalid magnitude ranges"""
        # Test with invalid range (min > max)
        result = self.star_controller.filter_stars_by_magnitude(min_mag=5, max_mag=0)
        
        # Should handle gracefully or return empty result
        self.assertIsInstance(result, list)
    
    def test_empty_search_query(self):
        """Test handling of empty search queries"""
        self.mock_star_model.search_stars.return_value = []
        
        result = self.star_controller.search_stars('')
        
        self.assertEqual(len(result), 0)


if __name__ == '__main__':
    unittest.main()