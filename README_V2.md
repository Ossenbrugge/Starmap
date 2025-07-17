# Starmap - Felgenland Saga (Technical Documentation)

A comprehensive 3D interactive starmap application for the Felgenland Saga universe, built with modern Flask architecture and featuring real astronomical data enhanced with fictional political entities.

## 🚀 Quick Start

```bash
# Install dependencies
pip install -r requirements.txt

# Run the application
python app.py
```

The app will be available at `http://localhost:8080`

## 📁 Project Structure

```
starmap/
├── app.py                    # Main Flask application - Felgenland Saga
├── controllers/              # API controllers
│   └── api_controller.py     # RESTful API endpoints
├── models/                   # Data models
│   └── database.py           # JSON-based database with caching
├── static/                   # Frontend assets
│   ├── css/starmap.css       # Space-themed styles
│   └── js/starmap.js         # 3D visualization JavaScript
├── templates/                # HTML templates
│   └── starmap.html          # Main starmap interface
├── data/                     # All data files (consolidated)
│   ├── stars.json            # 24,676 real stars from Gaia/Hipparcos
│   ├── nations.json          # 5 political nations with territories
│   ├── trade_routes.json     # 18 trade and military routes
│   ├── exoplanets.json       # 425 real exoplanets (NASA archive)
│   ├── fictional_stars.csv   # 1 fictional star (Tiefe-Grenze Tor)
│   ├── exoplanet_catalog_*.csv # 41 fictional planets + real data
│   └── stellar_regions.json  # Galactic octants (30 parsec scale)
└── _cleanup_backup/          # Legacy files (safe to delete)
```

## ✨ Core Features

### Universe Scope
- **30 parsec sphere** around Sol representing human expansion limits
- **Real astronomical data** from multiple space catalogs
- **Fictional political overlay** with territories and trade networks
- **Enhanced planetary systems** for major political capitals

### Interactive Starmap
- **3D WebGL visualization** with Plotly.js rendering
- **Real-time navigation** with mouse controls
- **Advanced filtering** by magnitude, spectral type, distance
- **Political overlays** showing nation territories and borders
- **Trade route visualization** with economic and military networks
- **Stellar regions** displaying galactic octants and directions

### Data Management
- **JSON-based database** with in-memory caching for performance
- **RESTful API** with standardized response formatting
- **Real vs fictional classification** for all astronomical objects
- **Search functionality** with fuzzy matching algorithms

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

### Core Endpoints
- `GET /api/stars` - Filtered star data with political associations
- `GET /api/star/{id}` - Detailed star info including planets
- `GET /api/nations` - Political entities with territories and capitals
- `GET /api/trade-routes` - Economic and military route networks
- `GET /api/fictional-exoplanets` - Enhanced planetary systems
- `GET /api/stellar-regions` - Galactic octants and regions
- `GET /api/search` - Star search with fuzzy matching

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

### Cleanup Summary
This version represents a major consolidation:
- ✅ **Removed legacy V1 architecture** and duplicate files
- ✅ **Consolidated all data** to single `/data` directory
- ✅ **Streamlined to single Flask app** with clean MVC pattern
- ✅ **Updated all file paths** and import references
- ✅ **Preserved all functionality** while improving maintainability
- ✅ **Enhanced with fictional planets** across major political systems
- ✅ **Fixed real vs fictional classification** for all astronomical objects

### Current State
- **Single application** with no legacy dependencies
- **Clean codebase** following modern Python/Flask patterns
- **Complete universe data** for Felgenland Saga setting
- **Production-ready** with error handling and optimization

Legacy files are safely stored in `_cleanup_backup/` and can be deleted once satisfied with the cleanup.

---

*Technical documentation for the **Starmap - Felgenland Saga** universe visualization platform.*