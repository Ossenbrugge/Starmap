# Starmap - Felgenland Saga

A 3D interactive starmap for the **Felgenland Saga** universe, featuring real astronomical data enhanced with fictional political entities, trade networks, and planetary systems.

## 🌌 Universe Overview

The **Felgenland Saga** is set in a region of space within 30 parsecs of Earth, where human civilization has expanded to form competing nations and trade networks. This starmap brings that universe to life with:

- **Real astronomical data** from Gaia, Hipparcos, and NASA catalogs
- **Fictional political nations** with territories and capitals
- **Trade routes** connecting major systems
- **Enhanced planetary systems** including habitable worlds and capitals

## ✨ Features

### Core Universe
- **24,676 Real Stars** with accurate astronomical data from multiple catalogs
- **5 Major Nations** controlling territories across human space:
  - **Terran Directorate** - Earth-centered authoritarian republic
  - **Felgenland Union** - Trade federation with Eclipse Festival culture
  - **Protelani Republic** - Ultra-capitalist republic on Protelan moon
  - **Dorsai Republic** - Elite military training specialists
  - **Pentothian Trade Conglomerate** - Neutral reptilian traders
- **18 Trade Routes** connecting capitals and resource systems
- **41 Fictional Planets** across key star systems including:
  - **Stahlburgh** - Capital of Felgenland Union (20 LMi system)
  - **Protelan** - Protelani Republic capital moon (61 UMa system)
  - **Pentothia Prime** - Reptilian trade hub (Groombridge 1618)
  - **Valorgraemo** - Dorsai military academy world (Fomalhaut)
- **425 Real Exoplanets** from NASA Exoplanet Archive

### Content Creation & Management
- **Fictional Entity Handlers** - Add new stars, planets, nations, and trade routes
- **Real-time Data Validation** - Ensures data integrity and cross-references
- **Automatic Coordinate Calculation** - 3D positioning from astronomical data
- **Dynamic Cache Management** - Instant updates when adding new content
- **RESTful API** - Complete CRUD operations for all entity types (requires authentication)

### Security & Authentication
- **Flask-Login Integration** - Session-based authentication for web interface
- **JWT Token Support** - API access tokens for external applications
- **Protected API Endpoints** - All data modification endpoints require authentication
- **User Management** - Built-in user system with configurable credentials

### Visualization & Interface
- **Interactive 3D Visualization** with political overlays
- **Real-time Search** and advanced filtering
- **Modern Responsive UI** with space-themed design
- **Secure Login Interface** - Space-themed authentication portal

## 🚀 Quick Start

1. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

2. **Run the application:**
   ```bash
   python app.py
   ```

3. **Open your browser to:** http://localhost:8080

4. **Login with default credentials:**
   - Username: `admin` / Password: `felgenland_secure_2025`
   - Username: `starmap_admin` / Password: `galactic_command_auth`
   
   **⚠️ Change these passwords in production!**

---

## 📚 Documentation Navigation

### Core Documentation
- **[README_V2.md](README_V2.md)** - Technical architecture and implementation details
- **[README_MONTYDB.md](README_MONTYDB.md)** - MontyDB enhanced features guide

### Detailed Guides
- **[API_REFERENCE.md](API_REFERENCE.md)** - Complete API documentation with examples
- **[HANDLERS_DOCUMENTATION.md](HANDLERS_DOCUMENTATION.md)** - Detailed handler implementation guide
- **[DATA_MANAGEMENT_GUIDE.md](DATA_MANAGEMENT_GUIDE.md)** - Data management workflows and comparison
- **[DEVELOPMENT.md](DEVELOPMENT.md)** - Development setup and contribution guide
- **[DOCUMENTATION_INDEX.md](DOCUMENTATION_INDEX.md)** - Complete documentation navigation hub

---

## 🛠️ API Reference

### Fictional Entity Management

The Starmap includes handlers for managing fictional content through RESTful API endpoints:

#### Fictional Stars
- `GET /api/fictional/stars` - Get all fictional stars
- `POST /api/fictional/stars` - Add a new fictional star
- `DELETE /api/fictional/stars/<star_id>` - Delete a fictional star

**Example JSON for adding a fictional star:**
```json
{
  "name": "New System Alpha",
  "ra": 180.5,
  "dec": 45.2,
  "dist": 25.0,
  "mag": 8.5,
  "spect": "G2V",
  "description": "A promising system for exploration"
}
```

#### Fictional Exoplanets
- `GET /api/fictional/exoplanets` - Get all fictional exoplanets
- `POST /api/fictional/exoplanets` - Add a new fictional exoplanet

**Example JSON for adding a fictional exoplanet:**
```json
{
  "name": "New World",
  "host_star_id": 999998,
  "orbital_period_days": 365.25,
  "semi_major_axis_au": 1.0,
  "radius_earth": 1.2,
  "mass_earth": 1.1,
  "description": "An Earth-like world"
}
```

#### Fictional Nations
- `GET /api/fictional/nations` - Get all fictional nations
- `POST /api/fictional/nations` - Add a new fictional nation
- `DELETE /api/fictional/nations/<nation_id>` - Delete a fictional nation

**Example JSON for adding a fictional nation:**
```json
{
  "name": "New Republic",
  "full_name": "The New Republic of Outer Systems",
  "government_type": "Federal Republic",
  "capital_system": "New Capital",
  "capital_star_id": 999997,
  "territories": [999997, 999996],
  "primary_color": "#FF6B35",
  "description": "A frontier republic"
}
```

#### Fictional Trade Routes
- `GET /api/fictional/trade-routes` - Get all fictional trade routes
- `POST /api/fictional/trade-routes` - Add a new fictional trade route
- `DELETE /api/fictional/trade-routes/<route_id>` - Delete a fictional trade route

**Example JSON for adding a fictional trade route:**
```json
{
  "name": "New Trade Corridor",
  "from_star_id": 999997,
  "to_star_id": 999996,
  "controlling_nation": "new_republic",
  "route_type": "Commercial",
  "cargo_types": ["Technology", "Raw Materials"],
  "frequency": "Daily"
}
```

### Handler Features

- **Data Validation**: All handlers validate required fields and cross-references
- **3D Coordinates**: Automatic calculation from astronomical data (RA/Dec/Distance)
- **Cache Management**: Database cache automatically updates when new entities are added
- **Error Handling**: Detailed error messages for validation failures
- **File Management**: Handles both JSON and CSV file formats as needed

See **[HANDLERS_DOCUMENTATION.md](HANDLERS_DOCUMENTATION.md)** for complete handler documentation.

## 🏛️ Major Star Systems

### Political Capitals
- **Sol** (Terran Directorate) - Earth and the Solar System
- **Holsten Tor** (20 LMi) - Felgenland Union capital with Stahlburgh world
- **61 Ursae Majoris** - Protelani Republic capital with Protelan moon
- **Fomalhaut** - Dorsai Republic with military training worlds
- **Pentothia Prime** (Groombridge 1618) - Neutral reptilian trade hub

### Key Frontier Systems
- **Tiefe-Grenze Tor** (HD 86729) - Deep frontier gateway of Felgenland Union
- **Brandenburg Tor** (11 LMi) - Manufacturing hub
- **Griefen Tor** (55 Cancri) - Resource extraction center

## 🛠️ Architecture

- **Backend**: Flask with clean MVC architecture and integrated authentication
- **Database**: Hybrid system with JSON-based storage + optional MontyDB for enhanced features
- **Frontend**: Modern JavaScript with Three.js for 3D visualization
- **UI**: Bootstrap 5 with custom space-themed styling
- **Security**: Flask-Login with JWT token support for API access

```
starmap/
├── app.py                    # Main Flask application with integrated auth
├── auth.py                   # Authentication system (Flask-Login + JWT)
├── controllers/              # API controllers
├── models/                   # Data models and database layers
├── handlers/                 # Entity management handlers
├── database/                 # MontyDB configuration (optional)
├── static/                   # Frontend assets (CSS, JS)
├── templates/                # HTML templates (starmap + login)
├── tests/                    # Organized test suite
└── data/                     # All data files (stars, nations, planets)
```

## 🔌 API Endpoints

### Authentication Required
- `GET /api/stars` - Get filtered star data
- `GET /api/star/{id}` - Get detailed star information with planets
- `GET /api/nations` - Get all political nations
- `GET /api/trade-routes` - Get trade and military routes
- `GET /api/search` - Search stars by name
- `POST /api/fictional/stars` - Add fictional stars
- `POST /api/fictional/nations` - Add fictional nations
- `POST /api/fictional/trade-routes` - Add trade routes
- `GET /api/network-analysis` - Get trade network analysis

### Public Access
- `GET /api/fictional-exoplanets` - Get fictional planetary systems
- `GET /api/exoplanets` - Get real exoplanet data
- `GET /api/stellar-regions` - Get galactic regions
- `GET /api/galactic-directions` - Get navigation references
- `GET /api/stats` - Get basic database statistics

### Authentication
- `POST /login` - Session-based login
- `POST /api/auth/token` - Generate JWT tokens
- `GET /logout` - Logout

## 🧪 Testing

Run the test suite from the tests directory:

```bash
# Run authentication tests (requires server to be running)
python tests/test_api_auth.py

# Run all tests
python -m pytest tests/
```

**Note**: Authentication tests require the server to be running on localhost:8080

## 🎮 Controls

- **Mouse**: Rotate, zoom, and pan the 3D starmap
- **Click**: Select stars for detailed information including planets
- **Search**: Find specific stars or systems
- **Filters**: Adjust magnitude, spectral type, and star count limits
- **Overlays**: Toggle nations, trade routes, galactic regions, and directions
- **Nations Legend**: View detailed information about political entities

## 📊 Data Sources

- **Real Stars**: Gaia DR3, Hipparcos, Henry Draper Catalog
- **Exoplanets**: NASA Exoplanet Archive with confirmed discoveries
- **Political Data**: Original Felgenland Saga universe lore
- **Trade Networks**: Custom economic and military route systems
- **Planetary Systems**: Mix of real confirmed planets and fictional worlds

## 🎯 Universe Scope

The starmap covers a **30 parsec sphere** around Sol, representing the practical limits of human expansion in the Felgenland Saga timeline. This includes:

- **Most stars visible to the naked eye**
- **All major nearby stellar neighbors**
- **Key systems for interstellar civilization**
- **Realistic travel distances for trade and politics**

## ⚡ Performance Features

- **In-memory data caching** for instant API responses
- **WebGL-accelerated 3D rendering** with smooth navigation
- **Efficient spatial filtering** for large star catalogs
- **Optimized search algorithms** with fuzzy matching
- **Responsive design** for desktop and mobile devices

## 📋 Current Status

**Version**: v0.0.1+  
**Status**: Development with integrated security  
**Features**: ✅ Authentication, ✅ 3D Visualization, ✅ API Protection, ✅ Test Suite  
**Database**: Hybrid JSON + optional MontyDB  
**Security**: Flask-Login + JWT tokens  

---

*Part of the **Felgenland Saga** universe - explore the political intrigue, trade networks, and frontier conflicts that define human expansion among the stars.*