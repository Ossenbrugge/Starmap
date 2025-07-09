# Starmap: Interactive 3D Stellar Cartography for the Felgenland Saga

An advanced 3D starmap application for science fiction world-building, featuring political overlays, planetary systems, trade route visualization, and galactic navigation tools. Built with Flask (Python) and Plotly.js, designed specifically for the Felgenland Saga universe.

## 🌟 Features Overview

### Core Visualization
- **Interactive 3D Starmap**: Navigate through 24,670+ real stars with smooth rotation, zoom, and pan controls
- **Real Astronomical Data**: Hipparcos star catalog with accurate positions, magnitudes, and spectral classifications
- **Multi-layered Overlays**: Political territories, trade routes, galactic directions, and stellar regions
- **High-Performance Rendering**: Optimized for large datasets with configurable star limits

### Political & Economic Systems
- **Fictional Nations**: 5 major political entities with territories, capitals, and descriptions
- **Trade Route Networks**: 28 comprehensive trade routes across 8 categories
- **Economic Zones**: Terran Core and Felgenland Free Trade zones with regulations
- **Territory Visualization**: Colored borders and spheres of influence around controlled systems

### Planetary Systems
- **Interactive System Maps**: Detailed orbital diagrams with animation support
- **Exoplanet Database**: Real and fictional worlds with comprehensive planetary data
- **Habitable Zone Display**: Visual indicators for potentially habitable worlds
- **Moon Systems**: Support for detailed moon data and orbital mechanics

### Advanced Navigation
- **Galactic Coordinate System**: Cardinal directions (Coreward, Rimward, Spinward, Anti-Spinward)
- **Stellar Regions**: Galactic octants with color-coded boundaries and star statistics
- **Distance Measurement**: Precise calculations between any two star systems
- **Search & Filtering**: Advanced search by name, spectral type, and properties

### Data Export & Integration
- **Multi-format Export**: PNG, JPG, PDF export with/without UI elements
- **CSV Data Export**: Complete star data with custom filtering
- **RESTful API**: Comprehensive endpoints for external integration
- **Real-time Updates**: Live data synchronization without page refresh

## 📖 Documentation Hub

### Getting Started
- **[Installation & Setup](#-installation)** - Get up and running quickly
- **[User Interface Guide](#-user-interface)** - Master the starmap controls
- **[First Steps](#first-steps)** - Tutorial for new users

### Feature Guides
- **[🪐 Planetary System Guide](PLANETARY_SYSTEM_GUIDE.md)** - Complete guide to planetary systems, adding worlds, and orbital mechanics
- **[🧭 Galactic Directions Guide](GALACTIC_DIRECTIONS.md)** - Coordinate systems, navigation overlays, and galactic orientation
- **[🛣️ Trade Routes Guide](TRADE_ROUTES_README.md)** - Trade network structure, route management, and economic zones

### Technical Documentation
- **[🏗️ Application Architecture](#-application-architecture)** - MVC structure and component overview
- **[📊 Data Sources](#-data-sources)** - Understanding the star catalogs and fictional data
- **[🔌 API Reference](#-api-reference)** - Complete backend API documentation
- **[🧪 Data Analysis Reports](#-data-analysis-reports)** - System verification and data quality reports

### Science Fiction Context
- **[🌌 The Felgenland Saga Universe](#-the-felgenland-saga-universe)** - Political entities, conflicts, and world-building
- **[📊 Data Analysis Report](PLANETARY_SYSTEMS_ANALYSIS.md)** - Comprehensive analysis of planetary systems and data integrity

## 🚀 Installation

### Prerequisites
- **Python 3.8+** (3.9+ recommended)
- **Modern web browser** with WebGL support
- **4GB RAM** (8GB+ recommended for large datasets)

### Quick Setup
```bash
# 1. Clone the repository
git clone <repository-url>
cd Starmap

# 2. Set up virtual environment
chmod +x activate_venv.sh
./activate_venv.sh

# 3. Launch the application
chmod +x run_starmap.sh
./run_starmap.sh
```

### Manual Setup
```bash
# Create virtual environment
python -m venv starmap_venv
source starmap_venv/bin/activate  # Linux/Mac
# or
starmap_venv\Scripts\activate  # Windows

# Install dependencies
pip install -r requirements.txt

# Run application
python app.py
```

### Access Points
- **Local**: http://localhost:8080
- **Network**: http://[your-ip]:8080
- **Status**: Check console for startup messages

## 🎮 User Interface

### Main Control Panel (Left)
- **Star Filtering**
  - Magnitude limits (0.0 to 15.0)
  - Star count limits (100 to 5000)
  - Spectral type filters (O, B, A, F, G, K, M)
- **Search Tools**
  - Star name search with autocomplete
  - Constellation filtering
  - Distance-based queries
- **Measurement Tools**
  - Distance measurement between stars
  - Coordinate display and conversion
  - Stellar region identification

### Overlay Controls
- **Political Overlays**
  - Nation territories with colored borders
  - Capital system highlighting
  - Government type indicators
- **Trade Route Networks**
  - 28 routes across 8 categories
  - Route frequency and cargo type display
  - Economic zone boundaries
- **Galactic Navigation**
  - Cardinal direction markers
  - Coordinate grid system
  - Stellar region boundaries

### Data Panel (Right)
- **Star Information**
  - Comprehensive stellar data
  - Spectral classification details
  - Distance and motion data
  - Fictional names and descriptions
- **Planetary Systems**
  - Interactive system maps
  - Orbital parameters and planet details
  - Habitable zone information
  - Moon system data
- **Political Data**
  - Nation allegiances
  - Trade route connections
  - Economic zone classifications
  - Historical establishment dates

### Export & Tools
- **Export Options**
  - Image formats: PNG, JPG, PDF
  - Data export: CSV with filtering
  - Include/exclude UI elements
- **View Controls**
  - Panel visibility toggles
  - Zoom and orientation reset
  - Full-screen mode

## 🏗️ Application Architecture

### MVC Structure
```
Starmap/
├── app.py                      # Main Flask application
├── requirements.txt            # Python dependencies
├── run_starmap.sh             # Launch script
├── activate_venv.sh           # Environment setup
│
├── models/                    # Data Layer
│   ├── star_model.py         # Star data management (24,670+ stars)
│   ├── planet_model.py       # Planetary system data
│   ├── nation_model.py       # Political entities and territories
│   ├── stellar_region_model.py # Galactic regions and boundaries
│   └── base_model.py         # Base model with caching
│
├── controllers/               # Business Logic
│   ├── star_controller.py    # Star operations and filtering
│   ├── planet_controller.py  # Planetary system operations
│   ├── nation_controller.py  # Political and trade route logic
│   ├── map_controller.py     # Galactic navigation features
│   ├── stellar_region_controller.py # Region management
│   └── base_controller.py    # Base controller functionality
│
├── views/                     # Presentation Layer
│   ├── api_views.py          # JSON API responses
│   └── base_view.py          # Base view functionality
│
├── static/                    # Frontend Assets
│   ├── css/style.css         # Application styling
│   └── js/
│       ├── starmap.js        # Main visualization logic
│       └── planetary_system.js # System minimap functionality
│
├── templates/
│   └── starmap.html          # Main application interface
│
└── data/                     # See Data Sources below
```

### Key Components
- **Flask Backend**: RESTful API with comprehensive endpoints
- **Plotly.js Frontend**: High-performance 3D visualization
- **Pandas Data Processing**: Efficient star catalog management
- **Caching System**: Optimized performance for large datasets
- **MVC Architecture**: Clean separation of concerns

## 📊 Data Sources

### Astronomical Data
- **`stars_output.csv`** - 24,670+ stars from Hipparcos catalog
  - Positions, magnitudes, spectral types
  - Proper motion and parallax data
  - Constellation assignments
- **`fictional_stars.csv`** - 13 additional fictional stars
  - Custom systems for story requirements
  - Consistent with astronomical constraints

### Science Fiction Content
- **`nations_data.json`** - Political entities and territories
  - 5 major nations with complete profiles
  - Economic zones and government types
  - Historical establishment dates
- **`trade_routes_data.json`** - 28 comprehensive trade routes
  - 8 categories from major nation routes to frontier exploration
  - Cargo types, frequencies, and security levels
  - Economic zone classifications
- **`fictional_planets.py`** - Planetary systems and worlds
  - 6 detailed star systems with 29+ planets
  - Orbital mechanics and atmospheric data
  - Fictional world descriptions

### Navigation & Naming
- **`stellar_regions.json`** - Galactic octant definitions
  - Color-coded region boundaries
  - Star count statistics per region
- **`fictional_names.py`** - Custom star system names
  - Fictional designations for story consistency
  - Source attribution and descriptions
- **`galactic_directions.py`** - Coordinate system management
  - Cardinal direction calculations
  - Grid overlay generation

### Supporting Systems
- **`star_naming.py`** - Designation management system
- **`habitability.py`** - Planetary habitability assessment
- **`fictional_nations.py`** - Political entity utilities

## 🔌 API Reference

### Star Data Endpoints
```http
GET /api/stars                         # Get filtered star list
GET /api/star/{id}                     # Get detailed star info
GET /api/star/{id}/habitability        # Get habitability assessment
GET /api/search?q={query}              # Search stars by name
GET /api/distance?star1={id}&star2={id} # Calculate distances
GET /api/spectral-types               # Get spectral type list
GET /export/csv                       # Export star data as CSV
```

### Political & Economic Data
```http
GET /api/nations                      # Get all political entities
GET /api/nation/{id}                  # Get nation details
GET /api/trade-routes                 # Get trade route networks
```

### Planetary Systems
```http
GET /api/systems                      # Get all planetary systems
GET /api/system/{star_id}             # Get planetary system details
POST /api/planet/add                  # Add new planet (JSON body)
```

### Galactic Navigation
```http
GET /api/galactic-directions          # Get cardinal direction markers
GET /api/stellar-regions              # Get galactic region data
GET /api/stellar-regions/summary      # Get region statistics
GET /api/stellar-region/{name}        # Get region details
GET /api/stellar-region/{name}/boundaries # Get region boundaries
```

### Response Formats
All endpoints return JSON with standardized error handling:
```json
{
  "success": true,
  "data": { ... },
  "metadata": {
    "total_count": 1000,
    "filters_applied": {...},
    "processing_time": "0.045s"
  }
}
```

## 🌌 The Felgenland Saga Universe

### Major Political Entities

#### 🔵 Terran Directorate
- **Capital**: Sol (Earth)
- **Government**: Authoritarian Republic
- **Territory**: 6 core systems including Alpha Centauri
- **Specialty**: Technology, military, central administration
- **Trade Routes**: 6 primary routes connecting core systems

#### 🔴 Felgenland Union
- **Capital**: Holsten Tor (Stahlburgh)
- **Government**: Personal Federal Republic
- **Territory**: 5 rimward systems
- **Specialty**: Trade, resource extraction, cultural exchange
- **Trade Routes**: 3 internal routes plus connections to allies

#### 🟦 Protelani Republic
- **Capital**: Protelan (61 Ursae Majoris)
- **Government**: Ultra-Capitalist Republic
- **Territory**: 1 system (Protelan)
- **Specialty**: Rimward trade hub, corporate operations
- **Trade Routes**: 4 routes connecting to major trade networks

#### 🟫 Dorsai Republic
- **Capital**: Fomalhaut (Valorgraemo)
- **Government**: Military Republic
- **Territory**: 1 system (Fomalhaut)
- **Specialty**: Elite military training, tactical defense
- **Trade Routes**: 6 routes focused on military alliance support

#### 🟣 Pentothian Trade Conglomerate
- **Capital**: Pentothia Prime (GJ 380)
- **Government**: Trade Conglomerate
- **Territory**: 1 system but extensive trade network
- **Specialty**: Neutral trade, inter-faction commerce
- **Trade Routes**: 15 routes spanning entire galaxy

### Trade Network Analysis
- **Total Routes**: 28 comprehensive trade routes
- **Route Categories**: 8 types from administrative to mining
- **Economic Zones**: 2 major zones with different regulations
- **Coverage**: Spans 25+ star systems across 200+ light years

### Stellar Geography
- **Galactic Sectors**: 8 color-coded regions
- **Core Systems**: High-security Terran space
- **Rimward Frontier**: Felgenland and allied territories
- **Neutral Zones**: Independent and contested systems
- **Frontier Space**: Exploration and mining outposts

## 🧪 Data Analysis Reports

### System Verification
- **[Planetary Systems Analysis](PLANETARY_SYSTEMS_ANALYSIS.md)** - Comprehensive report on planetary system data integrity, migration status, and system verification
- **Star Catalog Validation** - All 24,670+ stars verified against astronomical databases
- **Trade Route Verification** - All 28 routes validated for system connectivity

### Data Quality Metrics
- **Real Stars**: 24,670+ from Hipparcos catalog (100% verified)
- **Fictional Stars**: 13 custom additions (consistent with constraints)
- **Planetary Systems**: 6 detailed systems with 29+ planets
- **Political Entities**: 5 nations with complete profiles
- **Trade Routes**: 28 routes with full economic data

## 🔧 Performance & Optimization

### Recommended Settings
- **Star Limit**: 1000-2000 for optimal performance
- **Magnitude Limit**: 6.0 or lower for large datasets
- **Memory**: 4GB+ RAM for smooth operation
- **Browser**: Chrome or Firefox for best WebGL performance

### Large Dataset Handling
- **Caching**: Intelligent caching for frequently accessed data
- **Filtering**: Real-time filtering without full dataset reload
- **Pagination**: Efficient data loading for large result sets
- **Compression**: Optimized data transfer for network efficiency

### Network Deployment
- **Port Configuration**: Default 8080 (configurable)
- **Firewall**: Ensure port access for network sharing
- **Performance**: Recommended 1Mbps+ for smooth operation

## 🛠️ Customization Guide

### Adding New Content
1. **New Star Systems**: Edit `fictional_stars.csv` and restart
2. **New Planets**: Use `/api/planet/add` endpoint or edit `fictional_planets.py`
3. **New Nations**: Modify `nations_data.json` with territories and properties
4. **New Trade Routes**: Add to `trade_routes_data.json` with route details

### Configuration Options
- **Star Limits**: Adjust in UI controls or API parameters
- **Political Colors**: Modify nation color codes in `nations_data.json`
- **Coordinate System**: Customize in `galactic_directions.py`
- **Region Boundaries**: Edit `stellar_regions.json` for custom galactic sectors

## 🚨 Troubleshooting

### Common Issues
**Server Connection Problems**
```bash
# Check Python version
python --version  # Should be 3.8+

# Verify virtual environment
source starmap_venv/bin/activate
pip list | grep -E "(Flask|plotly|pandas)"
```

**Performance Issues**
- Reduce star count in magnitude controls
- Lower magnitude limit to show fewer stars
- Close unnecessary browser tabs
- Use Chrome/Firefox for better WebGL support

**Data Loading Problems**
- Ensure all CSV files are in root directory
- Check file permissions (readable)
- Verify UTF-8 encoding
- Look for error messages in browser console

**Network Access Issues**
```bash
# Find your IP address
ifconfig | grep "inet " | grep -v 127.0.0.1  # Mac/Linux
ipconfig | findstr "IPv4"                     # Windows
```

**Political Overlays Not Working**
- Check browser console for JavaScript errors
- Verify `nations_data.json` is valid JSON
- Ensure Flask loaded nations data successfully
- Try refreshing with hard reload (Ctrl+F5)

### Performance Optimization
- **Memory**: 8GB+ RAM recommended for large datasets
- **Network**: 1Mbps+ for smooth real-time updates
- **Storage**: 100MB+ free space for caching
- **GPU**: Dedicated graphics card helps with WebGL performance

## 📄 License & Usage

This project is designed for personal and educational use in science fiction writing and world-building. The astronomical data is from public catalogs. See [LICENSE](LICENSE) for complete terms.

## 🤝 Contributing & Adaptation

### For Science Fiction Writers
1. **Fork** this repository for your own universe
2. **Modify** `nations_data.json` for your political entities
3. **Update** `trade_routes_data.json` for your economic systems
4. **Customize** `fictional_planets.py` for your worlds
5. **Share** your creation with the community!

### Development Guidelines
- Follow MVC architecture patterns
- Add comprehensive API documentation
- Include data validation and error handling
- Test with various dataset sizes
- Maintain backward compatibility

---

**🌟 Ready to explore the galaxy?** Start with the [Installation Guide](#-installation) or dive into the [Planetary System Guide](PLANETARY_SYSTEM_GUIDE.md) to begin building your own worlds!

**📚 Need help?** Check the [Documentation Hub](#-documentation-hub) for comprehensive guides and tutorials.

**🔧 Having issues?** See the [Troubleshooting](#-troubleshooting) section for common solutions.