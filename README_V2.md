# Starmap - Felgenland Saga (Technical Documentation)

> **📚 Documentation Guide**  
> - For **Quick Start and User Guide**: See [README.md](README.md)  
> - For **Technical Architecture**: This document  
> - For **MontyDB Features**: See [README_MONTYDB.md](README_MONTYDB.md)

A comprehensive 3D interactive starmap application for the Felgenland Saga universe, built with modern Flask architecture, integrated authentication, and featuring real astronomical data enhanced with fictional political entities.

## 🚀 Quick Start

```bash
# Install dependencies
pip install -r requirements.txt

# Run the application
python app.py
```

The app will be available at `http://localhost:8080`

**Authentication required**: Login with `admin` / `felgenland_secure_2025` or `starmap_admin` / `galactic_command_auth`

## 📁 Project Structure

```
starmap/
├── app.py                    # Main Flask application with integrated auth
├── auth.py                   # Authentication system (Flask-Login + JWT)
├── controllers/              # API controllers
│   └── api_controller.py     # RESTful API endpoints
├── models/                   # Data models (hybrid JSON + MontyDB)
│   ├── database.py           # JSON-based database with caching
│   ├── star_model_db.py      # MontyDB star model (optional)
│   ├── nation_model_db.py    # MontyDB nation model (optional)
│   └── ...                   # Other MontyDB models
├── database/                 # MontyDB configuration (optional)
│   └── config.py             # Database initialization
├── handlers/                 # Entity management handlers
│   ├── star_handler.py       # Star CRUD operations
│   ├── nation_handler.py     # Nation CRUD operations
│   └── ...                   # Other entity handlers
├── static/                   # Frontend assets
│   ├── css/starmap.css       # Space-themed styles
│   └── js/                   # 3D visualization JavaScript
│       ├── starmap.js        # Plotly.js version
│       └── starmap-threejs.js # Three.js version
├── templates/                # HTML templates
│   ├── starmap.html          # Main starmap interface
│   └── login.html            # Authentication interface
├── tests/                    # Test suite (organized)
│   ├── test_api_auth.py      # Authentication tests
│   ├── test_performance.py   # Performance tests
│   └── ...                   # Other test files
├── data/                     # All data files (consolidated)
│   ├── stars.json            # 24,676 real stars from Gaia/Hipparcos
│   ├── nations.json          # 5 political nations with territories
│   ├── trade_routes.json     # 18 trade and military routes
│   ├── exoplanets.json       # 425 real exoplanets (NASA archive)
│   ├── fictional_stars.csv   # 1 fictional star (Tiefe-Grenze Tor)
│   ├── exoplanet_catalog_*.csv # 41 fictional planets + real data
│   ├── stellar_regions.json  # Galactic octants (30 parsec scale)
│   └── starmap.db/           # MontyDB database files (optional)
└── backup_*/                 # Data backups from migrations
```

## ✨ Core Features

### Universe Scope
- **30 parsec sphere** around Sol representing human expansion limits
- **Real astronomical data** from multiple space catalogs
- **Fictional political overlay** with territories and trade networks
- **Enhanced planetary systems** for major political capitals

### Interactive Starmap
- **3D WebGL visualization** with Three.js/Plotly.js rendering options
- **Real-time navigation** with mouse controls
- **Advanced filtering** by magnitude, spectral type, distance
- **Political overlays** showing nation territories and borders
- **Trade route visualization** with economic and military networks
- **Stellar regions** displaying galactic octants and directions
- **Secure access** with user authentication

### Data Management
- **Hybrid database** system (JSON + optional MontyDB)
- **RESTful API** with authentication and standardized responses
- **Real vs fictional classification** for all astronomical objects
- **Search functionality** with fuzzy matching algorithms
- **CRUD operations** for fictional entities with proper validation
- **Performance caching** for frequently accessed data

## 🏛️ Political Nations

### Major Powers
1. **Terran Directorate** (Sol) - Earth-centered authoritarian republic
2. **Felgenland Union** - Trade federation with Eclipse Festival culture
   - Capital: **Holsten Tor** (20 LMi) with Stahlburgh world
   - Territories: 20 LMi, 11 LMi, 55 Cancri, HD 86729
3. **Protelani Republic** - Ultra-capitalist republic
   - Capital: **61 Ursae Majoris** with Protelan habitable moon
4. **Dorsai Republic** - Elite military training specialists
   - Capital: **Fomalhaut** with Valorgraemo academy world
5. **Pentothian Trade Conglomerate** - Neutral reptilian traders
   - Capital: **Pentothia Prime** (Groombridge 1618)

### Trade Networks
- **18 active trade routes** connecting major systems
- **Economic zones** with different trade regulations
- **Military supply lines** for alliance coordination
- **Neutral trade corridors** facilitated by Pentothian merchants

## 🌍 Planetary Systems

### Fictional Worlds (41 total)
- **Stahlburgh** - Felgenland Union capital (Earth-like, 1.4g)
- **Protelan** - Protelani Republic capital moon (0.9g, Scandinavian culture)
- **Valorgraemo** - Dorsai military academy world
- **Tiefe-Grenze Tor** system - Frontier gateway with 4 worlds
- **Brandenburg/Griefen Tor** - Manufacturing and resource hubs

### Real Exoplanets (425 confirmed)
- **NASA Exoplanet Archive** data with discovery methods
- **Distance filtering** to 30 parsec limit
- **Habitability classification** for potentially habitable worlds
- **Host star association** with political territories

## 🔌 API Architecture

### Protected Endpoints (Require Authentication)
- `GET /api/stars` - Filtered star data with political associations
- `GET /api/star/{id}` - Detailed star info including planets
- `GET /api/nations` - Political entities with territories and capitals
- `GET /api/trade-routes` - Economic and military route networks
- `GET /api/search` - Star search with fuzzy matching
- `POST /api/fictional/*` - CRUD operations for fictional entities

### Public Endpoints
- `GET /api/fictional-exoplanets` - Enhanced planetary systems
- `GET /api/exoplanets` - Real exoplanet data
- `GET /api/stellar-regions` - Galactic octants and regions
- `GET /api/galactic-directions` - Navigation references
- `GET /api/stats` - Basic database statistics

### Authentication Endpoints
- `POST /login` - User login with session management
- `GET /logout` - User logout
- `POST /api/auth/token` - JWT token generation for API access

### Response Format
```json
{
  "success": true,
  "data": [...],
  "message": "Optional status message"
}
```

### Error Handling
- Standardized error responses with HTTP status codes
- Graceful fallbacks for missing data
- Input validation and sanitization

## 🎮 User Interface

### Control Panel
- **Search functionality** with autocomplete
- **Filter controls** for magnitude, spectral type, star count
- **Overlay toggles** for nations, trade routes, regions
- **Statistics display** with real-time data counts

### 3D Visualization
- **Mouse controls**: Rotate, zoom, pan
- **Star selection** with detailed information panels
- **Color coding** for spectral types and political affiliations
- **Overlay rendering** for territories and trade routes

### Responsive Design
- **Bootstrap 5** framework with custom space theme
- **Mobile-friendly** controls and layouts
- **Dark theme** optimized for starmap visualization

## ⚡ Performance Optimizations

### Data Layer
- **In-memory caching** of all star and political data
- **Efficient filtering** with pre-computed indices
- **Lazy loading** of detailed planetary information
- **JSON compression** for network transfer

### Frontend
- **WebGL acceleration** for 3D rendering
- **Batch updates** for overlay changes
- **Debounced search** to reduce API calls
- **Progressive loading** for large datasets

## 🧹 Development History

### Latest Updates (v0.0.1+)
This version represents a major consolidation and security enhancement:
- ✅ **Integrated authentication** with Flask-Login and JWT support
- ✅ **Merged security features** from separate secure version
- ✅ **Organized test suite** in dedicated `tests/` directory
- ✅ **Enhanced API protection** with authentication requirements
- ✅ **Hybrid database support** with optional MontyDB features
- ✅ **Updated documentation** for current architecture

### Previous Cleanup Summary
- ✅ **Removed legacy V1 architecture** and duplicate files
- ✅ **Consolidated all data** to single `/data` directory
- ✅ **Streamlined to single Flask app** with clean MVC pattern
- ✅ **Updated all file paths** and import references
- ✅ **Preserved all functionality** while improving maintainability
- ✅ **Enhanced with fictional planets** across major political systems
- ✅ **Fixed real vs fictional classification** for all astronomical objects

### Current State
- **Single unified application** with integrated security
- **Clean, secure codebase** following modern Python/Flask patterns
- **Complete universe data** for Felgenland Saga setting
- **Production-ready** with authentication, error handling, and optimization
- **Organized test suite** for quality assurance

Legacy files and backups are preserved for rollback if needed.

---

*Technical documentation for the **Starmap - Felgenland Saga** universe visualization platform.*