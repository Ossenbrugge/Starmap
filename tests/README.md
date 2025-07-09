# Starmap Test Suite

## Overview

This comprehensive test suite provides thorough testing coverage for all Starmap features and functions. The tests are designed to ensure robustness, performance, and reliability of the application under various conditions.

## Test Structure

The test suite is organized into the following categories:

### 🧪 Unit Tests
- **`test_database.py`** - Database layer (MontyDB) tests
- **`test_managers.py`** - CRUD manager tests
- **`test_models.py`** - Data model tests
- **`test_controllers.py`** - Controller layer tests
- **`test_api.py`** - API endpoint tests

### 🔗 Integration Tests
- **`test_integration.py`** - End-to-end workflow tests

### 🚀 Performance Tests
- **`test_stress.py`** - Stress testing and performance validation

### ⚙️ Configuration
- **`__init__.py`** - Test framework and base classes
- **`conftest.py`** - Pytest configuration and fixtures
- **`README.md`** - This documentation

## Quick Start

### Prerequisites

```bash
# Install testing dependencies
pip install pytest pytest-cov unittest-xml-reporting

# Ensure main dependencies are installed
pip install -r requirements.txt
```

### Running Tests

#### Run All Tests
```bash
# From project root
python -m pytest tests/ -v

# Or using unittest
python -m unittest discover tests -v
```

#### Run Specific Test Categories
```bash
# Unit tests only
python -m pytest tests/test_*.py -v

# Integration tests only
python -m pytest tests/test_integration.py -v

# Stress tests only
python -m pytest tests/test_stress.py -v
```

#### Run Individual Test Files
```bash
# Database tests
python -m pytest tests/test_database.py -v

# Manager tests
python -m pytest tests/test_managers.py -v

# API tests
python -m pytest tests/test_api.py -v
```

#### Run Specific Test Methods
```bash
# Specific test class
python -m pytest tests/test_database.py::TestDatabaseConfig -v

# Specific test method
python -m pytest tests/test_api.py::TestAPIEndpoints::test_api_stars_endpoint -v
```

### Test Coverage

```bash
# Run tests with coverage report
python -m pytest tests/ --cov=. --cov-report=html --cov-report=term

# View coverage report
open htmlcov/index.html
```

## Test Categories

### Database Tests (`test_database.py`)

Tests the MontyDB database layer:

- **Database Configuration**: Connection setup and initialization
- **Schema Validation**: Document structure and validation
- **Migration Testing**: Data migration from CSV/JSON to MontyDB
- **Performance**: Query performance and optimization

```bash
# Run database tests
python -m pytest tests/test_database.py -v
```

### Manager Tests (`test_managers.py`)

Tests all CRUD managers:

- **DataManager**: Unified data management interface
- **StarManager**: Star CRUD operations
- **NationManager**: Nation and territory management
- **TradeRouteManager**: Trade route operations
- **PlanetarySystemManager**: Planetary system management
- **FelgenlandCleanup**: Cleanup functionality

```bash
# Run manager tests
python -m pytest tests/test_managers.py -v
```

### Model Tests (`test_models.py`)

Tests data models and business logic:

- **BaseModel**: Base model functionality and caching
- **StarModel**: Star data operations (CSV version)
- **StarModelDB**: Star data operations (MontyDB version)
- **NationModel**: Nation data operations
- **PlanetModel**: Planetary system data
- **Performance**: Model performance characteristics

```bash
# Run model tests
python -m pytest tests/test_models.py -v
```

### Controller Tests (`test_controllers.py`)

Tests controller layer business logic:

- **StarController**: Star data processing
- **NationController**: Nation data processing
- **PlanetController**: Planetary system processing
- **MapController**: Map visualization data
- **StellarRegionController**: Galactic region processing
- **Input Validation**: Parameter validation and error handling

```bash
# Run controller tests
python -m pytest tests/test_controllers.py -v
```

### API Tests (`test_api.py`)

Tests Flask API endpoints:

- **Endpoint Testing**: All REST API endpoints
- **Request/Response**: JSON API communication
- **Error Handling**: HTTP error codes and messages
- **Security**: Input validation and XSS protection
- **Performance**: API response times
- **MontyDB Features**: Enhanced API endpoints

```bash
# Run API tests
python -m pytest tests/test_api.py -v
```

### Integration Tests (`test_integration.py`)

Tests complete workflows:

- **Data Workflows**: Complete CRUD workflows
- **Template Usage**: Template-based data creation
- **Cleanup Workflows**: Felgenland cleanup processes
- **API Integration**: End-to-end API workflows
- **Validation Integration**: System-wide validation
- **Performance Integration**: Realistic load testing

```bash
# Run integration tests
python -m pytest tests/test_integration.py -v
```

### Stress Tests (`test_stress.py`)

Tests system robustness under load:

- **Database Stress**: Concurrent database access
- **API Stress**: High-load API testing
- **Memory Stress**: Memory usage and management
- **Data Integrity**: Concurrent data modifications
- **System Limits**: Maximum capacity testing

```bash
# Run stress tests (may take longer)
python -m pytest tests/test_stress.py -v
```

## Performance Benchmarks

### Expected Performance Targets

| Operation | Target Time | Stress Test Limit |
|-----------|-------------|-------------------|
| Database Query | < 200ms | < 1000ms |
| API Response | < 500ms | < 2000ms |
| Bulk Insert (1000 items) | < 5s | < 10s |
| Search Query | < 1s | < 3s |
| Template Creation | < 100ms | < 500ms |

### Memory Usage Targets

| Component | Normal Usage | Stress Test Limit |
|-----------|-------------|-------------------|
| DataManager | < 50MB | < 150MB |
| API Server | < 100MB | < 300MB |
| Large Queries | < 200MB | < 500MB |

## Test Configuration

### Environment Variables

```bash
# Set test database path
export TEST_DB_PATH="./test_starmap_db"

# Enable debug mode for tests
export STARMAP_TEST_DEBUG=1

# Set test timeout (seconds)
export STARMAP_TEST_TIMEOUT=300
```

### Test Settings

The test configuration is defined in `tests/__init__.py`:

```python
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
```

## Writing New Tests

### Test Structure

Follow this structure for new tests:

```python
"""
Test module description
"""

import unittest
from unittest.mock import patch, MagicMock
from tests import BaseTestCase

class TestYourFeature(BaseTestCase):
    """Test your feature"""
    
    def setUp(self):
        super().setUp()
        # Setup test data
        
    def test_specific_functionality(self):
        """Test specific functionality"""
        # Test implementation
        self.assertEqual(expected, actual)
        
    def test_error_handling(self):
        """Test error conditions"""
        with self.assertRaises(ExpectedError):
            # Code that should raise error
            
    def test_performance(self):
        """Test performance requirements"""
        def operation_to_test():
            return your_function()
            
        result = self.assertPerformance(operation_to_test, max_time_ms=1000)
```

### Best Practices

1. **Use Descriptive Names**: Test method names should clearly describe what is being tested
2. **Test One Thing**: Each test method should test one specific behavior
3. **Use Mocks**: Mock external dependencies to isolate unit tests
4. **Test Edge Cases**: Include tests for boundary conditions and error cases
5. **Performance Tests**: Use `assertPerformance()` for performance-critical code
6. **Documentation**: Include docstrings explaining complex test scenarios

### Mocking Guidelines

```python
# Mock database operations
@patch('database.config.get_database')
def test_with_mocked_db(self, mock_db):
    mock_db_instance = MagicMock()
    mock_db.return_value = mock_db_instance
    # Test implementation

# Mock API responses
with patch('requests.get') as mock_get:
    mock_get.return_value.json.return_value = {'data': 'test'}
    # Test implementation
```

## Continuous Integration

### GitHub Actions

Create `.github/workflows/tests.yml`:

```yaml
name: Run Tests

on: [push, pull_request]

jobs:
  test:
    runs-on: ubuntu-latest
    
    steps:
    - uses: actions/checkout@v2
    
    - name: Set up Python
      uses: actions/setup-python@v2
      with:
        python-version: 3.9
        
    - name: Install dependencies
      run: |
        pip install -r requirements.txt
        pip install pytest pytest-cov
        
    - name: Run tests
      run: |
        python -m pytest tests/ --cov=. --cov-report=xml
        
    - name: Upload coverage
      uses: codecov/codecov-action@v1
```

### Pre-commit Hooks

Create `.pre-commit-config.yaml`:

```yaml
repos:
  - repo: local
    hooks:
      - id: tests
        name: tests
        entry: python -m pytest tests/
        language: system
        pass_filenames: false
        always_run: true
```

## Troubleshooting

### Common Issues

#### Import Errors
```bash
# Add project to Python path
export PYTHONPATH="${PYTHONPATH}:$(pwd)"

# Or run from project root
cd /path/to/Starmap
python -m pytest tests/
```

#### Database Connection Issues
```bash
# Check MontyDB installation
pip list | grep montydb

# Verify test database path
ls -la ./test_starmap_db/
```

#### Performance Test Failures
```bash
# Run with verbose output
python -m pytest tests/test_stress.py -v -s

# Adjust performance limits in test configuration
```

#### Memory Issues
```bash
# Install psutil for memory testing
pip install psutil

# Monitor memory during tests
python -m pytest tests/test_stress.py::TestMemoryStress -v
```

### Test Debugging

```bash
# Run specific failing test with debugging
python -m pytest tests/test_api.py::TestAPIEndpoints::test_api_stars_endpoint -v -s --pdb

# Print test output
python -m pytest tests/ -v -s

# Run tests with coverage and keep temp files
python -m pytest tests/ --cov=. --cov-report=html --keeptemp
```

## Performance Monitoring

### Profiling Tests

```python
import cProfile
import pstats

def profile_test():
    pr = cProfile.Profile()
    pr.enable()
    
    # Your test code here
    
    pr.disable()
    stats = pstats.Stats(pr)
    stats.sort_stats('cumulative')
    stats.print_stats(10)
```

### Memory Profiling

```python
import tracemalloc

def memory_profile_test():
    tracemalloc.start()
    
    # Your test code here
    
    current, peak = tracemalloc.get_traced_memory()
    print(f"Current memory usage: {current / 1024 / 1024:.1f} MB")
    print(f"Peak memory usage: {peak / 1024 / 1024:.1f} MB")
    tracemalloc.stop()
```

## Contributing

### Adding New Test Categories

1. Create new test file: `tests/test_new_feature.py`
2. Follow existing patterns and use `BaseTestCase`
3. Add tests to cover all functionality
4. Update this README with new test category
5. Run full test suite to ensure no regressions

### Test Coverage Goals

- **Unit Tests**: 90%+ code coverage
- **Integration Tests**: All major workflows covered
- **API Tests**: All endpoints tested
- **Performance Tests**: All critical paths benchmarked

## Related Documentation

- **[📖 Main Documentation](../README.md)** - Complete application overview
- **[🗄️ MontyDB Implementation](../README_MONTYDB.md)** - Database system details
- **[📝 Data Management Guide](../DATA_MANAGEMENT_GUIDE.md)** - CRUD operations and templates
- **[🔌 API Reference](../README.md#-api-reference)** - REST API documentation

---

**🧪 Ready to test?** Run `python -m pytest tests/ -v` to execute the full test suite and ensure system robustness!