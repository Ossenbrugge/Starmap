# Trade Routes Data Structure

## Overview
Trade routes have been separated from the main nations data to allow for easier updates and maintenance. This separation enables users to modify trade routes without affecting nation data and vice versa. The database now contains **28 comprehensive trade routes** across 8 categories, covering the entire Felgenland Saga universe.

## File Structure

### Core Files
- **`trade_routes_data.json`** - Main trade routes database (Version 2.0)
- **`trade_routes.py`** - Python module for loading and managing trade routes
- **`nations_data.json`** - Nations data (trade routes section removed)
- **`fictional_nations.py`** - Updated to exclude trade routes

### Data Files
- **`trade_routes_data.json`** contains all trade route information organized by categories:
  - `terran_primary_routes` - Terran Directorate routes (6 routes)
  - `felgenland_routes` - Felgenland Union routes (3 routes)
  - `protelani_routes` - Protelani Republic routes (3 routes) 
  - `dorsai_routes` - Dorsai Republic routes (2 routes)
  - `neutral_routes` - Neutral Zone/Pentothian routes (5 routes)
  - `frontier_routes` - Frontier exploration routes (4 routes)
  - `research_routes` - Research outpost routes (3 routes)
  - `mining_routes` - Mining colony routes (2 routes)

## Usage

### Adding New Trade Routes
1. Edit `trade_routes_data.json`
2. Add new routes to the appropriate category
3. Restart the application to load changes

### Trade Route Properties
Each route includes:
- `name` - Route display name
- `from_star_id` / `to_star_id` - Connected star systems
- `from_system` / `to_system` - System names
- `route_type` - Route classification (Primary Trade, Administrative, etc.)
- `established` - Year established
- `cargo_types` - Array of cargo types
- `travel_time_days` - Travel time in days
- `frequency` - Shipping frequency
- `controlling_nation` - Nation controlling the route
- `security_level` - Security classification
- `description` - Route description
- `regions` - Galactic regions the route traverses
- `economic_zone` - Economic zone classification

### Route Categories Explained

#### Major Nation Routes
- **Terran Primary Routes**: Core Directorate routes connecting Sol, Alpha Centauri, Sirius, Proxima Centauri, and Wolf 359
- **Felgenland Routes**: Internal Union routes connecting Holsten Tor, Brandenburg Tor, Griefen Tor, and Tiefe-Grenze Tor
- **Protelani Routes**: Corporate republic routes linking Protelan to Union and Directorate systems
- **Dorsai Routes**: Military alliance routes connecting Dorsai Republic to allied systems

#### Neutral & Frontier Routes
- **Neutral Routes**: Pentothian Trade Network routes connecting GJ 380 to major systems
- **Frontier Routes**: Long-range exploration and colony routes to distant systems
- **Research Routes**: Scientific outpost supply routes to research stations
- **Mining Routes**: Industrial supply routes to mining colonies

#### Route Types
- **Administrative**: Government and bureaucratic transport
- **Industrial**: Manufacturing and industrial supply
- **Colonial Supply**: Colony support and frontier logistics
- **Research/Military**: Scientific and defense operations
- **Internal Trade**: Nation-internal commerce
- **Resource Supply**: Raw material transport
- **Primary Trade**: Major commercial corridors
- **Inter-Nation Trade**: Cross-nation commerce
- **Military Alliance**: Defense cooperation routes
- **Defense Contract**: Security service routes
- **Neutral Trade**: Independent trader routes
- **Frontier Trade**: Exploration and colonization routes
- **Research Supply**: Scientific outpost support
- **Mining Supply**: Industrial extraction support

### Python API
```python
from trade_routes import get_all_trade_routes, get_trade_routes_summary

# Get all routes
routes = get_all_trade_routes()

# Get summary statistics
summary = get_trade_routes_summary()

# Get routes for specific nation
from trade_routes import get_trade_routes_by_nation
felgenland_routes = get_trade_routes_by_nation('felgenland_union')
```

### REST API
- `GET /api/trade-routes` - Get all trade routes with summary statistics
- `GET /api/nation/{nation_id}/routes` - Get routes for specific nation
- `GET /api/trade-route/{star1_id}/{star2_id}` - Find route between stars

## Benefits
1. **Easier Updates** - Trade routes can be modified without affecting nation data
2. **Cleaner Organization** - Separate concerns for nations vs. trade networks
3. **Better Maintainability** - Changes to trade routes don't require nation data reloads
4. **Extensibility** - New trade route types can be added easily

## Migration
The system automatically imports trade routes from the new module. No changes are needed to existing API calls or JavaScript code.