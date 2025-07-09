"""
Starmap Test Suite
Comprehensive testing framework for all Starmap features and functions
"""

import os
import sys
import unittest
from unittest.mock import Mock, patch, MagicMock

# Add project root to path for imports
project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, project_root)
sys.path.insert(0, os.path.join(project_root, 'database'))
sys.path.insert(0, os.path.join(project_root, 'managers'))
sys.path.insert(0, os.path.join(project_root, 'models'))
sys.path.insert(0, os.path.join(project_root, 'controllers'))
sys.path.insert(0, os.path.join(project_root, 'views'))
sys.path.insert(0, os.path.join(project_root, 'templates'))

# Test configuration
TEST_CONFIG = {
    'database': {
        'test_db_path': './test_starmap_db',
        'backup_original': True,
        'cleanup_after_tests': True
    },
    'performance': {
        'max_query_time_ms': 1000,
        'max_memory_mb': 100,
        'stress_test_iterations': 1000
    },
    'api': {
        'test_port': 8081,
        'timeout_seconds': 30
    }
}

class BaseTestCase(unittest.TestCase):
    """Base test case with common setup and utilities"""
    
    @classmethod
    def setUpClass(cls):
        """Set up test environment"""
        cls.test_config = TEST_CONFIG
        cls.original_db_path = None
        
    def setUp(self):
        """Set up individual test"""
        self.maxDiff = None  # Show full diff for failures
        
    def tearDown(self):
        """Clean up after individual test"""
        pass
        
    @classmethod
    def tearDownClass(cls):
        """Clean up test environment"""
        pass
        
    def assertPerformance(self, func, max_time_ms=None):
        """Assert that function executes within performance bounds"""
        import time
        max_time = max_time_ms or self.test_config['performance']['max_query_time_ms']
        
        start_time = time.time()
        result = func()
        end_time = time.time()
        
        execution_time_ms = (end_time - start_time) * 1000
        self.assertLess(execution_time_ms, max_time, 
                       f"Function took {execution_time_ms:.2f}ms, expected < {max_time}ms")
        return result
        
    def assertValidStarData(self, star_data):
        """Assert that star data has required fields and valid values"""
        required_fields = ['id', 'x', 'y', 'z', 'mag', 'spect']
        for field in required_fields:
            self.assertIn(field, star_data, f"Missing required field: {field}")
            
        # Validate ranges
        self.assertIsInstance(star_data['id'], int)
        self.assertGreaterEqual(star_data['mag'], -5.0)
        self.assertLessEqual(star_data['mag'], 15.0)
        self.assertIn(star_data['spect'][0], 'OBAFGKM', f"Invalid spectral class: {star_data['spect']}")
        
    def assertValidNationData(self, nation_data):
        """Assert that nation data has required fields and valid values"""
        required_fields = ['id', 'name', 'government_type', 'capital_star_id']
        for field in required_fields:
            self.assertIn(field, nation_data, f"Missing required field: {field}")
            
        self.assertIsInstance(nation_data['capital_star_id'], int)
        self.assertGreater(len(nation_data['name']), 0)
        
    def assertValidTradeRouteData(self, route_data):
        """Assert that trade route data has required fields and valid values"""
        required_fields = ['id', 'name', 'from_star_id', 'to_star_id', 'route_type']
        for field in required_fields:
            self.assertIn(field, route_data, f"Missing required field: {field}")
            
        self.assertIsInstance(route_data['from_star_id'], int)
        self.assertIsInstance(route_data['to_star_id'], int)
        self.assertNotEqual(route_data['from_star_id'], route_data['to_star_id'])

def run_all_tests():
    """Run all tests in the test suite"""
    loader = unittest.TestLoader()
    suite = loader.discover('tests', pattern='test_*.py')
    runner = unittest.TextTestRunner(verbosity=2)
    return runner.run(suite)

def run_specific_test(test_class_name):
    """Run a specific test class"""
    loader = unittest.TestLoader()
    suite = loader.loadTestsFromName(f'tests.{test_class_name}')
    runner = unittest.TextTestRunner(verbosity=2)
    return runner.run(suite)

if __name__ == '__main__':
    run_all_tests()