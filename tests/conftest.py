"""
Pytest configuration and fixtures for Starmap tests
"""

import pytest
import os
import sys
import tempfile
import shutil
from unittest.mock import patch, MagicMock

# Add project paths
project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, project_root)
sys.path.insert(0, os.path.join(project_root, 'database'))


@pytest.fixture(scope="session")
def test_database():
    """Create a test database for the session"""
    test_db_path = tempfile.mkdtemp(prefix="test_starmap_")
    original_db_path = None
    
    # Mock the database path
    with patch('database.config.DatabaseConfig') as mock_config:
        mock_instance = MagicMock()
        mock_instance.db_path = test_db_path
        mock_config.return_value = mock_instance
        
        yield test_db_path
    
    # Cleanup
    if os.path.exists(test_db_path):
        shutil.rmtree(test_db_path)


@pytest.fixture
def sample_star_data():
    """Sample star data for testing"""
    return {
        'id': 999001,
        'x': 12.34,
        'y': 56.78,
        'z': 90.12,
        'mag': 4.5,
        'spect': 'G2V',
        'name': 'Test Star',
        'fictional_name': 'Alpha Test',
        'fictional_description': 'A test star for unit testing'
    }


@pytest.fixture
def sample_nation_data():
    """Sample nation data for testing"""
    return {
        'id': 'test_nation',
        'name': 'Test Nation',
        'full_name': 'The Test Nation',
        'government_type': 'Test Republic',
        'capital_system': 'Test System',
        'capital_star_id': 999001,
        'capital_planet': 'Test World',
        'established_year': 2350,
        'description': 'A test nation for unit testing',
        'territories': [999001, 999002],
        'color': '#FF0000'
    }


@pytest.fixture
def sample_trade_route_data():
    """Sample trade route data for testing"""
    return {
        'id': 'test_route',
        'name': 'Test Route',
        'from_star_id': 999001,
        'from_system': 'Test System A',
        'to_star_id': 999002,
        'to_system': 'Test System B',
        'route_type': 'Test Route',
        'controlling_nation': 'test_nation',
        'cargo_types': ['Test Cargo'],
        'travel_time_days': 7,
        'frequency': 'Weekly',
        'security_level': 'Standard',
        'description': 'A test route for unit testing'
    }


@pytest.fixture
def sample_planetary_system_data():
    """Sample planetary system data for testing"""
    return {
        'star_id': 999001,
        'system_name': 'Test System',
        'planets': [
            {
                'name': 'Test Planet',
                'type': 'Terrestrial',
                'distance_au': 1.0,
                'mass_earth': 1.0,
                'radius_earth': 1.0,
                'orbital_period_days': 365,
                'temperature_k': 288,
                'atmosphere': 'N2, O2',
                'habitable': True,
                'inhabited': False
            }
        ],
        'total_planets': 1,
        'has_life': False,
        'colonized': False,
        'exploration_level': 'Surveyed',
        'description': 'A test planetary system'
    }


@pytest.fixture
def mock_database():
    """Mock database connection"""
    with patch('database.config.get_database') as mock_db:
        mock_db_instance = MagicMock()
        mock_db.return_value = mock_db_instance
        
        # Mock collections
        mock_db_instance.stars = MagicMock()
        mock_db_instance.nations = MagicMock()
        mock_db_instance.trade_routes = MagicMock()
        mock_db_instance.planetary_systems = MagicMock()
        mock_db_instance.stellar_regions = MagicMock()
        
        yield mock_db_instance


@pytest.fixture
def flask_app():
    """Create Flask test app"""
    import app_montydb
    app_montydb.app.config['TESTING'] = True
    app_montydb.app.config['WTF_CSRF_ENABLED'] = False
    return app_montydb.app


@pytest.fixture
def flask_client(flask_app):
    """Create Flask test client"""
    return flask_app.test_client()


# Performance testing fixtures
@pytest.fixture
def performance_timer():
    """Timer for performance tests"""
    import time
    
    class Timer:
        def __init__(self):
            self.start_time = None
            self.end_time = None
            
        def start(self):
            self.start_time = time.time()
            
        def stop(self):
            self.end_time = time.time()
            
        @property
        def elapsed_ms(self):
            if self.start_time and self.end_time:
                return (self.end_time - self.start_time) * 1000
            return None
            
        def assert_under(self, max_ms):
            assert self.elapsed_ms < max_ms, f"Operation took {self.elapsed_ms:.2f}ms, expected < {max_ms}ms"
    
    return Timer()


@pytest.fixture
def stress_test_data():
    """Generate data for stress testing"""
    def generate_stars(count=1000):
        return [
            {
                'id': 900000 + i,
                'x': (i % 100) * 0.1,
                'y': ((i // 100) % 100) * 0.1,
                'z': (i // 10000) * 0.1,
                'mag': 5.0 + (i % 10) * 0.1,
                'spect': ['G', 'K', 'M'][i % 3] + str((i % 5) + 1) + 'V',
                'name': f'Test Star {i}'
            }
            for i in range(count)
        ]
    
    def generate_nations(count=50):
        return [
            {
                'id': f'test_nation_{i}',
                'name': f'Test Nation {i}',
                'government_type': 'Test Republic',
                'capital_star_id': 900000 + i,
                'territories': [900000 + i + j for j in range(5)]
            }
            for i in range(count)
        ]
    
    def generate_trade_routes(count=200):
        return [
            {
                'id': f'test_route_{i}',
                'name': f'Test Route {i}',
                'from_star_id': 900000 + i,
                'to_star_id': 900000 + i + 1,
                'route_type': 'Test Route',
                'controlling_nation': f'test_nation_{i % 50}'
            }
            for i in range(count)
        ]
    
    return {
        'stars': generate_stars,
        'nations': generate_nations,
        'trade_routes': generate_trade_routes
    }