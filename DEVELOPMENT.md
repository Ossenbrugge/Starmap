# Starmap Development Guide

## 🚀 Development Environment Setup

### Prerequisites

- **Python 3.8+** (3.9+ recommended)
- **Git** for version control
- **Node.js 14+** (optional, for frontend development)
- **Modern web browser** with WebGL support
- **4GB+ RAM** (8GB+ recommended for development)

### Quick Setup

```bash
# Clone repository
git clone https://github.com/your-username/starmap.git
cd starmap

# Create virtual environment
python -m venv starmap_venv
source starmap_venv/bin/activate  # Linux/Mac
# or
starmap_venv\Scripts\activate     # Windows

# Install dependencies
pip install -r requirements.txt
pip install -r tests/requirements.txt

# Initialize database
chmod +x migrate_to_montydb.sh
./migrate_to_montydb.sh

# Run tests
python tests/run_tests.py --quick

# Start development server
python app_montydb.py
```

### Development Dependencies

```bash
# Core development
pip install flask==3.0.0
pip install montydb==2.5.3
pip install pandas==2.2.0
pip install plotly==5.17.0

# Testing
pip install pytest>=7.0.0
pip install pytest-cov>=4.0.0
pip install coverage>=7.0.0

# Code quality
pip install flake8
pip install black
pip install mypy

# Optional tools
pip install jupyter  # For data analysis
pip install psutil   # For performance monitoring
```

## 🏗️ Architecture Overview

### System Architecture

```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   Frontend      │    │   Backend       │    │   Database      │
│   (HTML/JS)     │◄──►│   (Flask)       │◄──►│   (MontyDB)     │
└─────────────────┘    └─────────────────┘    └─────────────────┘
│                      │                      │
│ • Plotly.js         │ • REST API           │ • SQLite Backend
│ • 3D Visualization  │ • MVC Architecture   │ • Document Store
│ • Interactive UI    │ • Template System    │ • Indexing
└─────────────────┘    └─────────────────┘    └─────────────────┘
```

### MVC Structure

```
app_montydb.py
├── Models (Data Layer)
│   ├── star_model_db.py      # Star data operations
│   ├── nation_model_db.py    # Nation data operations
│   └── trade_route_model_db.py # Trade route operations
│
├── Controllers (Business Logic)
│   ├── star_controller.py    # Star request handling
│   ├── nation_controller.py  # Nation request handling
│   └── planet_controller.py  # Planet request handling
│
├── Views (Presentation Layer)
│   ├── api_views.py          # JSON API responses
│   └── templates/starmap.html # Web interface
│
├── Managers (Service Layer)
│   ├── data_manager.py       # Unified data interface
│   ├── star_manager.py       # Star CRUD operations
│   └── nation_manager.py     # Nation CRUD operations
│
└── Database (Persistence Layer)
    ├── config.py             # Database configuration
    ├── schema.py             # Document schemas
    └── migrate.py            # Migration scripts
```

## 📊 Database Design

### MontyDB Collections

#### Stars Collection
```javascript
{
  _id: 12345,  // Star ID
  catalog_data: {
    hip: 87937,
    hd: "HD 186408",
    // ... other catalog identifiers
  },
  names: {
    primary_name: "Vega",
    fictional_name: "Elysium Prime",
    all_names: ["Vega", "Alpha Lyrae", "Elysium Prime"]
  },
  coordinates: {
    x: 7.76, y: 5.26, z: 13.43,
    ra: 279.23, dec: 38.78, dist: 7.68
  },
  physical_properties: {
    magnitude: 0.03,
    spectral_class: "A0Va",
    luminosity: 40.12
  },
  political: {
    nation_id: "terran_directorate",
    strategic_importance: "capital"
  }
}
```

#### Nations Collection
```javascript
{
  _id: "terran_directorate",
  name: "Terran Directorate",
  government: {
    type: "Authoritarian Republic",
    established_year: 2091
  },
  capital: {
    system: "Sol",
    star_id: 0,
    planet: "Earth"
  },
  territories: [0, 71456, 71453],
  appearance: {
    color: "#1565C0",
    border_color: "#0D47A1"
  }
}
```

### Schema Validation

```python
# Example schema validation
from database.schema import StarSchema

def validate_star_data(star_data):
    """Validate star data against schema"""
    required_fields = ['id', 'x', 'y', 'z', 'mag', 'spect']
    
    for field in required_fields:
        if field not in star_data:
            raise ValueError(f"Missing required field: {field}")
    
    # Validate ranges
    if not -5.0 <= star_data['mag'] <= 15.0:
        raise ValueError(f"Invalid magnitude: {star_data['mag']}")
    
    return StarSchema.create_document(star_data)
```

## 🔧 API Development

### REST API Structure

```python
# Example API endpoint
@app.route('/api/stars', methods=['GET'])
def get_stars():
    """Get filtered stars"""
    try:
        # Get parameters
        mag_limit = request.args.get('mag_limit', 6.0, type=float)
        count_limit = request.args.get('count_limit', 1000, type=int)
        
        # Get data through controller
        controller = StarController()
        stars = controller.get_filtered_stars(
            mag_limit=mag_limit,
            count_limit=count_limit
        )
        
        # Return response
        return jsonify({
            'success': True,
            'stars': stars,
            'metadata': {
                'count': len(stars),
                'mag_limit': mag_limit,
                'processing_time': f"{processing_time:.3f}s"
            }
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500
```

### Error Handling

```python
# Standardized error responses
def handle_api_error(error):
    """Handle API errors consistently"""
    return jsonify({
        'success': False,
        'error': str(error),
        'error_code': error.__class__.__name__,
        'timestamp': datetime.utcnow().isoformat()
    }), 500

# Custom exceptions
class StarNotFoundError(Exception):
    """Raised when star is not found"""
    pass

class ValidationError(Exception):
    """Raised when data validation fails"""
    pass
```

## 🧪 Testing Framework

### Test Structure

```python
# Example test class
class TestStarManager(BaseTestCase):
    """Test star manager functionality"""
    
    @patch('database.config.get_collection')
    def setUp(self, mock_get_collection):
        super().setUp()
        
        # Mock database collection
        self.mock_collection = MagicMock()
        mock_get_collection.return_value = self.mock_collection
        
        from managers.star_manager import StarManager
        self.star_manager = StarManager()
    
    def test_add_star(self):
        """Test adding a new star"""
        star_data = {
            'id': 999001,
            'x': 12.34, 'y': 56.78, 'z': 90.12,
            'mag': 4.5, 'spect': 'G2V'
        }
        
        self.mock_collection.find_one.return_value = None
        self.mock_collection.insert_one.return_value = MagicMock()
        
        result = self.star_manager.add_star(star_data)
        
        self.assertEqual(result, 999001)
        self.mock_collection.insert_one.assert_called_once()
```

### Running Tests

```bash
# Run all tests
python tests/run_tests.py all

# Run specific test categories
python tests/run_tests.py database
python tests/run_tests.py managers
python tests/run_tests.py api

# Run with coverage
python tests/run_tests.py --coverage

# Run performance tests
python tests/run_tests.py --performance
```

## 🎨 Frontend Development

### JavaScript Architecture

```javascript
// Main starmap functionality
class StarmapVisualization {
    constructor() {
        this.plot = null;
        this.stars = [];
        this.nations = [];
        this.filters = {
            magLimit: 6.0,
            countLimit: 1000,
            spectralTypes: ['O', 'B', 'A', 'F', 'G', 'K', 'M']
        };
    }
    
    async initializePlot() {
        // Initialize 3D plot
        this.plot = await Plotly.newPlot('starmap-container', [], {
            // Plot configuration
        });
        
        // Load initial data
        await this.loadStars();
        await this.loadPoliticalOverlays();
    }
    
    async loadStars() {
        try {
            const response = await fetch('/api/stars?' + new URLSearchParams({
                mag_limit: this.filters.magLimit,
                count_limit: this.filters.countLimit
            }));
            
            if (!response.ok) {
                throw new Error(`HTTP ${response.status}`);
            }
            
            const data = await response.json();
            this.stars = data.stars;
            this.updateVisualization();
            
        } catch (error) {
            console.error('Error loading stars:', error);
            this.showError('Failed to load star data');
        }
    }
}
```

### CSS Organization

```css
/* Component-based CSS structure */
.starmap-container {
    width: 100%;
    height: 600px;
    position: relative;
}

.control-panel {
    position: absolute;
    top: 10px;
    left: 10px;
    background: rgba(0, 0, 0, 0.8);
    color: white;
    padding: 15px;
    border-radius: 5px;
}

.data-panel {
    position: absolute;
    top: 10px;
    right: 10px;
    width: 300px;
    max-height: 580px;
    overflow-y: auto;
    background: rgba(0, 0, 0, 0.8);
    color: white;
    padding: 15px;
    border-radius: 5px;
}
```

## 📈 Performance Optimization

### Database Optimization

```python
# Database indexing
def create_indexes():
    """Create performance indexes"""
    db = get_database()
    
    # Coordinate indexes for spatial queries
    db.stars.create_index([
        ('coordinates.x', 1),
        ('coordinates.y', 1),
        ('coordinates.z', 1)
    ])
    
    # Magnitude index for filtering
    db.stars.create_index([('physical_properties.magnitude', 1)])
    
    # Nation index for political queries
    db.stars.create_index([('political.nation_id', 1)])
```

### Caching Strategy

```python
# Model caching
class CachedModel:
    def __init__(self):
        self._cache = {}
        self._cache_timeout = 300  # 5 minutes
    
    def get_cached(self, key):
        """Get cached data if valid"""
        if key in self._cache:
            data, timestamp = self._cache[key]
            if time.time() - timestamp < self._cache_timeout:
                return data
        return None
    
    def set_cache(self, key, data):
        """Set cache data"""
        self._cache[key] = (data, time.time())
```

### Frontend Performance

```javascript
// Efficient data handling
class DataManager {
    constructor() {
        this.cache = new Map();
        this.requestQueue = [];
        this.isProcessing = false;
    }
    
    async loadData(endpoint, params = {}) {
        // Check cache first
        const cacheKey = `${endpoint}:${JSON.stringify(params)}`;
        if (this.cache.has(cacheKey)) {
            return this.cache.get(cacheKey);
        }
        
        // Queue request to avoid duplicates
        return new Promise((resolve, reject) => {
            this.requestQueue.push({ endpoint, params, resolve, reject });
            this.processQueue();
        });
    }
    
    async processQueue() {
        if (this.isProcessing || this.requestQueue.length === 0) return;
        
        this.isProcessing = true;
        
        // Process requests in batches
        while (this.requestQueue.length > 0) {
            const batch = this.requestQueue.splice(0, 5);
            await Promise.all(batch.map(req => this.makeRequest(req)));
        }
        
        this.isProcessing = false;
    }
}
```

## 🔧 Development Tools

### Code Quality Tools

```bash
# Linting
flake8 --max-line-length=120 --ignore=E501,W503 .

# Code formatting
black --line-length=120 .

# Type checking
mypy --ignore-missing-imports .

# Import sorting
isort --profile=black .
```

### Development Scripts

```bash
# Development server with auto-reload
python app_montydb.py --debug

# Database migration
python database/migrate.py

# Test data generation
python -c "
from managers.data_manager import DataManager
dm = DataManager()
# Generate test data
"

# Performance profiling
python -m cProfile -o profile.stats app_montydb.py
```

### Debugging Tools

```python
# Debug configuration
import logging

logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

# Database query logging
import montydb
montydb.set_option('enable_query_logging', True)

# Performance monitoring
import time
import functools

def timing_decorator(func):
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        start = time.time()
        result = func(*args, **kwargs)
        end = time.time()
        print(f"{func.__name__} took {end - start:.3f}s")
        return result
    return wrapper
```

## 📚 Documentation

### Code Documentation

```python
# Docstring standards
class StarManager:
    """
    Manages star data operations including CRUD operations and validation.
    
    This class provides a high-level interface for star data management,
    including creation, retrieval, updating, and deletion of star records.
    It handles data validation and maintains referential integrity.
    
    Attributes:
        collection: MontyDB collection for star data
        validator: Schema validator for star data
        cache: In-memory cache for frequently accessed data
    
    Example:
        >>> star_manager = StarManager()
        >>> star_id = star_manager.add_star({
        ...     'id': 12345,
        ...     'x': 1.0, 'y': 2.0, 'z': 3.0,
        ...     'mag': 5.0, 'spect': 'G2V'
        ... })
        >>> star = star_manager.get_star(star_id)
    """
    
    def add_star(self, star_data: Dict[str, Any]) -> int:
        """
        Add a new star to the database.
        
        Args:
            star_data: Dictionary containing star information with required
                      fields: id, x, y, z, mag, spect
        
        Returns:
            The ID of the newly created star
        
        Raises:
            ValueError: If star data is invalid or star already exists
            DatabaseError: If database operation fails
        
        Example:
            >>> star_data = {
            ...     'id': 12345,
            ...     'x': 1.0, 'y': 2.0, 'z': 3.0,
            ...     'mag': 5.0, 'spect': 'G2V'
            ... }
            >>> star_id = star_manager.add_star(star_data)
        """
```

### API Documentation

```python
# OpenAPI/Swagger documentation
from flask_restx import Api, Resource, fields

api = Api(app, doc='/docs/')

star_model = api.model('Star', {
    'id': fields.Integer(required=True, description='Star ID'),
    'x': fields.Float(required=True, description='X coordinate'),
    'y': fields.Float(required=True, description='Y coordinate'),
    'z': fields.Float(required=True, description='Z coordinate'),
    'mag': fields.Float(required=True, description='Magnitude'),
    'spect': fields.String(required=True, description='Spectral class')
})

@api.route('/stars')
class StarList(Resource):
    @api.doc('get_stars')
    @api.param('mag_limit', 'Magnitude limit', type=float)
    @api.param('count_limit', 'Count limit', type=int)
    def get(self):
        """Get filtered list of stars"""
        pass
    
    @api.doc('add_star')
    @api.expect(star_model)
    def post(self):
        """Add a new star"""
        pass
```

## 🚀 Deployment

### Production Setup

```bash
# Production dependencies
pip install gunicorn
pip install nginx  # System package

# Configuration
gunicorn --bind 0.0.0.0:8000 --workers 4 app_montydb:app

# Systemd service
cat > /etc/systemd/system/starmap.service << EOF
[Unit]
Description=Starmap Application
After=network.target

[Service]
User=starmap
Group=starmap
WorkingDirectory=/opt/starmap
ExecStart=/opt/starmap/venv/bin/gunicorn --bind 0.0.0.0:8000 --workers 4 app_montydb:app
Restart=always

[Install]
WantedBy=multi-user.target
EOF
```

### Docker Setup

```dockerfile
# Dockerfile
FROM python:3.9-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

RUN chmod +x migrate_to_montydb.sh
RUN ./migrate_to_montydb.sh

EXPOSE 8080

CMD ["python", "app_montydb.py"]
```

## 📝 Release Process

### Version Management

```python
# version.py
__version__ = "0.1.0-alpha"
__version_info__ = (0, 1, 0, "alpha")

def get_version():
    return __version__
```

### Release Checklist

1. **Code Quality**
   - [ ] All tests passing
   - [ ] Code coverage > 90%
   - [ ] No linting errors
   - [ ] Documentation updated

2. **Testing**
   - [ ] Unit tests complete
   - [ ] Integration tests passing
   - [ ] Performance tests passing
   - [ ] Manual testing complete

3. **Documentation**
   - [ ] README updated
   - [ ] API documentation current
   - [ ] Change log updated
   - [ ] Migration guide (if needed)

4. **Release**
   - [ ] Version number updated
   - [ ] Git tag created
   - [ ] Release notes published
   - [ ] Distribution packages created

---

**Ready to develop? Start with the [Quick Setup](#quick-setup) and dive into the codebase! 🚀**