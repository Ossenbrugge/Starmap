"""
Pytest configuration and shared fixtures for Starmap tests
"""

import pytest
import os
import tempfile
import shutil
from pathlib import Path

# Set up test environment
os.environ["STARMAP_SECRET_KEY"] = "test-secret-key"
os.environ["FLASK_ENV"] = "testing"

@pytest.fixture(scope="session")
def project_root():
    """Get project root directory"""
    return Path(__file__).parent.parent

@pytest.fixture(scope="session")
def test_data_dir(project_root):
    """Get test data directory"""
    return project_root / "tests" / "data"

@pytest.fixture
def temp_dir():
    """Create temporary directory for tests"""
    temp_dir = tempfile.mkdtemp()
    yield Path(temp_dir)
    shutil.rmtree(temp_dir)

@pytest.fixture
def app_instance():
    """Create Flask app instance for testing"""
    import sys
    sys.path.insert(0, str(Path(__file__).parent.parent))
    
    from app import app
    app.config['TESTING'] = True
    app.config['SECRET_KEY'] = 'test-secret-key'
    
    with app.test_client() as client:
        with app.app_context():
            yield client

@pytest.fixture
def auth_headers():
    """Headers for authenticated requests"""
    return {
        'Content-Type': 'application/json',
        'Authorization': 'Bearer test-token'
    }

@pytest.fixture
def sample_star_data():
    """Sample star data for testing"""
    return {
        "id": 99999,
        "name": "Test Star",
        "x": 10.0,
        "y": 20.0, 
        "z": 30.0,
        "magnitude": 5.5,
        "spectral_class": "G2V",
        "distance": 25.0
    }

@pytest.fixture
def sample_nation_data():
    """Sample nation data for testing"""
    return {
        "id": "test_nation",
        "name": "Test Nation",
        "full_name": "Test Nation Republic",
        "government_type": "Republic",
        "capital_system": "Test System",
        "territories": [99999],
        "primary_color": "#ff0000"
    }

@pytest.fixture(autouse=True)
def setup_test_logging():
    """Set up logging for tests"""
    import logging
    logging.getLogger().setLevel(logging.WARNING)  # Reduce noise during tests
    yield
    logging.getLogger().setLevel(logging.INFO)  # Restore after tests

# Markers
pytest.mark.unit = pytest.mark.unit
pytest.mark.integration = pytest.mark.integration  
pytest.mark.performance = pytest.mark.performance
pytest.mark.security = pytest.mark.security
pytest.mark.slow = pytest.mark.slow